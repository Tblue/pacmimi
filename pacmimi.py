#!/usr/bin/env python

import argparse
import sys

from mirrorlist import Mirrorlist


def setup_argparser():
    arg_parser = argparse.ArgumentParser(
        description="Merges two Pacman mirrorlist files and outputs the result to stdout."
    )

    arg_parser.add_argument(
        "old_file",
        help="Currently used mirrorlist file."
    )
    arg_parser.add_argument(
        "new_file",
        help="New, unedited mirrorlist file (usually called `mirrorlist.pacnew')."
    )

    return arg_parser


parsed_args = setup_argparser().parse_args()

# Open both files for reading.
try:
    old_file = open(parsed_args.old_file, "r", encoding="utf-8")
    new_file = open(parsed_args.new_file, "r", encoding="utf-8")
except IOError as e:
    print("Could not open input file: %s" % e, file=sys.stderr)
    sys.exit(2)

# Now parse both files.
try:
    old_mirrorlist = Mirrorlist(old_file)
    new_mirrorlist = Mirrorlist(new_file)
except IOError as e:
    print("Could not parse input file: %s" % e, file=sys.stderr)
    sys.exit(3)

# Now merge both lists!
new_mirrorlist.merge_from_simple(old_mirrorlist)

# That's it. output the new mirrorlist.
print(new_mirrorlist.get_string())