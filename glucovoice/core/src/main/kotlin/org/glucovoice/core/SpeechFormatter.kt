package org.glucovoice.core

import java.time.Duration
import java.time.Instant

/**
 * Turns readings and failures into short sentences for text-to-speech, and into display fields.
 *
 * Safety rules baked in here rather than in the UI:
 *  - Every spoken reading carries value, trend and age, so a stale number is never mistaken for a
 *    current one.
 *  - A reading older than [staleAfter] is never spoken as a number at all.
 *  - mmol/L values always carry their unit, because "six point eight" and "sixty eight" are too
 *    easy to confuse when both units exist.
 */
class SpeechFormatter(
    val unit: GlucoseUnit = GlucoseUnit.MGDL,
    val speakUnits: Boolean = unit == GlucoseUnit.MMOL,
    val staleAfter: Duration = Duration.ofMinutes(15),
) {
    sealed class Spoken(val text: String) {
        class Reading(text: String, val reading: GlucoseReading, val ageMinutes: Long) : Spoken(text)
        class Stale(text: String, val reading: GlucoseReading, val ageMinutes: Long) : Spoken(text)
        class NoData(text: String) : Spoken(text)
        class Failure(text: String, val cause: Throwable) : Spoken(text)
    }

    data class Display(
        val value: String,
        val unitLabel: String,
        val arrow: String,
        val trend: String,
        val age: String,
        val isStale: Boolean,
    )

    fun forReading(reading: GlucoseReading?, now: Instant): Spoken {
        if (reading == null) return Spoken.NoData(NO_DATA)
        val age = reading.age(now)
        val minutes = age.toMinutes().coerceAtLeast(0)
        if (age > staleAfter) {
            return Spoken.Stale("Your latest reading is ${staleAgeText(minutes)} old. Check your Dexcom app.", reading, minutes)
        }
        val value = buildString {
            append(reading.valueText(unit))
            if (speakUnits || unit == GlucoseUnit.MMOL) append(' ').append(unit.spoken)
        }
        return Spoken.Reading("$value, ${reading.trend.spoken}, ${ageText(minutes)}.", reading, minutes)
    }

    fun forError(error: Throwable): Spoken.Failure {
        val text = when (error) {
            is GlucoseSourceException.Auth -> "Dexcom login failed. Check your username and password in settings."
            is GlucoseSourceException.Network -> "Could not reach Dexcom Share. Check your internet connection."
            is GlucoseSourceException.Session -> "Dexcom Share session expired. Try again."
            is GlucoseSourceException.Server -> "Dexcom Share gave an unexpected answer. Try again in a few minutes."
            else -> "Something went wrong reading your glucose. Check your Dexcom app."
        }
        return Spoken.Failure(text, error)
    }

    fun display(reading: GlucoseReading?, now: Instant): Display {
        if (reading == null) return Display("--", unit.label, "", "no data", "", false)
        val minutes = reading.age(now).toMinutes().coerceAtLeast(0)
        val stale = reading.age(now) > staleAfter
        return Display(
            value = reading.valueText(unit),
            unitLabel = unit.label,
            arrow = reading.trend.arrow,
            trend = reading.trend.spoken,
            age = ageText(minutes),
            isStale = stale,
        )
    }

    /** "47 minutes", "3 hours": age without the trailing "ago", for the stale sentence. */
    fun staleAgeText(minutes: Long): String = when {
        minutes < 60 -> "$minutes minutes"
        minutes < 120 -> "1 hour"
        minutes < 60 * 24 -> "${minutes / 60} hours"
        else -> "more than a day"
    }

    fun ageText(minutes: Long): String = when {
        minutes <= 0 -> "just now"
        minutes == 1L -> "1 minute ago"
        minutes < 60 -> "$minutes minutes ago"
        minutes < 120 -> "1 hour ago"
        minutes < 60 * 24 -> "${minutes / 60} hours ago"
        else -> "more than a day ago"
    }

    companion object {
        const val NO_DATA = "No glucose reading available. Check that Dexcom Share is turned on in your Dexcom app."
    }
}
