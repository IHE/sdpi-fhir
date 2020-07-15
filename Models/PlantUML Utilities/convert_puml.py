import argparse
import os
import subprocess
from pathlib import Path


def convert(java, plantuml, file, output_format):
    print('Convert "{}" to {}'.format(file, output_format))
    subprocess.run([java, '-jar', plantuml, '-t{}'.format(output_format), str(file)])


def main():
    parser = argparse.ArgumentParser(description="Takes PlantUML files and exports them to the SVG and/or PNG format")
    parser.add_argument("-j", "--java", dest="java", metavar='FILE', default='java',
                        help="path and filename of java executable")
    parser.add_argument("-u", "--plantuml", dest="plantuml", metavar='FILE', default='plantuml.jar',
                        help="path and filename of plantuml jar")
    parser.add_argument("-s", "--svg", dest="do_svg", action='store_true',
                        help="use to export to SVG")
    parser.add_argument("-p", "--png", dest="do_png", action='store_true',
                        help="use to export to PNG")
    parser.add_argument("-r", "--recursive", dest="do_recursive", action='store_true',
                        help="use for recursive directory searching")
    parser.add_argument("-f", "--filter", dest="filter", metavar='FILTER', default='*.puml',
                        help="input file filter")
    parser.add_argument("-d", "--directory", dest="input_directory", metavar="DIR", default='',
                        help="the input directory where to search PlantUML files")

    options = parser.parse_args()

    if not options.do_svg and not options.do_png:
        print('Caution: no target format defined. Use options --svg and/or --png to actually convert matching files.')

    directory_path = Path(options.input_directory)
    if options.do_recursive:
        affected_files = directory_path.rglob(options.filter.lower())
    else:
        affected_files = directory_path.glob(options.filter.lower())
    affected_files = [file for file in affected_files if not os.path.isdir(file)]

    for path in affected_files:
        print('Match {}'.format(os.path.basename(path)))
        if options.do_svg:
            convert(options.java, options.plantuml, path, 'svg')
        if options.do_png:
            convert(options.java, options.plantuml, path, 'png')

    print('Done.')


if __name__ == '__main__':
    main()
