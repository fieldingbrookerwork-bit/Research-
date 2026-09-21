package org.glucovoice.core

import java.time.Clock
import java.time.Instant
import kotlin.math.PI
import kotlin.math.roundToInt
import kotlin.math.sin

/**
 * Deterministic demo data: a slow three-hour swing plus a faster wobble, one reading every five
 * minutes, newest reading one to six minutes old. Lets the app be exercised with no Dexcom account.
 */
class FakeGlucoseSource(
    private val clock: Clock = Clock.systemUTC(),
    private val phaseSeconds: Long = 0,
) : GlucoseSource {

    override fun latest(): GlucoseReading? = recent(minutes = 1440, maxCount = 1).firstOrNull()

    override fun recent(minutes: Int, maxCount: Int): List<GlucoseReading> {
        val now = clock.instant().epochSecond
        val newest = ((now - 60) / STEP_SECONDS) * STEP_SECONDS
        val count = minOf(maxCount, minutes / 5).coerceAtLeast(0)
        return (0 until count).map { i ->
            val t = newest - i * STEP_SECONDS
            val value = valueAt(t)
            GlucoseReading(value, trendFor(value - valueAt(t - STEP_SECONDS)), Instant.ofEpochSecond(t))
        }
    }

    private fun valueAt(epochSeconds: Long): Int {
        val hours = (epochSeconds + phaseSeconds) / 3600.0
        val slow = 45 * sin(hours * 2 * PI / 3.0)
        val fast = 20 * sin(hours * 2 * PI / 0.7)
        return (130 + slow + fast).roundToInt().coerceIn(40, 400)
    }

    private fun trendFor(deltaPer5Min: Int): Trend = when {
        deltaPer5Min >= 15 -> Trend.DOUBLE_UP
        deltaPer5Min >= 10 -> Trend.SINGLE_UP
        deltaPer5Min >= 5 -> Trend.FORTY_FIVE_UP
        deltaPer5Min <= -15 -> Trend.DOUBLE_DOWN
        deltaPer5Min <= -10 -> Trend.SINGLE_DOWN
        deltaPer5Min <= -5 -> Trend.FORTY_FIVE_DOWN
        else -> Trend.FLAT
    }

    private companion object {
        const val STEP_SECONDS = 300L
    }
}
