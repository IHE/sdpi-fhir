#!/bin/bash
gem install asciidoctor
gem install asciidoctor-diagram
gem install asciidoctor-multipage
asciidoctor -V
asciidoctor-multipage -D SDPi_Supplement/sdpi-supplement/multipage SDPi_Supplement/sdpi-supplement.adoc