import json

from helper.api import XLadon, XGorgon, XArgus, XCylons, TCCryptor, TokenReqCryptor
from helper.protobuf import ProtoBuf


class ApiHelperTest:

    @staticmethod
    def test_x_ladon():
        ss1 = XLadon.decrypt("ltCyalMN4I88MKaornPKU+LSy5Tl6jDZcJFrMF3eokqTucfp")
        print(ss1)

        ss2 = XLadon.encrypt(1646098215, "1225625952")
        print(ss2)

        ss3 = XLadon.decrypt(ss2)
        print(ss3 == ss1)

    @staticmethod
    def test_x_gorgon():
        ss1 = XGorgon.decrypt("8404008900006d2495919861ae80fbdfc51b0161d0ded28ac70e")
        print(ss1)

        ss2 = XGorgon.encrypt(ss1)
        print(ss2)

        ss3 = XGorgon.decrypt(ss2)
        print(ss3 == (ss1))

    @staticmethod
    def test_x_argus():
        s1 = "4up7lV8l0txOeHMhPfVbpaSgUyqtZXii7SBk1RBZAu/colH8tJC+YKadXwoOw/RlILHO/jUzmw/NChqR2jKqyXS3uo7UtzBgjZSqW00SVLPgzF+tboWR1MozjpihOD0HnFZqw+QC5/GCHshpf2BR5H60OnehuepkccU3DODOed14A717LBDuATpB5njQNf/ALzFFFXfN5x6Kats1ylD2m2dwdQEkgTBclIfAf+JAJd9jsKiPXCnhGR/Lv65SwTxCrHY="
        ss1 = XArgus.decrypt(s1)
        ss1.dump()

        ss2 = XArgus.encrypt(ss1)
        print(ss2)

        ss3 = XArgus.decrypt(ss2)
        ss3.dump()
        print(ss3 == ss1)

    @staticmethod
    def test_x_cylons():
        x_cylons = "vCzcLbH1humC6lstWfdp4Cfl"
        ss1 = XCylons.decrypt(x_cylons)
        print(ss1)
        l = ss1.split(',')
        ss2 = XCylons.encrypt(l[1].strip(' '), l[0].strip(' '), l[2].strip(' '))
        print(ss2)
        print(ss2 == x_cylons)

    @staticmethod
    def read_file(filename: str) -> bytes:
        with open(filename, 'rb') as f:
            return f.read()
        return None

    @staticmethod
    def test_tc_cryptor():
        # 读取/service/2/device_register/请求内容
        data = ApiHelperTest.read_file("res/register.req")

        ss1 = TCCryptor.decrypt(data.hex())
        print(ss1)
        print(bytes.fromhex(ss1).decode('utf-8'))

        ss2 = TCCryptor.encrypt(ss1)
        # print(ss2)

        ss3 = TCCryptor.decrypt(ss2)
        print(ss3 == ss1)

    @staticmethod
    def test_token_request_decrypt():
        # 读取/sdi/get_token请求内容
        file_data = ApiHelperTest.read_file('res/get_token.req')
        pb = ProtoBuf(file_data)
        pb.dump()
        en_data = pb.getBytes(4)
        de_data = TokenReqCryptor.decrypt(en_data.hex())
        b = ProtoBuf(bytes.fromhex(de_data))
        b.dump()
        print(b)
        print("-----------------------")

        ProtoBuf(bytes.fromhex(b.getBytes(1).hex())).dump()
        print("----------end-------------")

    @staticmethod
    def test_token_response_decrypt():
        # 读取/sdi/get_token返回内容
        filedata = ApiHelperTest.read_file('res/get_token.resp')
        endata = ProtoBuf(filedata)
        endata.dump()
        endata = endata.getBytes(6)
        dedata = TokenReqCryptor.decrypt(endata.hex())
        ProtoBuf(bytes.fromhex(dedata)).dump()
        print("-----------------------")

    @staticmethod
    def test_app_log_req_decrypt():
        # 读取/service/2/device_register/请求内容
        data = ApiHelperTest.read_file("res/log.req")
        ss1 = TCCryptor.decrypt(data.hex())
        # print(bytes.fromhex(ss1).decode('utf-8'))
        data = json.loads(bytes.fromhex(ss1).decode('utf-8'))
        print(json.dumps(data, indent=4, ensure_ascii=False))
        # ss2 = TCCryptor.encrypt(ss1)
        # print(ss2)

        # ss3 = TCCryptor.decrypt(ss2)
        # print(ss3 == ss1)


    @staticmethod
    def test_app_log_resp_decrypt():
        # 读取/sdi/get_token返回内容
        filedata = ApiHelperTest.read_file('res/log.resp')
        endata = ProtoBuf(filedata).getBytes(6)
        dedata = TokenReqCryptor.decrypt(endata.hex())
        ProtoBuf(bytes.fromhex(dedata)).dump()

if __name__ == '__main__':
    ApiHelperTest.test_x_ladon()
    # ApiHelperTest.test_x_gorgon()
    # ApiHelperTest.test_x_argus()
    # ApiHelperTest.test_x_cylons()
    # ApiHelperTest.test_tc_cryptor()
    # ApiHelperTest.test_token_request_decrypt()
    # ApiHelperTest.test_token_response_decrypt()
    # ApiHelperTest.test_app_log_req_decrypt()
    # print("\n\nn\n\n")
    # ApiHelperTest.test_app_log_resp_decrypt()
    pass

    # s = "0a08216e6f747365742112096950686f6e65382c311a054e373141502212e2809c5043e2809de79a84206950686f6e652a03694f53320631322e312e343a083735302c3133333440044a08216e6f747365742150fd887a5a0131620f417369612f5368616e676861692c38687270c801780880011e8801fd887a900106a2012441343435374538392d323834332d344144412d383741422d353341334645383443374230aa0108216e6f7473657421b20108216e6f7473657421ba0108216e6f7473657421c20108216e6f7473657421c80190c6c3b00cd2012443453242373445342d393931322d343742332d414337422d463542433331364341323242d8018080968e17e20108216e6f7473657421e80182e7b7b00cf001fce6b7b00cfa0108216e6f747365742182020e3139322e3136382e33312e3134348a020e3139322e3136382e33312e323535920208216e6f74736574219a0208216e6f7473657421b20208216e6f7065726d21ba0208216e6f7065726d21c2020131d002fd887ad80202e20208216e6f7473657421e802fd887af002fd887afa022444443632314333312d394145432d343946382d383437462d4630383538413937393844358003fd887a8803fd887a92030c2e73622d306237643534636298039ee7b7b00ca003bcf5a7c60baa0308216e6f7473657421b20308216e6f7473657421ba0308216e6f7473657421c003fd887a"
    # print(bytes.fromhex(s))
    # print("============")
    # print(ProtoBuf(bytes.fromhex(s)).dump())
    # print(ProtoBuf(bytes.fromhex(s)).toBuf().hex())

    # ss3 = TCCryptor.decrypt(bytes.fromhex(s).hex())
    # print(ss3)

    print(hex(67307776<<1))