package org.glucovoice.app.tile

import android.app.PendingIntent
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Build
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService
import org.glucovoice.app.GlucoVoiceApp
import org.glucovoice.app.R
import org.glucovoice.app.ui.SpeakActivity
import java.time.Instant

/** Quick Settings tile: shows the cached value, tapping it speaks a fresh one. */
class GlucoseTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        refreshTile()
    }

    override fun onClick() {
        super.onClick()
        val intent = Intent(this, SpeakActivity::class.java)
            .setAction(SpeakActivity.ACTION_SPEAK)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startActivityAndCollapse(
                PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT),
            )
        } else {
            @Suppress("DEPRECATION")
            startActivityAndCollapse(intent)
        }
    }

    private fun refreshTile() {
        val tile = qsTile ?: return
        val repository = GlucoVoiceApp.from(this).repository
        val display = repository.formatter().display(repository.cachedReading(), Instant.now())
        tile.label = getString(R.string.tile_label)
        tile.state = if (repository.isConfigured()) Tile.STATE_ACTIVE else Tile.STATE_INACTIVE
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            tile.subtitle = if (display.value == "--") getString(R.string.tile_tap_to_speak)
            else "${display.value} ${display.arrow} ${display.age}"
        }
        tile.updateTile()
    }

    companion object {
        fun requestUpdate(context: Context) {
            TileService.requestListeningState(context, ComponentName(context, GlucoseTileService::class.java))
        }
    }
}
