package org.sdpi

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import java.io.ByteArrayOutputStream
import java.io.FileOutputStream
import java.nio.charset.Charset

internal class ConvertAndVerifySupplementTest {
    @Test
    fun testSequence() {
        val expectedOutput =
            javaClass.classLoader.getResourceAsStream("test_offset_expected_structure.txt")?.reader()?.readText()
                ?: throw Exception("Read failed")
        val actualOutput = ByteArrayOutputStream(expectedOutput.toByteArray().size)
        AsciidocConverter(
            AsciidocConverter.Input.StringInput(
                javaClass.classLoader.getResourceAsStream("test_offset_input.adoc")?.reader()?.readText()
                    ?: throw Exception("Read failed")
            ),
            ByteArrayOutputStream(),
            AsciidocConverter.Mode.Test(actualOutput)
        ).run()

        assertEquals(expectedOutput, actualOutput.toString(Charsets.UTF_8))
    }
}