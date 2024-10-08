import subprocess
import asyncio
import logging
from quart import Quart, request, jsonify

# تنظیمات اولیه لاگ
logging.basicConfig(filename='ipchecker.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = Quart(__name__)

async def ping_ip(ip, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} ping -c 4 {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Ping output: {stdout.decode()}")
        logging.error(f"Ping errors: {stderr.decode()}")
        return process.returncode == 0
    except Exception as e:
        logging.error(f"Ping error: {e}")
        return False

async def nmap_scan(ip, port, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} nmap -p {port} {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Nmap output: {stdout.decode()}")
        logging.error(f"Nmap errors: {stderr.decode()}")
        return "open" in stdout.decode()
    except Exception as e:
        logging.error(f"Nmap error: {e}")
        return False

async def telnet_check(ip, port, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} telnet {ip} {port}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Telnet output: {stdout.decode()}")
        logging.error(f"Telnet errors: {stderr.decode()}")
        return "Escape character" in stdout.decode()
    except Exception as e:
        logging.error(f"Telnet error: {e}")
        return False

async def nc_check(ip, port, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} nc -zv -w {timeout} {ip} {port}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"NC check output: {stdout.decode()}")
        logging.error(f"NC check errors: {stderr.decode()}")
        return "succeeded" in stdout.decode() or "open" in stdout.decode()
    except Exception as e:
        logging.error(f"NC check error: {e}")
        return False

async def traceroute_ip(ip, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} traceroute -m 5 {ip}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Traceroute output: {stdout.decode()}")
        logging.error(f"Traceroute errors: {stderr.decode()}")
        return 'traceroute' in stdout.decode() or 'hops' in stdout.decode()
    except Exception as e:
        logging.error(f"Traceroute error: {e}")
        return False

async def curl_https_check(ip, port, timeout):
    try:
        process = await asyncio.create_subprocess_shell(f'timeout {timeout} curl -s -o /dev/null -w "%{{http_code}}" https://{ip}:{port}', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Curl HTTPS output: {stdout.decode()}")
        logging.error(f"Curl HTTPS errors: {stderr.decode()}")
        return stdout.decode().strip() == '200'
    except Exception as e:
        logging.error(f"Curl HTTPS error: {e}")
        return False

@app.route('/check_all', methods=['POST'])
async def check_all():
    data = await request.get_json()
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected JSON list.'}), 400

    results = {}
    for entry in data:
        ip = entry.get('ip')
        port = entry.get('port', 443)  # پورت پیش‌فرض 443
        timeout = entry.get('timeout', 2)  # زمان انتظار پیش‌فرض 2 ثانیه

        if not ip:
            results[ip] = {
                'error': 'IP is required'
            }
            continue

        # اجرای تمامی روش‌ها به صورت همزمان
        ping_task = ping_ip(ip, timeout)
        nmap_task = nmap_scan(ip, port, timeout)
        telnet_task = telnet_check(ip, port, timeout)
        nc_task = nc_check(ip, port, timeout)
        traceroute_task = traceroute_ip(ip, timeout)
        curl_https_task = curl_https_check(ip, port, timeout)

        # اجرای تمامی توابع به صورت همزمان با استفاده از asyncio.gather
        result = await asyncio.gather(
            ping_task,
            nmap_task,
            telnet_task,
            nc_task,
            traceroute_task,
            curl_https_task
        )

        results[ip] = {
            'ping': result[0],
            'nmap': result[1],
            'telnet': result[2],
            'nc': result[3],
            'traceroute': result[4],
            'curl_https': result[5]
        }

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
