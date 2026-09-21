// Alternate settings for building :core alone, without the Android Gradle plugin on the classpath.
// Usage from the glucovoice/ directory:
//   ./gradlew -c tools/core-only.settings.gradle.kts :core:test
// Everything :core needs lives on Maven Central and the Gradle plugin portal.
pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
    }
    versionCatalogs {
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}

rootProject.name = "glucovoice"
rootProject.projectDir = file("..")
// Point the root at an empty build file so the real root's Android plugin declaration is not loaded.
rootProject.buildFileName = "tools/core-only.build.gradle.kts"

include(":core")
