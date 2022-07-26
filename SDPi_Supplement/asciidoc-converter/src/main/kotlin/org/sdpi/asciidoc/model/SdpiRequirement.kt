package org.sdpi.asciidoc.model

import org.sdpi.asciidoc.blockId
import org.sdpi.asciidoc.blockTitle

data class SdpiRequirement(
    val number: Int,
    val asciiDocAttributes: Map<String, Any>,
    val asciiDocLines: List<String>
) {
    val blockId = blockId(asciiDocAttributes)
    val blockTitle = blockTitle(asciiDocAttributes)
}