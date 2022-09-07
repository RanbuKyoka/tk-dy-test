# pip install --upgrade protobuf
from google.protobuf import json_format


def pb_to_json(pbStringRequest):
    return json_format.MessageToJson(pbStringRequest, preserving_proto_field_name=True)




