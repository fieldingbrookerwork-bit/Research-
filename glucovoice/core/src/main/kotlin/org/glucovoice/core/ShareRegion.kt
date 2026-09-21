package org.glucovoice.core

/**
 * Dexcom Share server per region. Values match the open-source pydexcom client; the
 * application IDs are the ones the Dexcom Follow app itself presents.
 */
enum class ShareRegion(val id: String, val label: String, val baseUrl: String, val applicationId: String) {
    US("us", "United States", "https://share2.dexcom.com/ShareWebServices/Services/", "d89443d2-327c-4a6f-89e5-496bbb0317db"),
    OUS("ous", "Outside the United States", "https://shareous1.dexcom.com/ShareWebServices/Services/", "d89443d2-327c-4a6f-89e5-496bbb0317db"),
    JP("jp", "Japan", "https://share.dexcom.jp/ShareWebServices/Services/", "d8665ade-9673-4e27-9ff6-92db4ce13d13");

    companion object {
        fun fromId(id: String?): ShareRegion = entries.firstOrNull { it.id == id } ?: US
    }
}
