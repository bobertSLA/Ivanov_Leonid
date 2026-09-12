"""
vps_log_generator.py
Симулятор генерации логов для мини-SOC на VPS.
Создает "искусственные" строки логов SSH (auth.log) и Nginx (access.log),
имитирующие обычный трафик, брутфорс-атаки и подозрительные веб-запросы.
"""

import random
from datetime import datetime, timedelta

# Пул IP-адресов: часть "обычных", часть "злонамеренных" (для брутфорса)
NORMAL_IPS = ["192.168.1.10", "10.0.0.5", "172.16.0.20", "203.0.113.7"]
ATTACKER_IPS = ["45.12.34.56", "89.44.10.2", "198.51.100.23"]

USERNAMES = ["root", "admin", "ubuntu", "test", "deploy", "oracle"]

SUSPICIOUS_PATHS = [
    "/wp-admin/",
    "/.env",
    "/admin/config.php",
    "/phpmyadmin/",
    "/etc/passwd",
    "/../../../../etc/shadow",
    "/wp-login.php",
    "/xmlrpc.php",
    "/shell.php",
]

NORMAL_PATHS = [
    "/",
    "/index.html",
    "/about",
    "/images/logo.png",
    "/api/v1/status",
    "/favicon.ico",
]


def _random_timestamp(base_time, offset_minutes):
    return (base_time + timedelta(minutes=offset_minutes)).strftime("%b %d %H:%M:%S")


def generate_mock_ssh_logs(num_lines=100):
    """
    Генерирует искусственные строки лога SSH (аналог /var/log/auth.log).
    Часть строк — обычные неудачные попытки входа со случайных IP,
    часть — целенаправленный брутфорс с нескольких "атакующих" IP.
    """
    lines = []
    base_time = datetime(2026, 1, 1, 0, 0, 0)
    host = "vps-server"

    for i in range(num_lines):
        minute_offset = i
        if random.random() < 0.4:
            ip = random.choice(ATTACKER_IPS)
        else:
            ip = random.choice(NORMAL_IPS + ATTACKER_IPS)

        user = random.choice(USERNAMES)
        port = random.randint(30000, 65000)
        ts = _random_timestamp(base_time, minute_offset)

        if random.random() < 0.05:
            line = f"{ts} {host} sshd[{1000+i}]: Accepted password for {user} from {ip} port {port} ssh2"
        else:
            line = f"{ts} {host} sshd[{1000+i}]: Failed password for {user} from {ip} port {port} ssh2"

        lines.append(line)

    return lines


def generate_mock_nginx_logs(num_lines=50):
    """
    Генерирует искусственные строки лога Nginx (аналог access.log)
    в формате Combined Log Format. Часть запросов — обычный трафик,
    часть — подозрительные пути (попытки эксплуатации/сканирования).
    """
    lines = []
    base_time = datetime(2026, 1, 1, 0, 0, 0)
    methods = ["GET", "POST"]
    referers = ["-", "https://google.com/", "https://example.com/"]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "curl/7.68.0",
        "Mozilla/5.0 (X11; Linux x86_64)",
    ]

    for i in range(num_lines):
        ip = random.choice(NORMAL_IPS + ATTACKER_IPS)
        method = random.choice(methods)

        if random.random() < 0.3:
            path = random.choice(SUSPICIOUS_PATHS)
            status = random.choice([403, 404, 401])
        else:
            path = random.choice(NORMAL_PATHS)
            status = 200

        ts = (base_time + timedelta(minutes=i)).strftime("%d/%b/%Y:%H:%M:%S +0000")
        size = random.randint(200, 5000)
        referer = random.choice(referers)
        ua = random.choice(user_agents)

        line = f'{ip} - - [{ts}] "{method} {path} HTTP/1.1" {status} {size} "{referer}" "{ua}"'
        lines.append(line)

    return lines
