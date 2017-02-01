def byte_to_bits(b):
    fstr = bin(ord(b))[2:]
    return "%s%s" % ("0" * (8 - len(fstr)), fstr)
