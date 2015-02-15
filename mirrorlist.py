from collections import OrderedDict, namedtuple
import re
import sys


MirrorSection = namedtuple("MirrorSection", ["used", "unused"])


class Mirrorlist:
    def __init__(self, file_obj):
        self._file = file_obj
        self.servers = OrderedDict()

        self._parse()

    def _parse(self):
        # Read all lines from the file.
        lines = self._file.readlines()
        section = None

        for (i, line) in enumerate(lines):
            # Start of new section?
            match = re.search(r'^\s*##\s*(.+?)\s*$', line)
            if match is not None:
                section = match.group(1)
                continue

            match = re.search(r'^\s*(#)?\s*Server\s*=\s*(.+?)\s*$', line)
            if match is None:
                continue

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

    def merge_from_simple(self, other_mirrorlist):
        """
        Merges the other_mirrorlist into this one, ignoring commonly untouched data.

        This ignores all unused servers in the other mirrorlist and only copies over used servers which are
        also in this mirrorlist.

        :param other_mirrorlist: The Mirrorlist to copy data from.
        :return: None
        """
        for section in other_mirrorlist.servers:
            if section not in self.servers:
                print("W: Section `%s' has been dropped." % section, file=sys.stderr)
                continue

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
        data = ""
        for section in self.servers:
            if section is not None:
                data += "\n## %s\n" % section

                for used_server in self.servers[section].used:
                    data += "Server = %s\n" % used_server

                for unused_server in self.servers[section].unused:
                    data += "#Server = %s\n" % unused_server

        return data