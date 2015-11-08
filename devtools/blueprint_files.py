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
"""

import struct
from enum import Enum


class EntityTypes(Enum):
    ship = 0
    shop = 1
    station = 2
    asteroid = 3
    planet = 4


class BinFileParser(object):
    def __init__(self, file):
        self.file = file

    def get(self, decoder):
        """
        Parameters
        ----------
        fmt: instance of `struct.Struct`
             or format string accepted by `struct.unpack`
        """
        if isinstance(decoder, str):
            decoder = struct.Struct(decoder)
        return decoder.unpack(self.file.read(decoder.size))


class Header(object):
    static_format = struct.Struct('>iiffffffI')
    element_format = struct.Struct('>HI')
    def __init__(self, version, type, xmin, ymin, zmin, xmax, ymax, zmax,
                 elements):
        self.version = version
        self.type = EntityTypes(type)
        self.xmin = xmin
        self.ymin = ymin
        self.zmin = zmin
        self.xmax = xmax
        self.ymax = ymax
        self.zmax = zmax
        self.elements = elements

    @staticmethod
    def from_file(filename):
        with open(filename, 'rb') as file:
            stream = BinFileParser(file)
            result = stream.get(Header.static_format)
            n_elements = result[-1]
            elements = dict(stream.get(Header.element_format) for _ in range(n_elements))
        return Header(*result[:-1], elements)

    def to_file(self, filename):
        with open(filename, 'wb') as file:
            file.write(Header.static_format.pack(self.version, self.type.value,
                                                 self.xmin, self.ymin,
                                                 self.zmin, self.xmax,
                                                 self.ymax, self.zmax,
                                                 len(self.elements)))
            for block_id in sorted(self.elements):
                count = self.elements[block_id]
                file.write(Header.element_format.pack(block_id, count))

    def __repr__(self):
        return "Header(version={}, type={}, xmin={}, ymin={}, zmin={}, " \
               "xmax={}, ymax={}, zmax={}, elements={})".format(
            self.version, self.type, self.xmin, self.ymin, self.zmin,
            self.xmax, self.ymax, self.zmax, self.elements)
