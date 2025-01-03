from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
import hashlib
import urllib.parse
import os
import logging

app = Flask(__name__)
CORS(app)  # 启用 CORS，以允许跨域请求

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

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
def hashed_id(value):
    if "+" in value:
        type_value = "1"
    elif "@" in value:
        type_value = "2"
    else:
        type_value = "3"
    hashed_id_str = value + "aDy0TUhtql92P7hScCs97YWMT-jub2q9"
    hashed_value = hashlib.sha256(hashed_id_str.encode()).hexdigest()
    return f"hashed_id={hashed_value}&type={type_value}"

# 请求并解析结果
def check_account_status(acc):
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
            '_rticket': str(int(time.time())),
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
        payload = hashed_id(acc)
        headers = {
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'passport-sdk-version': '6010090',
            'User-Agent': 'com.ss.android.tt.creator/320906 (Linux; U; Android 9; en_US; SM-G960N; Build/PQ3A.190605.07291528;tt-ok/3.12.13.4-tiktok)',
            'x-vc-bdturing-sdk-version': '2.3.4.i18n',
        }

        logging.info(f"Sending POST request to {url} with payload: {payload}")
        
        # 发送请求
        response = session.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()  # 检查HTTP请求是否成功
        response_data = response.json()

        logging.info(f"Received response: {response_data}")

        if 'error_code' in response_data:
            error_code = response_data['error_code']
            if error_code == 1105:
                return {"acc": acc, "registered": False}

        # 解析返回数据
        country_code = response_data.get('data', {}).get('country_code', '')
        if country_code.lower() != 'sg':
            return {"acc": acc, "registered": True}
        else:
            return {"acc": acc, "registered": False}

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error: {req_err}")
        return {"acc": acc, "registered": False, "message": f"Request error: {str(req_err)}"}
    except ValueError as val_err:
        logging.error(f"JSON decode error: {val_err}")
        return {"acc": acc, "registered": False, "message": "Invalid JSON response"}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"acc": acc, "registered": False, "message": f"Unexpected error: {str(e)}"}

# 路由处理
@app.route('/check/<path:acc>', methods=['GET'])
def check(acc):
    try:
        # 解码 URL 中的参数
        acc_decoded = urllib.parse.unquote(acc)
        client_ip = request.remote_addr
        logging.info(f"Received acc: '{acc_decoded}' from IP: {client_ip}")

        if not acc_decoded:
            logging.warning("No account provided in the request")
            return jsonify({"error": "No account provided"}), 400

        result = check_account_status(acc_decoded)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in /check route: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/')
def index():
    return jsonify({"message": "请使用 /check/<手机号或邮箱> 来检测 TikTok 注册状态。"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)
