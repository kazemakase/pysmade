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
import struct

from nose.tools import assert_equal, assert_tuple_equal

from devtools.blueprint_files import BinFileParser, EntityTypes, Header
from devtools.blueprint_files import Meta, MetaDockedEntry, TagRoot, Tag
from devtools.blueprint_files import Payload, TagStruct, TagList


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


def assert_meta_equal(a, b):
    assert_equal(a.version, b.version)
    for da, db in zip(a.docked, b.docked):
        assert_docked_equal(da, db)
    assert_equal(a.tags.version, b.tags.version)
    assert_tags_equal(a.tags.tag, b.tags.tag)


def assert_docked_equal(a, b):
    assert_equal(a.name, b.name)
    assert_equal(a.pos, b.pos)
    assert_equal(a.size, b.size)
    assert_equal(a.style, b.style)
    assert_equal(a.orientation, b.orientation)


def assert_tags_equal(a, b):
    assert_equal(a.name, b.name)
    assert_payload_equal(a.payload, b.payload)


def assert_taglist_equal(a, b):
    assert_equal(a.type, b.type)
    assert_equal(len(a.list), len(b.list))
    for pa, pb in zip(a.list, b.list):
        assert_payload_equal(pa, pb)


def assert_tagstruct_equal(a, b):
    assert_equal(len(a.tags), len(b.tags))
    for ta, tb in zip(a.tags, b.tags):
        assert_tags_equal(ta, tb)


def assert_payload_equal(a, b):
    assert_equal(a.type, b.type)
    if a.type == 0:
        assert_equal(a.data, None)
        assert_equal(b.data, None)
    elif a.type in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15]:
        assert_equal(a.data, b.data)
    elif a.type == 12:
        assert_taglist_equal(a.data, b.data)
    elif a.type == 13:
        assert_tagstruct_equal(a.data, b.data)


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


def test_meta():
    docked = [MetaDockedEntry("name", [1, 2, 3], [1.0, 2.0, 3.0], 7, -1)]

    bytearray_tag = Tag(None, Payload(7, b'123'))

    list_tag = Tag(None, Payload(12, TagList(1, [Payload(1, 1), Payload(1, 2), Payload(1, 3)])))

    named_vector_tag = Tag("named_vector", Payload(10, (0, 4, 2)))

    struct_tag = Tag(None, Payload(13, TagStruct([list_tag, bytearray_tag, named_vector_tag])))

    tags = TagRoot(version=0, tag=struct_tag)

    meta = Meta(version=0, docked=docked, tags=tags)
    meta.to_file('test.smbpm')

    reload = Meta.from_file('test.smbpm')

    assert_meta_equal(meta, reload)