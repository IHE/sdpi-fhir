package org.sdpi.asciidoc

import org.apache.logging.log4j.kotlin.Logging
import java.io.ByteArrayOutputStream
import java.io.PrintStream

/**
 * Checks for Asciidoc error messages.
 *
 * Starts capturing the process' error stream when initialized, seeks Asciidoc error messages and throws if at least one is found.
 */
class AsciidocErrorChecker {
    private val errorStream = ByteArrayOutputStream().also {
        System.setErr(PrintStream(it))
    }

    /**
     * Runs the check on the latest captured error stream.
     */
    fun run() {
        val errors = errorStream.toByteArray().decodeToString()
            .split("\n").count {
                when (it.startsWith(ERROR_HINT, true)) {
                    true -> logger.error {
                        "Asciidoc issue detected: ${it.substring(ERROR_HINT.length)}"
                    }.let { true }
                    false -> false
                }
            }
        if (errors > 0) {
            throw Exception("Found $errors Asciidoc error(s) that need to be fixed (see previous output)")
        }
    }

    private companion object : Logging {
        const val ERROR_HINT = "information: "
    }
}
