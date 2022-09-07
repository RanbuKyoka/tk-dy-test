

from helper.api import XLadon, XGorgon, XArgus, TCCryptor, TokenReqCryptor
from helper.protobuf import ProtoBuf
from test_reg import RegApi

if __name__ == "__main__":
    body = RegApi.get_token()
    pb = ProtoBuf(body)
    pb.dump()
    print("=================")
    pb_4 = pb.getBytes(4)
    pb_4_data = TokenReqCryptor.decrypt(pb_4.hex())
    b = ProtoBuf(bytes.fromhex(pb_4_data))
    b.dump()
    print("=================")
    ProtoBuf(b.getBytes(1)).dump()
    #
    print("=================")

    c = RegApi.file_content("res/register.req")
    ss1 = TCCryptor.decrypt(c.hex())
    print(bytes.fromhex(ss1).decode('utf-8'))
    # gen_token()

    c = RegApi.file_content("res/log.req")
    ss1 = TCCryptor.decrypt(c.hex())
    print(bytes.fromhex(ss1).decode('utf-8'))

    c = RegApi.file_content("res/log.resp")
    ss1 = TCCryptor.decrypt(c.hex())
    print(bytes.fromhex(ss1).decode('utf-8'))
    pass