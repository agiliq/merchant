

# Utilties for building functions to pass to json.loads and json.dumps
# for custom encoding/decoding.

def chain_custom_encoders(encoders):
    def combined_encoder(obj):
        for encoder in encoders:
            try:
                return encoder(obj)
            except TypeError:
                continue
        raise TypeError("Unknown type %s" % obj.__class__)
    return combined_encoder


def chain_custom_decoders(decoders):
    def combined_decoder(dct):
        for decoder in decoders:
            dct = decoder(dct)
            if not hasattr(dct, '__getitem__'):
                # Already changed
                return dct
        return dct
    return combined_decoder
