#!/bin/bash
gem install asciidoctor
gem install asciidoctor-diagram
gem install asciidoctor-multipage
asciidoctor -V
cd SDPi_Supplement/asciidoc
asciidoctor -r asciidoctor-diagram -r asciidoctor-multipage -b multipage_html5 -D ../sdpi-supplement/multipage sdpi-supplement.adoc
cp -R images ../sdpi-supplement/multipage/images
rm -rf ../sdpi-supplement/multipage/.asciidoctor
cp -R images ../sdpi-supplement/singlepage/images
rm -rf ../sdpi-supplement/singlepage/.asciidoctor
cp -R js ../sdpi-supplement/singlepage/js
