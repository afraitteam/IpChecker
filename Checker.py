import subprocess
import asyncio
import logging
from flask import Flask, request, jsonify

# تنظیمات اولیه لاگ
logging.basicConfig(filename='ipchecker.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)

async def ping_ip(ip, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} ping -c 4 {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Ping output: {stdout.decode()}")
        logging.error(f"Ping errors: {stderr.decode()}")
        if process.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Ping error: {e}")
        return False

async def nmap_scan(ip, port, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} nmap -p {port} {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Nmap output: {stdout.decode()}")
        logging.error(f"Nmap errors: {stderr.decode()}")
        if "open" in stdout.decode():
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Nmap error: {e}")
        return False

async def telnet_check(ip, port, timeout):
    try:
        process = await asyncio.create_subprocess_shell(
            f'timeout {timeout} telnet {ip} {port}',  # timeout برای محدود کردن زمان
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        logging.info(f"Telnet output: {stdout.decode()}")
        logging.error(f"Telnet errors: {stderr.decode()}")
        if "Escape character" in stdout.decode():
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Telnet error: {e}")
        return False

async def nc_check(ip, port, timeout):
    try:
        process = await asyncio.create_subprocess_shell(
            f'timeout {timeout} nc -zv -w {timeout} {ip} {port}',  # -w برای timeout
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        logging.info(f"NC check output: {stdout.decode()}")
        logging.error(f"NC check errors: {stderr.decode()}")
        if "succeeded" in stdout.decode() or "open" in stdout.decode():
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"NC check error: {e}")
        return False

async def traceroute_ip(ip, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} traceroute -m 5 {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Traceroute output: {stdout.decode()}")
        logging.error(f"Traceroute errors: {stderr.decode()}")
        if 'traceroute' in stdout.decode() or 'hops' in stdout.decode():
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Traceroute error: {e}")
        return False

async def curl_https_check(ip, port, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} curl -s -o /dev/null -w "%{{http_code}}" https://{ip}:{port}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Curl HTTPS output: {stdout.decode()}")
        logging.error(f"Curl HTTPS errors: {stderr.decode()}")
        # بررسی کد وضعیت HTTP
        if stdout.decode().strip() == '200':
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Curl HTTPS error: {e}")
        return False

# روت برای چک کردن همه متدها به صورت موازی
@app.route('/check_all', methods=['POST'])
async def check_all():
    data = request.get_json()
    ip = data.get('ip')
    port = data.get('port', 443)  # پورت پیش‌فرض 443
    timeout = data.get('timeout', 2)  # زمان انتظار پیش‌فرض 2 ثانیه

    if not ip:
        return jsonify({'error': 'IP is required'}), 400

    # اجرای تمامی روش‌ها به صورت موازی
    ping_result = await ping_ip(ip, timeout)
    nmap_result = await nmap_scan(ip, port, timeout)
    telnet_result = await telnet_check(ip, port, timeout)
    nc_result = await nc_check(ip, port, timeout)
    traceroute_result = await traceroute_ip(ip, timeout)
    curl_https_result = await curl_https_check(ip, port, timeout)

    # ساختن خروجی به صورت JSON
    return jsonify({
        'ip': ip,
        'data': {
            'ping': ping_result,
            'nmap': nmap_result,
            'telnet': telnet_result,
            'nc': nc_result,
            'traceroute': traceroute_result,
            'curl_https': curl_https_result
        }
    })

# روت تکی برای چک کردن یک روش خاص
@app.route('/check', methods=['POST'])
async def check():
    data = request.get_json()
    pack = data.get('pack', 'nmap')
    ip = data.get('ip')
    port = data.get('port', 443)  # پورت پیش‌فرض 443
    timeout = data.get('timeout', 2)  # زمان انتظار پیش‌فرض 2 ثانیه

    if not ip or not pack:
        return jsonify({'error': 'IP and pack are required'}), 400

    result = False
    if pack == "ping":
        result = await ping_ip(ip, timeout)
    elif pack == "nmap":
        result = await nmap_scan(ip, port, timeout)
    elif pack == "telnet":
        result = await telnet_check(ip, port, timeout)
    elif pack == "nc":
        result = await nc_check(ip, port, timeout)
    elif pack == "traceroute":
        result = await traceroute_ip(ip, timeout)
    elif pack == "curl_https":
        result = await curl_https_check(ip, port, timeout)
    else:
        return jsonify({'error': 'Invalid pack'}), 400

    # تغییر فرمت خروجی به شکل دلخواه
    return jsonify({
        'ip': ip,
        'pack': pack,
        'status': result
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
