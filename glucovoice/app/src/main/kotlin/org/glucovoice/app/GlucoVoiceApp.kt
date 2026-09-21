package org.glucovoice.app

import android.app.Application
import android.content.Context
import org.glucovoice.app.data.GlucoseRepository
import org.glucovoice.app.work.RefreshWorker

class GlucoVoiceApp : Application() {

    lateinit var repository: GlucoseRepository
        private set

    override fun onCreate() {
        super.onCreate()
        repository = GlucoseRepository(this)
        if (repository.isConfigured()) RefreshWorker.schedule(this)
    }

    companion object {
        fun from(context: Context): GlucoVoiceApp = context.applicationContext as GlucoVoiceApp
    }
}
