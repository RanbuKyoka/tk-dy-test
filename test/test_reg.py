import json
import os
import random
import time
import uuid
from hashlib import md5
from urllib.parse import urlencode, quote

import requests

from helper.api import XLadon, XGorgon, XArgus, TCCryptor, TokenReqCryptor
from helper.protobuf import ProtoBuf


class DeviceApp:
    display_name = "抖音"
    package = "com.ss.iphone.ugc.Aweme"
    aid = "1128"
    app_name = "aweme"
    app_version = '22.0.0'
    build_number = "220015"
    channel = "App%20Store"
    version_code = '22.0.0'
    sdk_version_str = 'v04.03.09-ml-iOS'
    sdk_version = 0x4030901
    license_id = "712198790"
    ttnet_version = "4.1.94.10"
    cronet_version = 'e099df08_2022-06-20'
    x_vc_bdturing_sdk_version = "2.2.7"
    passport_sdk_version = "5.12.1"
    xlog_sdk_verion = 265
    tt_sdk_version = "2"


class DeviceInfo:
    model = "iPhone10,2"
    platform = "iphone"
    osName = "iOS"
    osVersion = "14.2"

    # idfa = "E1F9EC92-82FC-4E65-9415-DEE4D928097F"
    # cdid = "DEEBA33C-D1E6-30FF-BA78-8EC2997C1074"
    # vendorId = "4594F944-2A2E-4471-A791-3AA8A2E46859"
    # openudid = "d3986af2bdd746809d560532e1c531b6be927151"
    # idfv = "E8F9EC92-24FC-4E32-9135-DEE3D908397F"
    idfa = "00000000-0000-0000-0000-000000000000"
    idfv = "00000000-0000-0000-0000-000000000000"
    cdid = str(uuid.uuid4()).upper()
    vendor_id = str(uuid.uuid4()).upper()
    openudid = random.randbytes(20).hex()
    mac = "02:00:00:00:00:00"
    region = "zh"
    language = "zh-CN"
    timezone = "8"
    timezoneName = "Asia/Singapore"
    access = "WIFI"
    carrier = ""
    locale = "zh"


