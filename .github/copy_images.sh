#!/bin/bash
gem install asciidoctor
gem install asciidoctor-diagram
gem install asciidoctor-multipage
asciidoctor -V
cd SDPi_Supplement/asciidoc
asciidoctor -r asciidoctor-diagram -r asciidoctor-multipage -b multipage_html5 -D ../ sdpi-supplement.adoc
cp -R images ../sdpi-supplement/images
rm -rf ../sdpi-supplement/.asciidoctor
rm -rf ../.asciidoctor
cp -R js ../sdpi-supplement/js
