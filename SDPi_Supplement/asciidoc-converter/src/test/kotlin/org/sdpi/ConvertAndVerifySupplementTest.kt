package org.sdpi

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import java.io.ByteArrayOutputStream

internal class ConvertAndVerifySupplementTest {
    @Test
    fun testOffset() {
        val testInputResourceName = "test_offset_input.adoc"
        val expectedStructureResourceName = "test_offset_expected_structure.txt"
        performTest(testInputResourceName, expectedStructureResourceName)
    }

    @Test
    fun testLevel() {
        val testInputResourceName = "test_level_input.adoc"
        val expectedStructureResourceName = "test_level_expected_structure.txt"
        performTest(testInputResourceName, expectedStructureResourceName)
    }

    private fun performTest(testInputResourceName: String, expectedStructureResourceName: String) {
        val expectedOutput =
            javaClass.classLoader.getResourceAsStream(expectedStructureResourceName)?.reader()?.readText()
                ?: throw Exception("Read failed")
        val actualOutput = ByteArrayOutputStream(expectedOutput.toByteArray().size)
        AsciidocConverter(
            AsciidocConverter.Input.StringInput(
                javaClass.classLoader.getResourceAsStream(testInputResourceName)?.reader()?.readText()
                    ?: throw Exception("Read failed")
            ),
            ByteArrayOutputStream(),
            AsciidocConverter.Mode.Test(actualOutput)
        ).run()

        assertEquals(expectedOutput, actualOutput.toString(Charsets.UTF_8))
    }
}