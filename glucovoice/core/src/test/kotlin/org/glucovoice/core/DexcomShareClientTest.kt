package org.glucovoice.core

import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.contentOrNull
import java.io.IOException
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import kotlin.test.assertTrue

class DexcomShareClientTest {

    private class ScriptedTransport(vararg responses: HttpResponse) : HttpTransport {
        private val queue = ArrayDeque(responses.toList())
        val calls = mutableListOf<Pair<String, String>>()

        override fun postJson(url: String, body: String): HttpResponse {
            calls += url to body
            return queue.removeFirstOrNull() ?: error("unexpected request to $url")
        }
    }

    private fun ok(body: String) = HttpResponse(200, body)
    private fun shareError(code: String) = HttpResponse(500, """{"Code":"$code","Message":"x"}""")

    private val account = "\"aaaaaaaa-1111-2222-3333-444444444444\""
    private val session = "\"bbbbbbbb-1111-2222-3333-444444444444\""
    private val oneReading = """[{"WT":"Date(1691455258000)","Value":112,"Trend":"Flat"}]"""

    private fun bodyField(body: String, key: String) =
        ((ShareParser.json.parseToJsonElement(body) as JsonObject)[key] as JsonPrimitive).contentOrNull

    @Test
    fun `logs in with authenticate then loginById and posts to the readings endpoint`() {
        val transport = ScriptedTransport(ok(account), ok(session), ok(oneReading))
        val client = DexcomShareClient(ShareRegion.US, "me@example.com", "pw", transport)

        val latest = client.latest()

        assertEquals(112, latest?.mgdl)
        assertEquals(3, transport.calls.size)
        val (authUrl, authBody) = transport.calls[0]
        assertEquals(ShareRegion.US.baseUrl + DexcomShareClient.AUTHENTICATE, authUrl)
        assertEquals("me@example.com", bodyField(authBody, "accountName"))
        assertEquals("pw", bodyField(authBody, "password"))
        assertEquals(ShareRegion.US.applicationId, bodyField(authBody, "applicationId"))

        val (loginUrl, loginBody) = transport.calls[1]
        assertEquals(ShareRegion.US.baseUrl + DexcomShareClient.LOGIN_BY_ID, loginUrl)
        assertEquals("aaaaaaaa-1111-2222-3333-444444444444", bodyField(loginBody, "accountId"))

        val (readUrl, readBody) = transport.calls[2]
        assertTrue(readUrl.startsWith(ShareRegion.US.baseUrl + DexcomShareClient.READINGS + "?sessionId=bbbbbbbb-1111-2222-3333-444444444444"))
        assertTrue(readUrl.endsWith("&minutes=1440&maxCount=1"))
        assertEquals("{}", readBody)
    }

    @Test
    fun `japan region uses its own application id`() {
        val transport = ScriptedTransport(ok(account), ok(session), ok("[]"))
        DexcomShareClient(ShareRegion.JP, "me", "pw", transport).latest()
        assertEquals(ShareRegion.JP.applicationId, bodyField(transport.calls[0].second, "applicationId"))
        assertTrue(transport.calls[0].first.startsWith("https://share.dexcom.jp/"))
    }

    @Test
    fun `uuid username skips the authenticate step`() {
        val transport = ScriptedTransport(ok(session), ok(oneReading))
        DexcomShareClient(ShareRegion.US, "aaaaaaaa-1111-2222-3333-444444444444", "pw", transport).latest()
        assertEquals(2, transport.calls.size)
        assertTrue(transport.calls[0].first.endsWith(DexcomShareClient.LOGIN_BY_ID))
    }

    @Test
    fun `expired session triggers exactly one re-login without re-authenticating`() {
        val transport = ScriptedTransport(
            ok(account), ok(session), ok(oneReading),        // first call
            shareError("SessionNotValid"), ok(session), ok(oneReading), // second call: expired -> relogin -> ok
        )
        val client = DexcomShareClient(ShareRegion.US, "me", "pw", transport)
        client.latest()
        client.latest()
        assertEquals(6, transport.calls.size)
        assertTrue(transport.calls[4].first.endsWith(DexcomShareClient.LOGIN_BY_ID), "re-login uses cached account id")
    }

    @Test
    fun `second session failure surfaces as Session error not an infinite loop`() {
        val transport = ScriptedTransport(ok(account), ok(session), shareError("SessionNotValid"), ok(session), shareError("SessionIdNotFound"))
        assertFailsWith<GlucoseSourceException.Session> {
            DexcomShareClient(ShareRegion.US, "me", "pw", transport).latest()
        }
        assertEquals(5, transport.calls.size)
    }

    @Test
    fun `bad password is an Auth error`() {
        val transport = ScriptedTransport(shareError("AccountPasswordInvalid"))
        assertFailsWith<GlucoseSourceException.Auth> {
            DexcomShareClient(ShareRegion.US, "me", "wrong", transport).login()
        }
    }

    @Test
    fun `blank credentials fail before any network call`() {
        val transport = ScriptedTransport()
        assertFailsWith<GlucoseSourceException.Auth> { DexcomShareClient(ShareRegion.US, "", "pw", transport).login() }
        assertFailsWith<GlucoseSourceException.Auth> { DexcomShareClient(ShareRegion.US, "me", " ", transport).login() }
        assertEquals(0, transport.calls.size)
    }

    @Test
    fun `all-zero account id means unknown account`() {
        val transport = ScriptedTransport(ok("\"${DexcomShareClient.DEFAULT_UUID}\""))
        assertFailsWith<GlucoseSourceException.Auth> {
            DexcomShareClient(ShareRegion.US, "me", "pw", transport).login()
        }
    }

    @Test
    fun `io failure is a Network error`() {
        val transport = HttpTransport { _, _ -> throw IOException("offline") }
        assertFailsWith<GlucoseSourceException.Network> {
            DexcomShareClient(ShareRegion.US, "me", "pw", transport).latest()
        }
    }

    @Test
    fun `non-json body is a Server error`() {
        val transport = ScriptedTransport(HttpResponse(200, "<html>maintenance</html>"))
        assertFailsWith<GlucoseSourceException.Server> {
            DexcomShareClient(ShareRegion.US, "me", "pw", transport).login()
        }
        val transport2 = ScriptedTransport(HttpResponse(502, "Bad Gateway"))
        assertFailsWith<GlucoseSourceException.Server> {
            DexcomShareClient(ShareRegion.US, "me", "pw", transport2).login()
        }
    }

    @Test
    fun `empty readings list yields null latest`() {
        val transport = ScriptedTransport(ok(account), ok(session), ok("[]"))
        assertNull(DexcomShareClient(ShareRegion.US, "me", "pw", transport).latest())
    }

    @Test
    fun `argument ranges are enforced`() {
        val client = DexcomShareClient(ShareRegion.US, "me", "pw", ScriptedTransport())
        assertFailsWith<IllegalArgumentException> { client.recent(minutes = 0) }
        assertFailsWith<IllegalArgumentException> { client.recent(maxCount = 289) }
    }
}