class RegApi:
    did = ""
    iid = ""

    @classmethod
    def rand_str(cls, length):
        rand = ''
        random_str = '0123456789abcdef'
        for _ in range(length):
            rand += random.choice(random_str)
        return rand

    @classmethod
    def _get_trace_id(cls):
        """
        gen trace id
        """
        timestamp = "%x" % (round(time.time() * 1000) & 0xffffffff)
        random_str = str(timestamp) + "010" + cls.rand_str(17) + "0000"
        trace_id = "00-"
        trace_id += random_str
        trace_id += "-"
        trace_id += random_str[:16]
        trace_id += '-01'
        return trace_id

    @classmethod
    def encrypt_header(cls, query_str: str, body: bytes):
        x_ss_stub = None
        if cls.did is None or len(cls.did) == 0:
            cls.did = None

        if body is not None:
            x_ss_stub = md5(body).hexdigest().upper()

        x_khronos = int(time.time())
        x_ladon = XLadon.encrypt(x_khronos, DeviceApp.license_id)
        x_gorgon = XGorgon.build(query_str, x_ss_stub, DeviceApp.sdk_version, x_khronos)
        x_argus = XArgus.build_local({
            'deviceID': cls.did,
            'licenseID': DeviceApp.license_id,
            'appVersion': DeviceApp.app_version,
            'sdkVersionStr': DeviceApp.sdk_version_str,
            'sdkVersion': DeviceApp.sdk_version,
            'x_khronos': x_khronos,
            'x_ss_stub': x_ss_stub,  # get请求为空
            'secDeviceToken': '',  # 可为空字符串
            'query': query_str,
            'x_bd_lanusk': None,  # 登录前为空, 登录后login返回
        })

        return {
            'tt-request-time': str(int(time.time() * 1000)),
            'x-khronos': str(x_khronos),
            'x-ss-stub': x_ss_stub,
            'x-argus': x_argus,
            'x-gorgon': x_gorgon,
            'x-ladon': x_ladon,
        }

    @classmethod
    def service_app_alert_check(cls):
        # https://ichannel.snssdk.com/service/2/app_alert_check/?mcc_mnc=&app_name=aweme&channel=App%20Store&device_platform=iphone&idfa=00000000-0000-0000-0000-000000000000&vid=AAD2B91A-F1FF-4A77-9C64-CCBE3C8CD0E9&device_token=&is_upgrade_user=0&version_code=22.0.0&ac=WIFI&timezone=8&os_version=14.4.1&aid=1128&is_activated=0
        query = {
            "ac": "WIFI",
            "aid": "1128",
            "app_name": "aweme",
            "channel": "App Store",
            "device_platform": "iphone",
            # "idfa": "00000000-0000-0000-0000-000000000000",
            "idfa": DeviceInfo.idfa,
            "is_activated": "0",
            "is_upgrade_user": "0",
            "os_version": "14.4.1",
            "timezone": "8",
            "version_code": "22.0.0",
            # "vid": "AAD2B91A-F1FF-4A77-9C64-CCBE3C8CD0E9"
            "vid": DeviceInfo.vendor_id
        }

        query_str = urlencode(query, safe='/', quote_via=quote) + '&'
        print(query_str)
        url = "https://ichannel.snssdk.com/service/2/app_alert_check/"
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Host": "ichannel.snssdk.com",
            "User-Agent": "Aweme 22.0.0 rv:220015 (iPhone; iOS 14.4.1; zh_CN) Cronet",
            # "X-Argus": "+H/LiGN0Po0jW5My78DWFpuryzTWQNkjOIyoc6AW5t0EqZdUZ77jEOBRzNvy9dGLkMdzjEsIuOfrcvQj305zyFXwAnhKABoXTSOHLxY0+jHTogS2FXOZgETPY7EJUVv2zkX9tVwQXQU0E9wvFbMq9rCOO3cJrut4p9zROpeDBIpLS0nmZARYU+pzirgp9bi1Rd1RdwYQIMnC0sYVcb+bQA24",

            # "X-Gorgon": "8404004600002120460d603f4231bde454075fe062884ebdfcbb",
            # "X-Khronos": "1662019394",
            # "X-Ladon": "5UG6EDdZGfvJ3MrUco1CW7+AkPRaEXtAB+/6x8nxD2HIc9Eq",
            "passport-sdk-version": "5.12.1",
            "sdk-version": "2",
            # "tt-request-time": "1662019394387",
            "x-tt-request-tag": "t=0;n=1",
            # "x-tt-trace-id": "00-f8135cdc0104aa5701e8e3b359850468-f8135cdc0104aa57-01",
            "x-vc-bdturing-sdk-version": "2.2.7"
        } | cls.encrypt_header(query_str, None)
        print("\n\n\n======================\n\n\n")
        print(headers)
        resp = requests.get(
            url=f"{url}?{query_str}",
            headers=headers,
            verify=False,
            proxies={},
            timeout=15)

        print(resp.text)
        print(resp.cookies.get_dict())
        print(resp.headers)

    @classmethod
    def service_2_device_register(cls):
        query = {
            "tt_data": "a",
            "is_activated": "0",
            "ac": "WIFI",
            "aid": "1128",
            "appTheme": "light",
            "app_name": "aweme",
            "app_version": "22.0.0",
            "build_number": "220015",
            # "cdid": "78EDE0F6-2C30-4335-9429-BFC85161070F",
            "cdid": DeviceInfo.cdid,
            "channel": "App Store",
            "device_platform": "iphone",
            "device_type": "iPhone8,1",
            # "idfa": "00000000-0000-0000-0000-000000000000",
            "idfa": DeviceInfo.idfa,

            "is_guest_mode": "0",
            "is_vcd": "1",
            "js_sdk_version": "2.63.1.2",
            "minor_status": "0",
            "need_personal_recommend": "1",
            # "openudid": "705ea0dd8b90740ccb8f56dc43878e607b631635",
            "openudid": DeviceInfo.openudid,
            "os_api": "18",
            "os_version": "14.4.1",
            "package": "com.ss.iphone.ugc.Aweme",
            "screen_width": "750",
            "tma_jssdk_version": "2.63.1.2",
            "version_code": "22.0.0",
            # "vid": "AAD2B91A-F1FF-4A77-9C64-CCBE3C8CD0E9"
            "vid": DeviceInfo.vendor_id
        }

        query_str = urlencode(query, safe='/', quote_via=quote)
        print(query_str)
        url = "https://log.snssdk.com/service/2/device_register/"
        body = {
            "magic_tag": "ss_app_log",
            "header": {
                "region": "CN",
                "access": "WIFI",
                "os_version": "14.4.1",
                "device_model": "iPhone8,1",
                "app_name": "aweme",
                "carrier": "",
                # "vendor_id": "AAD2B91A-F1FF-4A77-9C64-CCBE3C8CD0E9",
                "vendor_id": DeviceInfo.vendor_id,
                "scene": 0,
                "sdk_version": 265,
                "custom": {
                    "app_region": "CN",
                    "earphone_status": "off",
                    "web_ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
                    "filter_warn": 0,
                    "loc_switch": False,
                    "user_period": 0,
                    "user_mode": 0,
                    "app_language": "zh",
                    "build_number": "220015"
                },
                "model_display_name": "iPhone8,1",
                # "display_name": "抖音",
                "display_name": "抖音",
                "phone_name": "867e57bd062c7169995dc03cc0541c19",
                "device_token": "",
                "disk_total": 15968497664,
                "channel": "App Store",
                "boot_time": "1662013781.555757",
                "app_region": "CN",
                "hardware_model": "N71mAP",
                "auth_status": 2,
                "user_agent": "Aweme 22.0.0 rv:220015 (iPhone; iOS 14.4.1; zh_CN) Cronet",
                "mem_total": 2107850752,
                # "idfa": "00000000-0000-0000-0000-000000000000",
                "idfa": DeviceInfo.idfa,
                "mb_time": "1646466534.697089",
                "os": "iOS",
                "tz_name": "Asia/Shanghai",
                "cpu_num": 2,
                "tz_offset": 28800,
                "local_tz_name": "Asia/Shanghai",
                "carrier_region": "",
                "app_language": "zh",
                "is_upgrade_user": False,
                "mcc_mnc": "",
                "aid": "1128",
                "package": "com.ss.iphone.ugc.Aweme",
                "is_jailbroken": False,
                "language": "zh-CN",
                "locale_language": "zh-CN",
                # "cdid": "78EDE0F6-2C30-4335-9429-BFC85161070F",
                "cdid": DeviceInfo.cdid,
                "app_version": "22.0.0",
                "resolution": "750*1334",
                "timezone": 8
            }
        }
        body_hex = TCCryptor.encrypt(json.dumps(body).encode('utf-8').hex())
        body = bytes.fromhex(body_hex)
        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br",
            "aid": "1128",
            "content-type": "application/octet-stream;tt-data=a",
            "passport-sdk-version": "5.12.1",
            "sdk-version": "2",
            # "tt-request-time": "1662019394382",
            "user-agent": "Aweme 22.0.0 rv:220015 (iPhone; iOS 14.4.1; zh_CN) Cronet",
            # "x-argus": "oNn0UIz6bCdy5HXblnX4Iyids2ENYN45oaXRV7cidfCGfhZCUUDqFVjvZ/YzM9ae1q31oYbZ83SZY4FZkpG/Xk5YVVZOHfKAxqJMR2YMAbeHoMW6qFzOZvezQs06uWK+vecb+7/APDv95esm0mx3yaWmsvVHKovke2xKVYmx95n/FWMpHHxaMWcvB8fWiRF6eC5EIfh5uQn1CV4QGfE0BOwO",
            # "x-gorgon": "84042044000028d5b521087a754c51ebd8dd71a773bf34a28f2a",
            # "x-khronos": "1662019394",
            # "x-ladon": "+EJTeJv9+NM3m7qC4Mb9FOxFhoA3qiQYWNFuMudHqFb2YRBZ",
            # "x-ss-stub": "4D74EC0B9B3D1CAC70F09E803E66EBCA",
            "x-tt-request-tag": "t=0;n=1",
            # "x-tt-trace-id": "00-f8135cd7010195ad1a0ebbb67cc90468-f8135cd7010195ad-01",
            "x-vc-bdturing-sdk-version": "2.2.7"
        } | cls.encrypt_header(query_str, body)
        print("\n\n\n======================\n\n\n")
        print(headers)
        resp = requests.post(
            url=f"{url}?{query_str}",
            headers=headers,
            data=body,
            verify=False,
            proxies={},
            timeout=15)
        print(resp.text)
        print(resp.cookies.get_dict())
        print(resp.headers)
        return json.loads(resp.text)

    @classmethod
    def get_token(cls):
        path = "res/token2.req"
        if not os.access(path, os.R_OK):
            return None

        with open(path, "rb") as fp:
            body = fp.read()
        return body

    @classmethod
    def file_content(cls, path):
        if not os.access(path, os.R_OK):
            return None
        with open(path, "rb") as fp:
            body = fp.read()
        return body

    @classmethod
    def get_sdi_body(cls):
        pp = {
            1: "!notset!",
            2: "iPhone8,1",
            3: "N71mAP",
            4: "iPhone",
            5: "iOS",
            6: "14.4.1",
            7: "750,1334",
            8: 4,
            9: "!notset!",
            10: 1999997,
            11: "1",
            12: "Asia/Shanghai,8",
            13: 76,
            14: 200,
            15: 8,
            16: 30,
            17: 1999997,
            18: 14,
            20: "AAD2B91A-F1FF-4A77-9C64-CCBE3C8CD0E9",  # vid
            21: "!notset!",
            22: "!notset!",
            23: "!notset!",
            24: "!notset!",
            25: 3324027562,
            26: "D9573F01-C168-4E32-A8B5-D753C67DAFBA",
            27: 169246720,
            28: "!notset!",
            29: 3292933028,
            30: 3292933022,
            31: "!notset!",
            32: "192.168.31.72",
            33: "192.168.31.255",
            34: "!notset!",
            35: "!notset!",
            38: "!noperm!",
            39: "!noperm!",
            40: "1",
            42: 1999997,
            43: 2,
            44: "!notset!",
            45: 1999997,
            46: 1999997,
            47: "D1FD4CB2-A94B-4586-A479-611AF07E4E6D",
            48: 1999997,
            49: 1999997,
            50: ".sb-f09dbb5a",
            51: 3292933068,
            52: 3155731200,
            53: "!notset!",
            54: "!notset!",
            55: "!notset!",
            56: 1999997,
        }
        pb4_dict = {
            1: ProtoBuf(pp).toBuf(),
            3: "iOS",
            4: "v04.03.09-ml-iOS",
            5: 134615554,
            6: "1128",
            7: "22.0.0",
            8: "1895974765599303",
            9: "0000000000000000",
            10: 1999997,
            11: 1999997,
            12: "F51416C8-022A-4C6E-94DA-11286EDC21B3",
            16: 1999997,

        }
        ProtoBuf(pb4_dict[1]).dump()
        # print(ProtoBuf(pb4_dict).dump())
        # en = TokenReqCryptor.encrypt(ProtoBuf(pb4_dict).toBuf().hex())
        # print(en)
        # de = TokenReqCryptor.decrypt(en)
        # print(de)
        result = {
            1: 1077938244,
            2: 2,
            3: 2,
            4: bytes.fromhex(
                TokenReqCryptor.encrypt(ProtoBuf(pb4_dict).toBuf().hex())
            ),
            5: 3324038790882
        }
        return ProtoBuf(result).toBuf()

    @classmethod
    def sdi_get_token(cls):
        # https://mssdk.bytedance.com/sdi/get_token?lc_id=712198790&platform=iOS&device_platform=ios&sdk_ver=v04.03.09-ml-iOS&sdk_ver_code=67307777&app_ver=22.0.0&version_code=220015&aid=1128&sdkid=&subaid=&iid=2969098115104206&did=1895974765599303&bd_did=&client_type=inhouse&region_type=ml&mode=2
        query = {
            "aid": "1128",
            "app_ver": "22.0.0",
            "client_type": "inhouse",
            "device_platform": "ios",
            "did": "1895974765599303",
            "iid": "2969098115104206",
            "lc_id": "712198790",
            "mode": "2",
            "platform": "iOS",
            "region_type": "ml",
            "sdk_ver": "v04.03.09-ml-iOS",
            "sdk_ver_code": "67307777",
            "version_code": "220015"
        }
        query_str = urlencode(query, safe='/', quote_via=quote)
        print(query_str)
        url = "https://mssdk.bytedance.com/sdi/get_token"
        body = cls.get_sdi_body()
        headers = {
          "accept": "*/*",
          "accept-encoding": "gzip, deflate, br",
          "content-type": "application/octet-stream",
          "cookie": "sessionid=",
          "sdk_aid": "3019",
          "user-agent": "ByteDance-MSSDK",
          # "x-argus": "LaRCGD8ZTtCHwL1Wg4AyFBpDu7pPdhmB2Net4JhEQqNpXh3d43oi2DfEDTE9RixADSZgGXYnt6JSjIeVi4n1fhLbDe2R3Ar2vRopD38JeDva586JgaJU3DbDF57QwPZ2PhucgM6Q9kD2IQMhbTjhXHjIPY7I4H6aeSKB73+1IIKEZOSNwrxy/YD5Ii1VbXfxhgSwntNuRPULqMvj64RtaBwLRSPiYU5r9D1LhgBtJ6qhqQ==",
          # "x-gorgon": "8404e03d0000ffd2847009e0df74a86d152063fd9e51ec008de9",
          # "x-khronos": "1662019395",
          # "x-ladon": "9fX6bozrM2EX1uZF4IUDscbZlY2GUBhpQr4OXiLJZOmNVN96",
          # "x-ss-stub": "5B634404B1AD1F1D7BE3E6022A3CD26E",
          "x-tt-request-tag": "t=0;n=1",
          "x-tt-trace-id": "00-f8136122010654bb0ea39fbc96ff0468-f8136122010654bb-01",
          "x-vc-bdturing-sdk-version": "2.2.7"
        } | cls.encrypt_header(query_str, body)
        print(headers)
        resp = requests.post(
            url=f"{url}?{query_str}",
            headers=headers,
            data=body,
            verify=False,
            proxies={},
            timeout=15)
        print(ProtoBuf(resp.content).dump())


if __name__ == "__main__":
        RegApi.service_app_alert_check()
        result = RegApi.service_2_device_register()
        RegApi.iid = str(result['install_id'])
        RegApi.did = str(result['device_id'])
        RegApi.sdi_get_token()

        # xa = "+H/LiGN0Po0jW5My78DWFpuryzTWQNkjOIyoc6AW5t0EqZdUZ77jEOBRzNvy9dGLkMdzjEsIuOfrcvQj305zyFXwAnhKABoXTSOHLxY0+jHTogS2FXOZgETPY7EJUVv2zkX9tVwQXQU0E9wvFbMq9rCOO3cJrut4p9zROpeDBIpLS0nmZARYU+pzirgp9bi1Rd1RdwYQIMnC0sYVcb+bQA24"
        # d = XArgus.decrypt(xa)
        # d.dump()


