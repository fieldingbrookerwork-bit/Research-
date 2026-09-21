package org.glucovoice.core

import java.time.Instant
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertIs
import kotlin.test.assertNull

class ShareParserTest {

    @Test
    fun `parses share date with and without display offset`() {
        assertEquals(Instant.ofEpochMilli(1691455258000), ShareParser.parseShareDate("Date(1691455258000)"))
        assertEquals(Instant.ofEpochMilli(1691455258000), ShareParser.parseShareDate("Date(1691455258000-0400)"))
        assertEquals(Instant.ofEpochMilli(1691455258000), ShareParser.parseShareDate("/Date(1691455258000+0100)/"))
        assertNull(ShareParser.parseShareDate("garbage"))
        assertNull(ShareParser.parseShareDate(null))
    }

    @Test
    fun `parses a real-shaped readings array newest first`() {
        val body = """
            [
              {"WT":"Date(1691455258000)","ST":"Date(1691455258000)","DT":"Date(1691455258000-0400)","Value":85,"Trend":"Flat"},
              {"WT":"Date(1691455558000)","ST":"Date(1691455558000)","DT":"Date(1691455558000-0400)","Value":91,"Trend":"FortyFiveUp"}
            ]
        """.trimIndent()
        val readings = ShareParser.parseReadings(ShareParser.json.parseToJsonElement(body))
        assertEquals(2, readings.size)
        assertEquals(91, readings[0].mgdl)
        assertEquals(Trend.FORTY_FIVE_UP, readings[0].trend)
        assertEquals(Instant.ofEpochMilli(1691455558000), readings[0].time)
        assertEquals(85, readings[1].mgdl)
        assertEquals(Trend.FLAT, readings[1].trend)
    }

    @Test
    fun `accepts legacy integer trend and numeric value forms`() {
        val body = """[{"WT":"Date(1691455258000)","Value":120.0,"Trend":4}]"""
        val reading = ShareParser.parseReadings(ShareParser.json.parseToJsonElement(body)).single()
        assertEquals(120, reading.mgdl)
        assertEquals(Trend.FLAT, reading.trend)
    }

    @Test
    fun `unknown trend degrades to NONE rather than failing`() {
        val body = """[{"WT":"Date(1691455258000)","Value":120,"Trend":"SomethingNew"}]"""
        assertEquals(Trend.NONE, ShareParser.parseReadings(ShareParser.json.parseToJsonElement(body)).single().trend)
    }

    @Test
    fun `rejects readings without value or timestamp`() {
        assertFailsWith<GlucoseSourceException.Server> {
            ShareParser.parseReadings(ShareParser.json.parseToJsonElement("""[{"WT":"Date(1)","Trend":"Flat"}]"""))
        }
        assertFailsWith<GlucoseSourceException.Server> {
            ShareParser.parseReadings(ShareParser.json.parseToJsonElement("""[{"Value":100,"Trend":"Flat"}]"""))
        }
        assertFailsWith<GlucoseSourceException.Server> {
            ShareParser.parseReadings(ShareParser.json.parseToJsonElement("""{"not":"a list"}"""))
        }
    }

    @Test
    fun `maps share error codes to typed exceptions`() {
        fun err(code: String, message: String = "") =
            ShareParser.errorFor(ShareParser.json.parseToJsonElement("""{"Code":"$code","Message":"$message"}"""), 500)

        assertIs<GlucoseSourceException.Session>(err("SessionNotValid"))
        assertIs<GlucoseSourceException.Session>(err("SessionIdNotFound"))
        assertIs<GlucoseSourceException.Auth>(err("AccountPasswordInvalid"))
        assertIs<GlucoseSourceException.Auth>(err("SSO_AuthenticateMaxAttemptsExceeded"))
        assertIs<GlucoseSourceException.Auth>(err("SSO_InternalError", "Cannot Authenticate by AccountName"))
        assertIs<GlucoseSourceException.Server>(err("SSO_InternalError", "Something else"))
        assertIs<GlucoseSourceException.Auth>(err("InvalidArgument", "accountName is required"))
        assertIs<GlucoseSourceException.Server>(err("BrandNewCode"))
        assertIs<GlucoseSourceException.Server>(ShareParser.errorFor(ShareParser.json.parseToJsonElement("\"nope\""), 503))
    }
}
