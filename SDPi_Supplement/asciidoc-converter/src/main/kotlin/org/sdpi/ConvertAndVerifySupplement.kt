package org.sdpi

import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.parameters.options.default
import com.github.ajalt.clikt.parameters.options.option
import com.github.ajalt.clikt.parameters.options.required
import com.github.ajalt.clikt.parameters.options.validate
import com.github.ajalt.clikt.parameters.types.choice
import com.github.ajalt.clikt.parameters.types.file
import org.apache.logging.log4j.kotlin.Logging
import org.asciidoctor.Asciidoctor
import org.asciidoctor.Options
import org.asciidoctor.SafeMode
import org.sdpi.asciidoc.extension.RequirementsBlockProcessor
import java.io.File

fun main(args: Array<String>) = ConvertAndVerifySupplement().main(
    when (System.getenv().containsKey("CI")) {
        true -> args.firstOrNull()?.split(" ") ?: listOf() // caution: blanks in quotes not covered here!
        false -> args.toList()
    }
)

class ConvertAndVerifySupplement : CliktCommand("convert-supplement") {
    private companion object : Logging

    // for some reason, github actions do not digest double quotes correctly right now - requires hard coded config
    private val adocInputFile by option("--input-file", help = "path to ascii doc input file")
        .file()
        .required()
        .validate {
            require(it.exists()) { "Input file '$it' does not exist." }
        }

    private val outputFolder by option("--output-folder", help = "path to artifact doc output folder")
        .file()
        .required()
        .validate {
            require(it.parentFile.exists()) { "Output parent folder '${it.parentFile.absolutePath}' does not exist." }
            if (!it.exists()) {
                require(it.mkdir()) { "Output folder '${it.absolutePath}' could not be created" }
            }
        }

    private val backend by option("--backend", help = "'pdf' (default) or 'html' to set output type")
        .choice("pdf", "html", ignoreCase = true)
        .default("pdf")

    override fun run() {
        runCatching {
            logger.info { "Start conversion of '${adocInputFile.canonicalPath}'" }

            val outFile = File(
                outputFolder.absolutePath + File.separator + adocInputFile.nameWithoutExtension + ".$backend"
            )

            logger.info { "Write output to '${outFile.canonicalPath}'" }

            val options = Options.builder()
                .safe(SafeMode.UNSAFE)
                .backend(backend.lowercase())
                .toFile(outFile).build()

            val asciidoctor = Asciidoctor.Factory.create()

            asciidoctor.javaExtensionRegistry().block(RequirementsBlockProcessor())

            asciidoctor.requireLibrary("asciidoctor-diagram") // enables plantuml
            asciidoctor.convertFile(adocInputFile, options)
            asciidoctor.shutdown()

            logger.info { "File successfully written" }
        }.onFailure {
            logger.error { it.message }
            logger.trace(it) { it.message }
        }
    }
}

