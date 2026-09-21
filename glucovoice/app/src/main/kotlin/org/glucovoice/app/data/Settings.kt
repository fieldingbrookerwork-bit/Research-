package org.glucovoice.app.data

import android.content.Context
import androidx.core.content.edit
import org.glucovoice.core.GlucoseReading
import org.glucovoice.core.GlucoseUnit
import org.glucovoice.core.ShareRegion
import org.glucovoice.core.Trend
import java.time.Instant

/** Non-secret preferences plus a cache of the last reading for the widget and tile. */
class Settings(context: Context) {
    private val prefs = context.getSharedPreferences("settings", Context.MODE_PRIVATE)

    var region: ShareRegion
        get() = ShareRegion.fromId(prefs.getString(KEY_REGION, null))
        set(value) = prefs.edit { putString(KEY_REGION, value.id) }

    var unit: GlucoseUnit
        get() = GlucoseUnit.fromId(prefs.getString(KEY_UNIT, null))
        set(value) = prefs.edit { putString(KEY_UNIT, value.id) }

    var speakUnits: Boolean
        get() = prefs.getBoolean(KEY_SPEAK_UNITS, false)
        set(value) = prefs.edit { putBoolean(KEY_SPEAK_UNITS, value) }

    var speakOnOpen: Boolean
        get() = prefs.getBoolean(KEY_SPEAK_ON_OPEN, true)
        set(value) = prefs.edit { putBoolean(KEY_SPEAK_ON_OPEN, value) }

    var demoMode: Boolean
        get() = prefs.getBoolean(KEY_DEMO, false)
        set(value) = prefs.edit { putBoolean(KEY_DEMO, value) }

    var setupDone: Boolean
        get() = prefs.getBoolean(KEY_SETUP_DONE, false)
        set(value) = prefs.edit { putBoolean(KEY_SETUP_DONE, value) }

    fun cacheReading(reading: GlucoseReading?) = prefs.edit {
        if (reading == null) {
            remove(KEY_LAST_MGDL); remove(KEY_LAST_TREND); remove(KEY_LAST_TIME)
        } else {
            putInt(KEY_LAST_MGDL, reading.mgdl)
            putString(KEY_LAST_TREND, reading.trend.shareName)
            putLong(KEY_LAST_TIME, reading.time.toEpochMilli())
        }
    }

    fun cachedReading(): GlucoseReading? {
        if (!prefs.contains(KEY_LAST_TIME)) return null
        return GlucoseReading(
            mgdl = prefs.getInt(KEY_LAST_MGDL, 0),
            trend = Trend.fromShare(prefs.getString(KEY_LAST_TREND, null)),
            time = Instant.ofEpochMilli(prefs.getLong(KEY_LAST_TIME, 0L)),
        )
    }

    private companion object {
        const val KEY_REGION = "region"
        const val KEY_UNIT = "unit"
        const val KEY_SPEAK_UNITS = "speak_units"
        const val KEY_SPEAK_ON_OPEN = "speak_on_open"
        const val KEY_DEMO = "demo_mode"
        const val KEY_SETUP_DONE = "setup_done"
        const val KEY_LAST_MGDL = "last_mgdl"
        const val KEY_LAST_TREND = "last_trend"
        const val KEY_LAST_TIME = "last_time"
    }
}
