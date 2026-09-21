package org.glucovoice.core

import java.time.Duration
import java.time.Instant
import java.util.Locale

enum class GlucoseUnit(val id: String, val label: String, val spoken: String) {
    MGDL("mgdl", "mg/dL", "milligrams per deciliter"),
    MMOL("mmol", "mmol/L", "millimoles per liter");

    companion object {
        fun fromId(id: String?): GlucoseUnit = entries.firstOrNull { it.id == id } ?: MGDL
    }
}

/** One CGM reading. [time] is the sensor's wall-clock time (Share field `WT`). */
data class GlucoseReading(val mgdl: Int, val trend: Trend, val time: Instant) {

    /** Same value in mmol/L, rounded to one decimal. */
    val mmol: Double
        get() = Math.round(mgdl / MGDL_PER_MMOL * 10.0) / 10.0

    fun valueText(unit: GlucoseUnit): String = when (unit) {
        GlucoseUnit.MGDL -> mgdl.toString()
        GlucoseUnit.MMOL -> String.format(Locale.US, "%.1f", mmol)
    }

    fun age(now: Instant): Duration = Duration.between(time, now)

    companion object {
        const val MGDL_PER_MMOL = 18.0182
    }
}
