import subprocess
import asyncio
import logging
from quart import Quart, request, jsonify

# تنظیمات اولیه لاگ
logging.basicConfig(filename='ipchecker.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = Quart(__name__)

async def run_command(command):
    try:
        process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        logging.info(f"Command output: {stdout.decode()}")
        logging.error(f"Command errors: {stderr.decode()}")
        return stdout.decode(), stderr.decode(), process.returncode
    except Exception as e:
        logging.error(f"Command error: {e}")
        return '', str(e), -1

async def ping_ip(ip, timeout):
    command = f'timeout {timeout} ping -c 4 {ip}'
    stdout, stderr, returncode = await run_command(command)
    return returncode == 0

async def nmap_scan(ip, port, timeout):
    command = f'timeout {timeout} nmap -p {port} {ip}'
    stdout, stderr, returncode = await run_command(command)
    return "open" in stdout

async def telnet_check(ip, port, timeout):
    command = f'timeout {timeout} telnet {ip} {port}'
    stdout, stderr, returncode = await run_command(command)
    return "Escape character" in stdout

async def nc_check(ip, port, timeout):
    command = f'timeout {timeout} nc -zv -w {timeout} {ip} {port}'
    stdout, stderr, returncode = await run_command(command)
    return "succeeded" in stdout or "open" in stdout

async def traceroute_ip(ip, timeout):
    command = f'timeout {timeout} traceroute -m 5 {ip}'
    stdout, stderr, returncode = await run_command(command)
    return 'traceroute' in stdout or 'hops' in stdout

async def curl_https_check(ip, port, timeout):
    command = f'timeout {timeout} curl -s -o /dev/null -w "%{{http_code}}" https://{ip}:{port}'
    stdout, stderr, returncode = await run_command(command)
    return stdout.strip() == '200'

@app.route('/check_all', methods=['POST'])
async def check_all():
    data = await request.get_json()
    ip = data.get('ip')
    port = data.get('port', 443)  # پورت پیش‌فرض 443
    timeout = data.get('timeout', 2)  # زمان انتظار پیش‌فرض 2 ثانیه

    if not ip:
        return jsonify({'error': 'IP is required'}), 400

    # اجرای تمامی روش‌ها به صورت همزمان
    ping_task = ping_ip(ip, timeout)
    nmap_task = nmap_scan(ip, port, timeout)
    telnet_task = telnet_check(ip, port, timeout)
    nc_task = nc_check(ip, port, timeout)
    traceroute_task = traceroute_ip(ip, timeout)
    curl_https_task = curl_https_check(ip, port, timeout)

    # اجرای تمامی توابع به صورت همزمان با استفاده از asyncio.gather
    results = await asyncio.gather(
        ping_task,
        nmap_task,
        telnet_task,
        nc_task,
        traceroute_task,
        curl_https_task
    )

    # ساختن خروجی به صورت JSON
    return jsonify({
        'ip': ip,
        'data': {
            'ping': results[0],
            'nmap': results[1],
            'telnet': results[2],
            'nc': results[3],
            'traceroute': results[4],
            'curl_https': results[5]
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
