pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
        google()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
        google()
    }
}

rootProject.name = "glucovoice"

include(":core")
include(":app")

// To build and test :core on a machine that cannot reach dl.google.com (no Android SDK, no AGP):
//   ./gradlew -c tools/core-only.settings.gradle.kts :core:test
