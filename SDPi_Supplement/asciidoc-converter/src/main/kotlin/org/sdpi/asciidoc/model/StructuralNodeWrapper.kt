package org.sdpi.asciidoc.model

import org.asciidoctor.ast.Document
import org.asciidoctor.ast.Section
import org.asciidoctor.ast.StructuralNode

/**
 * Creates a [StructuralNodeWrapper] from a structural node.
 */
fun StructuralNode.toSealed(): StructuralNodeWrapper {
    // this "when" will grow as other blocks need to be handled
    return when (this.context) {
        "section" -> StructuralNodeWrapper.Section(this as Section)
        "document" -> StructuralNodeWrapper.Document(this as Document)
        else -> StructuralNodeWrapper.Unknown
    }
}

/**
 * Wrapper class for improved functional dispatching.
 */
sealed class StructuralNodeWrapper() {
    data class Section(val wrapped: org.asciidoctor.ast.Section) : StructuralNodeWrapper()
    data class Document(val wrapped: org.asciidoctor.ast.Document) : StructuralNodeWrapper()
    object Unknown : StructuralNodeWrapper()
}

