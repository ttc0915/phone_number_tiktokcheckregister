from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import requests
import time
import hashlib
import urllib.parse

app = FastAPI(title="TikTok Account Checker", version="1.0.0")

# 定义设备信息
device = {
    "payload": {
        "iid": "7432390588739929861",
        "device_id": "7432390066955470341",
        "passport-sdk-version": "19",
        "ac": "wifi",
        "channel": "googleplay",
        "aid": "1233",
        "app_name": "musical_ly",
        "version_code": "320402",
        "version_name": "32.4.2",
        "device_platform": "android",
        "os": "android",
        "ab_version": "32.4.2",
        "ssmix": "a",
        "device_type": "SHARP_D9XLH",
        "device_brand": "sharp",
        "language": "en",
        "os_api": "26",
        "os_version": "8.0.0",
        "openudid": "d34d7bc383c9a34e",
        "manifest_version_code": "2023204020",
        "resolution": "1080*1920",
        "dpi": "320",
        "update_version_code": "2023204020",
        "app_type": "normal",
        "sys_region": "SG",
        "mcc_mnc": "5255",
        "timezone_name": "Asia/Singapore",
        "timezone_offset": "28800",
        "build_number": "32.4.2",
        "region": "SG",
        "carrier_region": "SG",
        "uoo": "0",
        "app_language": "en",
        "locale": "en",
        "op_region": "SG",
        "ac2": "wifi",
        "host_abi": "armeabi-v7a",
        "cdid": "841d4caf-1b90-450f-b717-b897ff555177",
        "support_webview": "1",
        "okhttp_version": "4.2.137.31-tiktok",
        "use_store_region_cookie": "1",
        "user-agent": "com.zhiliaoapp.musically/2023204020 (Linux; U; Android 8.0.0; en_SG; SHARP_D9XLH; Build/N2G48H;tt-ok/3.12.13.4-tiktok)"
    }
}

# 哈希函数
def hashed_id(value: str) -> str:
    if "+" in value:
        type_value = "1"
    elif "@" in value:
        type_value = "2"
    else:
        type_value = "3"
    hashed_id_str = value + "aDy0TUhtql92P7hScCs97YWMT-jub2q9"
    hashed_value = hashlib.sha256(hashed_id_str.encode()).hexdigest()
    return f"hashed_id={hashed_value}&type={type_value}"

# 响应模型
class CheckResponse(BaseModel):
    acc: str
    registrationstatus: str

# 检查账户状态的函数
def check_account_status(phone_or_email: str) -> dict:
    try:
        session = requests.Session()

        # 准备请求参数
        params = {
            'iid': device['payload']['iid'],
            'device_id': device['payload']['device_id'],
            'ac': 'wifi',
            'channel': 'googleplay',
            'aid': '567753',
            'app_name': 'tiktok_studio',
            'version_code': '320906',
            'version_name': '32.9.6',
            'device_platform': 'android',
            'os': 'android',
            'ab_version': '32.9.6',
            'ssmix': 'a',
            'device_type': device['payload']['device_type'],
            'device_brand': device['payload']['device_brand'],
            'language': 'en',
            'os_api': '28',
            'os_version': '9',
            'openudid': device['payload']['openudid'],
            'manifest_version_code': '320906',
            'resolution': '540*960',
            'dpi': '240',
            'update_version_code': '320906',
            '_rticket': str(int(time.time() * 1000)),
            'is_pad': '0',
            'current_region': device['payload']['carrier_region'],
            'app_type': 'normal',
            'sys_region': 'US',
            'mcc_mnc': '45201',
            'timezone_name': device['payload']['timezone_name'],
            'carrier_region_v2': '452',
            'residence': device['payload']['carrier_region'],
            'app_language': 'en',
            'carrier_region': device['payload']['carrier_region'],
            'ac2': 'wifi5g',
            'uoo': '0',
            'op_region': device['payload']['carrier_region'],
            'timezone_offset': device['payload']['timezone_offset'],
            'build_number': '32.9.6',
            'host_abi': 'arm64-v8a',
            'locale': 'en',
            'region': device['payload']['carrier_region'],
            'content_language': 'en',
            'ts': str(int(time.time())),
            'cdid': device['payload']['cdid']
        }

        url_encoded_str = urllib.parse.urlencode(params, doseq=True).replace('%2A', '*')
        url = f"https://api16-normal-useast5.tiktokv.us/passport/app/region/?{url_encoded_str}"

        # 获取哈希后的手机号或邮箱
        payload = hashed_id(phone_or_email)
        headers = {
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'passport-sdk-version': '6010090',
            'User-Agent': 'com.ss.android.tt.creator/320906 (Linux; U; Android 9; en_US; SM-G960N; Build/PQ3A.190605.07291528;tt-ok/3.12.13.4-tiktok)',
            'x-vc-bdturing-sdk-version': '2.3.4.i18n',
        }

        # 发送请求
        response = session.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        response_data = response.json()

        if 'error_code' in response_data:
            error_code = response_data['error_code']
            if error_code == 1105:
                return {"message": "Account is banned"}

        # 解析返回数据
        country_code = response_data.get('data', {}).get('country_code', '')
        if country_code.lower() != 'sg':
            return {"message": "Phone number or email is registered"}
        else:
            return {"message": "Phone number or email is not registered or inactive"}

    except requests.exceptions.RequestException as req_err:
        return {"message": f"Request error occurred: {str(req_err)}"}
    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}

# API 端点
@app.get("/check", response_model=CheckResponse)
def check_account(acc: str = Query(..., description="Phone number or Email to check")):
    if not acc:
        raise HTTPException(status_code=400, detail="Account (phone/email) parameter is required.")
    
    result = check_account_status(acc)
    status = result.get("message", "Unknown status")
    
    return CheckResponse(acc=acc, registrationstatus=status)
