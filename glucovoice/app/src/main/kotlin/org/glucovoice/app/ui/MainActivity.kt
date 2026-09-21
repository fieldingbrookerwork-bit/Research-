package org.glucovoice.app.ui

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import org.glucovoice.app.GlucoVoiceApp
import org.glucovoice.app.R
import org.glucovoice.app.data.GlucoseRepository
import org.glucovoice.app.databinding.ActivityMainBinding
import org.glucovoice.app.speech.Speaker
import org.glucovoice.core.GlucoseReading
import java.time.Instant

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private lateinit var repository: GlucoseRepository
    private var speaker: Speaker? = null
    private var setupShown = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository = GlucoVoiceApp.from(this).repository
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnSpeak.setOnClickListener { refresh(speak = true) }
        binding.btnRefresh.setOnClickListener { refresh(speak = false) }
        binding.btnSettings.setOnClickListener { startActivity(Intent(this, SetupActivity::class.java)) }
        render(repository.cachedReading(), null)
    }

    override fun onResume() {
        super.onResume()
        if (!repository.isConfigured()) {
            // First time: go to Settings. If the user backs out without configuring, let them leave.
            if (setupShown) {
                finish()
                return
            }
            setupShown = true
            startActivity(Intent(this, SetupActivity::class.java))
            return
        }
        setupShown = false
        if (speaker == null) speaker = Speaker(this)
        refresh(speak = repository.settings.speakOnOpen)
    }

    override fun onDestroy() {
        speaker?.shutdown()
        speaker = null
        super.onDestroy()
    }

    private fun refresh(speak: Boolean) {
        binding.btnSpeak.isEnabled = false
        binding.btnRefresh.isEnabled = false
        binding.tvStatus.text = getString(R.string.status_fetching)
        lifecycleScope.launch {
            val formatter = repository.formatter()
            val result = repository.fetchLatest()
            val now = Instant.now()
            val spokenText = result.fold(
                onSuccess = { reading ->
                    render(reading, null)
                    formatter.forReading(reading, now).text
                },
                onFailure = { error ->
                    val failure = formatter.forError(error)
                    render(repository.cachedReading(), failure.text)
                    failure.text
                },
            )
            binding.btnSpeak.isEnabled = true
            binding.btnRefresh.isEnabled = true
            if (speak) speaker?.speak(spokenText)
        }
    }

    private fun render(reading: GlucoseReading?, error: String?) {
        val display = repository.formatter().display(reading, Instant.now())
        binding.tvValue.text = display.value
        binding.tvUnit.text = display.unitLabel
        binding.tvArrow.text = display.arrow
        binding.tvTrend.text = display.trend
        binding.tvAge.text = display.age
        binding.tvValue.alpha = if (display.isStale) 0.4f else 1f
        binding.tvStatus.text = error ?: when {
            repository.settings.demoMode -> getString(R.string.status_demo)
            reading != null && display.isStale -> getString(R.string.status_stale)
            else -> ""
        }
        binding.readingGroup.contentDescription = if (reading == null) {
            getString(R.string.cd_no_reading)
        } else {
            getString(R.string.cd_reading, display.value, display.unitLabel, display.trend, display.age)
        }
    }
}
