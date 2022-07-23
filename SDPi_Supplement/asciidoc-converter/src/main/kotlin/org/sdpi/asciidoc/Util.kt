package org.sdpi.asciidoc

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