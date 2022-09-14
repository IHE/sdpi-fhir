package org.sdpi.asciidoc.extension

import org.asciidoctor.ast.Document
import org.asciidoctor.extension.Preprocessor
import org.asciidoctor.extension.PreprocessorReader

/**
 * Removes any occurrences of `:sectnums:` from the document to prevent the AscidoctorJ parser from rendering
 * additional section numbers.
 */
class DisableSectNumsProcessor : Preprocessor() {
    override fun process(document: Document, reader: PreprocessorReader) {
        reader.restoreLines(reader.readLines().filter {
            it.trim() != ":sectnums:"
        })
    }
}