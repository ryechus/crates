import struct


def decode_struct(data):
    ret = []
    i = 0
    while i < len(data):
        tag = data[i : i + 4].decode("ascii")

        length = struct.unpack(">I", data[i + 4 : i + 8])[0]
        value = data[i + 8 : i + 8 + length]
        value = decode(value, tag=tag)
        ret.append((tag, value))
        i += 8 + length
    return ret


def encode_struct(string):
    # encode the song path
    encoded = encode_unicode(string)
    # get length of song path
    len_encoded = len(encoded)
    # pack length into hex value
    hex_pack = struct.pack(">I", len_encoded)
    # concat ptrk + hex value + encoded song path
    ptrk = bytes("ptrk", "utf-8") + hex_pack + encoded

    otrk_hex_pack = struct.pack(">I", len(ptrk))

    otrk = bytes("otrk", "utf-8") + otrk_hex_pack + ptrk
    # get length of concat
    # pack length into hex value
    # concat otrk + hex value + concatted ptrk
    return otrk


def decode_unicode(data):
    return data.decode("utf-16-be")


def encode_unicode(data):
    return data.encode("utf-16-be")


def decode_unsigned(data):
    return struct.unpack(">I", data)[0]


def noop(data):
    return data


DECODE_FUNC_FULL = {
    None: decode_struct,
    "vrsn": decode_unicode,
    "sbav": noop,
}

DECODE_FUNC_FIRST = {
    "o": decode_struct,
    "t": decode_unicode,
    "p": decode_unicode,
    "u": decode_unsigned,
    "b": noop,
}


def decode(data, tag=None):
    if tag in DECODE_FUNC_FULL:
        decode_func = DECODE_FUNC_FULL[tag]
    else:
        decode_func = DECODE_FUNC_FIRST[tag[0]]

    return decode_func(data)


def loadcrate(fname):
    with open(fname, "rb") as f:
        return decode(f.read())
