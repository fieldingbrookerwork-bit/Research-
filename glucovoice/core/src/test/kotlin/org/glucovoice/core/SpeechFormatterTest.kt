package org.glucovoice.core

import java.io.IOException
import java.time.Duration
import java.time.Instant
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertIs
import kotlin.test.assertTrue

class SpeechFormatterTest {
    private val now = Instant.parse("2026-09-21T12:00:00Z")
    private fun reading(mgdl: Int, trend: Trend, ageMinutes: Long) =
        GlucoseReading(mgdl, trend, now.minus(Duration.ofMinutes(ageMinutes)))

    @Test
    fun `fresh mgdl reading speaks value trend and age`() {
        val spoken = SpeechFormatter(GlucoseUnit.MGDL).forReading(reading(123, Trend.SINGLE_UP, 2), now)
        assertIs<SpeechFormatter.Spoken.Reading>(spoken)
        assertEquals("123, rising, 2 minutes ago.", spoken.text)
    }

    @Test
    fun `just now and one minute wording`() {
        val f = SpeechFormatter(GlucoseUnit.MGDL)
        assertEquals("98, steady, just now.", f.forReading(reading(98, Trend.FLAT, 0), now).text)
        assertEquals("98, steady, 1 minute ago.", f.forReading(reading(98, Trend.FLAT, 1), now).text)
    }

    @Test
    fun `mmol always carries its unit even when speakUnits is off`() {
        val spoken = SpeechFormatter(GlucoseUnit.MMOL, speakUnits = false).forReading(reading(123, Trend.FLAT, 3), now)
        assertEquals("6.8 millimoles per liter, steady, 3 minutes ago.", spoken.text)
    }

    @Test
    fun `mgdl can optionally speak its unit`() {
        val spoken = SpeechFormatter(GlucoseUnit.MGDL, speakUnits = true).forReading(reading(70, Trend.SINGLE_DOWN, 4), now)
        assertEquals("70 milligrams per deciliter, falling, 4 minutes ago.", spoken.text)
    }

    @Test
    fun `stale reading never speaks the number`() {
        val f = SpeechFormatter(GlucoseUnit.MGDL)
        val spoken = f.forReading(reading(55, Trend.DOUBLE_DOWN, 47), now)
        assertIs<SpeechFormatter.Spoken.Stale>(spoken)
        assertEquals("Your latest reading is 47 minutes old. Check your Dexcom app.", spoken.text)
        assertFalse("55" in spoken.text)
        val hours = f.forReading(reading(55, Trend.FLAT, 200), now)
        assertEquals("Your latest reading is 3 hours old. Check your Dexcom app.", hours.text)
    }

    @Test
    fun `boundary at exactly staleAfter is still fresh`() {
        val f = SpeechFormatter(GlucoseUnit.MGDL, staleAfter = Duration.ofMinutes(15))
        assertIs<SpeechFormatter.Spoken.Reading>(f.forReading(reading(100, Trend.FLAT, 15), now))
        assertIs<SpeechFormatter.Spoken.Stale>(f.forReading(GlucoseReading(100, Trend.FLAT, now.minus(Duration.ofMinutes(15)).minusSeconds(1)), now))
    }

    @Test
    fun `future timestamp from clock skew is treated as just now`() {
        val spoken = SpeechFormatter().forReading(GlucoseReading(100, Trend.FLAT, now.plusSeconds(90)), now)
        assertEquals("100, steady, just now.", spoken.text)
    }

    @Test
    fun `no data and errors have their own sentences`() {
        val f = SpeechFormatter()
        assertIs<SpeechFormatter.Spoken.NoData>(f.forReading(null, now))
        assertTrue("Dexcom login failed" in f.forError(GlucoseSourceException.Auth("x")).text)
        assertTrue("internet" in f.forError(GlucoseSourceException.Network("x", IOException())).text)
        assertTrue("unexpected" in f.forError(GlucoseSourceException.Server("x")).text)
        assertTrue("Check your Dexcom app" in f.forError(IllegalStateException("x")).text)
    }

    @Test
    fun `display fields`() {
        val d = SpeechFormatter(GlucoseUnit.MGDL).display(reading(180, Trend.FORTY_FIVE_UP, 6), now)
        assertEquals("180", d.value)
        assertEquals("mg/dL", d.unitLabel)
        assertEquals("↗", d.arrow)
        assertEquals("rising slowly", d.trend)
        assertEquals("6 minutes ago", d.age)
        assertFalse(d.isStale)
        assertTrue(SpeechFormatter().display(reading(180, Trend.FLAT, 30), now).isStale)
        assertEquals("--", SpeechFormatter().display(null, now).value)
    }

    @Test
    fun `mmol conversion rounds to one decimal`() {
        assertEquals(6.8, GlucoseReading(123, Trend.FLAT, now).mmol)
        assertEquals(3.9, GlucoseReading(70, Trend.FLAT, now).mmol)
        assertEquals("10.0", GlucoseReading(180, Trend.FLAT, now).valueText(GlucoseUnit.MMOL))
    }
}
