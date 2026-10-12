"""BNF glyph token codec, including the native zero-token end marker.

The game's reader at 0x81145a38 stops on a zero token, not the next glyph's
offset or an FCAA declared length. Bound reads/writes here to reject records
which would make it continue into the following record.
"""
import struct

from dr12ae_extract import MAGIC


def decode_record(data, expected_size=338):
    position = 12 if data[:4] == MAGIC else 0
    output = bytearray()
    previous = 1

    def read(count):
        nonlocal position
        if position + count > len(data):
            raise ValueError('BNF glyph missing native terminator or truncated token')
        value = data[position:position + count]
        position += count
        return value

    def append(values):
        if len(output) + len(values) > expected_size:
            raise ValueError('BNF glyph exceeds native output capacity')
        output.extend(values)

    while True:
        token = read(1)[0]
        if token == 0:
            if len(output) != expected_size:
                raise ValueError('BNF glyph ended before its bitmap was complete')
            if any(data[position:]):
                raise ValueError('BNF glyph has data after its native terminator')
            return bytes(output)
        if token & 128:
            count = ((token >> 5) & 3) + 4
            offset = ((token & 31) << 8) + read(1)[0]
            previous = offset
        elif token & 64 and token & 32:
            count, offset = token & 31, previous
        elif token & 64:
            count = token & 15
            if token & 16:
                count = (count << 8) + read(1)[0]
            count += 4
            append(read(1) * count)
            continue
        else:
            count = token & 31
            if token & 32:
                count = (count << 8) + read(1)[0]
            append(read(count))
            continue
        if offset == 0 or offset > len(output):
            raise ValueError('Invalid BNF glyph back-reference')
        for _ in range(count):
            append(bytes([output[-offset]]))


def encode_record(bitmap):
    if len(bitmap) != 338:
        raise ValueError('BNF glyph bitmap must contain 338 bytes')
    # One extended literal, followed by the native zero-token terminator.
    result = bytes([0x20 | (len(bitmap) >> 8), len(bitmap) & 255]) + bitmap + b'\0'
    if decode_record(result) != bitmap:
        raise ValueError('Native BNF glyph did not round trip')
    return result
