// Root build file. Every plugin is declared here once with `apply false`, then applied in the
// module that needs it. The Android and Kotlin plugins must share a classloader, so this is the
// only layout that works (it is also what Android Studio generates).
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.jvm) apply false
    alias(libs.plugins.kotlin.serialization) apply false
}
