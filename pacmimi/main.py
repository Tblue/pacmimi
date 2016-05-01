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
import functools
import os
import os.path
import re
import sys

from . import app_version
from .mirrorlist import Mirrorlist


# Default value for -b when option is specified by the user without an explicit value.
BACKUP_CONST_ARG = os.path.join("%d", "_orig_%b")


def setup_argparser():
    arg_parser = argparse.ArgumentParser(
        description="Merges two Pacman mirrorlist files and outputs the result to stdout."
    )

    arg_parser.add_argument(
        "-s",
        "--sane-defaults",
        action="store_true",
        help="Enable sane/useful defaults for regular use. Equal to specifying the options `-f -i -u -b'."
    )
    arg_parser.add_argument(
        "-b",
        "--backup",
        nargs="?",
        metavar="FORMAT",
        default=False,
        const=BACKUP_CONST_ARG,
        help="If given, make a backup of old_file before modifying it. %(metavar)s determines the name of the backup "
             "file and may contain the following format specifiers: "
             "`%%b' gets replaced by the basename of old_file; "
             "`%%p' gets replaced by old_file as specified on the command line; "
             "`%%d' gets replaced by the directory name of old_file as specified on the command line; "
             "`%%%%' gets replaced by a single `%%' char. "
             "Implies --in-place. Default %(metavar)s if option given without an explicit value: `%(const)s'."
    )
    arg_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite the backup of old_file if it exists."
    )
    arg_parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="Modify old_file directly instead of outputting results to stdout."
    )
    arg_parser.add_argument(
        "-u",
        "--remove-new",
        action="store_true",
        help="Remove new_file after a successful run."
    )
    arg_parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s " + app_version.version,
        help="Display the version of this program and exit."
    )

    arg_parser.add_argument(
        "old_file",
        help="Currently used mirrorlist file (merge target)."
    )
    arg_parser.add_argument(
        "new_file",
        help="New, unedited mirrorlist file (merge source; usually called `mirrorlist.pacnew')."
    )

    return arg_parser


def process_backup_format(orig_format, replacements, match):
    m = match.group(0)

    if m not in replacements:
        print(
            "W: Unhandled format specifier `%s' in backup format `%s'." % (m, orig_format),
            file=sys.stderr
        )
        return m

    return replacements[m]


def main():
    parsed_args = setup_argparser().parse_args()

    if parsed_args.sane_defaults:
        # -s (--sane-defaults) implies -f -i -u -b
        parsed_args.force = True
        parsed_args.in_place = True
        parsed_args.remove_new = True
        parsed_args.backup = BACKUP_CONST_ARG

    # Open both files for reading.
    try:
        old_file = open(parsed_args.old_file, "r", encoding="utf-8")
        new_file = open(parsed_args.new_file, "r", encoding="utf-8")
    except IOError as e:
        print("Could not open input file: %s" % e, file=sys.stderr)
        return 2

    # Now parse both files.
    try:
        old_mirrorlist = Mirrorlist(old_file)
        new_mirrorlist = Mirrorlist(new_file)
    except IOError as e:
        print("Could not parse input file: %s" % e, file=sys.stderr)
        return 3
    finally:
        old_file.close()
        new_file.close()

    # Now merge both lists!
    new_mirrorlist.merge_from_simple(old_mirrorlist)

    # Do we need to backup the original old_file?
    if parsed_args.backup is not False:
        # --backup implies --in-place.
        parsed_args.in_place = True

        parsed_args.backup = re.sub(
            "%.",
            functools.partial(process_backup_format,
                              parsed_args.backup, {
                                  "%%": "%",
                                  "%b": os.path.basename(parsed_args.old_file),
                                  "%p": parsed_args.old_file,
                                  "%d": os.path.dirname(parsed_args.old_file) or os.path.curdir
                              }),
            parsed_args.backup
        )

        try:
            if not parsed_args.force and os.access(parsed_args.backup, os.F_OK):
                raise OSError("Destination file exists")

            os.rename(parsed_args.old_file, parsed_args.backup)
        except OSError as e:
            print(
                "Could not backup input file `%s' to `%s': %s" % (parsed_args.old_file, parsed_args.backup, e),
                file=sys.stderr
            )
            return 4

    # That's it. output the new mirrorlist.
    output_file = sys.stdout

    if parsed_args.in_place:
        try:
            output_file = open(parsed_args.old_file, "w", encoding="utf-8")
        except IOError as e:
            print("Could not open output file: %s" % e, file=sys.stderr)
            return 5

    print(new_mirrorlist.get_string(), file=output_file)

    if parsed_args.in_place:
        output_file.close()

    # Finally, unlink the merge source, if requested.
    if parsed_args.remove_new:
        try:
            os.unlink(parsed_args.new_file)
        except IOError as e:
            print("Warning: Could not remove merge source: %s" % e, file=sys.stderr)
