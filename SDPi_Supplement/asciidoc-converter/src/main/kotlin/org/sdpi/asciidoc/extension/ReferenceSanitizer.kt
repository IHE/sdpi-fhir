package org.sdpi.asciidoc.extension

import org.asciidoctor.ast.Document
import org.asciidoctor.extension.Postprocessor
import org.jsoup.Jsoup
import org.jsoup.nodes.Element
import java.net.URI

enum class LabelSource {
    SECTION,
    TABLE_OR_FIGURE,
    APPENDIX
}

data class LabelInfo(
    val label: String,
    val source: LabelSource,
    val prefix: String = ""
)

class ReferenceSanitizer(private val anchorLabels: Map<String, LabelInfo>) : Postprocessor() {
    override fun process(document: Document, output: String): String {
        val doc = Jsoup.parse(output, "UTF-8")

        val anchors = doc.getElementsByTag("a")
        anchors.forEach { anchor ->
            if (!isInToc(anchor)) {
                val href = anchor.attr("href") ?: ""
                anchorLabels[URI.create(href).fragment]?.let {
                    when (it.source) {
                        LabelSource.SECTION -> anchor.text("Section ${it.label}")
                        LabelSource.TABLE_OR_FIGURE -> anchor.text(it.label)
                        LabelSource.APPENDIX -> anchor.text("Appendix ${it.prefix}:${it.label}")
                    }
                }
            }
        }

        return doc.html()
    }

    private fun isInToc(element: Element) = element.parents().firstOrNull { it.id() == "toc" } != null
}