package org.glucovoice.core

import java.time.Clock
import java.time.Duration
import java.time.Instant
import java.time.ZoneOffset
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class FakeGlucoseSourceTest {
    private val now = Instant.parse("2026-09-21T12:03:20Z")
    private val source = FakeGlucoseSource(Clock.fixed(now, ZoneOffset.UTC))

    @Test
    fun `latest is one to six minutes old and in a sane range`() {
        val latest = assertNotNull(source.latest())
        val age = Duration.between(latest.time, now)
        assertTrue(age >= Duration.ofMinutes(1) && age <= Duration.ofMinutes(6), "age was $age")
        assertTrue(latest.mgdl in 40..400)
    }

    @Test
    fun `recent is newest first on five minute steps and deterministic`() {
        val a = source.recent(minutes = 60, maxCount = 288)
        val b = source.recent(minutes = 60, maxCount = 288)
        assertEquals(12, a.size)
        assertEquals(a, b)
        a.zipWithNext().forEach { (newer, older) ->
            assertEquals(Duration.ofMinutes(5), Duration.between(older.time, newer.time))
        }
    }

    @Test
    fun `trend matches the direction of change`() {
        val readings = source.recent(minutes = 1440, maxCount = 288)
        readings.zipWithNext().forEach { (newer, older) ->
            val delta = newer.mgdl - older.mgdl
            when (newer.trend) {
                Trend.DOUBLE_UP, Trend.SINGLE_UP, Trend.FORTY_FIVE_UP -> assertTrue(delta > 0)
                Trend.DOUBLE_DOWN, Trend.SINGLE_DOWN, Trend.FORTY_FIVE_DOWN -> assertTrue(delta < 0)
                else -> assertTrue(kotlin.math.abs(delta) < 5)
            }
        }
    }
}
