@ECHO OFF

where /q asciidoctor
IF ERRORLEVEL 1 (
    ECHO The asciidoctor application is missing. Ensure it is installed and placed in your PATH.
    ECHO For installation hints, go visit https://asciidoctor.org/#installation.
    ECHO Do also ensure asciidoctor-diagram and asciidoctor-multipage plugins are installed.
    ECHO asciidoctor-diagram: https://docs.asciidoctor.org/diagram-extension/latest/#installation
    ECHO asciidoctor-multipage: https://github.com/owenh000/asciidoctor-multipage#installation
    PAUSE
    EXIT /B
)

ECHO Start multipage conversion...
ECHO asciidoctor
ECHO   -r asciidoctor-diagram
ECHO   -r asciidoctor-multipage
ECHO   -b multipage_html5
ECHO   -D sdpi-supplement/multipage
ECHO   asciidoc/sdpi-supplement.adoc
call asciidoctor -r asciidoctor-diagram -r asciidoctor-multipage -b multipage_html5 -D ../sdpi-supplement/multipage sdpi-supplement.adoc

ECHO Copy images...
ECHO xcopy
ECHO   asciidoc\images
ECHO   sdpi-supplement\multipage\images
ECHO   /s /e /i /y
call xcopy images ..\sdpi-supplement\multipage\images /s /e /i /y

@ECHO ON