package org.sdpi.asciidoc.extension

import org.apache.logging.log4j.kotlin.Logging
import org.asciidoctor.ast.Block
import org.asciidoctor.ast.Document
import org.asciidoctor.ast.Section
import org.asciidoctor.ast.StructuralNode
import org.asciidoctor.extension.Treeprocessor
import org.sdpi.asciidoc.Attributes
import org.sdpi.asciidoc.BlockAttribute
import org.sdpi.asciidoc.isAppendix
import org.sdpi.asciidoc.model.StructuralNodeWrapper
import org.sdpi.asciidoc.model.toSealed
import org.sdpi.asciidoc.validate
import java.io.OutputStream

/**
 * Takes care of section numbering.
 *
 * The supplement has a strict numbering scheme to fit into the technical framework. As automatic numbering in AsciiDoc
 * does not allow mixing in manual numbering, this class takes over numbering while accepting custom offsets.
 *
 * Option name: sdpi_offset
 *
 * Furthermore, AsciiDoc does only allow for numbering of a maximum depths of [MAX_HEADING_DEPTH]. To add additional
 * levels, this classes can process an option to insert levels on top of the largest heading depth.
 *
 * Option name: sdpi_level
 */
class NumberingProcessor(private val structureDump: OutputStream? = null) : Treeprocessor() {
    private var numbering = mutableListOf<Number>()
    private var currentAdditionalLevel = 0
    private val startFromLevel = 1
    private var currentAppendix = 'A'
    private var appendixCaption = ""
    private var currentSection = ""
    private var figureNumber = 1
    private var tableNumber = 1
    private var currentVolumeCaption = ""
    private var isInAppendix = false

    override fun process(document: Document): Document {
        processBlock(document as StructuralNode)
        return document
    }

    private fun createSectionId(numbers: List<Number>, level: Int): String {
        if (numbers.find { it.clear } != null) {
            return ""
        }

        var cutFrom = numbers.indexOfFirst { it.appendix != null }
        if (cutFrom == -1) {
            cutFrom = startFromLevel
        } else {
            if (level - cutFrom == 0) {
                return ""
            }
        }

        if (cutFrom > level) {
            return ""
        }

        return when (cutFrom) {
            -1 -> numbers.subList(0, level + 1)
            else -> numbers.subList(cutFrom, level + 1)
        }.joinToString(separator = ".") {
            when (it.appendix) {
                null -> (it.offset ?: it.current).toString()
                else -> it.appendix
            }
        }
    }

    private fun processBlock(block: StructuralNode) {
        block.toSealed().let { node ->
            when (node) {
                is StructuralNodeWrapper.Document -> {
                    if (node.wrapped.attributes.containsKey(ATTRIBUTE_APPENDIX_CAPTION)) {
                        appendixCaption = node.wrapped.attributes[ATTRIBUTE_APPENDIX_CAPTION].toString().trim() + " "
                    }

                    logger.info { "Set appendix caption to '$appendixCaption'" }

                    node.wrapped.blocks.forEach {
                        validate(it.level > 0 || !it.isAppendix(), it) {
                            "Part is not allowed to be appendix"
                        }

                        processBlock(it)
                    }
                }

                is StructuralNodeWrapper.Section -> {
                    val level = processLevelOption(node.wrapped)

                    if (node.wrapped.isAppendix()) {
                        isInAppendix = true
                    }

                    if (level == 0 && !node.wrapped.isAppendix()) {
                        currentVolumeCaption = Attributes(node.wrapped.attributes)[BlockAttribute.VOLUME_CAPTION] ?: ""
                    }

                    initSectionNumbers(node.wrapped, level)
                    processOffsetOption(node.wrapped, level)
                    sanitizeAppendix(node.wrapped, level)

                    // attach section number to section title
                    createSectionId(numbering, level).let {
                        currentSection = it
                        // trim leading blanks in case of an empty section id (i.e. appendix)
                        "$it ${node.wrapped.title}".trim()

                    }.also {
                        logger.info { "Attach section number: ${node.wrapped.caption ?: ""}$it" }
                        node.wrapped.title = it
                    }.also {
                        structureDump?.write("${node.wrapped.caption ?: ""}$it\n".toByteArray())
                    }

                    // recursively process children of this child block
                    block.blocks.forEach {
                        processBlock(it)
                    }
                    isInAppendix = false
                }

                is StructuralNodeWrapper.Paragraph -> {
                    println("Source\n======")
                    println(node.wrapped.source)

                    // node.wrapped.source = "__"

                    block.blocks.forEach {
                        processBlock(it)
                    }
                }

                is StructuralNodeWrapper.Image -> replaceCaption(node.wrapped, "Figure", figureNumber++)

                is StructuralNodeWrapper.Table -> replaceCaption(node.wrapped, "Table", tableNumber++)

                else -> logger.debug { "Ignore block of type '${block.context}'" }
            }
        }
    }

    private fun replaceCaption(block: StructuralNode, prefix: String, objectNumber: Int) {
        val volumeCaption = when (currentVolumeCaption) {
            "" -> ""
            else -> "$currentVolumeCaption:"
        }

        val section = when (currentSection.length) {
            0 -> if (isInAppendix) currentAppendix.toString() else ""
            else -> currentSection
        }

        if (block.title != null) {
            block.caption = ""
            block.title = "$prefix $volumeCaption${section}-$objectNumber. ${block.title}"
        }
    }

