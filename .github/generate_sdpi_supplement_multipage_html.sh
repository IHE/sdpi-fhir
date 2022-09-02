#!/bin/bash
gem install asciidoctor
gem install asciidoctor-diagram
gem install asciidoctor-multipage
asciidoctor -V
asciidoctor -r asciidoctor-diagram -r asciidoctor-multipage -b multipage_html5 -D SDPi_Supplement/sdpi-supplement/multipage SDPi_Supplement/sdpi-supplement.adoc