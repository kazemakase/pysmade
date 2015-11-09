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


class TagTypes(Enum):
    finish = 1
    segment_manager = 2
    docking = 3


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

    def get_one(self, decoder):
        """
        Parameters
        ----------
        fmt: instance of `struct.Struct`
             or format string accepted by `struct.unpack`
        """
        if isinstance(decoder, str):
            decoder = struct.Struct(decoder)
        return decoder.unpack(self.file.read(decoder.size))[0]


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


class String(object):
    @staticmethod
    def deserialize(stream):
        len = stream.get_one('>H')
        return stream.get_one('>%ds' % len).decode('ascii')

    @staticmethod
    def to_file(file, s):
        file.write(struct.pack('>H', len(s)))
        file.write(struct.pack('>%ds' % len(s), s.encode('ascii')))


class ByteArray(object):
    @staticmethod
    def deserialize(stream):
        len = stream.get_one('>H')
        return stream.get_one('>%ds' % len)

    @staticmethod
    def to_file(file, b):
        file.write(struct.pack('>H', len(b)))
        file.write(struct.pack('>%ds' % len(b), b))


class TagList(object):
    def __init__(self, type, tl):
        self.list = tl
        self.type = type

    @staticmethod
    def deserialize(stream):
        type, length = stream.get('>bI')
        list = [Payload.deserialize(stream, type) for _ in range(length)]
        return TagList(type, list)

    def to_file(self, file):
        file.write(struct.pack('>bI', self.type, len(self.list)))
        for pl in self.list:
            pl.to_file(file)

    def __repr__(self):
        return '[' + ', '.join(repr(pl) for pl in self.list) + ']'


class TagStruct(object):
    def __init__(self, tags):
        self.tags = tags

    @staticmethod
    def deserialize(stream):
        tags = []
        while True:
            tag = Tag.deserialize(stream)
            if tag.type() == 0:
                break
            tags.append(tag)
        return TagStruct(tags)

    def to_file(self, file):
        for tag in self.tags:
            tag.to_file(file)
        EmptyTag.to_file(file)

    def __repr__(self):
        return '\n'.join(repr(tag) for tag in self.tags)


class Tag(object):
    def __init__(self, name=None, payload=None):
        self.name = name
        self.payload = payload

    @staticmethod
    def deserialize(stream):
        type = stream.get_one('>b')
        name = None
        if type > 0:
            name = String.deserialize(stream)
        payload = Payload.deserialize(stream, abs(type))
        return Tag(name, payload)

    def to_file(self, file):
        file.write(struct.pack('>b', self.type()))
        if self.name is not None:
            String.to_file(file, self.name)
        self.payload.to_file(file)

    def type(self):
        if self.payload is None:
            return 0
        type = self.payload.type
        if self.name is None:
            return -type
        return type

    def __repr__(self):
        return "Tag(name={}, payload={})".format(self.name, self.payload)


class Payload(object):
    def __init__(self, type, data):
        self.type = type
        self.data = data

    @staticmethod
    def deserialize(stream, type):
        if type == 0:
            data = None
        elif type == 1:
            data = stream.get_one('b')  # int8
        elif type == 2:
            data = stream.get_one('>h')  # int16
        elif type == 3:
            data = stream.get_one('>i')  # int32
        elif type == 4:
            data = stream.get_one('>q')  # int64
        elif type == 5:
            data = stream.get_one('>f')  # float
        elif type == 6:
            data = stream.get_one('>d')  # double
        elif type == 7:
            data = ByteArray.deserialize(stream)
        elif type == 8:
            data = String.deserialize(stream)
        elif type == 9:
            data = stream.get('>fff')  # float vector
        elif type == 10:
            data = stream.get('>iii')  # int vector
        elif type == 11:
            data = stream.get('>bbb')  # byte vector
        elif type == 12:
            data = TagList.deserialize(stream)
        elif type == 13:
            data = TagStruct.deserialize(stream)
        elif type == 14:
            data = stream.get_one('b')  # factory registration
        elif type == 15:
            data = stream.get('>ffff')  # float 4 vector
        else:
            raise ValueError('unknown tag-payload type: {}'.format(type))
        return Payload(type, data)

    def to_file(self, file):
        if self.type == 0:
            return
        elif self.type == 1:
            file.write(struct.pack('b', self.data))
        elif self.type == 2:
            file.write(struct.pack('>h', self.data))
        elif self.type == 3:
            file.write(struct.pack('>i', self.data))
        elif self.type == 4:
            file.write(struct.pack('>q', self.data))
        elif self.type == 5:
            file.write(struct.pack('>f', self.data))
        elif self.type == 6:
            file.write(struct.pack('>d', self.data))
        elif self.type == 7:
            ByteArray.to_file(file, self.data)
        elif self.type == 8:
            String.to_file(file, self.data)
        elif self.type == 9:
            file.write(struct.pack('>fff', *self.data))
        elif self.type == 10:
            file.write(struct.pack('>iii', *self.data))
        elif self.type == 11:
            file.write(struct.pack('>bbb', *self.data))
        elif self.type == 12:
            self.data.to_file(file)
        elif self.type == 13:
            self.data.to_file(file)
        elif self.type == 14:
            file.write(struct.pack('b', self.data))
        elif self.type == 15:
            file.write(struct.pack('>ffff', *self.data))
        else:
            raise ValueError('unknown tag-payload type: {}'.format(self.type))

    def __repr__(self):
        return repr(self.data)


