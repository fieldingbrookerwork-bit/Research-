package org.glucovoice.app.data

import android.content.Context
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import org.glucovoice.app.widget.WidgetUpdater
import org.glucovoice.app.work.RefreshWorker
import org.glucovoice.core.DexcomShareClient
import org.glucovoice.core.FakeGlucoseSource
import org.glucovoice.core.GlucoseReading
import org.glucovoice.core.GlucoseSource
import org.glucovoice.core.GlucoseSourceException
import org.glucovoice.core.ShareRegion
import org.glucovoice.core.SpeechFormatter

/**
 * Single entry point the UI, tile, widget and worker use. Owns the active [GlucoseSource],
 * the credential store and the last-reading cache. All network work runs on Dispatchers.IO and
 * is serialized so two callers never trigger two logins at once.
 */
class GlucoseRepository(private val context: Context) {
    val settings = Settings(context)
    private val secure = SecureStore(context)
    private val fetchMutex = Mutex()

    private var source: GlucoseSource? = null
    private var sourceKey: String? = null

    fun isConfigured(): Boolean = settings.setupDone && (settings.demoMode || hasCredentials())

    fun hasCredentials(): Boolean = secure.get(KEY_USER) != null && secure.get(KEY_PASS) != null

    fun username(): String? = secure.get(KEY_USER)

    fun formatter(): SpeechFormatter = SpeechFormatter(settings.unit, settings.speakUnits)

    fun cachedReading(): GlucoseReading? = settings.cachedReading()

    suspend fun fetchLatest(): Result<GlucoseReading?> = withContext(Dispatchers.IO) {
        fetchMutex.withLock {
            attempt { currentSource().latest() }.onSuccess { reading ->
                settings.cacheReading(reading)
                WidgetUpdater.updateAll(context)
            }
        }
    }

    /** Verifies the login against Dexcom Share and, only if it works, stores it. */
    suspend fun testAndSave(region: ShareRegion, username: String, password: String): Result<GlucoseReading?> =
        withContext(Dispatchers.IO) {
            fetchMutex.withLock {
                attempt {
                    val client = DexcomShareClient(region, username, password)
                    client.login()
                    client.latest()
                }.onSuccess { reading ->
                    secure.put(KEY_USER, username)
                    secure.put(KEY_PASS, password)
                    settings.region = region
                    settings.demoMode = false
                    settings.setupDone = true
                    settings.cacheReading(reading)
                    invalidateSource()
                    RefreshWorker.schedule(context)
                    WidgetUpdater.updateAll(context)
                }
            }
        }

    fun enableDemo() {
        settings.demoMode = true
        settings.setupDone = true
        invalidateSource()
        RefreshWorker.schedule(context)
    }

    fun forgetCredentials() {
        secure.remove(KEY_USER)
        secure.remove(KEY_PASS)
        settings.cacheReading(null)
        settings.setupDone = settings.demoMode
        invalidateSource()
        WidgetUpdater.updateAll(context)
    }

    @Synchronized
    private fun currentSource(): GlucoseSource {
        val key = if (settings.demoMode) "demo" else "share:${settings.region.id}:${secure.get(KEY_USER)}"
        if (source == null || key != sourceKey) {
            source = if (settings.demoMode) {
                FakeGlucoseSource()
            } else {
                val user = secure.get(KEY_USER) ?: throw GlucoseSourceException.Auth("No Dexcom login saved")
                val pass = secure.get(KEY_PASS) ?: throw GlucoseSourceException.Auth("No Dexcom login saved")
                DexcomShareClient(settings.region, user, pass)
            }
            sourceKey = key
        }
        return source!!
    }

    @Synchronized
    private fun invalidateSource() {
        source = null
        sourceKey = null
    }

    private inline fun <T> attempt(block: () -> T): Result<T> = try {
        Result.success(block())
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        Result.failure(e)
    }

    private companion object {
        const val KEY_USER = "share_username"
        const val KEY_PASS = "share_password"
    }
}
