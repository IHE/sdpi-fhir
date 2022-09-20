package org.sdpi.asciidoc

import org.apache.logging.log4j.kotlin.loggerOf
import org.asciidoctor.ast.Section
import org.asciidoctor.ast.StructuralNode
import org.sdpi.asciidoc.model.StructuralNodeWrapper
import org.sdpi.asciidoc.model.toSealed

/**
 * Resolves the block id attribute from an attributes map.
 */
fun blockId(attributes: Map<String, Any>) = attributes[BlockAttribute.ID.key].toString()

/**
 * Resolves the block title attribute from an attributes map.
 */
fun blockTitle(attributes: Map<String, Any>) = attributes[BlockAttribute.TITLE.key].toString()


/**
 * Creates a context name without a leading colon.
 *
 * `BlockProcessor.createBlock()` requires a context name without a leading colon.
 * Use this function to check the format and remove the leading colon for you.
 */
fun plainContext(context: String) = "^:([a-z]+)$".toRegex()
    .findAll(context)
    .map { it.groupValues[1] }
    .toList()
    .first()

/**
 * Checks if an expression holds true, prints out an error message and throws if not.
 *
 * @param value The expression that is tested.
 * @param node The node from which file and line number is extracted. Make sure map source is enabled.
 * @param msg A function that creates the error message.
 */
fun validate(value: Boolean, node: StructuralNode, msg: () -> String) {
    if (value) {
        return
    }

    val msgWithLocation = "Error in file ${node.sourceLocation.path}@${node.sourceLocation.lineNumber}: ${msg()}"
    checkNotNull(node.sourceLocation) { "Fatal error: map source disabled" }
    loggerOf(Any::class.java).error { msgWithLocation }
    throw Exception(msgWithLocation)
}

fun StructuralNode.isAppendix() = when (val section = this.toSealed()) {
    is StructuralNodeWrapper.Section -> section.wrapped.sectionName == "appendix"
    else -> false
}