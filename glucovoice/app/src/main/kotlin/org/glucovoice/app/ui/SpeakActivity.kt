package org.glucovoice.app.ui

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import org.glucovoice.app.GlucoVoiceApp
import org.glucovoice.app.speech.Speaker
import java.time.Instant

/**
 * No visible UI. Fetches the latest reading, speaks it, shows the same words as a toast for
 * anyone who can see the screen, then finishes. Launched by the widget, the Quick Settings tile,
 * the launcher shortcut and (via "open GlucoVoice") voice assistants.
 */
class SpeakActivity : AppCompatActivity() {
    private var speaker: Speaker? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val repository = GlucoVoiceApp.from(this).repository
        if (!repository.isConfigured()) {
            startActivity(Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
            finish()
            return
        }
        val speaker = Speaker(this).also { this.speaker = it }
        lifecycleScope.launch {
            val formatter = repository.formatter()
            val spoken = repository.fetchLatest().fold(
                onSuccess = { formatter.forReading(it, Instant.now()) },
                onFailure = { formatter.forError(it) },
            )
            Toast.makeText(this@SpeakActivity, spoken.text, Toast.LENGTH_LONG).show()
            speaker.speak(spoken.text)
            finish()
        }
    }

    override fun onDestroy() {
        speaker?.shutdown()
        super.onDestroy()
    }

    companion object {
        const val ACTION_SPEAK = "org.glucovoice.app.action.SPEAK"
    }
}
