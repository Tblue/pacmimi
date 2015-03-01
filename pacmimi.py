#!/usr/bin/env python
#
# pacmimi - Arch Linux Pacman mirrorlist merging utility
#
# Copyright (c) 2015, Tilman Blumenbach
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import os
import sys

from mirrorlist import Mirrorlist


def setup_argparser():
    arg_parser = argparse.ArgumentParser(
        description="Merges two Pacman mirrorlist files and outputs the result to stdout."
    )

    arg_parser.add_argument(
        "-b",
        "--backup",
        nargs="?",
        metavar="SUFFIX",
        default=False,
        const="~",
        help="If given, make a backup of out_file before modifying it. The file is moved to a file with the same "
             "name, but with a special suffix appended (default: `%(const)s'). An alternative suffix can be given as "
             "an argument to this option. Implies --in-place."
    )
    arg_parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="Modify old_file directly instead of outputting results to stdout."
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

# --backup implies --in-place.
if parsed_args.backup is not False:
    parsed_args.in_place = True

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
finally:
    old_file.close()
    new_file.close()

# Now merge both lists!
new_mirrorlist.merge_from_simple(old_mirrorlist)

# Do we need to backup the original old_file?
if parsed_args.backup is not False:
    backup_file = parsed_args.old_file + parsed_args.backup

    try:
        if os.access(backup_file, os.F_OK):
            raise OSError("Destination file exists")

        os.rename(parsed_args.old_file, backup_file)
    except OSError as e:
        print(
            "Could not backup input file `%s' to `%s': %s" % (parsed_args.old_file, backup_file, e),
            file=sys.stderr
        )
        sys.exit(4)

# That's it. output the new mirrorlist.
output_file = sys.stdout
if parsed_args.in_place:
    try:
        output_file = open(parsed_args.old_file, "w", encoding="utf-8")
    except IOError as e:
        print("Could not open output file: %s" % e, file=sys.stderr)
        sys.exit(5)

print(new_mirrorlist.get_string(), file=output_file)
