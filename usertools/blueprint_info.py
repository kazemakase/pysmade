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

from os import path
from argparse import ArgumentParser

from devtools.blueprint_files import Header
from devtools.block_config import BlockConfig


if __name__ == "__main__":
    parser = ArgumentParser(description='Show informations about a blueprint',
                            epilog="""pysmade  Copyright (C) 2015, Martin
Billinger. This program comes with ABSOLUTELY NO WARRANTY; This is free
software, and you are welcome to redistribute it under certain conditions; see
the GNU General Public License for more details.""")
    parser.add_argument('PATH_TO_BLUEPRINT')
    parser.add_argument('--starmade', dest='PATH_TO_STARMADE', help='Path to Starmade')
    args = vars(parser.parse_args())

    header = Header.from_file(path.join(args['PATH_TO_BLUEPRINT'],
                                        'header.smbph'))
    print(args['PATH_TO_BLUEPRINT'])
    print('\nHeader\n------')
    print('    Version : {}'.format(header.version))
    print('Entity type : {}'.format(header.type.name))
    print('Bounding box: ({}, {}, {}) - ({}, {}, {})'.format(header.xmin,
                                                             header.ymin,
                                                             header.zmin,
                                                             header.xmax,
                                                             header.ymax,
                                                             header.zmax))

    if args['PATH_TO_STARMADE']:
        blocks = BlockConfig(path.join(args['PATH_TO_STARMADE'],
                                       'data/config/BlockTypes.properties'),
                             path.join(args['PATH_TO_STARMADE'],
                                       'data/config/BlockConfig.xml')).blocks
        print('     count Block ID')
        for block_id in sorted(header.elements):
            count = header.elements[block_id]
            print('{:>10} {}'.format(count, blocks[block_id].name))
        print('({:>9} {})'.format(sum(header.elements.values()), 'Total'))
    else:
        print('Block ID   count')
        for block_id in sorted(header.elements):
            count = header.elements[block_id]
            print('{:>8} : {}'.format(block_id, count))
        print('   Total : {}'.format(sum(header.elements.values())))