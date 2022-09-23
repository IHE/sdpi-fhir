package org.sdpi.asciidoc.extension

import org.asciidoctor.ast.Document
import org.asciidoctor.extension.Preprocessor
import org.asciidoctor.extension.PreprocessorReader
import java.io.File

/**
 * Removes any occurrences of `:sectnums:` from the document to prevent the AscidoctorJ parser from rendering
 * additional section numbers.
 */
class DisableSectNumsProcessor(private val inputFile: File) : Preprocessor() {
    override fun process(document: Document, reader: PreprocessorReader) {
        reader.readLines().filter {
            it.trim() != ":sectnums:"
        }.let {
            val mutableLines = it.toMutableList()
            var inPlantUml = false
            it.withIndex().forEach {
                val trimmedLine = it.value.trim()
                if (trimmedLine == "@startuml") {
                    inPlantUml = true
                }
                if (trimmedLine == "@enduml") {
                    inPlantUml = false
                }
                if (inPlantUml) {
                    plantUmlIncludeRegex.find(trimmedLine)?.let { match ->
                        match.groupValues[1].let { groupValue ->
                            val replaceIncludePath = inputFile.parentFile.absolutePath +
                                    File.separatorChar + PLANTUML_SOURCES_FOLDER_NAME +
                                    File.separatorChar + groupValue
                            mutableLines[it.index] = "!include $replaceIncludePath"
                        }
                    }
                }
            }
            mutableLines
        }.also {
            reader.restoreLines(it)
        }
    }

    private companion object {
        const val PLANTUML_SOURCES_FOLDER_NAME = "plantuml"

        private val plantUmlIncludeRegex = "^!include\\s+?(\\S.*)$".toRegex()
    }
}