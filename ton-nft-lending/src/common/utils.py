
import base64, ctypes, math

def crc16(data):
    POLY = 0x1021
    reg = 0
    message = bytes(data) + bytes(2)

    for byte in message:
        mask = 0x80
        while mask > 0:
            reg <<= 1
            if byte & mask:
                reg += 1
            mask >>= 1
            if reg > 0xFFFF:
                reg &= 0xFFFF
                reg ^= POLY

    return bytearray([math.floor(reg / 256), reg % 256])


def string_to_bytes(string, size=1):  # ?
    if size == 1:
        buf = (ctypes.c_uint8 * len(string))()
    elif size == 2:
        buf = (ctypes.c_uint16 * len(string) * 2)()
    elif size == 4:
        buf = (ctypes.c_uint32 * len(string) * 4)()

    for i, c in enumerate(string):
        # buf[i] = ord(c)
        buf[i] = c  # ?

    return bytes(buf)


def to_public_key_address(addr_str):
    addr_str = addr_str.replace("-", "+").replace("_", "/")
    if len(addr_str) > 48:
        # raise "User-friendly address should contain strictly 48 characters"
        return addr_str

    # avoid padding error (https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770)
    data = string_to_bytes(base64.b64decode(addr_str + "=="))

    if len(data) != 36:
        raise "Unknown address type: byte length is not equal to 36"

    addr = data[:34]
    crc = data[34:36]
    calced_crc = crc16(addr)
    if not (calced_crc[0] == crc[0] and calced_crc[1] == crc[1]):
        raise "Wrong crc16 hashsum"

    tag = addr[0]
    is_test_only = False
    is_bounceable = False
    if tag & 0x80:
        is_test_only = True
        tag ^= 0x80
    if (tag != 0x11) and (tag != 0x51):
        raise "Unknown address tag"

    is_bounceable = tag == 0x11

    if addr[1] == 0xFF:
        workchain = -1
    else:
        workchain = addr[1]
    if workchain != 0 and workchain != -1:
        raise f"Invalid address wc {workchain}"

    hash_part = bytearray(addr[2:34])
    return f"{workchain}:{hash_part.hex().lower()}"

