package org.glucovoice.app.ui

import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import org.glucovoice.app.GlucoVoiceApp
import org.glucovoice.app.R
import org.glucovoice.app.data.GlucoseRepository
import org.glucovoice.app.databinding.ActivitySetupBinding
import org.glucovoice.core.GlucoseUnit
import org.glucovoice.core.ShareRegion
import java.time.Instant

class SetupActivity : AppCompatActivity() {
    private lateinit var binding: ActivitySetupBinding
    private lateinit var repository: GlucoseRepository

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        repository = GlucoVoiceApp.from(this).repository
        binding = ActivitySetupBinding.inflate(layoutInflater)
        setContentView(binding.root)

        val settings = repository.settings
        binding.spRegion.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_dropdown_item,
            ShareRegion.entries.map { it.label },
        )
        binding.spRegion.setSelection(ShareRegion.entries.indexOf(settings.region))
        binding.etUsername.setText(repository.username() ?: "")
        if (settings.unit == GlucoseUnit.MMOL) binding.rbMmol.isChecked = true else binding.rbMgdl.isChecked = true
        binding.swSpeakUnits.isChecked = settings.speakUnits
        binding.swSpeakOnOpen.isChecked = settings.speakOnOpen
        binding.swDemo.isChecked = settings.demoMode
        binding.btnForget.isVisible = repository.hasCredentials()

        binding.btnSave.setOnClickListener { save() }
        binding.btnForget.setOnClickListener {
            repository.forgetCredentials()
            binding.etUsername.setText("")
            binding.etPassword.setText("")
            binding.btnForget.isVisible = false
            binding.tvStatus.text = getString(R.string.status_forgotten)
        }
    }

    private fun save() {
        val settings = repository.settings
        settings.unit = if (binding.rbMmol.isChecked) GlucoseUnit.MMOL else GlucoseUnit.MGDL
        settings.speakUnits = binding.swSpeakUnits.isChecked
        settings.speakOnOpen = binding.swSpeakOnOpen.isChecked
        val region = ShareRegion.entries[binding.spRegion.selectedItemPosition]
        val username = binding.etUsername.text?.toString()?.trim().orEmpty()
        val password = binding.etPassword.text?.toString().orEmpty()

        if (binding.swDemo.isChecked) {
            settings.region = region
            repository.enableDemo()
            Toast.makeText(this, R.string.status_demo_saved, Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        if (password.isEmpty() && repository.hasCredentials() && username == repository.username()) {
            // Only preferences changed; keep the stored login.
            settings.region = region
            settings.demoMode = false
            settings.setupDone = true
            Toast.makeText(this, R.string.status_saved, Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        if (username.isEmpty() || password.isEmpty()) {
            binding.tvStatus.text = getString(R.string.status_need_credentials)
            return
        }

        binding.btnSave.isEnabled = false
        binding.tvStatus.text = getString(R.string.status_testing)
        lifecycleScope.launch {
            val result = repository.testAndSave(region, username, password)
            binding.btnSave.isEnabled = true
            result.fold(
                onSuccess = { reading ->
                    binding.btnForget.isVisible = true
                    if (reading == null) {
                        binding.tvStatus.text = getString(R.string.status_login_ok_no_data)
                    } else {
                        val d = repository.formatter().display(reading, Instant.now())
                        Toast.makeText(
                            this@SetupActivity,
                            getString(R.string.status_login_ok, "${d.value} ${d.unitLabel} ${d.arrow}, ${d.age}"),
                            Toast.LENGTH_LONG,
                        ).show()
                        finish()
                    }
                },
                onFailure = { error ->
                    binding.tvStatus.text = repository.formatter().forError(error).text
                },
            )
        }
    }
}
