package org.glucovoice.core

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.doubleOrNull
import kotlinx.serialization.json.intOrNull
import java.time.Instant

/** Parses Dexcom Share JSON. Kept separate from the client so it is trivially testable. */
object ShareParser {
    val json: Json = Json { ignoreUnknownKeys = true; isLenient = true }

    // Share encodes times as "Date(1691455258000)" or "Date(1691455258000-0400)". The number is
    // epoch milliseconds; the optional suffix is a display offset we do not need.
    private val DATE_REGEX = Regex("""Date\((-?\d+)(?:[+-]\d{4})?\)""")

    fun parseReadings(element: JsonElement): List<GlucoseReading> {
        val array = element as? JsonArray
            ?: throw GlucoseSourceException.Server("Dexcom Share did not return a list of readings")
        return array.map(::parseReading).sortedByDescending { it.time }
    }

    fun parseReading(element: JsonElement): GlucoseReading {
        val obj = element as? JsonObject
            ?: throw GlucoseSourceException.Server("Dexcom Share reading is not an object")
        val valuePrim = obj["Value"] as? JsonPrimitive
        val value = valuePrim?.intOrNull ?: valuePrim?.doubleOrNull?.toInt()
            ?: throw GlucoseSourceException.Server("Dexcom Share reading has no Value")
        val trend = Trend.fromShare((obj["Trend"] as? JsonPrimitive)?.contentOrNull)
        val rawTime = (obj["WT"] as? JsonPrimitive)?.contentOrNull
            ?: (obj["ST"] as? JsonPrimitive)?.contentOrNull
        val time = parseShareDate(rawTime)
            ?: throw GlucoseSourceException.Server("Dexcom Share reading has no usable timestamp")
        return GlucoseReading(value, trend, time)
    }

    fun parseShareDate(raw: String?): Instant? {
        if (raw == null) return null
        val match = DATE_REGEX.find(raw) ?: return null
        return Instant.ofEpochMilli(match.groupValues[1].toLong())
    }

    /** Maps a Share error body (`{"Code": ..., "Message": ...}`) to a typed exception. */
    fun errorFor(element: JsonElement, status: Int): GlucoseSourceException {
        val obj = element as? JsonObject
        val code = (obj?.get("Code") as? JsonPrimitive)?.contentOrNull
        val message = (obj?.get("Message") as? JsonPrimitive)?.contentOrNull ?: ""
        return when (code) {
            "SessionIdNotFound", "SessionNotValid" ->
                GlucoseSourceException.Session("Dexcom Share session expired")
            "AccountPasswordInvalid" ->
                GlucoseSourceException.Auth("Dexcom rejected the username or password")
            "SSO_AuthenticateMaxAttemptsExceeded" ->
                GlucoseSourceException.Auth("Too many failed logins. Wait a while before trying again")
            "SSO_InternalError" ->
                if ("Cannot Authenticate" in message) GlucoseSourceException.Auth("Dexcom rejected the username or password")
                else GlucoseSourceException.Server("Dexcom Share internal error: $message")
            "InvalidArgument" ->
                GlucoseSourceException.Auth("Dexcom Share rejected the login details: $message")
            null -> GlucoseSourceException.Server("Dexcom Share returned HTTP $status")
            else -> GlucoseSourceException.Server("Dexcom Share error $code: $message")
        }
    }
}
