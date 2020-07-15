import argparse
import os
import re
from pathlib import Path

INCLUDE_PATTERN = pattern = re.compile('^\\s*(!include)?\\s+(.*)$')


def process_recursive(output_file, path):
    with open(path) as input_file:
        lines = input_file.readlines()
        for line in lines:
            result = pattern.search(line)
            if result is None or result.group(1) is None:
                output_file.write(line)
                continue

            process_recursive(output_file, os.path.join(os.path.dirname(path), result.group(2).strip()))
            output_file.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Takes PlantUML files, recursively expands included references and "
                                                 "stores a copy under <FILE-NAME>.expanded")
    parser.add_argument("-r", "--recursive", dest="do_recursive", action='store_true',
                        help="use for recursive directory searching")
    parser.add_argument("-f", "--filter", dest="filter", metavar='FILTER', default='*.puml',
                        help="input file filter")
    parser.add_argument("-d", "--directory", dest="input_directory", metavar="DIR", default='',
                        help="the input directory where to search PlantUML files")

    options = parser.parse_args()

    directory_path = Path(options.input_directory)
    if options.do_recursive:
        affected_files = directory_path.rglob(options.filter.lower())
    else:
        affected_files = directory_path.glob(options.filter.lower())
    affected_files = [file for file in affected_files if not os.path.isdir(file)]

    for path in affected_files:
        out_name = str(path) + '.expanded'
        print('Read from {}'.format(str(path)))
        print('Write to {}'.format(out_name))
        with open(out_name, "w") as output_file:
            process_recursive(output_file, str(path))

    print('Done.')


if __name__ == '__main__':
    main()
