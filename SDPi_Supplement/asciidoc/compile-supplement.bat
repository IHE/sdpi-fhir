@ECHO OFF

WHERE /q asciidoctor
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
CALL asciidoctor -r asciidoctor-diagram -r asciidoctor-multipage -b multipage_html5 -D ../sdpi-supplement/multipage sdpi-supplement.adoc

ECHO Copy images...
ECHO XCOPY
ECHO   asciidoc\images
ECHO   sdpi-supplement\multipage\images
ECHO   /s /e /i /y
CALL XCOPY images ..\sdpi-supplement\multipage\images /S /E /I /Y

ECHO Delete temporary files...
ECHO RMDIR
ECHO   ..\sdpi-supplement\multipage\.asciidoctor
ECHO   /S /Q
RMDIR ..\sdpi-supplement\multipage\.asciidoctor /S /Q

@ECHO ON