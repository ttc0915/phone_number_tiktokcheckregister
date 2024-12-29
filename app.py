from flask import Flask, jsonify, request, render_template
import requests
import os
import hashlib
import urllib.parse
import time
import logging
import threading
from queue import Queue
import re

app = Flask(__name__)

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义设备信息（从环境变量获取）
device = {
    "payload": {
        "iid": os.getenv("IID", "7432390588739929861"),
        "device_id": os.getenv("DEVICE_ID", "7432390066955470341"),
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
        type_value = "1"  # 手机号
    elif "@" in value:
        type_value = "2"  # 邮箱
    else:
        type_value = "3"  # 其他
    hashed_id_str = value + "aDy0TUhtql92P7hScCs97YWMT-jub2q9"
    hashed_value = hashlib.sha256(hashed_id_str.encode()).hexdigest()
    return f"hashed_id={hashed_value}&type={type_value}"

# 输入验证函数
def is_valid_acc(acc):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    phone_regex = r'^\+\d{10,15}$'
    return re.match(email_regex, acc) or re.match(phone_regex, acc)

# 获取域名信息并检查账户状态
def getdomain(acc, session, device, queue):
    try:
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
        url = f"https://api22-normal-c-alisg.tiktokv.com/passport/account_lookup/mobile/?{url_encoded_str}"

        payload = hashed_id(acc)
        headers = {
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'passport-sdk-version': '6010090',
            'User-Agent': 'com.ss.android.tt.creator/320906 (Linux; U; Android 9; en_US; SM-G960N; Build/PQ3A.190605.07291528;tt-ok/3.12.13.4-tiktok)',
            'x-vc-bdturing-sdk-version': '2.3.4.i18n',
        }

        response = session.post(url, headers=headers, data=payload)
        response.raise_for_status()
        response_data = response.json()

        # 检查账户是否被封禁
        if 'error_code' in response_data:
            error_code = response_data['error_code']
            if error_code == 1105:
                queue.put({
                    "acc": acc,
                    "segistrationstatus": "Banned"
                })
                return

        # 根据返回的数据判断是否注册
        if response_data.get('data', {}).get('country_code') != 'sg':
            queue.put({
                "acc": acc,
                "segistrationstatus": True
            })
        else:
            queue.put({
                "acc": acc,
                "segistrationstatus": False
            })

    except Exception as e:
        logger.error(f"Error in getdomain for {acc}: {str(e)}")
        queue.put({
            "acc": acc,
            "segistrationstatus": "Error",
            "message": str(e)
        })

# 路由处理，检测手机号或邮箱是否注册（API 端点）
@app.route('/check', methods=['GET'])
def check_registration():
    try:
        # 从查询参数中获取所有 'acc' 参数
        acc_list = request.args.getlist('acc')

        if not acc_list:
            return jsonify({
                "message": "No accounts provided"
            }), 400

        results = []
        session = requests.Session()
        queue = Queue()
        threads = []

        for acc in acc_list:
            acc = acc.strip()
            if not acc:
                continue
            if not is_valid_acc(acc):
                results.append({
                    "acc": acc,
                    "segistrationstatus": "Error",
                    "message": "Invalid account format"
                })
                continue
            thread = threading.Thread(target=getdomain, args=(acc, session, device, queue))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        while not queue.empty():
            results.append(queue.get())

        return jsonify({
            "results": results
        }), 200

    except Exception as e:
        logger.error(f"Error in check_registration: {str(e)}")
        return jsonify({
            "message": f"Error: {str(e)}"
        }), 500

# 根路由提供前端界面
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # 启动 Flask 应用，确保监听所有外部请求
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))  # Railway 会自动设置环境变量 PORT
