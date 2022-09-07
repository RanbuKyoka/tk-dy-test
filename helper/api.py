from __future__ import annotations

import json
import random
from hashlib import md5
from typing import Any

import requests

from helper.protobuf import ProtoBuf
from helper.sm3 import sm3_hash


class ApiHelper:
    URL = "http://154.31.166.148:8181/result"
    TOKEN = "08011001180a2202637328e80730904e38eff3a704"
    APPID = 1128  # appId TikTok美版-1180 TikTok欧版-1233 国内版抖音-1128
    PROXIES = {}

    @classmethod
    def send(cls, func: str, params: list[str]) -> Any | None:
        # print("请求:", cls.URL)
        resp = requests.post(cls.URL, json={
            'token': cls.TOKEN,
            'appId': cls.APPID,
            'function': func,
            'params': params
        }, proxies=cls.PROXIES)
        # print("status:", resp.status_code)
        if resp.status_code != 200:
            raise Exception("签名网络异常")
        result: dict = json.loads(resp.content)
        # print("body:", json.dumps(result, indent=4, ensure_ascii=False))
        if result['code'] != 0:
            print("签名接口异常:", result['msg'])
            raise Exception(result['msg'])
        return result['data']


class XLadon:
    @staticmethod
    def encrypt(x_khronos: int, lc_id: str) -> str:
        """
        加密X-Ladon字符串
        """
        return ApiHelper.send('XLadon_encrypt', [
            "{}-{}-{}".format(x_khronos, lc_id, ApiHelper.APPID),
            str(ApiHelper.APPID)
        ])

    @staticmethod
    def decrypt(x_ladon: str) -> str:
        """
        解密X-Ladon字符串
        """
        return ApiHelper.send('XLadon_decrypt', [
            x_ladon,
            str(ApiHelper.APPID)
        ])


class XGorgon:
    @staticmethod
    def build(url_query: str, x_ss_stub: str, sdk_ver: int, x_khronos: int) -> str:
        default_str = '00000000'
        if url_query is None or len(url_query) == 0:
            url_query_md5_hex = md5(b'').hexdigest()[0:8]
        else:
            url_query_md5_hex = md5(url_query.encode('utf-8')).hexdigest()[0:8]

        if x_ss_stub is None or len(x_ss_stub) == 0:
            x_ss_stub = default_str
        else:
            x_ss_stub = x_ss_stub[0:8]

        sdk_ver_hex = sdk_ver.to_bytes(4, 'little').hex()
        time_hex = x_khronos.to_bytes(4, 'big').hex()
        build_str = url_query_md5_hex + x_ss_stub + default_str + sdk_ver_hex + time_hex
        return XGorgon.encrypt(build_str)

    @staticmethod
    def encrypt(build_str: str) -> str:
        return ApiHelper.send('XGorgon_encrypt', [
            build_str
        ])

    @staticmethod
    def decrypt(x_gorgon: str) -> str:
        return ApiHelper.send('XGorgon_decrypt', [
            x_gorgon
        ])


class XCylons:
    @staticmethod
    def encrypt(query_md5_hex: str, lc_id: str, timestamp: int) -> str:
        return ApiHelper.send('XCylons_encrypt', [
            query_md5_hex,
            lc_id,
            str(timestamp)
        ])

    @staticmethod
    def decrypt(x_cylons: str) -> str:
        return ApiHelper.send('XCylons_decrypt', [
            x_cylons
        ])


