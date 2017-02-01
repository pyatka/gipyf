import binascii

from gipyf.binop import byte_to_bits
from gipyf.graphics import Palete, Color
from gipyf.compression import Table


class GiPyF:
    def __init__(self):
        self.version = None
        self.width = 0
        self.height = 0
        self.is_global_color_table = True
        self.color_resolution = 0
        self.is_color_sorted = False
        self.table_colors_count = 0
        self.global_palete = None
        self.background = b'00'
        self.width_to_height = b'00'

        self.blocks = []

        self.frames_count = 0

    def save_frames(self):
        i = 0
        for block in self.blocks:
            if type(block) == Image:
                block.save_to_file("t/%s.png" % i)
                i += 1

    def parse(self, source):
        stream = source
        if type(source) == str:
            stream = open(source, 'rb')

        self.version = stream.read(6).decode()
        self.width = int.from_bytes(stream.read(2), byteorder='little')
        self.height = int.from_bytes(stream.read(2), byteorder='little')

        header_bit_data = byte_to_bits(stream.read(1))
        self.is_global_color_table = int(header_bit_data[0]) == 1
        self.color_resolution = pow(2, int(header_bit_data[1:4], 2) + 1)
        self.is_color_sorted = int(header_bit_data[5]) == 1
        self.table_colors_count = pow(2, int(header_bit_data[5:], 2) + 1)

        self.background = binascii.hexlify(stream.read(1))
        self.width_to_height = binascii.hexlify(stream.read(1))

        self.global_palete = Palete()
        pos = 0
        palete_bytes = stream.read(self.table_colors_count * 3)
        while pos < len(palete_bytes) - 2:
            self.global_palete.add_color(Color(palete_bytes[pos], palete_bytes[pos + 1], palete_bytes[pos + 2]))
            pos += 3

        part_marker = stream.read(1)
        while ord(part_marker) != 0x3b:
            if ord(part_marker) == 0x21:
                extention_type = ord(stream.read(1))
                if extention_type == 0xf9:
                    data = stream.read(int.from_bytes(stream.read(1), byteorder='little'))
                    color_alpha_index = int.from_bytes(data[-1:], byteorder='little')
                    play_delay = (
                    int.from_bytes(data[-3:-2], byteorder='little'), int.from_bytes(data[-2:-1], byteorder='little'))
                    binascii.hexlify(stream.read(1))

                    self.blocks.append(GraphicControlExtension(color_alpha_index, play_delay))
                else:
                    # print("skip block %s" % (extention_type))
                    block_length = int.from_bytes(stream.read(1), byteorder='little')
                    while block_length != 0:
                        stream.read(block_length)
                        block_length = int.from_bytes(stream.read(1), byteorder='little')
            elif ord(part_marker) == 0x2c:
                top_left_x = int.from_bytes(stream.read(2), byteorder='little')
                top_left_y = int.from_bytes(stream.read(2), byteorder='little')

                width = int.from_bytes(stream.read(2), byteorder='little')
                height = int.from_bytes(stream.read(2), byteorder='little')

                local_color_table = stream.read(1)

                lzw_length = int.from_bytes(stream.read(1), byteorder='little') + 1

                image = Image(width, height, lzw_length, self.global_palete, top_left_x=top_left_x, top_left_y=top_left_y,
                              local_color_table=local_color_table)

                parts = b''
                length = int.from_bytes(stream.read(1), byteorder='little')
                while length != 0:
                    parts += stream.read(length)
                    length = int.from_bytes(stream.read(1), byteorder='little')

                image.set_binary_data(parts)

                self.blocks.append(image)
                self.frames_count += 1

            part_marker = stream.read(1)

        for block in self.blocks:
            if type(block) == Image:
                block.unpack_binary_data()


class GraphicControlExtension:
    def __init__(self, color_alpha_index, play_delay):
        self.color_alpha_index = color_alpha_index
        self.play_delay = play_delay


class Image:
    def __init__(self, width, height, lzw_length, global_palete, top_left_x=0, top_left_y=0, local_color_table=b'00'):
        self.global_palete = global_palete
        self.local_color_table = local_color_table
        self.top_left_y = top_left_y
        self.top_left_x = top_left_x
        self.lzw_length = lzw_length
        self.height = height
        self.width = width

        self.binary_data = b''
        self.colors_data = []

    def set_binary_data(self, data):
        self.binary_data = data

    def save_to_file(self, name):
        try:
            import PIL.Image
        except:
            pass
        im = PIL.Image.new('RGB', (self.width, self.height))
        im.putdata([c.rgb() for c in self.colors_data])
        im.save(name)

    def unpack_binary_data(self):
        result = []
        full_result = []
        prev_block = None
        self._lzw_table = Table(self.global_palete.get_size())
        self._current_lzw_length = self.lzw_length
        generator = self._read_bits()
        block = next(generator)

        while block != None:
            if not self._lzw_table.is_end(block):
                if not self._lzw_table.is_clear(block):
                    if block == self._lzw_table.get_size():
                        ref = result[-1][:]
                        ref.append(ref[0])
                        self._lzw_table.add(ref)

                    result.append(self._lzw_table.get_value(block))

                    if prev_block is not None:
                        add = prev_block[:]
                        add.append(self._lzw_table.get_value(block)[0])
                        self._lzw_table.add(add)

                    prev_block = self._lzw_table.get_value(block)[:]
                else:
                    self._lzw_table = Table(self.global_palete.get_size())
                    self._current_lzw_length = self.lzw_length
                    prev_block = None


            if self._lzw_table.is_end(block) or self._lzw_table.is_clear(block):
                for r in result:
                    full_result += r
                result = []

            block = next(generator)

        for c in full_result:
            self.colors_data.append(self.global_palete.get_color(c))

    def _read_bits(self):
        pos = 7
        dataByte = 0
        cByte = byte_to_bits(self.binary_data[dataByte:dataByte + 1])

        while dataByte < len(self.binary_data) - 1:
            result = []

            if self._lzw_table.get_size() >= pow(2, self._current_lzw_length) and self._current_lzw_length < 12:
                self._current_lzw_length += 1

            for k in range(self._current_lzw_length):
                result.insert(0, cByte[pos])
                pos -= 1
                if pos < 0:
                    pos = 7
                    dataByte += 1
                    if len(self.binary_data) - dataByte == 0:
                        for ap in range(self._current_lzw_length - k):
                            result.insert(0, 0)

                        break
                    else:
                        cByte = byte_to_bits(self.binary_data[dataByte:dataByte + 1])

            yield int("".join([str(i) for i in result]), 2)

        yield None
