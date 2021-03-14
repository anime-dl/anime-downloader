from jsbeautifier.unpackers import javascriptobfuscator, myobfuscate, packer

UNPACKERS = [javascriptobfuscator, myobfuscate, packer]


def unpack(js):
    for unpacker in UNPACKERS:
        if unpacker.detect(js):
            return unpacker.unpack(js)
    return js