EmptyPayload = Payload(0, None)
EmptyTag = Tag(name=None, payload=EmptyPayload)


class TagRoot(object):
    def __init__(self, version=0, tag=EmptyTag):
        self.version = version
        self.tag = tag

    @staticmethod
    def deserialize(stream):
        version = stream.get_one('>H')
        if version == 0x1:
            raise NotImplementedError('Compressed tags not supported yet.')
        tag = Tag.deserialize(stream)
        return TagRoot(version, tag)

    def to_file(self, file):
        file.write(struct.pack('>H', self.version))
        self.tag.to_file(file)

    def __repr__(self):
        return "TagRoot(version={}, tag={}".format(self.version, self.tag)


class MetaDockedEntry(object):
    def __init__(self, name, pos, size, style, orientation):
        self.name = name
        self.pos = tuple(pos)
        self.size = tuple(size)
        self.style = style
        self.orientation = orientation

    @staticmethod
    def from_file(stream):
        name = String.deserialize(stream)
        pos = stream.get('>iii')
        size = stream.get('>fff')
        style, orientation = stream.get('>hb')
        return MetaDockedEntry(name, pos, size, style, orientation)

    def to_file(self, file):
        String.to_file(file, self.name)
        file.write(struct.pack('>iii', *self.pos))
        file.write(struct.pack('>fff', *self.size))
        file.write(struct.pack('>hb', self.style, self.orientation))


class Meta(object):
    def __init__(self, version, docked=None, tags=None):
        self.version = version
        self.docked = docked
        self.tags = tags

    @staticmethod
    def from_file(filename):
        with open(filename, 'rb') as file:
            stream = BinFileParser(file)
            version, = stream.get('>i')
            docked = None
            tags = None
            while True:
                tag = TagTypes(stream.get_one('>b'))

                if tag == TagTypes.finish:
                    break
                elif tag == TagTypes.segment_manager:
                    tags = TagRoot.deserialize(stream)
                    break
                elif tag == TagTypes.docking:
                    docked_count = stream.get_one('>I')
                    docked = [MetaDockedEntry.from_file(stream) for _ in
                              range(docked_count)]

        return Meta(version, docked, tags)

    def to_file(self, filename):
        with open(filename, 'wb') as file:
            file.write(struct.pack('>i', self.version))

            if self.docked is not None:
                file.write(struct.pack('>b', TagTypes.docking.value))
                file.write(struct.pack('>I', len(self.docked)))
                for d in self.docked:
                    d.to_file(file)

            if self.tags is not None:
                file.write(struct.pack('>b', TagTypes.segment_manager.value))
                self.tags.to_file(file)

            file.write(struct.pack('>b', TagTypes.finish.value))

#meta = Meta.from_file("../data/Isanth-VI/meta.smbpm")
#meta = Meta.from_file("/home/billinger/.local/share/Steam/SteamApps/common/StarMade/StarMade/blueprints-stations/pirate/Piratestation Alpha/meta.smbpm")
