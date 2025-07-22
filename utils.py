import zlib
import base64
import json

def encode_message(payload_dict):
    json_str = json.dumps(payload_dict)
    compressed = zlib.compress(json_str.encode('utf-8'))
    encoded = base64.b64encode(compressed).decode('utf-8')
    return encoded

def decode_message(encoded_str):
    decoded = base64.b64decode(encoded_str)
    decompressed = zlib.decompress(decoded).decode('utf-8')
    return json.loads(decompressed)
