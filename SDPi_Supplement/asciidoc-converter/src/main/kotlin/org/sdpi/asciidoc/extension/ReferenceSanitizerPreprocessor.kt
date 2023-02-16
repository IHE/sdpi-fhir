package org.sdpi.asciidoc.extension

import org.asciidoctor.extension.Preprocessor
import org.asciidoctor.extension.PreprocessorReader

class ReferenceSanitizerPreprocessor(private val customReferenceTexts: MutableSet<String>) : Preprocessor() {

    override fun process(document: org.asciidoctor.ast.Document, reader: PreprocessorReader) {
        val lines = reader.readLines().also {
            reader.restoreLines(it)
        }

        // creates a lookup table for references that have to remain untouched by the ReferenceSanitizerPostprocessor
        lines.forEach { line ->
            referenceMatcher.findAll(line).forEach { match ->
                val parts = match.groupValues[1].split(",", limit = 2)
                if (parts.size > 1) {
                    customReferenceTexts.add(parts.first())
                }
            }
        }
    }

    companion object {
        private val referenceMatcher = """<<(.+?)>>""".toRegex()
    }
}