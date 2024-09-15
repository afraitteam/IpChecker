import subprocess
import asyncio
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# تنظیمات لاگ
logging.basicConfig(filename='ping_log.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

def ping_ip(ip, timeout=10):
    try:
        # اجرای دستور پینگ با subprocess و تنظیم تایم‌اوت
        result = subprocess.run(['ping', '-c', '1', '-W', str(timeout), ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        return False

async def check_port(ip, port, timeout=10):
    try:
        # چک کردن دسترسی به پورت با استفاده از Telnet
        proc = await asyncio.create_subprocess_exec('telnet', ip, str(port),
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE)
        await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode == 0
    except asyncio.TimeoutError:
        return False

def run_tcpdump(ip, timeout=5):
    try:
        # ضبط ترافیک ورودی و خروجی به مدت timeout ثانیه
        result = subprocess.run(['timeout', str(timeout), 'tcpdump', '-n', 'host', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return len(result.stdout) > 0  # اگر پکتی دریافت شده باشد، IP فعال است
    except Exception as e:
        return False

def run_nmap(ip, port=None):
    try:
        # اجرای دستور nmap برای اسکن IP و پورت خاص (در صورت وجود)
        if port:
            result = subprocess.run(['nmap', '-p', str(port), ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            result = subprocess.run(['nmap', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return "open" in result.stdout.decode('utf-8')  # اگر پورت باز باشد، "open" در خروجی خواهد بود
    except Exception as e:
        return False

@app.route('/check-ip', methods=['POST'])
async def check_ip():
    data = request.get_json()
    ip = data.get('ip', '')
    port = data.get('port', None)  # پورت اختیاری
    pack = data.get('pack', 'ping')  # انتخاب ابزار پیش‌فرض: ping

    if not ip:
        return jsonify({'error': 'IP address is required'}), 400

    # بر اساس ابزار انتخاب‌شده از کاربر
    if pack == 'ping':
        result = ping_ip(ip)
    elif pack == 'tcpdump':
        result = run_tcpdump(ip)
    elif pack == 'nmap':
        result = run_nmap(ip, port)
    else:
        return jsonify({'error': f'Unknown tool: {pack}'}), 400

    # ثبت لاگ
    logging.info(f'IP: {ip}, Tool: {pack}, Result: {result}, Port: {port}')

    return jsonify({
        'ip': ip,
        'tool': pack,
        'result': result,
        'port': port
    })

if __name__ == '__main__':
    app.run(debug=True)
