package org.glucovoice.app.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.widget.RemoteViews
import org.glucovoice.app.GlucoVoiceApp
import org.glucovoice.app.R
import org.glucovoice.app.tile.GlucoseTileService
import org.glucovoice.app.ui.SpeakActivity
import java.time.Instant

object WidgetUpdater {

    fun updateAll(context: Context) {
        val manager = AppWidgetManager.getInstance(context)
        val ids = manager.getAppWidgetIds(ComponentName(context, GlucoseWidgetProvider::class.java))
        if (ids.isNotEmpty()) {
            val views = build(context)
            ids.forEach { manager.updateAppWidget(it, views) }
        }
        GlucoseTileService.requestUpdate(context)
    }

    fun build(context: Context): RemoteViews {
        val repository = GlucoVoiceApp.from(context).repository
        val display = repository.formatter().display(repository.cachedReading(), Instant.now())
        val views = RemoteViews(context.packageName, R.layout.widget_glucose)
        views.setTextViewText(R.id.widget_value, display.value)
        views.setTextViewText(R.id.widget_arrow, display.arrow)
        views.setTextViewText(
            R.id.widget_age,
            if (display.value == "--") context.getString(R.string.widget_tap) else "${display.unitLabel} · ${display.age}",
        )
        views.setFloat(R.id.widget_value, "setAlpha", if (display.isStale) 0.4f else 1f)
        views.setContentDescription(
            R.id.widget_root,
            if (repository.cachedReading() == null) context.getString(R.string.cd_no_reading)
            else context.getString(R.string.cd_reading, display.value, display.unitLabel, display.trend, display.age),
        )
        val intent = Intent(context, SpeakActivity::class.java).setAction(SpeakActivity.ACTION_SPEAK)
        views.setOnClickPendingIntent(
            R.id.widget_root,
            PendingIntent.getActivity(context, 0, intent, PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT),
        )
        return views
    }
}
