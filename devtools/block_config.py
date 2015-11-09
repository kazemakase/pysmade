""" This file is part of pysmade.

    pysmade is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pysmade is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

    Copyright 2015, Martin Billinger

    The binary file decoders in this file are based on information from the
    Starmade Wiki page "Blueprint File Formats"
    <https://starmadepedia.net/wiki/Blueprint_File_Formats> (June 4, 2015).
"""

from collections import deque, namedtuple
import xml.etree.ElementTree as ET


Block = namedtuple('Block', ['name', 'category'])


class BlockConfig(object):
    def __init__(self, idmapfile='BlockTypes.properties', blockcfgfile='BlockConfig.xml'):
        idmap = {}
        for line in open(idmapfile):
            ids = [l.strip() for l in line.split('=')]
            if ids == ['']:
                continue
            idmap[ids[0]] = int(ids[1])

        xmltree = ET.parse(blockcfgfile)
        root = xmltree.getroot()

        queue = deque([('Blocks', i) for i in root.find('Element')])

        self.blocks = {}
        while queue:
            category, item = queue.popleft()
            if item.tag != 'Block':
                category += '.' + item.tag
                for child in item:
                    queue.append((category, child))
            else:
                id = idmap[item.attrib['type']]
                self.blocks[id] = Block(name=item.attrib['name'],
                                        category=category)

#BlockConfig('../data/BlockTypes.properties', '../data/BlockConfig.xml')