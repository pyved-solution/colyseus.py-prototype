import struct
import io

# Example binary format used below:
# b'\x80\x01\x81\x01\xff\x01\x80\x00\x02\x80\x01\x03\xff\x02\x81\x04\x80\x00\xff\x03\x81\x05\x80\x01\xff\x04\x80\x00\x06\x80\x01\x07\x80\x02\x08\xff\x05\x80\x00\t\x80\x01\n\x80\x02\x0b\xff\x06\x80\xa1x\x81\xa6number\xff\x07\x80\xa1y\x81\xa6number\xff\x08\x80\xa4tick\x81\xa6number\xff\t\x80\xa8mapWidth\x81\xa6number\xff\n\x80\xa9mapHeight\x81\xa6number\xff\x0b\x80\xa7players\x82\x00\x81\xa3map'
#
# or, in another format:
#
# b'\x80\x01\x81\x01\xFF
# \x01\x80\x00\x02\x80\x01\x03\xFF
# \x02\x81\x04\x80\x00\xFF
# \x03\x81\x05\x80\x01\xFF
# \x04\x80\x00\x06\x80\x01\x07\x80\x02\x08\xFF
# \x05\x80\x00\t\x80\x01\n\x80\x02\x0b\xFF
# \x06\x80\xa1x\x81\xa6number\xFF
# \x07\x80\xa1y\x81\xa6number\xFF
# \x08\x80\xa4tick\x81\xa6number\xFF
# \t\x80\xa8mapWidth\x81\xa6number\xFF
# \n\x80\xa9mapHeight\x81\xa6number\xFF
# \x0b\x80\xa7players\x82\x00\x81\xa3map'
"""
THE METHOD:
Schema.from_binary_description(binary_dest:bytes)
is probably the most important in this file

byte_values = [
    0x80, 0x1, 0x81, 0x1, 0xff, 0x1, 0x80, 0x0, 0x2, 0x80, 0x1, 0x3, 0xff,
    0x2, 0x81, 0x4, 0x80, 0x0, 0xff, 0x3, 0x81, 0x5, 0x80, 0x1, 0xff, 0x4,
    0x80, 0x0, 0x6, 0x80, 0x1, 0x7, 0x80, 0x2, 0x8, 0xff, 0x5, 0x80, 0x0,
    0x9, 0x80, 0x1, 0xa, 0x80, 0x2, 0xb, 0xff, 0x6, 0x80, 0xa1, 0x78, 0x81,
    0xa6, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72, 0xff, 0x7, 0x80, 0xa1, 0x79,
    0x81, 0xa6, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72, 0xff, 0x8, 0x80, 0xa4,
    0x74, 0x69, 0x63, 0x6b, 0x81, 0xa6, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72,
    0xff, 0x9, 0x80, 0xa8, 0x6d, 0x61, 0x70, 0x57, 0x69, 0x64, 0x74, 0x68,
    0x81, 0xa6, 0x6e, 0x75, 0x6d, 0x62, 0x65, 0x72, 0xff, 0xa, 0x80, 0xa9,
    0x6d, 0x61, 0x70, 0x48, 0x65, 0x69, 0x67, 0x68, 0x74, 0x81, 0xa6, 0x6e,
    0x75, 0x6d, 0x62, 0x65, 0x72, 0xff, 0xb, 0x80, 0xa7, 0x70, 0x6c, 0x61,
    0x79, 0x65, 0x72, 0x73, 0x82, 0x0, 0x81, 0xa3, 0x6d, 0x61, 0x70
]
and what I expect to get is:

field 0 : ??
field 1 : ??
field 2 : ??
field 3 : ??
field 4 : ??
field 5 : ??

field 6 : x number
field 7 : y number
field 8 : tick number
field 9 : mapWidth number
field 10: mapHeight number
field 11: players map
"""


class EncodedFieldType:
    END_OF_STRUCTURE = 0xC1,  # (msgpack spec: never used)
    NIL = 0xC0,
    INDEX_CHANGE = 0xD4,
    FLOAT_32 = 0xCA,
    FLOAT_64 = 0xCB,

    U_INT_8 = 0xCC,
    U_INT_16 = 0xCD,
    U_INT_32 = 0xCE,
    U_INT_64 = 0xCF


# other possible encoded fieldTypes

# {
#     // uint 64
#     return (varint_t) decodeUint64(bytes, it);
# }
# else if (prefix == 0xd0)
# {
#     // int 8
#     return (varint_t) decodeInt8(bytes, it);
# }
# else if (prefix == 0xd1)
# {
#     // int 16
#     return (varint_t) decodeInt16(bytes, it);
# }
# else if (prefix == 0xd2)
# {
#     // int 32
#     return (varint_t) decodeInt32(bytes, it);
# }
# else if (prefix == 0xd3)
# {
#     // int 64
#     return (varint_t) decodeInt64(bytes, it);
# }
# else if (prefix > 0xdf)
# {
#     // negative fixint
#     return (varint_t) ((0xff - prefix + 1) * -1);
# }