    private fun processOffsetOption(section: Section, level: Int) {
        when (val sdpiOffset = section.attributes[OPTION_OFFSET]) {
            null -> {
                numbering[level] = numbering[level].let { last ->
                    last.copy(current = last.current + 1, offset = last.offset?.let { it + 1 })
                }
            }

            else -> (sdpiOffset as String).let {
                if (section.isAppendix()) {
                    validate(optionAppendixOffsetRegex.matches(sdpiOffset), section) {
                        "Option $OPTION_OFFSET set to '$sdpiOffset' for appendix. " +
                                "Valid values: $OPTION_APPENDIX_OFFSET_PATTERN"
                    }
                } else {
                    validate(optionOffsetRegex.matches(sdpiOffset), section) {
                        "Option $OPTION_OFFSET set to '$sdpiOffset'. " +
                                "Valid values: $OPTION_OFFSET_PATTERN"
                    }
                }

                when (sdpiOffset) {
                    CLEAR_NUMBERING -> numbering[level] = numbering[level].let { last ->
                        last.copy(current = last.current + 1, offset = last.offset?.let { it + 1 }, clear = true)
                    }

                    else -> if (section.isAppendix()) {
                        currentAppendix = sdpiOffset.first()
                    } else {
                        numbering[level] = sdpiOffset.toInt().let {
                            numbering[level].copy(offset = it)
                        }.also {
                            logger.debug { "Found numbering offset at level ${level}: $sdpiOffset" }
                        }
                    }
                }
            }
        }
    }

    private fun processLevelOption(section: Section): Int {
        return when (val sdpiLevel = section.attributes[OPTION_LEVEL]) {
            null -> section.level
            else -> (sdpiLevel as String).let {
                validate(!section.isAppendix(), section) {
                    "Custom heading level does not support appendices."
                }
                validate(section.level + 1 == MAX_HEADING_DEPTH, section) {
                    "Option $OPTION_LEVEL set on level ${section.level + 1}. " +
                            "Only allowed on level $MAX_HEADING_DEPTH."
                }
                validate(optionLevelRegex.matches(sdpiLevel), section) {
                    "Option $OPTION_LEVEL set to '$sdpiLevel'. " +
                            "Valid values: $OPTION_LEVEL_PATTERN"
                }

                val sdpiLevelInt = sdpiLevel.substring(1).toInt()
                if (sdpiLevelInt < currentAdditionalLevel) {
                    (currentAdditionalLevel - sdpiLevelInt).let {
                        if (it > 0) {
                            numbering = numbering.dropLast(it).toMutableList()
                            currentAdditionalLevel -= it
                        }
                    }
                }

                val currentLevel = MAX_HEADING_DEPTH + sdpiLevelInt - 1
                if (currentLevel > numbering.size) {
                    val distance = currentLevel - numbering.size + 1
                    validate(distance <= MAX_DISTANCE, section) {
                        "Additional heading level depth is only allowed to grow by $MAX_DISTANCE. " +
                                "Found increment of $distance."
                    }
                }

                if (numbering.size == currentLevel) {
                    currentAdditionalLevel++
                    numbering.add(Number(section.title))
                }

                currentLevel
            }
        }
    }

    private fun initSectionNumbers(section: Section, level: Int) {
        for (i in level..numbering.lastIndex) {
            numbering[i] = numbering[i].copy(appendix = null, clear = false)
        }
        for (i in level + 1..numbering.lastIndex) {
            numbering[i] = numbering[i].copy(current = 0, offset = null)
        }

        while (numbering.lastIndex < level) {
            if (numbering.lastIndex == level - 1) {
                numbering.add(Number(section.title))
            } else {
                numbering.add(Number("<MISSING-PART-PLACEHOLDER>"))
            }
        }
    }

    private fun sanitizeAppendix(section: Section, level: Int) {
        numbering[level] = numbering[level].copy(
            title = section.title,
            appendix = if (section.isAppendix()) {
                validate(currentAppendix <= 'Z', section) {
                    "Maximum number of appendices exceeded (26, A to Z)."
                }
                section.caption = "$appendixCaption$currentAppendix: "
                (currentAppendix++).toString()
            } else {
                null
            }
        )

        logger.debug { "Update number at level $level for ${section.id}: ${numbering[level]}" }
    }

    private data class Number(
        val title: String, // for debug purposes
        val current: Int = 0,
        val offset: Int? = null,
        val appendix: String? = null,
        val clear: Boolean = false
    )

    private companion object : Logging {
        const val CLEAR_NUMBERING = "clear"

        const val MAX_HEADING_DEPTH = 6
        const val MAX_DISTANCE = 1

        const val ATTRIBUTE_APPENDIX_CAPTION = "appendix-caption"

        const val OPTION_OFFSET = "sdpi_offset"
        const val OPTION_OFFSET_PATTERN = "^[0-9]+|$CLEAR_NUMBERING|$"
        const val OPTION_APPENDIX_OFFSET_PATTERN = "^[A-Z]$"

        val optionOffsetRegex = OPTION_OFFSET_PATTERN.toRegex()
        val optionAppendixOffsetRegex = OPTION_APPENDIX_OFFSET_PATTERN.toRegex()

        const val OPTION_LEVEL = "sdpi_level"
        const val OPTION_LEVEL_PATTERN = "^\\+[0-9]+$"
        val optionLevelRegex = OPTION_LEVEL_PATTERN.toRegex()
    }
}