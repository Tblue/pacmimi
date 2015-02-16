# This file is part of pacmimi - Arch Linux Pacman mirrorlist merging utility.
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

from collections import OrderedDict, namedtuple
import re
import sys
import time


MirrorSection = namedtuple("MirrorSection", ["used", "unused"])


class Mirrorlist:
    def __init__(self, file_obj):
        self._file = file_obj
        self.gen_time = None
        self.servers = OrderedDict()

        self._parse()

    def _parse(self):
        lines = self._file.readlines()
        section = None

        for (i, line) in enumerate(lines):
            # Is this the generation date of the mirrorlist?
            if self.gen_time is None:
                match = re.search(r'^## Generated on (\d{4}-\d{2}-\d{2})\b', line)
                if match is not None:
                    try:
                        self.gen_time = time.strptime(match.group(1), "%Y-%m-%d")
                    except ValueError:
                        # Invalid date. Ignore it and try again if a similar line is encountered.
                        pass

                    continue

            match = re.search(r'^\s*(#)?\s*Server\s*=\s*(.+?)\s*$', line)
            if match is None:
                continue

            # Are we in a new section?
            if i > 0:
                section_match = re.search(r'^\s*##\s*(.+?)\s*$', lines[i-1])
                if section_match is not None:
                    section = section_match.group(1)

            servers = self.servers.setdefault(
                section,
                MirrorSection(OrderedDict(), OrderedDict())
            )
            server = match.group(2)

            if match.group(1) is None:
                # Uncommented (used) server found.
                servers.used[server] = None
            else:
                # Commented (unused) server found.
                servers.unused[server] = None

    def merge_from_simple(self, other_mirrorlist, reorder=True):
        """
        Merges the other_mirrorlist into this one, ignoring commonly untouched data.

        This ignores all unused servers in the other mirrorlist and only copies over used servers which are
        also in this mirrorlist.

        :param other_mirrorlist: The Mirrorlist to copy data from.
        :param reorder: If True, then the sections of this mirrorlist will be reordered to match the order of sections
        in the other_mirrorlist.
        :return: None
        """
        for section in other_mirrorlist.servers:
            if section not in self.servers:
                print("W: Section `%s' has been dropped." % section, file=sys.stderr)
                continue

            if reorder:
                self.servers.move_to_end(section)

            for used_server in other_mirrorlist.servers[section].used:
                if used_server in self.servers[section].used:
                    # Nothing to do.
                    continue

                if used_server not in self.servers[section].unused:
                    print("W: Section `%s': Server has been dropped: %s" % (section, used_server), file=sys.stderr)
                    continue

                self.servers[section].used[used_server] = None
                del self.servers[section].unused[used_server]

    def get_string(self):
        data = "##\n## Arch Linux repository mirrorlist\n"
        data += "## Generated on %s" % time.strftime("%Y-%m-%d", time.gmtime())

        if self.gen_time is not None:
            data += " (originally %s)" % time.strftime("%Y-%m-%d", self.gen_time)

        data += "\n##\n"

        for section in self.servers:
            data += "\n"

            if section is not None:
                data += "## %s\n" % section

            for used_server in self.servers[section].used:
                data += "Server = %s\n" % used_server

            for unused_server in self.servers[section].unused:
                data += "#Server = %s\n" % unused_server

        return data
