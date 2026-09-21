// Root build file. Kotlin plugins are declared here once (not applied) so both modules share one
// plugin classloader. The Android Gradle plugin is deliberately NOT declared here: resolving it
// needs dl.google.com, and keeping it inside :app lets `-PskipAndroid=true` builds of :core work
// on machines that cannot reach that host.
plugins {
    alias(libs.plugins.kotlin.jvm) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.serialization) apply false
}
