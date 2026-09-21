package org.glucovoice.core

/**
 * Anything that can supply CGM readings. Implementations are blocking; call them off the main
 * thread. The app depends only on this interface so the data source can be swapped (Dexcom Share
 * today, Nightscout or an official Dexcom partner API later) without touching the UI.
 */
interface GlucoseSource {
    /** Most recent reading from the past 24 hours, or null if the source has none. */
    @Throws(GlucoseSourceException::class)
    fun latest(): GlucoseReading?

    /** Up to [maxCount] readings from the past [minutes] minutes, newest first. */
    @Throws(GlucoseSourceException::class)
    fun recent(minutes: Int = 1440, maxCount: Int = 288): List<GlucoseReading>
}

sealed class GlucoseSourceException(message: String, cause: Throwable? = null) : Exception(message, cause) {
    /** Credentials rejected, account locked, or account not recognized. */
    class Auth(message: String) : GlucoseSourceException(message)

    /** Session expired. Clients retry once with a fresh login before surfacing this. */
    class Session(message: String) : GlucoseSourceException(message)

    /** Could not reach the service. */
    class Network(message: String, cause: Throwable? = null) : GlucoseSourceException(message, cause)

    /** Service reachable but its answer was malformed or an unknown error. */
    class Server(message: String) : GlucoseSourceException(message)
}
