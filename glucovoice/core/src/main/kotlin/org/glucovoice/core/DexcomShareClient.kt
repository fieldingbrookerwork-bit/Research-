package org.glucovoice.core

import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.put
import java.io.IOException
import java.net.URLEncoder

/**
 * Reads real-time glucose values through Dexcom Share, the same undocumented service the Dexcom
 * Follow app uses. The user logs in with their own Dexcom account (the publisher, not a follower).
 *
 * Flow: AuthenticatePublisherAccount (username -> account ID) -> LoginPublisherAccountById
 * (account ID -> session ID) -> ReadPublisherLatestGlucoseValues. Expired sessions are renewed
 * once automatically. If [username] is already an account UUID the first step is skipped.
 *
 * This is not an official API. Dexcom can change or shut it off at any time; see docs/DATA_SOURCES.md.
 */
class DexcomShareClient(
    private val region: ShareRegion,
    private val username: String,
    private val password: String,
    private val transport: HttpTransport = UrlConnectionTransport(),
) : GlucoseSource {

    private val lock = Any()

    @Volatile
    private var accountId: String? = if (UUID_REGEX.matches(username)) username else null

    @Volatile
    private var sessionId: String? = null

    val isLoggedIn: Boolean get() = sessionId != null

    override fun latest(): GlucoseReading? = recent(minutes = MAX_MINUTES, maxCount = 1).firstOrNull()

    override fun recent(minutes: Int, maxCount: Int): List<GlucoseReading> {
        require(minutes in 1..MAX_MINUTES) { "minutes must be within 1..$MAX_MINUTES" }
        require(maxCount in 1..MAX_COUNT) { "maxCount must be within 1..$MAX_COUNT" }
        if (sessionId == null) login()
        return try {
            fetchReadings(minutes, maxCount)
        } catch (expired: GlucoseSourceException.Session) {
            login()
            fetchReadings(minutes, maxCount)
        }
    }

    /** Authenticates and opens a session. Also the cheapest way to validate credentials. */
    fun login() {
        synchronized(lock) {
            if (username.isBlank()) throw GlucoseSourceException.Auth("Username is empty")
            if (password.isBlank()) throw GlucoseSourceException.Auth("Password is empty")
            val account = accountId ?: post(
                AUTHENTICATE,
                buildJsonObject {
                    put("accountName", username)
                    put("password", password)
                    put("applicationId", region.applicationId)
                }.toString(),
            ).asUuid("account ID").also { accountId = it }
            sessionId = post(
                LOGIN_BY_ID,
                buildJsonObject {
                    put("accountId", account)
                    put("password", password)
                    put("applicationId", region.applicationId)
                }.toString(),
            ).asUuid("session ID")
        }
    }

    private fun fetchReadings(minutes: Int, maxCount: Int): List<GlucoseReading> {
        val sid = sessionId ?: throw GlucoseSourceException.Session("No Dexcom Share session")
        val endpoint = "$READINGS?sessionId=${URLEncoder.encode(sid, "UTF-8")}&minutes=$minutes&maxCount=$maxCount"
        return ShareParser.parseReadings(post(endpoint, "{}"))
    }

    private fun post(endpoint: String, body: String): JsonElement {
        val response = try {
            transport.postJson(region.baseUrl + endpoint, body)
        } catch (e: IOException) {
            throw GlucoseSourceException.Network("Could not reach Dexcom Share", e)
        }
        val element = try {
            ShareParser.json.parseToJsonElement(response.body)
        } catch (e: Exception) {
            throw GlucoseSourceException.Server(
                if (response.status in 200..299) "Dexcom Share returned malformed JSON"
                else "Dexcom Share returned HTTP ${response.status}",
            )
        }
        if (response.status !in 200..299) throw ShareParser.errorFor(element, response.status)
        return element
    }

    private fun JsonElement.asUuid(what: String): String {
        val value = (this as? JsonPrimitive)?.contentOrNull
        if (value == null || !UUID_REGEX.matches(value)) {
            throw GlucoseSourceException.Server("Dexcom Share returned an invalid $what")
        }
        if (value == DEFAULT_UUID) throw GlucoseSourceException.Auth("Dexcom Share did not recognize this account")
        return value
    }

    companion object {
        const val MAX_MINUTES = 1440
        const val MAX_COUNT = 288
        const val AUTHENTICATE = "General/AuthenticatePublisherAccount"
        const val LOGIN_BY_ID = "General/LoginPublisherAccountById"
        const val READINGS = "Publisher/ReadPublisherLatestGlucoseValues"
        const val DEFAULT_UUID = "00000000-0000-0000-0000-000000000000"
        val UUID_REGEX = Regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    }
}
