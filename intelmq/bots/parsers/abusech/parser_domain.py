# -*- coding: utf-8 -*-
"""
Parsers simple newline separated list of domains.

Docs:
 - https://feodotracker.abuse.ch/blocklist/
 - https://palevotracker.abuse.ch/blocklists.php
 - https://zeustracker.abuse.ch/blocklist.php
"""

import sys

import dateutil.parser

from intelmq.lib.bot import Bot
from intelmq.lib.message import Event

SOURCE_FEEDS = {'https://feodotracker.abuse.ch/blocklist/?download=domainblocklist': 'Cridex',
                'https://palevotracker.abuse.ch/blocklists.php?download=domainblocklist': 'Palevo',
                'https://zeustracker.abuse.ch/blocklist.php?download=baddomains': 'Zeus'}


class AbusechDomainParserBot(Bot):
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
            event.add('source.fqdn', line)
            event.add("raw", line)
            event.add("malware.name", SOURCE_FEEDS[report["feed.url"]])
            yield event

    def recoverline(self, line):
        return '\n'.join(self.tempdata + [line])


if __name__ == "__main__":
    bot = AbusechDomainParserBot(sys.argv[1])
    bot.start()
