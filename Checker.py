import subprocess
import asyncio
import logging
from flask import Flask, request, jsonify

# تنظیمات اولیه لاگ
logging.basicConfig(filename='ipchecker.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)

async def ping_ip(ip):
    try:
        process = await asyncio.create_subprocess_shell(f'ping -c 4 {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Ping error: {e}")
        return False

async def nmap_scan(ip, port):
    try:
        process = await asyncio.create_subprocess_shell(f'nmap -p {port} {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if "open" in stdout.decode():
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Nmap error: {e}")
        return False

async def telnet_check(ip, port):
    try:
        process = await asyncio.create_subprocess_shell(f'telnet {ip} {port}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if "Escape character" in stdout.decode():
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Telnet error: {e}")
        return False

async def nc_check(ip, port):
    try:
        process = await asyncio.create_subprocess_shell(
            f'nc -zv -w 5 {ip} {port}',  # -z برای بررسی فقط اتصال، -v برای نمایش جزئیات، -w 5 برای timeout 5 ثانیه
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

async def traceroute_ip(ip):
    try:
        process = await asyncio.create_subprocess_shell(f'traceroute -m 5 {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

async def curl_https_check(ip, port):
    try:
        process = await asyncio.create_subprocess_shell(f'curl -s -o /dev/null -w "%{{http_code}}" https://{ip}:{port}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

@app.route('/check', methods=['POST'])
async def check():
    data = request.get_json()
    pack = data.get('pack', 'nmap')
    ip = data.get('ip')
    port = data.get('port', 443)  # پورت پیش‌فرض 443

    if not ip or not pack:
        return jsonify({'error': 'IP and pack are required'}), 400

    result = False
    if pack == "ping":
        result = await ping_ip(ip)
    elif pack == "nmap":
        result = await nmap_scan(ip, port)
    elif pack == "telnet":
        result = await telnet_check(ip, port)
    elif pack == "nc":
        result = await nc_check(ip, port)
    elif pack == "traceroute":
        result = await traceroute_ip(ip)
    elif pack == "curl_https":
        result = await curl_https_check(ip, port)
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
