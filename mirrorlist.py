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
        # Read all lines from the file.
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
            if section is not None:
                data += "\n## %s\n" % section

                for used_server in self.servers[section].used:
                    data += "Server = %s\n" % used_server

                for unused_server in self.servers[section].unused:
                    data += "#Server = %s\n" % unused_server

        return data