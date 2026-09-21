package org.glucovoice.core

import java.io.IOException
import java.net.HttpURLConnection
import java.net.URI

data class HttpResponse(val status: Int, val body: String)

/** Minimal HTTP seam so the Share client can be unit-tested with scripted responses. */
fun interface HttpTransport {
    @Throws(IOException::class)
    fun postJson(url: String, body: String): HttpResponse
}

/** HttpURLConnection-based transport. Works on the JVM and on Android without extra libraries. */
class UrlConnectionTransport(
    private val timeoutMs: Int = 15_000,
    private val userAgent: String = "GlucoVoice/0.1",
) : HttpTransport {
    override fun postJson(url: String, body: String): HttpResponse {
        val conn = URI.create(url).toURL().openConnection() as HttpURLConnection
        try {
            conn.requestMethod = "POST"
            conn.connectTimeout = timeoutMs
            conn.readTimeout = timeoutMs
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.setRequestProperty("Accept", "application/json")
            conn.setRequestProperty("User-Agent", userAgent)
            conn.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
            val status = conn.responseCode
            val stream = if (status in 200..299) conn.inputStream else conn.errorStream
            val text = stream?.bufferedReader(Charsets.UTF_8)?.use { it.readText() } ?: ""
            return HttpResponse(status, text)
        } finally {
            conn.disconnect()
        }
    }
}
