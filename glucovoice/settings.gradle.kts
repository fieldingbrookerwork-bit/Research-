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

// :app needs Google's Maven repository (dl.google.com). Pass -PskipAndroid=true to build and
// test :core alone on machines where that host is unreachable.
if (providers.gradleProperty("skipAndroid").orNull != "true") {
    include(":app")
}
