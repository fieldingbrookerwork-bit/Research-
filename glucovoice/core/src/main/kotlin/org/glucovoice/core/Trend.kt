package org.glucovoice.core

/**
 * Glucose trend as reported by Dexcom Share.
 *
 * Share returns the trend as a string (`"Flat"`, `"SingleUp"`, ...). Older responses used the
 * integer codes in [legacyCode]; both forms are accepted.
 */
enum class Trend(val shareName: String, val legacyCode: Int, val spoken: String, val arrow: String) {
    NONE("None", 0, "trend unavailable", ""),
    DOUBLE_UP("DoubleUp", 1, "rising fast", "↑↑"),
    SINGLE_UP("SingleUp", 2, "rising", "↑"),
    FORTY_FIVE_UP("FortyFiveUp", 3, "rising slowly", "↗"),
    FLAT("Flat", 4, "steady", "→"),
    FORTY_FIVE_DOWN("FortyFiveDown", 5, "falling slowly", "↘"),
    SINGLE_DOWN("SingleDown", 6, "falling", "↓"),
    DOUBLE_DOWN("DoubleDown", 7, "falling fast", "↓↓"),
    NOT_COMPUTABLE("NotComputable", 8, "trend unavailable", "?"),
    RATE_OUT_OF_RANGE("RateOutOfRange", 9, "changing very fast", "!");

    companion object {
        fun fromShare(raw: String?): Trend {
            if (raw.isNullOrBlank()) return NONE
            entries.firstOrNull { it.shareName.equals(raw, ignoreCase = true) }?.let { return it }
            raw.toIntOrNull()?.let { return fromLegacy(it) }
            return NONE
        }

        fun fromLegacy(code: Int): Trend = entries.firstOrNull { it.legacyCode == code } ?: NONE
    }
}
