package org.glucovoice.app.speech

import android.content.Context
import android.media.AudioAttributes
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.withTimeoutOrNull
import java.util.UUID

/** Thin coroutine wrapper over the system text-to-speech engine. One instance per screen. */
class Speaker(context: Context) {
    private val ready = CompletableDeferred<Boolean>()
    private val tts = TextToSpeech(context.applicationContext) { status ->
        ready.complete(status == TextToSpeech.SUCCESS)
    }

    /** Speaks [text] and suspends until the engine finishes. Returns false if it could not speak. */
    suspend fun speak(text: String, timeoutMs: Long = 20_000): Boolean {
        val engineReady = withTimeoutOrNull(5_000) { ready.await() } ?: false
        if (!engineReady) return false

        tts.setAudioAttributes(
            AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_ASSISTANT)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                .build(),
        )
        val utteranceId = UUID.randomUUID().toString()
        val finished = CompletableDeferred<Boolean>()
        tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(id: String?) {}
            override fun onDone(id: String?) { if (id == utteranceId) finished.complete(true) }
            @Deprecated("Deprecated in Java")
            override fun onError(id: String?) { if (id == utteranceId) finished.complete(false) }
            override fun onError(id: String?, errorCode: Int) { if (id == utteranceId) finished.complete(false) }
        })
        if (tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, utteranceId) != TextToSpeech.SUCCESS) return false
        return withTimeoutOrNull(timeoutMs) { finished.await() } ?: false
    }

    fun shutdown() {
        tts.stop()
        tts.shutdown()
    }
}
