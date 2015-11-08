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

from nose.tools import assert_equal, assert_tuple_equal

from devtools.blueprint_files import BinFileParser, EntityTypes, Header


def assert_headers_equal(a, b):
    assert_equal(a.version, b.version)
    assert_equal(a.type, b.type)
    assert_equal(a.xmin, b.xmin)
    assert_equal(a.ymin, b.ymin)
    assert_equal(a.zmin, b.zmin)
    assert_equal(a.xmax, b.xmax)
    assert_equal(a.ymax, b.ymax)
    assert_equal(a.zmax, b.zmax)
    assert_equal(a.elements, b.elements)


def test_binfileparser():
    with open('test.bin', 'wb') as file:
        file.write(b'\00\01\02')
    with open('test.bin', 'rb') as file:
        parser = BinFileParser(file)
        assert_tuple_equal(parser.get('bbb'), (0, 1, 2))


def test_header_repr():
    original = Header(1, EntityTypes.asteroid, -1, -2, -3, 4, 5, 6, {7: 800, 13: 900, 3: 42})
    copied = eval(repr(original))
    assert_headers_equal(original, copied)


def test_header_read_write_consistency():
    original = Header(1, EntityTypes.asteroid, -1, -2, -3, 4, 5, 6, {7: 800, 13: 900, 3: 42})
    original.to_file('test.smbph')
    copied = Header.from_file('test.smbph')
    os.remove('test.smbph')
    assert_headers_equal(original, copied)
