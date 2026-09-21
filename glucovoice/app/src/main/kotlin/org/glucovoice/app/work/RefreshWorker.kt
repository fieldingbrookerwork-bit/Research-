package org.glucovoice.app.work

import android.content.Context
import androidx.work.BackoffPolicy
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import org.glucovoice.app.GlucoVoiceApp
import org.glucovoice.app.widget.WidgetUpdater
import org.glucovoice.core.GlucoseSourceException
import java.util.concurrent.TimeUnit

/**
 * Keeps the widget and tile roughly current. Android allows periodic work no more often than
 * every 15 minutes; on-demand fetches (tap, speak) always go straight to Dexcom Share anyway.
 */
class RefreshWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) {

    override suspend fun doWork(): Result {
        val repository = GlucoVoiceApp.from(applicationContext).repository
        if (!repository.isConfigured()) return Result.success()
        val outcome = repository.fetchLatest()
        WidgetUpdater.updateAll(applicationContext)
        return when {
            outcome.isSuccess -> Result.success()
            outcome.exceptionOrNull() is GlucoseSourceException.Auth -> Result.success() // retrying will not fix a bad password
            else -> Result.retry()
        }
    }

    companion object {
        private const val UNIQUE_NAME = "glucovoice.refresh"

        fun schedule(context: Context) {
            val request = PeriodicWorkRequestBuilder<RefreshWorker>(15, TimeUnit.MINUTES)
                .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
                .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 5, TimeUnit.MINUTES)
                .build()
            WorkManager.getInstance(context)
                .enqueueUniquePeriodicWork(UNIQUE_NAME, ExistingPeriodicWorkPolicy.KEEP, request)
        }
    }
}
