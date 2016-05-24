# -*- coding: utf-8 -*-
"""
Parsers simple newline separated list of IPs.

Docs:
 - https://feodotracker.abuse.ch/blocklist/
 - https://palevotracker.abuse.ch/blocklists.php
 - https://zeustracker.abuse.ch/blocklist.php
"""

import sys

import dateutil

from intelmq.lib.bot import Bot
from intelmq.lib.message import Event

SOURCE_FEEDS = {'https://feodotracker.abuse.ch/blocklist/?download=ipblocklist': 'Cridex',
                'https://palevotracker.abuse.ch/blocklists.php?download=ipblocklist': 'Palevo',
                'https://zeustracker.abuse.ch/blocklist.php?download=badips': 'Zeus'}


class AbusechIPParserBot(Bot):
    lastgenerated = None

    def parseline(self, line, report):
        if line.startswith('#'):
            self.tempdata.append(line)
            if 'Generated on' in line:
                row = line.strip('# ')[13:]
                self.lastgenerated = dateutil.parser.parse(row).isoformat()
        else:
            event = Event(report)
            event.add('time.source', self.lastgenerated)
            event.add('classification.type', 'c&c')
            event.add('source.ip', line)
            event.add("raw", line)
            event.add("malware.name", SOURCE_FEEDS[report["feed.url"]])
            yield event

    def recoverline(self, line):
        return '\n'.join(self.tempdata + [line])


if __name__ == "__main__":
    bot = AbusechIPParserBot(sys.argv[1])
    bot.start()
