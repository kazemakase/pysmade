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

import os

from nose.tools import assert_equal, assert_tuple_equal, assert_raises

from devtools.block_config import BlockConfig


def test_blockconfig():
    bc = BlockConfig("tests/BlockTypes.properties", "tests/BlockConfig.xml")
    assert_raises(KeyError, lambda: bc.blocks[0])

    assert_tuple_equal(bc.blocks[1], ('Ship Core', 'Blocks.Ship'))
    assert_tuple_equal(bc.blocks[6], ('Cannon Computer', 'Blocks.Ship.Weapons'))
    assert_tuple_equal(bc.blocks[16], ('Cannon Barrel', 'Blocks.Ship.Weapons'))

