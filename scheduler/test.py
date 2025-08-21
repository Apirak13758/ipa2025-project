import json
from bson import BSON, json_util

# 1. Your JSON string
json_string = '{"name": "Alice", "age": 30, "city": "New York"}'

try:
    # 2. Parse the JSON string into a Python dictionary
    data_dict = json.loads(json_string)

    # 3. Encode the dictionary to BSON bytes
    bson_data = BSON.encode(data_dict)

    decode_data = BSON.decode(bson_data)
    dump = json.dumps(decode_data)

    # Now, bson_data contains the binary BSON representation
    # You can then store this BSON data or transmit it as needed.
    print(f"Original JSON: {json_string}")
    print(f"Encoded BSON (bytes): {bson_data}")
    print(f"Encoded BSON (bytes): {decode_data}")

except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")

json_string = '{"_id": {"$oid": "68a71c06ed5abcdd4d339121"}, "ip": "10.30.6.1", "username": "admin", "password": "cisco"}'
try:

    decode_data = json_util.loads(json_string)

    # Now, bson_data contains the binary BSON representation
    # You can then store this BSON data or transmit it as needed.
    print(f"Original JSON: {decode_data}")

except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")