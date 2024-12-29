from flask import Flask, jsonify, request, render_template
import requests
import os
import hashlib
import urllib.parse
import time
import logging

app = Flask(__name__)

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义设备信息（建议将敏感信息移至环境变量）
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
        type_value = "1"  # 手机号
    elif "@" in value:
        type_value = "2"  # 邮箱
    else:
        type_value = "3"  # 其他
    hashed_id_str = value + "aDy0TUhtql92P7hScCs97YWMT-jub2q9"
    hashed_value = hashlib.sha256(hashed_id_str.encode()).hexdigest()
    return f"hashed_id={hashed_value}&type={type_value}"

# 获取域名信息
def getdomain(acc, session, device):
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
        response_json = response.json()

        # 检查响应中是否包含 'data' 字段
        if 'data' in response_json:
            return {
                "data": response_json['data'],
                "message": "success"
            }
        else:
            return {
                "message": "No data found in response"
            }
    except Exception as e:
        logger.error(f"Error in getdomain for {acc}: {str(e)}")
        return {
            "message": f"error: {str(e)}"
        }

# 新的路由处理，检测手机号或邮箱是否注册
@app.route('/check/<acc>', methods=['GET'])
def check_registration(acc):
    try:
        session = requests.Session()
        result = getdomain(acc, session, device)

        if result.get("message") == "success":
            # 根据返回数据判断是否注册
            # 假设 'country_code' 不等于 'sg' 表示已注册
            if result["data"].get('country_code') != 'sg':
                registration_status = True
            else:
                registration_status = False

            return jsonify({
                "acc": acc,
                "segistrationstatus": registration_status
            }), 200
        else:
            return jsonify({
                "acc": acc,
                "segistrationstatus": "Error",
                "message": result.get("message", "Unknown error")
            }), 500

    except Exception as e:
        logger.error(f"Error in check_registration for {acc}: {str(e)}")
        return jsonify({
            "acc": acc,
            "segistrationstatus": "Error",
            "message": str(e)
        }), 500

# 主页提供一个表单，用户可以输入手机号或邮箱
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        acc = request.form.get('acc').strip()
        if not acc:
            return jsonify({
                "acc": acc,
                "segistrationstatus": "Error",
                "message": "No account provided"
            }), 400
        return check_registration(acc)
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>TikTok 账号检测</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f2f2f2;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .container {
                background-color: #fff;
                padding: 20px 30px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                width: 400px;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            button {
                padding: 10px 20px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
            pre {
                background-color: #f4f4f4;
                padding: 10px;
                border-radius: 4px;
                margin-top: 10px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>TikTok 账号检测</h2>
            <form method="POST">
                <label for="acc">手机号或邮箱：</label>
                <input type="text" id="acc" name="acc" placeholder="请输入手机号或邮箱" required>
                <button type="submit">检测</button>
            </form>
            {% if response %}
                <h3>结果：</h3>
                <pre>{{ response | tojson(indent=2) }}</pre>
            {% endif %}
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # 启动 Flask 应用，确保监听所有外部请求
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))  # Railway 会自动设置环境变量 PORT