class XArgus:
    @staticmethod
    def decrypt(x_argus: str) -> ProtoBuf:
        resp = ApiHelper.send('XArgus_decrypt', [x_argus])
        return ProtoBuf(bytes.fromhex(resp))

    @staticmethod
    def encrypt(x_argus: ProtoBuf) -> str:
        return ApiHelper.send('XArgus_encrypt', [x_argus.toBuf().hex()])

    @staticmethod
    def build(x_argus_simple_bean: dict) -> str:
        '''
        xargus_simple_bean = {
            'deviceID':         device_id,  #可为空
            'licenseID':        lc_id,
            'appVersion':       app_version,
            'sdkVersionStr':    sdk_ver_str,
            'sdkVersion':       sdk_ver,
            'x_khronos':        x_khronos,
            'x_ss_stub':        x_ss_stub, #get请求可为空
            'secDeviceToken':   "AnPPIveUCQlIiFroHGG17nXK6", #可为空
            'queryHex':         query_str.encode('utf-8').hex(),
            'x_bd_lanusk': '',  #/passport/user/login/ 返回头 关注、点赞必需
        }
        '''
        return ApiHelper.send('XArgus_build', [
            json.dumps(x_argus_simple_bean).encode('utf-8').hex()
        ])

    @staticmethod
    def get_body_hash(x_ss_stub=None):
        if x_ss_stub is None or len(x_ss_stub) == 0:
            return sm3_hash(bytes(16))[0:6]
        return sm3_hash(bytes.fromhex(x_ss_stub))[0:6]

    @staticmethod
    def get_query_hash(query: str):
        if query is None or len(query) == 0:
            return sm3_hash(bytes(16))[0:6]
        return sm3_hash(query.encode('utf-8'))[0:6]

    @staticmethod
    def get_psk_hash(x_bd_lanusk: str):
        if x_bd_lanusk is None or len(x_bd_lanusk) == 0:
            return None
        if type(x_bd_lanusk) == bytes:
            return x_bd_lanusk
        return md5(x_bd_lanusk.encode('utf-8')).digest()

    @staticmethod
    def get_psk_cal_hash(query: str, x_ss_stub: str):
        body_hash = bytes(16)
        if x_ss_stub is not None and len(x_ss_stub) != 0:
            body_hash = bytes.fromhex(x_ss_stub)
        buf = query.encode('utf-8') + body_hash + '0'.encode('utf-8')
        return sm3_hash(buf)

    @staticmethod
    def build_local(params: dict) -> str:
        '''
        params = {
            'deviceID': '',
            'licenseID': '',
            'appVersion': '',
            'sdkVersionStr': '',
            'sdkVersion': 0,
            'x_khronos': 0,
            'x_ss_stub': '',  #get请求为空
            'secDeviceToken': '', #可为空字符串
            'query': '',
            'x_bd_lanusk': '',    #登录前为空, 登录后login返回
        }
        '''
        env_code = 0x120
        queryHash = XArgus.get_query_hash(params['query'])
        bodyHash = XArgus.get_body_hash(params['x_ss_stub'])
        psk_hash = XArgus.get_psk_hash(params['x_bd_lanusk'])
        if psk_hash is not None:
            pskVersion = '0'
            pskCalHash = XArgus.get_psk_cal_hash(params['query'], params['x_ss_stub'])
        else:
            pskVersion = 'none'
            pskCalHash = None

        xa_bean = {
            1: 0x20200929 << 1,  # magic
            2: 2,  # version
            3: random.randint(0, 0x7FFFFFFF),  # rand
            4: str(ApiHelper.APPID),  # msAppID
            5: params['deviceID'],  # deviceID
            6: params['licenseID'],  # licenseID
            7: params['appVersion'],  # appVersion
            8: params['sdkVersionStr'],  # sdkVersionStr
            9: params['sdkVersion'] << 1,  # sdkVersion
            10: env_code.to_bytes(8, 'little'),  # envcode  越狱检测
            11: 1,  # platform
            12: params['x_khronos'] << 1,  # createTime
            13: bodyHash,  # bodyHash
            14: queryHash,  # queryHash
            15: {
                1: 172,  # signCount
                2: 1388734,  # reportCount
                3: 1388734,  # settingCount
            },
            16: params['secDeviceToken'],  # secDeviceToken
            17: params['x_khronos'] << 1,  # isAppLicense
            18: psk_hash,    # pskHash
            19: pskCalHash,  # pskCalHash
            20: pskVersion,  # pskVersion
            21: 738,  # callType
        }
        xa_pb = ProtoBuf(xa_bean)
        return XArgus.encrypt(xa_pb)


class TokenReqCryptor:
    @staticmethod
    def encrypt(_hex: str) -> str:
        """
        加密/sdi/get_token请求body中的部分数据
        """
        return ApiHelper.send('TokenReq_encrypt', [_hex])

    @staticmethod
    def decrypt(_hex: str) -> str:
        """
        解密/sdi/get_token请求body中的部分数据
        """
        return ApiHelper.send('TokenReq_decrypt', [_hex])


class TCCryptor:
    @staticmethod
    def encrypt(_hex: str) -> str:
        """
        加密/service/2/device_register/请求body
        """
        return ApiHelper.send('TCCryptor_encrypt', [_hex])

    @staticmethod
    def decrypt(_hex: str) -> str:
        """
        解密/service/2/device_register/请求body
        """
        return ApiHelper.send('TCCryptor_decrypt', [_hex])