class SchemaField:
    """
    we prefer to introduce this class,
    in case the field becomes packed with more information
    """
    def __init__(self, name, field_type):
        self.name = name
        self.field_type = field_type

    @property
    def encoded_field_type(self):
        return NotImplementedError
    # self.encoded_fiend_type = None


class Schema:
    def __init__(self):
        """
        in case you wish to create an emply schema
        """
        self.fields = {}
        self.curr_data = {}

    def add_field(self, name, field_type):
        self.fields[name] = SchemaField(name, field_type)
        self.curr_data[name] = None

    @classmethod
    def from_binary_description(cls, binary_desc: bytes) -> None:
        """
        Method goal is to create a schema from a binary description
        :param binary_desc:
        :return:
        """
        raise NotImplementedError

        offset = 0
        num_fields = binary_description[offset]
        offset += 1

        for _ in range(num_fields):
            name_length = binary_description[offset]
            offset += 1
            name = binary_description[offset:offset + name_length].decode('utf-8')
            offset += name_length

            field_type = binary_description[offset]
            offset += 1

            # Map field_type value to actual type
            if field_type == 1:
                self.add_field(name, "int")
            elif field_type == 2:
                self.add_field(name, "float")
            elif field_type == 3:
                self.add_field(name, "string")
            else:
                raise ValueError(f"Unknown field type: {field_type}")

    def deserialize(self, data):
        """
        Deserialize binary data based on the schema.
        """
        deserialized_data = {}
        offset = 0
        for field in self.fields.values():
            if field.field_type == "int":
                deserialized_data[field.name], offset = self._read_int(data, offset)
            elif field.field_type == "float":
                deserialized_data[field.name], offset = self._read_float(data, offset)
            elif field.field_type == "string":
                deserialized_data[field.name], offset = self._read_string(data, offset)
        return deserialized_data

    @staticmethod
    def _read_int(data, offset):
        value = int.from_bytes(data[offset:offset + 4], "big")
        return value, offset + 4

    @staticmethod
    def _read_float(data, offset):
        value = struct.unpack(">f", data[offset:offset + 4])[0]
        return value, offset + 4

    @staticmethod
    def _read_string(data, offset):
        length = data[offset]
        offset += 1
        value = data[offset:offset + length].decode("utf-8")
        return value, offset + length

    def __str__(self) -> str:
        x = id(self)

        buffer = io.StringIO()
        print(f'<SCHEMA {x}>', file=buffer)
        print('{', file=buffer)
        fields_cp = list(self.fields.keys())
        fields_cp.sort()
        for e in fields_cp:
            print(' ', e, ':', self.fields[e].field_type, file=buffer)
        print('}', file=buffer)

        contents = buffer.getvalue()
        buffer.close()
        return contents

    def apply_delta(self, data: bytes, current_state: dict):
        """
        Apply a delta update to the existing state.

        Parameters:
        data (bytes): The delta data received from the server, containing only fields that have changed.
        current_state (dict): The current state of the schema, which will be updated with the delta changes.

        Returns:
        dict: The updated state after applying the delta changes.
        """

        # TODO ajuster l'implem de la methode, suivant la réponse à:
        #  le schema contient-il aussi la data,
        # ou le schema en contient pas ??

        offset = 0
        while offset < len(data):
            # First byte represents the field ID, not length of name
            field_id = data[offset]
            print(f'byte{offset:2x}', field_id)

            if field_id == 15:
                print('fieldtype: 15 donc ??')
            elif field_id == EncodedFieldType.U_INT_8:
                print('uint8')
            elif field_id == EncodedFieldType.U_INT_16:
                print('uint16')
            elif field_id == EncodedFieldType.U_INT_32:
                print('uint32')
            elif field_id == EncodedFieldType.U_INT_64:
                print('uint64')
            else:
                print('??')
            offset += 1
            continue
            # Get field name based on field ID in schema
            field = list(self.fields.values())[field_id]

            # Update the field in the current state based on the field type
            if field.field_type == "int":
                current_state[field.name], offset = self._read_int(data, offset)
            elif field.field_type == "float":
                current_state[field.name], offset = self._read_float(data, offset)
            elif field.field_type == "string":
                current_state[field.name], offset = self._read_string(data, offset)
            else:
                raise ValueError(f"Unsupported field type: {field.field_type}")

        return current_state
