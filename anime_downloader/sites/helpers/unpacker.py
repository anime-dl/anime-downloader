try:
    from jsbeautifier.unpackers import javascriptobfuscator, myobfuscate, packer
    UNPACKERS = [javascriptobfuscator, myobfuscate, packer]
    def deobfuscate_packed_js(js):
        for unpacker in UNPACKERS:
            if unpacker.detect(js):
                return unpacker.unpack(js)
        return js
except ImportError:
    def deobfuscate_packed_js(js):
        return js
