package org.glucovoice.core

import kotlin.test.Test
import kotlin.test.assertEquals

class TrendTest {
    @Test
    fun `share names and legacy codes round trip`() {
        Trend.entries.forEach { t ->
            assertEquals(t, Trend.fromShare(t.shareName))
            assertEquals(t, Trend.fromShare(t.legacyCode.toString()))
            assertEquals(t, Trend.fromLegacy(t.legacyCode))
        }
        assertEquals(Trend.FLAT, Trend.fromShare("flat"))
        assertEquals(Trend.NONE, Trend.fromShare(null))
        assertEquals(Trend.NONE, Trend.fromShare(""))
        assertEquals(Trend.NONE, Trend.fromShare("42"))
    }
}
