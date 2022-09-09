package org.sdpi.asciidoc.extension

import org.apache.logging.log4j.kotlin.Logging
import org.asciidoctor.ast.Document
import org.asciidoctor.ast.Section
import org.asciidoctor.ast.StructuralNode
import org.asciidoctor.extension.Treeprocessor
import org.sdpi.asciidoc.model.StructuralNodeWrapper
import org.sdpi.asciidoc.model.toSealed
import org.sdpi.asciidoc.validate

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
class NumberingProcessor : Treeprocessor() {
    private var numbering = mutableListOf<Number>()
    private var currentAdditionalLevel = 0

    override fun process(document: Document): Document {
        processBlock(document as StructuralNode)
        return document
    }

    private fun createSectionId(numbers: List<Number>) =
        numbers.map { it.offset ?: it.current }.joinToString(separator = ".")


    private fun processBlock(block: StructuralNode) {
        // enter new level, increase numbering depth
        numbering.add(Number())
        for (childBlock in block.blocks) {
            childBlock.toSealed().let { node ->
                when (node) {
                    is StructuralNodeWrapper.Section -> {
                        processLevelOption(node.wrapped)
                        processOffsetOption(node.wrapped)

                        // attach section number to section title
                        createSectionId(numbering).let {
                            "$it ${node.wrapped.title}"
                        }.also {
                            logger.debug { "Attach section number: $it" }
                            node.wrapped.title = it
                        }

                        // recursively process children of this child block
                        processBlock(childBlock)

                        // leave level, decrease numbering depth
                        numbering.removeLast()
                    }
                    else -> Unit
                }
            }
        }
    }

    private fun processOffsetOption(section: Section) {
        when (val sdpiOffset = section.attributes[OPTION_OFFSET]) {
            null -> {
                numbering[numbering.lastIndex] = numbering.last().let { last ->
                    last.copy(current = last.current + 1, offset = last.offset?.let { it + 1 })
                }
            }

            else -> (sdpiOffset as String).let {
                validate(optionOffsetRegex.matches(sdpiOffset), section) {
                    "Option $OPTION_OFFSET set to '$sdpiOffset'. " +
                            "Valid values: $OPTION_OFFSET_PATTERN"
                }

                when (sdpiOffset) {
                    CLEAR_NUMBERING -> numbering[numbering.lastIndex] = numbering.last().let { last ->
                        last.copy(
                            current = last.current + 1, offset = null
                        )
                    }

                    else -> numbering[numbering.lastIndex] = sdpiOffset.toInt().let {
                        numbering.last().copy(offset = it)
                    }.also {
                        logger.debug { "Found numbering offset at depth ${numbering.size}: $sdpiOffset" }
                    }
                }
            }
        }
    }

    private fun processLevelOption(section: Section) {
        when (val sdpiLevel = section.attributes[OPTION_LEVEL]) {
            null -> (numbering.size - MAX_HEADING_DEPTH).let {
                if (it > 0) {
                    numbering = numbering.dropLast(it).toMutableList()
                }
            }

            else -> (sdpiLevel as String).let {
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
                    numbering.add(Number())
                }
            }
        }
    }

    private data class Number(val current: Int = 0, val offset: Int? = null)

    private companion object : Logging {
        const val CLEAR_NUMBERING = "clear"

        const val MAX_HEADING_DEPTH = 6
        const val MAX_DISTANCE = 1

        const val OPTION_OFFSET = "sdpi_offset"
        const val OPTION_OFFSET_PATTERN = "^[0-9]+|$CLEAR_NUMBERING$"
        val optionOffsetRegex = OPTION_OFFSET_PATTERN.toRegex()

        const val OPTION_LEVEL = "sdpi_level"
        const val OPTION_LEVEL_PATTERN = "^\\+[0-9]+$"
        val optionLevelRegex = OPTION_LEVEL_PATTERN.toRegex()
    }
}