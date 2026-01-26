# Full corrected Ctd_Version2.py
# - Fixed unterminated f-string at EOF
# - Added safe_json_loads to robustly parse incoming messages
# - Replaced fragile JSON parsing in on_message with safe_json_loads
# - Replaced a few bare excepts with except Exception and log_debug where appropriate
# - Kept original logic and features; minor defensive hardening only

import threading
import base64
import os
import time
import re
import json
import random
import requests
import socket
import sys
import logging
import math
from time import sleep
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor  
from urllib.parse import urlparse, parse_qs
from typing import Any, Dict, Tuple, Optional, List
from collections import deque
import pytz
import websocket

try:
    from faker import Faker
    from requests import session
    from colorama import Fore, Style, Back
    import pystyle
except ImportError:
    os.system("pip install faker requests colorama bs4 pystyle")
    os.system("pip3 install requests pysocks")
    print('__Vui Lòng Chạy Lại Tool__')
    sys.exit()

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    PRIMARY = '\033[38;5;141m'
    SECONDARY = '\033[38;5;117m'
    SUCCESS = '\033[38;5;120m'
    WARNING = '\033[38;5;221m'
    ERROR = '\033[38;5;210m'
    INFO = '\033[38;5;159m'
    ACCENT = '\033[38;5;183m'
    MUTED = '\033[38;5;250m'
    WHITE = '\033[97m'
    GRAD1 = '\033[38;5;147m'
    GRAD2 = '\033[38;5;153m'
    GRAD3 = '\033[38;5;159m'
    
    ORANGE = '\033[38;5;208m'

C = Colors()

def apply_theme():
    """Thay đổi theme màu nếu đang dùng thuật toán Hoá Thần (TT5)"""
    global C
    if settings.get("algo") == "Hoá Thần":
        C.PRIMARY = '\033[38;5;208m'
        C.SECONDARY = '\033[38;5;214m'
        C.INFO = '\033[38;5;220m'
        C.ACCENT = '\033[38;5;226m'
        C.MUTED = '\033[38;5;252m'
        C.GRAD1 = '\033[38;5;208m'
        C.GRAD2 = '\033[38;5;214m'
        C.GRAD3 = '\033[38;5;220m'

def animate_text(text, delay=0.001, color=None):
    if color is None:
        color = C.PRIMARY
    for char in text:
        sys.stdout.write(color + char + C.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_line(char='=', length=60, color=None):
    if color is None:
        color = C.MUTED
    print(color + char * length + C.RESET)

def print_box(text, color=None):
    if color is None:
        color = C.PRIMARY
    line_length = len(text) + 2
    print(f"{color}+{'-' * line_length}+{C.RESET}")
    print(f"{color}| {C.BOLD}{text}{C.RESET}{color} |{C.RESET}")
    print(f"{color}+{'-' * line_length}+{C.RESET}")

def encrypt_data(data):
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted_data):
    return base64.b64decode(encrypted_data.encode()).decode()

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    banner_lines = [
        f"{C.GRAD1}    ███╗   ███╗      ████████╗ ██████╗  ██████╗ ██╗     ",
        f"{C.GRAD2}    ████╗ ████║      ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ",
        f"{C.GRAD3}    ██╔████╔██║ █████╗  ██║   ██║   ██║██║   ██║██║     ",
        f"{C.GRAD2}    ██║╚██╔╝██║ ╚════╝  ██║   ██║   ██║██║   ██║██║     ",
        f"{C.GRAD1}    ██║ ╚═╝ ██║         ██║   ╚██████╔╝╚██████╔╝███████╗",
        f"{C.GRAD2}    ╚═╝     ╚═╝         ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝"
    ]
    print()
    for line in banner_lines:
        print(line + C.RESET)
        time.sleep(0.05)
    print()
    print_line('─', 70, C.ACCENT)
    info = [
        f"{C.PRIMARY}+- {C.BOLD}Tool bởi{C.RESET}       {C.SECONDARY}| {C.ACCENT}/DUY HOÀNG TU TIÊN{C.RESET}",
        f"{C.PRIMARY}+- {C.BOLD}Version{C.RESET}        {C.SECONDARY}| {C.SUCCESS}V1.2 - Update thuật toán{C.RESET}",
        f"{C.PRIMARY}+- {C.BOLD}Kênh Youtube{C.RESET}   {C.SECONDARY}| {C.INFO}BIJANHACK{C.RESET}",
        f"{C.PRIMARY}+- {C.BOLD}Group Zalo{C.RESET}     {C.SECONDARY}| {C.WARNING}https://zalo.me/g/iaoaaq307{C.RESET}",
    ]
    for line in info:
        print(line)
        time.sleep(0.05)
    print_line('─', 70, C.ACCENT)
    print()

def get_ip_address():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip_data = response.json()
        return ip_data.get('ip')
    except Exception as e:
        print(f"{C.ERROR}Lỗi khi lấy IP: {e}{C.RESET}")
        return None

def display_ip_address(ip_address):
    if ip_address:
        banner()
        print(f"{C.INFO}IP Address: {C.ACCENT}{ip_address}{C.RESET}")
        print()
    else:
        print(f"{C.ERROR}Không thể lấy địa chỉ IP của thiết bị.{C.RESET}")

def luu_thong_tin_ip(ip, key, expiration_date):
    data = {ip: {'key': key, 'expiration_date': expiration_date.isoformat()}}
    encrypted_data = encrypt_data(json.dumps(data))
    with open('TUTIENLAMDAO_key.json', 'w') as file:
        file.write(encrypted_data)

def tai_thong_tin_ip():
    try:
        with open('TUTIENLAMDAO_key.json', 'r') as file:
            encrypted_data = file.read()
        data = json.loads(decrypt_data(encrypted_data))
        return data
    except Exception:
        return None

def kiem_tra_ip(ip):
    data = tai_thong_tin_ip()
    if not data or ip not in data:
        return None
    info = data[ip]
    if 'expiration_date' not in info:
        try:
            os.remove('TUTIENLAMDAO_key.json')
        except Exception:
            pass
        return None
    try:
        expiration_date = datetime.fromisoformat(info['expiration_date'])
    except Exception:
        try:
            os.remove('TUTIENLAMDAO_key.json')
        except Exception:
            pass
        return None
    if expiration_date > datetime.now():
        return info['key']
    return None

def generate_key_and_url(ip_address):
    ngay = int(datetime.now().day)
    key1 = str(ngay * 27 + 27)
    ip_numbers = ''.join(filter(str.isdigit, ip_address))
    key = f'HOANG-{key1}{ip_numbers}'
    expiration_date = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
    url = f'https://haidang-coder.neocities.org/api_key/?key={key}'
    return url, key, expiration_date

def da_qua_gio_moi():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return now >= midnight
    
UPDATE_KEYS = {
    "DuyHoangNgoL": "2100-12-31", # Key:  (YYYY-MM-DD)
    "HoangLoCac": "2100-01-15",
    # Thêm các key update khác ở đây
}
LOCAL_UPDATE_KEY_FILE = "TUTIENLAMDAO_update_key.json"

def save_local_update_key(key, expiry_date_str):
    try:
        data = {'key': key, 'expiry': expiry_date_str}
        encrypted_data = encrypt_data(json.dumps(data))
        with open(LOCAL_UPDATE_KEY_FILE, 'w', encoding='utf-8') as f:
            f.write(encrypted_data)
        return True
    except Exception:
        return False

def load_local_update_key():
    try:
        if os.path.exists(LOCAL_UPDATE_KEY_FILE):
            with open(LOCAL_UPDATE_KEY_FILE, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
                decrypted = decrypt_data(encrypted_data)
                return json.loads(decrypted)
        return None
    except Exception:
        return None

def check_local_update_key():
    local_data = load_local_update_key()
    if not local_data:
        return False, "Chưa có key Update", 0
    
    try:
        expiry_date = datetime.strptime(local_data['expiry'], "%Y-%m-%d")
        if datetime.now() > expiry_date:
            return False, "Key Update đã hết hạn", 0
        days_left = (expiry_date - datetime.now()).days + 1
        return True, f"Key Update còn {days_left} ngày", days_left
    except Exception:
        return False, "Lỗi kiểm tra file key", 0

def validate_and_save_update_key(key_input):
    if key_input not in UPDATE_KEYS:
        return False, "Key Update không hợp lệ", 0
    
    expiry_str = UPDATE_KEYS[key_input]
    
    try:
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
        if datetime.now() > expiry_date:
            return False, "Key Update này đã hết hạn", 0
        days_left = (expiry_date - datetime.now()).days + 1
    except Exception:
        return False, "Lỗi định dạng ngày của key", 0
    
    save_local_update_key(key_input, expiry_str)
    
    return True, f"Kích hoạt Key Update thành công! Còn {days_left} ngày", days_left

def menu_input_update_key():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    
    print(f"{C.PRIMARY}NHẬP KEY UPDATE{C.RESET}")
    print_line('=', 70, C.PRIMARY)
    print(f"{C.SUCCESS}Key Update không cần vượt link hàng ngày{C.RESET}")
    print(f"{C.MUTED}Liên hệ admin TUTIENLAMDAO (99% CON BẠC TỪ BỎ SAO KHI THẮNG LỚN) để lấy key{C.RESET}")
    print_line('=', 70, C.PRIMARY)
    print()
    
    key_input = input(f"{C.PRIMARY}Nhập Key Update: {C.RESET}").strip()
    
    if not key_input:
        return False
    
    print(f"\n{C.INFO}Đang xác thực key...{C.RESET}\n")
    time.sleep(0.5)
    
    success, message, days_left = validate_and_save_update_key(key_input)
    
    if success:
        print(f"{C.SUCCESS}{message}{C.RESET}")
        time.sleep(2)
        return True
    else:
        print(f"{C.ERROR}{message}{C.RESET}")
        retry = input(f"\n{C.WARNING}Thử lại? (y/n): {C.RESET}").strip().lower()
        if retry == 'y':
            return menu_input_update_key()
        return False

def get_shortened_link_phu(url):
    try:
        token = "6881fc748541867cf929b20b"
        api_url = f"https://link4m.co/api-shorten/v2?api={token}&url={url}"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": "Không thể kết nối đến dịch vụ rút gọn URL."}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi khi rút gọn URL: {e}"}

def main():
    ip_address = get_ip_address()
    display_ip_address(ip_address)
    
    if not ip_address:
        print(f"{C.ERROR}Không thể lấy IP. Tool sẽ thoát.{C.RESET}")
        time.sleep(3)
        sys.exit(1)

    update_valid, update_msg, days_left = check_local_update_key()
    
    print()
    print_line('=', 70, C.PRIMARY)
    print(f"{C.BOLD}{C.PRIMARY}CHỌN LOẠI KEY{C.RESET}")
    print_line('=', 70, C.PRIMARY)
    print()
    
    if update_valid:
        print(f"{C.SUCCESS}KEY UPDATE ĐANG HOẠT ĐỘNG{C.RESET}")
        print(f"{C.INFO}Trạng thái: {C.BOLD}{update_msg}{C.RESET}")
        print()
    
    print(f"{C.PRIMARY}[1] Lấy Key Free (vượt link hàng ngày){C.RESET}")
    print(f"{C.WARNING}[2] Nhập Key Update{C.RESET}")
    print()
    
    if update_valid:
        print(f"{C.MUTED}Nhấn Enter để tiếp tục với Key Update hiện tại...{C.RESET}")
        print()
    
    try:
        choice = input(f"{C.SECONDARY}Lựa chọn: {C.RESET}").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{C.PRIMARY}Cảm ơn bạn đã dùng Tool !!!{C.RESET}")
        sys.exit()
    
    print_line('-', 70, C.MUTED)
    print()
    
    if choice == "2":
        if menu_input_update_key():
            print(f"{C.SUCCESS}Key Update hợp lệ! Đang khởi động tool...{C.RESET}")
            time.sleep(2)
            return
        else:
            print(f"{C.WARNING}Chuyển sang chế độ Key Free{C.RESET}")
            time.sleep(1)
    
    elif choice == "1":
        print(f"{C.INFO}Chế độ Key Free - Cần vượt link{C.RESET}")
        time.sleep(1)
    
    elif choice == "" and update_valid:
        print(f"{C.SUCCESS}Tiếp tục với Key Update{C.RESET}")
        time.sleep(1)
        return 
    
    else:
        print(f"{C.WARNING}Lựa chọn không hợp lệ, chuyển sang Key Free{C.RESET}")
        time.sleep(1)
    
    existing_key = kiem_tra_ip(ip_address)
    if existing_key:
        print_box("KEY FREE HỢP LỆ - VUI LÒNG SỬ DỤNG TOOL", C.SUCCESS)
        time.sleep(2)
    else:
        if da_qua_gio_moi():
            print_box("KEY HẾT HẠN", C.ERROR)
            sys.exit()

        url, key, expiration_date = generate_key_and_url(ip_address)

        with ThreadPoolExecutor(max_workers=2) as executor:
            print(f"{C.PRIMARY}Nhập [1] để lấy Key Free{C.RESET}")
            print(f"{C.MUTED}Hoặc Ctrl+C để thoát{C.RESET}\n")

            while True:
                try:
                    choice = input(f"{C.SECONDARY}Lựa chọn: {C.RESET}").strip()
                    print_line('-', 70, C.MUTED)
                    
                    if choice == "1":
                        print(f"{C.INFO}Đang tạo link vượt key...{C.RESET}")
                        yeumoney_future = executor.submit(get_shortened_link_phu, url)
                        yeumoney_data = yeumoney_future.result()
                        
                        if yeumoney_data and yeumoney_data.get('status') == "error":
                            print(f"{C.ERROR}{yeumoney_data.get('message')}{C.RESET}")
                            sys.exit()
                        else:
                            link_key_yeumoney = yeumoney_data.get('shortenedUrl')
                            print(f"\n{C.INFO}Link vượt key: {C.ACCENT}{link_key_yeumoney}{C.RESET}\n")

                        while True:
                            keynhap = input(f"{C.WARNING}Nhập key đã vượt: {C.RESET}").strip()
                            if keynhap == key:
                                print(f"\n{C.SUCCESS}Key chính xác! Đang khởi động tool...{C.RESET}")
                                sleep(2)
                                luu_thong_tin_ip(ip_address, keynhap, expiration_date)
                                return 
                            else:
                                print(f"{C.ERROR}Key sai! Vui lòng vượt lại link: {C.ACCENT}{link_key_yeumoney}{C.RESET}\n")
                    else:
                        print(f"{C.WARNING}Vui lòng nhập số 1{C.RESET}")
                        
                except ValueError:
                    print(f"{C.ERROR}Vui lòng nhập số hợp lệ.{C.RESET}")
                except KeyboardInterrupt:
                    print(f"\n{C.PRIMARY}Cảm ơn bạn đã dùng Tool !!!{C.RESET}")
                    sys.exit()

def show_main_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print()
    print_line('═', 70, C.PRIMARY)
    animate_text("             HOANGTOOL VTH", 0.02, C.GRAD1)
    print_line('═', 70, C.PRIMARY)
    print(f"{C.INFO}   Biển Quàn by {C.BOLD}DUY HOÀNG{C.RESET} {C.SECONDARY}|{C.RESET} {C.ACCENT}Youtube: BIJANHACK{C.RESET}")
    print_line('═', 70, C.PRIMARY)
    print()

tz = pytz.timezone("Asia/Ho_Chi_Minh")

logger = logging.getLogger("escape_HOANG_ai_rebuild")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler("escape_HOANG_ai_rebuild.log", encoding="utf-8"))

BET_API_URL = "https://api.escapemaster.net/escape_game/bet"
WS_URL = "wss://api.escapemaster.net/escape_master/ws"
WALLET_API_URL = "https://wallet.3games.io/api/wallet/user_asset"

HTTP = requests.Session()
try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    adapter = HTTPAdapter(
        pool_connections=20, pool_maxsize=50,
        max_retries=Retry(total=3, backoff_factor=0.2,
                          status_forcelist=(500, 502, 503, 504))
    )
    HTTP.mount("https://", adapter)
    HTTP.mount("http://", adapter)
except Exception as e:
    log_debug = lambda msg: None  # fallback if logger not ready
    pass

ROOM_NAMES = {
    1: "Nhà kho", 2: "Phòng họp", 3: "Phòng giám đốc", 4: "Phòng trò chuyện",
    5: "Phòng giám sát", 6: "Văn phòng", 7: "Phòng tài vụ", 8: "Phòng nhân sự"
}
ROOM_ORDER = [1, 2, 3, 4, 5, 6, 7, 8]

# --- Special external-room mapping for the custom mode requested ---
SPECIAL_EXTERNAL_ROOM_ID = 272756317835
SPECIAL_MODE_KEY = "MẤY THẰNG ĐÉO CÓ NGƯỜI YÊU NHẬP VÀO CON ĐƯỜNG MA ĐẠO TA ĐỊT SÁT THỦ ĐỂ TĂNG TU VI"
# map external id deterministically into internal room index (1..8)
SPECIAL_MAPPED_ROOM = int(SPECIAL_EXTERNAL_ROOM_ID % len(ROOM_ORDER)) + 1

USER_ID: Optional[int] = None
SECRET_KEY: Optional[str] = None
issue_id: Optional[int] = None
issue_start_ts: Optional[float] = None
count_down: Optional[int] = None
killed_room: Optional[int] = None
round_index: int = 0
_skip_active_issue: Optional[int] = None

room_state: Dict[int, Dict[str, Any]] = {r: {"players": 0, "bet": 0} for r in ROOM_ORDER}
room_stats: Dict[int, Dict[str, Any]] = {r: {"kills": 0, "survives": 0, "last_kill_round": None, "last_players": 0, "last_bet": 0} for r in ROOM_ORDER}

predicted_room: Optional[int] = None
last_killed_room: Optional[int] = None
prediction_locked: bool = False

current_build: Optional[float] = None
current_usdt: Optional[float] = None
current_world: Optional[float] = None
last_balance_ts: Optional[float] = None
last_balance_val: Optional[float] = None
starting_balance: Optional[float] = None
cumulative_profit: float = 0.0

win_streak: int = 0
lose_streak: int = 0
max_win_streak: int = 0
max_lose_streak: int = 0

base_bet: float = 1.0
multiplier: float = 2.0
current_bet: Optional[float] = None
run_mode: str = "AUTO"

bet_rounds_before_skip: int = 0
_rounds_placed_since_skip: int = 0
skip_next_round_flag: bool = False

random_bet_enabled: bool = False  

bet_history: deque = deque(maxlen=500)
bet_sent_for_issue: set = set()

pause_after_losses: int = 0
_skip_rounds_remaining: int = 0
profit_target: Optional[float] = None
stop_when_profit_reached: bool = False
stop_loss_target: Optional[float] = None
stop_when_loss_reached: bool = False
stop_flag: bool = False

ui_state: str = "IDLE"
analysis_start_ts: Optional[float] = None
analysis_blur: bool = False
last_msg_ts: float = time.time()
last_balance_fetch_ts: float = 0.0
BALANCE_POLL_INTERVAL: float = 4.0
_ws: Dict[str, Any] = {"ws": None}

ASSET_TYPE: str = "BUILD" # Mặc định là BUILD, có thể đổi thành USDT

SELECTION_CONFIG = {
    "max_bet_allowed": float("inf"),
    "max_players_allowed": 9999,
    "avoid_last_kill": True,
}

SELECTION_MODES = {
    "LUYỆN KHÍ": "IT BUILD",
    "TRÚC CƠ": "NHIỀU BUILD",
    "TINH ANH": "NHIỀU BUILD",
    "NHẬP MÔN": "NHAP THỂ BUILD CHO MẤY THẰNG HAY THUA",
    "LUYỆN KHÍ HOÁ THẦN": "Thần thức toả ra 8 hướng (TT5)",
    "NHẬP MA": "RƠI VÀO CON ĐƯỜNG MA ĐẠO",
    "(:": "Theo Sát Thủ (TT7) [Đang Lỗi]",
    SPECIAL_MODE_KEY: f"Áp dụng cho external room {SPECIAL_EXTERNAL_ROOM_ID}"
}
settings = {"algo": ""}

# --- New NHẬP MA advanced sequence state (requested logic 5.8.7,3,2,6,4,2) ---
# The sequence will be cycled; if the next room was the last killed room (bad), the logic will pick
# the following room in the sequence or a safe alternative. Occasionally (small chance) it will
# inject a randomized offset to avoid predictability.
nhap_ma_sequence: List[int] = [5, 8, 7, 3, 2, 6, 4, 2]
nhap_ma_index: int = 0
nhap_ma_last_chosen: Optional[int] = None

algo5_last_random_time: float = 0.0
algo5_current_target: Optional[int] = None

algo6_next_room: int = 1

algo7_skip_first_round: bool = True 
algo7_last_kill: Optional[int] = None 

_num_re = re.compile(r"-?\d+[\d,]*\.?\d*")

def log_debug(msg: str):
    try:
        logger.debug(msg)
    except Exception:
        pass

def safe_json_loads(s: Any) -> Optional[dict]:
    """
    Safely parse a JSON-like string into a dict.
    Returns dict on success or None on failure.
    Tries strict json.loads first, then a tolerant replace, else returns None.
    """
    if s is None:
        return None
    try:
        if isinstance(s, dict):
            return s
        if isinstance(s, bytes):
            s = s.decode("utf-8", errors="replace")
        if not isinstance(s, str):
            s = str(s)
        return json.loads(s)
    except Exception as e:
        try:
            s2 = s.replace("'", '"')
            return json.loads(s2)
        except Exception as e2:
            log_debug(f"safe_json_loads failed: {e} / {e2}")
            return None

def check_internet_connection(host: str = "1.1.1.1", port: int = 53, timeout: float = 0.5) -> bool:
    """
    Quick internet connectivity check using a TCP socket to a public DNS server.
    Returns True if connection succeeds, False otherwise.

    Default host/port: Cloudflare DNS 1.1.1.1:53 (fast and generally reachable).
    """
    try:
        # socket.create_connection will raise on failure or timeout
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def _parse_number(x: Any) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x)
    m = _num_re.search(s)
    if not m:
        return None
    token = m.group(0).replace(",", "")
    try:
        return float(token)
    except Exception:
        return None

def human_ts() -> str:
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def safe_input(prompt: str, default=None, cast=None):
    try:
        s = input(prompt).strip()
    except EOFError:
        return default
    if s == "":
        return default
    if cast:
        try:
            return cast(s)
        except Exception:
            return default
    return s

def _parse_balance_from_json(j: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    if not isinstance(j, dict):
        return None, None, None
    build = None
    world = None
    usdt = None

    data = j.get("data") if isinstance(j.get("data"), dict) else j
    if isinstance(data, dict):
        cwallet = data.get("cwallet") if isinstance(data.get("cwallet"), dict) else None
        if cwallet:
            for key in ("ctoken_contribute", "ctoken", "build", "balance", "amount"):
                if key in cwallet and build is None:
                    build = _parse_number(cwallet.get(key))
        for k in ("build", "ctoken", "ctoken_contribute"):
            if build is None and k in data:
                build = _parse_number(data.get(k))
        for k in ("usdt", "kusdt", "usdt_balance"):
            if usdt is None and k in data:
                usdt = _parse_number(data.get(k))
        for k in ("world", "xworld"):
            if world is None and k in data:
                world = _parse_number(data.get(k))

    found = []

    def walk(o: Any, path=""):
        if isinstance(o, dict):
            for kk, vv in o.items():
                nk = (path + "." + str(kk)).strip(".")
                if isinstance(vv, (dict, list)):
                    walk(vv, nk)
                else:
                    n = _parse_number(vv)
                    if n is not None:
                        found.append((nk.lower(), n))
        elif isinstance(o, list):
            for idx, it in enumerate(o):
                walk(it, f"{path}[{idx}]")

    walk(j)

    for k, n in found:
        if build is None and any(x in k for x in ("ctoken", "build", "contribute", "balance")):
            build = n
        if usdt is None and "usdt" in k:
            usdt = n
        if world is None and any(x in k for x in ("world", "xworld")):
            world = n

    return build, world, usdt

def balance_headers_for(uid: Optional[int] = None, secret: Optional[str] = None) -> Dict[str, str]:
    h = {
        "accept": "*/*",
        "accept-language": "vi,en;q=0.9",
        "cache-control": "no-cache",
        "country-code": "vn",
        "origin": "https://xworld.info",
        "pragma": "no-cache",
        "referer": "https://xworld.info/",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36",
        "user-login": "login_v2",
        "xb-language": "vi-VN",
    }
    if uid is not None:
        h["user-id"] = str(uid)
    if secret:
        h["user-secret-key"] = str(secret)
    return h

def fetch_balances_3games(retries=2, timeout=6, params=None, uid=None, secret=None):
    global current_build, current_usdt, current_world, last_balance_ts
    global starting_balance, last_balance_val, cumulative_profit

    uid = uid or USER_ID
    secret = secret or SECRET_KEY
    payload = {"user_id": int(uid) if uid is not None else None, "source": "home"}

    attempt = 0
    while attempt <= retries:
        attempt += 1
        try:
            r = HTTP.post(
                WALLET_API_URL,
                json=payload,
                headers=balance_headers_for(uid, secret),
                timeout=timeout,
            )
            r.raise_for_status()
            j = r.json()

            build = None
            world = None
            usdt = None
            build, world, usdt = _parse_balance_from_json(j)

            if build is not None:
                if ASSET_TYPE == "BUILD": 
                    if last_balance_val is None:
                        starting_balance = build
                        last_balance_val = build
                    else:
                        delta = float(build) - float(last_balance_val)
                        if abs(delta) > 0:
                            cumulative_profit += delta
                            last_balance_val = build
                current_build = build
            
            if usdt is not None:
                if ASSET_TYPE == "USDT": 
                    if last_balance_val is None:
                        starting_balance = usdt
                        last_balance_val = usdt
                    else:
                        delta = float(usdt) - float(last_balance_val)
                        if abs(delta) > 0:
                            cumulative_profit += delta
                            last_balance_val = usdt
                current_usdt = usdt

            if world is not None:
                current_world = world

            last_balance_ts = time.time()
            return current_build, current_world, current_usdt

        except Exception as e:
            log_debug(f"wallet fetch attempt {attempt} error: {e}")
            time.sleep(min(0.6 * attempt, 2))

    return current_build, current_world, current_usdt

FORMULAS: List[Dict[str, Any]] = []
FORMULA_SEED = 1234567

def _room_features_enhanced(rid: int):
    st = room_state.get(rid, {})
    stats = room_stats.get(rid, {})
    players = float(st.get("players", 0))
    bet = float(st.get("bet", 0))
    bet_per_player = (bet / players) if players > 0 else bet

    players_norm = min(1.0, players / 50.0)
    bet_norm = 1.0 / (1.0 + bet / 2000.0)
    bpp_norm = 1.0 / (1.0 + bet_per_player / 1200.0)

    kill_count = float(stats.get("kills", 0))
    survive_count = float(stats.get("survives", 0))
    kill_rate = (kill_count + 0.5) / (kill_count + survive_count + 1.0)
    survive_score = 1.0 - kill_rate

    recent_history = list(bet_history)[-12:]
    recent_pen = 0.0
    for i, rec in enumerate(reversed(recent_history)):
        if rec.get("room") == rid:
            recent_pen += 0.12 * (1.0 / (i + 1))

    last_pen = 0.0
    if last_killed_room == rid:
        last_pen = 0.35 if SELECTION_CONFIG.get("avoid_last_kill", True) else 0.0

    hot_score = max(0.0, survive_score - 0.2)
    cold_score = max(0.0, kill_rate - 0.4)

    return {
        "players_norm": players_norm,
        "bet_norm": bet_norm,
        "bpp_norm": bpp_norm,
        "survive_score": survive_score,
        "recent_pen": recent_pen,
        "last_pen": last_pen,
        "hot_score": hot_score,
        "cold_score": cold_score,
    }

def _init_formulas(mode: str = "HOÀNG"):
    global FORMULAS
    
    if mode in ["Hoá Thần", "Tuần tự", "Theo sát thủ"]:
        FORMULAS = []
        return
        
    rng = random.Random(FORMULA_SEED)
    formulas = []

    def mk_formula(base_bias: Optional[str] = None):
        w = {
            "players": rng.uniform(0.2, 0.8),
            "bet": rng.uniform(0.1, 0.6),
            "bpp": rng.uniform(0.05, 0.6),
            "survive": rng.uniform(0.05, 0.4),
            "recent": rng.uniform(0.05, 0.3),
            "last": rng.uniform(0.1, 0.6),
            "hot": rng.uniform(0.0, 0.35),
            "cold": rng.uniform(0.0, 0.35),
        }
        noise = rng.uniform(0.0, 0.08)
        if base_bias == "hot":
            w["hot"] += rng.uniform(0.2, 0.5)
            w["survive"] += rng.uniform(0.05, 0.2)
        elif base_bias == "cold":
            w["cold"] += rng.uniform(0.2, 0.5)
            w["last"] += rng.uniform(0.05, 0.2)
        return {"w": w, "noise": noise, "adapt": 1.0}

    if mode == "HOÀNG":
        for _ in range(50):
            formulas.append(mk_formula())
    elif mode == "LUYỆN KHÍ":
        for _ in range(35):
            formulas.append(mk_formula())
        for _ in range(10):
            formulas.append(mk_formula(base_bias="hot"))
        for _ in range(5):
            formulas.append(mk_formula(base_bias="cold"))
    elif mode == "TRÚC CƠ":
        for _ in range(50):
            formulas.append(mk_formula())
        for _ in range(25):
            formulas.append(mk_formula(base_bias="hot"))
        for _ in range(25):
            formulas.append(mk_formula(base_bias="cold"))
    elif mode == "TINH ANH":
        for _ in range(40):
            formulas.append(mk_formula())
        for _ in range(6):
            formulas.append(mk_formula(base_bias="hot"))
        for _ in range(4):
            formulas.append(mk_formula(base_bias="cold"))
    else:
        for _ in range(50):
            formulas.append(mk_formula())

    FORMULAS = formulas

_init_formulas("HOANGDZ")

def choose_room(mode: str = "HOANGDZ") -> Tuple[int, str]:
    global FORMULAS, algo5_current_target, algo6_next_room, algo7_skip_first_round, algo7_last_kill
    global nhap_ma_index, nhap_ma_sequence, nhap_ma_last_chosen, last_killed_room
    
    # Special mode: Hoá Thần (randomized target -> locked later)
    if mode == "Hoá Thần":
        final_room = algo5_current_target or random.choice(ROOM_ORDER)
        algo5_current_target = None 
        return final_room, "Hoá Thần"

    # Sequential mode
    if mode == "Tuần tự":
        room = algo6_next_room
        algo6_next_room = (room % 8) + 1
        return room, "Tuần tự"

    # Theo sát thủ mode: uses last kill
    if mode == "Theo sát thủ":
        if algo7_skip_first_round or algo7_last_kill is None:
            return 0, "Theo sát thủ" 
        room = algo7_last_kill
        return room, "Theo sát thủ"

    # New custom explicit mode requested by user: strong bias to mapped room
    if mode == SPECIAL_MODE_KEY:
        try:
            mapped = SPECIAL_MAPPED_ROOM
            # if mapped is last_killed_room and we avoid last kill, pick safe alternative
            if SELECTION_CONFIG.get("avoid_last_kill", True) and last_killed_room is not None and mapped == last_killed_room:
                # choose room with lowest recent_penalty excluding last_killed_room
                scores = [(r, _room_features_enhanced(r)["recent_pen"]) for r in ROOM_ORDER if r != last_killed_room]
                scores.sort(key=lambda x: x[1])
                if scores:
                    return scores[0][0], SPECIAL_MODE_KEY
                else:
                    return mapped, SPECIAL_MODE_KEY
            # majority bias to mapped room to "ép sát thủ"
            if random.random() < 0.85:
                return mapped, SPECIAL_MODE_KEY
            # fallback: do a lightweight scoring to pick best alternative (small chance)
            best = None
            best_score = -1e9
            for r in ROOM_ORDER:
                f = _room_features_enhanced(r)
                score = f["survive_score"] + 0.5 * f["players_norm"] - f["recent_pen"] - 0.5 * f["last_pen"]
                if score > best_score:
                    best_score = score
                    best = r
            return best or mapped, SPECIAL_MODE_KEY
        except Exception as e:
            log_debug(f"Special custom mode error: {e}")
            # fallback to main algorithm below
            pass

    # New advanced NHẬP MA logic (sequence-based with safety and small jitter)
    if mode == "NHẬP MA":
        try:
            # cycle through the configured sequence
            seq = nhap_ma_sequence or [5,8,7,3,2,6,4,2]
            idx = nhap_ma_index % len(seq)
            candidate = seq[idx]

            # If candidate is the last killed room and avoid_last_kill enabled, try next items in sequence
            if SELECTION_CONFIG.get("avoid_last_kill", True) and last_killed_room is not None and candidate == last_killed_room:
                found = False
                for step in range(1, len(seq)):
                    alt = seq[(idx + step) % len(seq)]
                    if alt != last_killed_room:
                        candidate = alt
                        nhap_ma_index = (idx + step) % len(seq)
                        found = True
                        break
                if not found:
                    # fallback: pick a room with lowest recent_penalty
                    scores = [(r, _room_features_enhanced(r)["recent_pen"]) for r in ROOM_ORDER]
                    scores.sort(key=lambda x: x[1])
                    candidate = scores[0][0]

            # Occasionally add slight randomness to avoid being exploitable (5% chance)
            if random.random() < 0.05:
                candidate = random.choice([r for r in ROOM_ORDER if r != last_killed_room])

            # record chosen and advance index normally
            nhap_ma_last_chosen = candidate
            nhap_ma_index = (nhap_ma_index + 1) % len(seq)

            return candidate, "NHẬP MA"
        except Exception as e:
            log_debug(f"NHẬP MA choose_room err: {e}")
            # fallback to safe generic method
            pass

    # Ensure formula pools sizes for some modes
    if mode == "NHẬP MÔN" and len(FORMULAS) != 100:
        _init_formulas(mode)
    if mode == "NHẬP MA" and len(FORMULAS) != 50:
        _init_formulas(mode)
    if mode == "LUYỆN KHÍ" and len(FORMULAS) < 40:
        _init_formulas(mode)
    if mode == "TINH ANH" and len(FORMULAS) < 40:
        _init_formulas(mode)

    cand = [r for r in ROOM_ORDER]
    agg_scores = {r: 0.0 for r in cand}

    for idx, fentry in enumerate(FORMULAS):
        weights = fentry["w"]
        adapt = fentry.get("adapt", 1.0)
        noise_scale = fentry.get("noise", 0.02)
        best_room = None
        best_score = -1e9
        for r in cand:
            f = _room_features_enhanced(r)
            score = 0.0
            score += weights.get("players", 0.0) * f["players_norm"]
            score += weights.get("bet", 0.0) * f["bet_norm"]
            score += weights.get("bpp", 0.0) * f["bpp_norm"]
            score += weights.get("survive", 0.0) * f["survive_score"]
            score -= weights.get("recent", 0.0) * f["recent_pen"]
            score -= weights.get("last", 0.0) * f["last_pen"]
            score += weights.get("hot", 0.0) * f["hot_score"]
            score -= weights.get("cold", 0.0) * f["cold_score"]
            noise = (math.sin((idx + 1) * (r + 1) * 12.9898) * 43758.5453) % 1.0
            noise = (noise - 0.5) * (noise_scale * 2.0)
            score += noise
            score *= adapt
            if score > best_score:
                best_score = score
                best_room = r
        agg_scores[best_room] += best_score

    n = max(1, len(FORMULAS))
    for r in agg_scores:
        agg_scores[r] /= n

    for r in cand:
        f = _room_features_enhanced(r)
        agg_scores[r] += 0.02 * f["hot_score"]
        agg_scores[r] -= 0.02 * f["cold_score"]

    ranked = sorted(agg_scores.items(), key=lambda kv: (-kv[1], kv[0]))
    best_room = ranked[0][0]
    return best_room, mode

def update_formulas_after_result(predicted_room: Optional[int], killed_room: Optional[int], mode: str = "ĐẸP TRAI", lr: float = 0.12):
    global FORMULAS
    if mode != "TINH ANH":
        return
    if not FORMULAS:
        return

    votes_for_pred = []
    votes_for_killed = []
    for idx, fentry in enumerate(FORMULAS):
        weights = fentry["w"]
        best_room = None
        best_score = -1e9
        for r in ROOM_ORDER:
            feat = _room_features_enhanced(r)
            score = 0.0
            score += weights.get("players", 0.0) * feat["players_norm"]
            score += weights.get("bet", 0.0) * feat["bet_norm"]
            score += weights.get("bpp", 0.0) * feat["bpp_norm"]
            score += weights.get("survive", 0.0) * feat["survive_score"]
            score -= weights.get("recent", 0.0) * feat["recent_pen"]
            score -= weights.get("last", 0.0) * feat["last_pen"]
            score += weights.get("hot", 0.0) * feat["hot_score"]
            score -= weights.get("cold", 0.0) * feat["cold_score"]
            if score > best_score:
                best_score = score
                best_room = r
        if best_room == predicted_room:
            votes_for_pred.append(idx)
        if best_room == killed_room:
            votes_for_killed.append(idx)

    win = (predicted_room is not None and killed_room is not None and predicted_room != killed_room)

    for idx, fentry in enumerate(FORMULAS):
        aw = fentry.get("adapt", 1.0)
        if win:
            if idx in votes_for_pred:
                aw = aw * (1.0 + lr)
            if idx in votes_for_killed:
                aw = aw * (1.0 - lr * 0.6)
        else:
            if idx in votes_for_pred:
                aw = max(0.1, aw * (1.0 - lr))
            if idx in votes_for_killed:
                aw = aw * (1.0 + lr * 0.6)
        aw = min(max(aw, 0.1), 5.0)
        fentry["adapt"] = aw

def api_headers() -> Dict[str, str]:
    return {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "user-id": str(USER_ID) if USER_ID else "",
        "user-secret-key": SECRET_KEY if SECRET_KEY else ""
    }

def place_bet_http(issue: int, room_id: int, amount: float) -> dict:
    payload = {"asset_type": ASSET_TYPE, "user_id": USER_ID, "room_id": int(room_id), "bet_amount": float(amount)}
    try:
        r = HTTP.post(BET_API_URL, headers=api_headers(), json=payload, timeout=6)
        try:
            return r.json()
        except Exception:
            return {"raw": r.text, "http_status": r.status_code}
    except Exception as e:
        return {"error": str(e)}

def record_bet(issue: int, room_id: int, amount: float, resp: dict, algo_used: Optional[str] = None) -> dict:
    now = datetime.now(tz).strftime("%H:%M:%S")
    rec = {"issue": issue, "room": room_id, "amount": float(amount), "time": now, "resp": resp, "result": "Đang", "algo": algo_used, "delta": 0.0, "win_streak": win_streak, "lose_streak": lose_streak}
    bet_history.append(rec)
    return rec

def place_bet_async(issue: int, room_id: int, amount: float, algo_used: Optional[str] = None):
    def worker():
        time.sleep(random.uniform(0.02, 0.25))
        res = place_bet_http(issue, room_id, amount)
        rec = record_bet(issue, room_id, amount, res, algo_used=algo_used)
        if isinstance(res, dict) and (res.get("msg") == "ok" or res.get("code") == 0 or res.get("status") in ("ok", 1)):
            bet_sent_for_issue.add(issue)
    threading.Thread(target=worker, daemon=True).start()

def lock_prediction_if_needed(force: bool = False):
    global prediction_locked, predicted_room, ui_state, current_bet, _rounds_placed_since_skip, skip_next_round_flag, _skip_rounds_remaining, _skip_active_issue, algo7_skip_first_round
    
    if stop_flag:
        return
    if prediction_locked and not force:
        return
    if issue_id is None:
        return

    algo = settings.get("algo", "HOÀNG")
    try:
        chosen, algo_used = choose_room(algo)
    except Exception as e:
        log_debug(f"choose_room error: {e}")
        chosen, algo_used = choose_room("HOANG")
    
    predicted_room = chosen
    prediction_locked = True
    
    is_skipping = False
    
    
    if algo == "Theo sát thủ" and algo7_skip_first_round:
        is_skipping = True
        algo7_skip_first_round = False  
    elif _skip_rounds_remaining > 0:
        if _skip_active_issue != issue_id:
            _skip_rounds_remaining -= 1
            _skip_active_issue = issue_id
        is_skipping = True
    
    if is_skipping:
        ui_state = "SKIPPING"
        return
    
    ui_state = "PREDICTED"

    if run_mode == "AUTO" and not skip_next_round_flag:
        bld, _, _ = fetch_balances_3games(params={"userId": str(USER_ID)} if USER_ID else None)
        
        current_balance = current_usdt if ASSET_TYPE == "USDT" else current_build
        
        if current_balance is None:
            prediction_locked = False
            ui_state = "ANALYZING"
            return
        global current_bet

        if current_bet is None:
            current_bet = base_bet
            
        amt = 0.0
        
        if random_bet_enabled and algo in ["LUYỆN KHÍ", "TINH ANH", "Hoá Thần"]:
            max_bet_limit = current_balance or base_bet * 10 
            amt = random.uniform(base_bet, max_bet_limit)
            
            if amt > current_balance:
                amt = current_balance
            
        else:
            amt = float(current_bet)
            
        if current_balance is not None and amt > current_balance:
            amt = current_balance * 0.5
            log_debug(f"Bet amount {amt} adjusted to 50% of balance ({current_balance}) for safety.")
        
        amt = round(amt, 4) 
        
        if amt <= 0.0001: 
            prediction_locked = False
            ui_state = "ANALYZING"
            return
            
        place_bet_async(issue_id, predicted_room, amt, algo_used=algo_used)
        
        _rounds_placed_since_skip += 1
        if bet_rounds_before_skip > 0 and _rounds_placed_since_skip >= bet_rounds_before_skip:
            skip_next_round_flag = True
            _rounds_placed_since_skip = 0
            
    elif skip_next_round_flag:
        skip_next_round_flag = False
        ui_state = "SKIPPING"

def safe_send_enter_game(ws):
    if not ws:
        log_debug("safe_send_enter_game: ws None")
        return
    try:
        payload = {"msg_type": "handle_enter_game", "asset_type": ASSET_TYPE, "user_id": USER_ID, "user_secret_key": SECRET_KEY}
        ws.send(json.dumps(payload))
        log_debug("Sent enter_game")
    except Exception as e:
        log_debug(f"safe_send_enter_game err: {e}")

def _extract_issue_id(d: Dict[str, Any]) -> Optional[int]:
    if not isinstance(d, dict):
        return None
    possible = []
    for key in ("issue_id", "issueId", "issue", "id"):
        v = d.get(key)
        if v is not None:
            possible.append(v)
    if isinstance(d.get("data"), dict):
        for key in ("issue_id", "issueId", "issue", "id"):
            v = d["data"].get(key)
            if v is not None:
                possible.append(v)
    for p in possible:
        try:
            return int(p)
        except Exception:
            try:
                return int(str(p))
            except Exception:
                continue
    return None

def on_open(ws):
    _ws["ws"] = ws
    safe_send_enter_game(ws)

def _background_fetch_balance_after_result():
    try:
        fetch_balances_3games()
    except Exception:
        pass

def _mark_bet_result_from_issue(res_issue: Optional[int], krid: int):
    global current_bet, win_streak, lose_streak, max_win_streak, max_lose_streak
    global _skip_rounds_remaining, stop_flag, _skip_active_issue
    global algo7_last_kill 

    if res_issue is None:
        return

    algo7_last_kill = krid

    if res_issue not in bet_sent_for_issue:
        log_debug(f"_mark_bet_result_from_issue: skip issue {res_issue} (no bet placed)")
        return

    rec = next((b for b in reversed(bet_history) if b.get("issue") == res_issue), None)
    if rec is None:
        log_debug(f"_mark_bet_result_from_issue: no record found for issue {res_issue}, skip")
        return

    if rec.get("settled"):
        log_debug(f"_mark_bet_result_from_issue: issue {res_issue} already settled, skip")
        return

    try:
        placed_room = int(rec.get("room"))
        if placed_room != int(krid):
            rec["result"] = "Thắng"
            rec["settled"] = True
            current_bet = base_bet
            win_streak += 1
            lose_streak = 0
            if win_streak > max_win_streak:
                max_win_streak = win_streak
        else:
            rec["result"] = "Thua"
            rec["settled"] = True
            try:
                if random_bet_enabled and settings.get("algo") in ["SS++", "TINH ANH"]:
                    current_bet = base_bet 
                else:
                    old_bet = current_bet
                    current_bet = float(rec.get("amount")) * float(multiplier)
            except Exception as e:
                current_bet = base_bet
            lose_streak += 1
            win_streak = 0
            if lose_streak > max_lose_streak: 
                max_lose_streak = lose_streak 
            if pause_after_losses > 0:
                _skip_rounds_remaining = pause_after_losses
                _skip_active_issue = None
    except Exception as e:
        log_debug(f"_mark_bet_result_from_issue err: {e}")
    finally:
        try:
            bet_sent_for_issue.discard(res_issue)
        except Exception:
            pass

    try:
        update_formulas_after_result(predicted_room, krid, settings.get("algo", "NHẬP MA"))
    except Exception as e:
        log_debug(f"update_formulas_after_result err: {e}")

def on_message(ws, message):
    global issue_id, count_down, killed_room, round_index, ui_state, analysis_start_ts, issue_start_ts
    global prediction_locked, predicted_room, last_killed_room, last_msg_ts, current_bet
    global win_streak, lose_streak, max_win_streak, max_lose_streak, cumulative_profit, _skip_rounds_remaining, stop_flag, analysis_blur
    global algo5_last_random_time, algo5_current_target
    
    last_msg_ts = time.time()
    try:
        # Robust parsing using safe_json_loads
        data = safe_json_loads(message)

        # If message contains nested JSON in string under "data", merge it
        if isinstance(data, dict) and isinstance(data.get("data"), str):
            inner = safe_json_loads(data.get("data"))
            if isinstance(inner, dict):
                merged = dict(data)
                merged.update(inner)
                data = merged

        msg_type = data.get("msg_type") if isinstance(data, dict) else ""
        if msg_type is None:
            msg_type = ""
        msg_type = str(msg_type)
        new_issue = _extract_issue_id(data) if isinstance(data, dict) else None

        if msg_type == "notify_issue_stat" or "issue_stat" in msg_type:
            rooms = data.get("rooms") or []
            if not rooms and isinstance(data.get("data"), dict):
                rooms = data["data"].get("rooms", [])
            for rm in (rooms or []):
                try:
                    rid = int(rm.get("room_id") or rm.get("roomId") or rm.get("id"))
                except Exception:
                    continue
                players = int(rm.get("user_cnt") or rm.get("userCount") or 0) or 0
                bet = int(rm.get("total_bet_amount") or rm.get("totalBet") or rm.get("bet") or 0) or 0
                room_state[rid] = {"players": players, "bet": bet}
                room_stats[rid]["last_players"] = players
                room_stats[rid]["last_bet"] = bet
            if new_issue is not None and new_issue != issue_id:
                log_debug(f"New issue: {issue_id} -> {new_issue}")
                issue_id = new_issue
                issue_start_ts = time.time()
                round_index += 1
                killed_room = None
                prediction_locked = False
                predicted_room = None
                ui_state = "ANALYZING"
                analysis_start_ts = time.time()
                
                algo5_current_target = None
                algo5_last_random_time = 0.0

        elif msg_type == "notify_count_down" or "count_down" in msg_type:
            count_down = data.get("count_down") or data.get("countDown") or data.get("count") or count_down
            try:
                count_val = int(count_down)
            except Exception:
                count_val = None
                
            if count_val is not None:
                try:
                    algo = settings.get("algo", "HOÀNG")
                    lock_time = 5 if algo == "Hoá Thần" else 10

                    if algo == "Hoá Thần" and count_val > lock_time and not prediction_locked:
                        now = time.time()
                        if now - algo5_last_random_time > 0.4:
                            algo5_current_target = random.choice(ROOM_ORDER)
                            algo5_last_random_time = now
                            predicted_room = algo5_current_target

                    if count_val <= lock_time and not prediction_locked:
                        analysis_blur = False
                        lock_prediction_if_needed() 
                    elif count_val <= 45:
                        ui_state = "ANALYZING"
                        analysis_start_ts = time.time()
                        analysis_blur = True
                except Exception:
                    pass

        elif msg_type == "notify_result" or "result" in msg_type:
            kr = data.get("killed_room") if isinstance(data, dict) else None
            if kr is None and isinstance(data.get("data"), dict):
                kr = data["data"].get("killed_room") or data["data"].get("killed_room_id")
            if kr is not None:
                try:
                    krid = int(kr)
                except Exception:
                    krid = kr
                killed_room = krid
                last_killed_room = krid
                for rid in ROOM_ORDER:
                    if rid == krid:
                        room_stats[rid]["kills"] += 1
                        room_stats[rid]["last_kill_round"] = round_index
                    else:
                        room_stats[rid]["survives"] += 1

                res_issue = new_issue if new_issue is not None else issue_id
                _mark_bet_result_from_issue(res_issue, krid)
                threading.Thread(target=_background_fetch_balance_after_result, daemon=True).start()

            ui_state = "RESULT"

            def _check_stop_conditions():
                global stop_flag
                try:
                    current_balance = current_usdt if ASSET_TYPE == "USDT" else current_build
                    if current_balance is None:
                        return
                        
                    if stop_when_profit_reached and profit_target is not None and current_balance >= profit_target:
                        stop_flag = True
                        try:
                            wsobj = _ws.get("ws")
                            if wsobj:
                                wsobj.close()
                        except Exception:
                            pass
                    if stop_when_loss_reached and stop_loss_target is not None and current_balance <= stop_loss_target:
                        stop_flag = True
                        try:
                            wsobj = _ws.get("ws")
                            if wsobj:
                                wsobj.close()
                        except Exception:
                            pass
                except Exception:
                    pass
            threading.Timer(1.2, _check_stop_conditions).start()

    except Exception as e:
        log_debug(f"on_message err: {e}")

def on_close(ws, code, reason):
    log_debug(f"WS closed: {code} {reason}")

def on_error(ws, err):
    log_debug(f"WS error: {err}")

def start_ws():
    global stop_flag
    backoff = 0.6
    while not stop_flag:
        # Note: check_internet_connection was removed by request.
        try:
            ws_app = websocket.WebSocketApp(WS_URL, on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
            _ws["ws"] = ws_app
            ws_app.run_forever(ping_interval=12, ping_timeout=6)
        except Exception as e:
            log_debug(f"start_ws exception: {e}")
        t = min(backoff + random.random() * 0.5, 30)
        log_debug(f"Reconnect WS after {t}s")
        time.sleep(t)
        backoff = min(backoff * 1.5, 30)

def monitor_loop():
    global last_balance_fetch_ts, last_msg_ts, stop_flag
    while not stop_flag:
        # Note: check_internet_connection was removed by request.
        now = time.time()
        if now - last_balance_fetch_ts >= BALANCE_POLL_INTERVAL:
            last_balance_fetch_ts = now
            try:
                fetch_balances_3games(params={"userId": str(USER_ID)} if USER_ID else None)
            except Exception as e:
                log_debug(f"monitor fetch err: {e}")
        if now - last_msg_ts > 8:
            log_debug("No ws msg >8s, send enter_game")
            try:
                safe_send_enter_game(_ws.get("ws"))
            except Exception as e:
                log_debug(f"monitor send err: {e}")
        if now - last_msg_ts > 30:
            log_debug("No ws msg >30s, force reconnect")
            try:
                wsobj = _ws.get("ws")
                if wsobj:
                    try:
                        wsobj.close()
                    except Exception:
                        pass
            except Exception:
                pass
        time.sleep(0.6)

def get_progress_bar(current, total, length=20):
    if total <= 0:
        return f"[{' ' * length}]"
    filled = int((current / total) * length)
    bar = '█' * filled + '░' * (length - filled)
    return f"[{bar}]"

def format_number(num):
    if num is None:
        return "-"
    if isinstance(num, (int, float)):
        return f"{num:,.4f}"
    return str(num)

def display_status_header():
    b = format_number(current_build)
    u = format_number(current_usdt)
    x = format_number(current_world)
    
    pnl_val = cumulative_profit if cumulative_profit is not None else 0.0
    pnl_str = f"{pnl_val:+,.4f}"
    pnl_color = C.SUCCESS if pnl_val > 0 else (C.ERROR if pnl_val < 0 else C.WARNING)
    pnl_symbol = "↑" if pnl_val > 0 else ("↓" if pnl_val < 0 else "→")
    
    pnl_percent = ""
    current_asset_balance = current_usdt if ASSET_TYPE == "USDT" else current_build
    
    if starting_balance and starting_balance > 0 and current_asset_balance:
        percent = ((current_asset_balance - starting_balance) / starting_balance) * 100
        pnl_percent = f"({percent:+.2f}%)"
    
    algo_label = SELECTION_MODES.get(settings.get('algo'), settings.get('algo'))
    
    runtime_str = "-"
    if starting_balance is not None and last_balance_ts is not None:
        runtime = int(time.time() - last_balance_ts) if last_balance_ts else 0
        hours = runtime // 3600
        minutes = (runtime % 3600) // 60
        seconds = runtime % 60
        runtime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    total_bets = len([b for b in bet_history if b.get('result') in ('Thắng', 'Thua')])
    wins = len([b for b in bet_history if b.get('result') == 'Thắng'])
    win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
    
    print()
    print_line('═', 80, C.PRIMARY)
    
    print(f"{C.BOLD}{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.BOLD}{C.PRIMARY}║{C.RESET}  {C.GRAD1}🎮 VUA THOÁT HIỂM - HOANGTOOL{C.RESET}                    {C.MUTED}Phiên #{issue_id or '---'}{C.RESET}  {C.PRIMARY}║{C.RESET}")
    print(f"{C.BOLD}{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
    
    print_line('─', 80, C.MUTED)
    
    print(f"{C.INFO}┌─ 💰 TÀI KHOẢN{C.RESET}")
    print(f"{C.INFO}│{C.RESET}  {C.BOLD}BUILD:{C.RESET} {C.ACCENT}{b}{C.RESET}  {C.MUTED}│{C.RESET}  {C.BOLD}USDT:{C.RESET} {C.ACCENT}{u}{C.RESET}  {C.MUTED}│{C.RESET}  {C.BOLD}WORLD:{C.RESET} {C.ACCENT}{x}{C.RESET}")
    print(f"{C.INFO}└─{C.RESET} {C.BOLD}Lãi/Lỗ ({ASSET_TYPE}):{C.RESET} {pnl_color}{pnl_symbol} {C.BOLD}{pnl_str}{C.RESET} {pnl_color}{pnl_percent}{C.RESET}")
    
    print()
    
    print(f"{C.INFO}┌─ 📊 THỐNG KÊ PHIÊN{C.RESET}")
    print(f"{C.INFO}│{C.RESET}  {C.BOLD}Tổng ván:{C.RESET} {C.ACCENT}{len(bet_history)}{C.RESET}  {C.MUTED}│{C.RESET}  {C.SUCCESS}Thắng: {wins}{C.RESET}  {C.MUTED}│{C.RESET}  {C.ERROR}Thua: {total_bets - wins}{C.RESET}  {C.MUTED}│{C.RESET}  {C.WARNING}Tỷ lệ: {win_rate:.1f}%{C.RESET}")
    print(f"{C.INFO}│{C.RESET}  {C.SUCCESS}🔥 Chuỗi thắng:{C.RESET} {C.BOLD}{win_streak}{C.RESET} {C.MUTED}(Max: {max_win_streak}){C.RESET}  {C.MUTED}│{C.RESET}  {C.ERROR}❄️ Chuỗi thua:{C.RESET} {C.BOLD}{lose_streak}{C.RESET} {C.MUTED}(Max: {max_lose_streak}){C.RESET}")
    print(f"{C.INFO}└─{C.RESET} {C.BOLD}Thuật toán:{C.RESET} {C.ACCENT}{algo_label}{C.RESET}")
    
    print()
    
    next_bet = format_number(current_bet or base_bet)
    
    bet_mode = next_bet
    bet_color = C.WARNING
    if settings.get("algo") in ["NHẬP MA", "NHẬP MA", "Hoá Thần"] and random_bet_enabled:
        bet_mode = "NGẪU NHIÊN"
        bet_color = C.ORANGE
        
    print(f"{C.INFO}┌─ ⚙️ CẤU HÌNH{C.RESET}")
    print(f"{C.INFO}│{C.RESET}  {C.BOLD}Cược tiếp:{C.RESET} {bet_color}{C.BOLD}{bet_mode} {ASSET_TYPE}{C.RESET}  {C.MUTED}│{C.RESET}  {C.BOLD}Nhân (nếu thua):{C.RESET} {C.WARNING}x{multiplier}{C.RESET}")
    
    targets = []
    if stop_when_profit_reached and profit_target is not None:
        targets.append(f"{C.SUCCESS}🎯 Mục tiêu: {profit_target:.2f} {ASSET_TYPE}{C.RESET}")
    if stop_when_loss_reached and stop_loss_target is not None:
        targets.append(f"{C.ERROR}🛑 Cắt lỗ: {stop_loss_target:.2f} {ASSET_TYPE}{C.RESET}")
    if targets:
        print(f"{C.INFO}│{C.RESET}  {' │ '.join(targets)}")
    
    if _skip_rounds_remaining > 0:
        print(f"{C.INFO}│{C.RESET}  {C.WARNING}😴 Đang nghỉ: {_skip_rounds_remaining} ván{C.RESET}")
    elif settings.get("algo") == "Theo sát thủ" and algo7_skip_first_round:
        print(f"{C.INFO}│{C.RESET}  {C.MUTED}💤 Nghỉ ván đầu (TT7) để xác định sát thủ{C.RESET}")
    
    print(f"{C.INFO}└─{C.RESET} {C.MUTED}[{human_ts()}]{C.RESET}")
    
    print_line('═', 80, C.PRIMARY)

def display_game_status():
    print()
    
    if count_down is not None:
        try:
            cd = int(count_down)
            total_time = 60
            progress = get_progress_bar(total_time - cd, total_time, 40)
            color = C.SUCCESS if cd > 30 else (C.WARNING if cd > 10 else C.ERROR)
            print(f"{C.INFO}⏱️  {C.BOLD}THỜI GIAN:{C.RESET} {color}{progress}{C.RESET} {color}{C.BOLD}{cd}s{C.RESET}")
            print()
        except:
            pass
    
    if ui_state == "ANALYZING":
        print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
        
        if settings.get("algo") == "Hoá Thần" and predicted_room is not None:
            rand_room_name = ROOM_NAMES.get(predicted_room, f'Phòng {predicted_room}')
            print(f"{C.PRIMARY}║{C.RESET}  {C.ORANGE} {C.BOLD}ĐANG RANDOM: {rand_room_name:20}{C.RESET}                                {C.PRIMARY}║{C.RESET}")
        else:
            print(f"{C.PRIMARY}║{C.RESET}  {C.INFO}🔍 {C.BOLD}ĐANG PHÂN TÍCH DỮ LIỆU...{C.RESET}                                              {C.PRIMARY}║{C.RESET}")
            
        if last_killed_room:
            room_name = ROOM_NAMES.get(last_killed_room, f'Phòng {last_killed_room}')
            print(f"{C.PRIMARY}║{C.RESET}  {C.MUTED}☠️  Sát thủ ván trước: {C.ERROR}{room_name}{C.RESET}                                      {C.PRIMARY}║{C.RESET}")
        print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
    
    elif ui_state == "PREDICTED":
        room_name = ROOM_NAMES.get(predicted_room, f'Phòng {predicted_room}')
        
        bet_amt = format_number(current_bet or base_bet)
        
        bet_mode = bet_amt
        bet_color = C.WARNING
        if settings.get("algo") in ["LUYỆN KHÍ", "TRÚC CƠ", "Hoá Thần"] and random_bet_enabled:
            bet_mode = "NGẪU NHIÊN"
            bet_color = C.ORANGE
        
        print(f"{C.SUCCESS}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.SUCCESS}║{C.RESET}  {C.SUCCESS}🎯 {C.BOLD}DỰ ĐOÁN: {room_name:20}{C.RESET}                                       {C.SUCCESS}║{C.RESET}")
        print(f"{C.SUCCESS}║{C.RESET}  {C.INFO}💰 Đặt cược: {bet_color}{C.BOLD}{bet_mode} {ASSET_TYPE}{C.RESET}                                        {C.SUCCESS}║{C.RESET}")
        print(f"{C.SUCCESS}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")

    elif ui_state == "SKIPPING":
        print(f"{C.MUTED}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.MUTED}║{C.RESET}  {C.WARNING}⏸️  {C.BOLD}ĐANG BỎ QUA VÁN NÀY...{C.RESET} (Chống soi / TT7 Ván đầu / Nghỉ khi thua)  {C.MUTED}║{C.RESET}")
        if last_killed_room:
            room_name = ROOM_NAMES.get(last_killed_room, f'Phòng {last_killed_room}')
            print(f"{C.MUTED}║{C.RESET}  {C.MUTED}☠️  Sát thủ ván trước: {C.ERROR}{room_name}{C.RESET}                                      {C.MUTED}║{C.RESET}")
        print(f"{C.MUTED}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
    
    elif ui_state == "RESULT":
        if killed_room:
            room_name = ROOM_NAMES.get(killed_room, f'Phòng {killed_room}')
            last_result = bet_history[-1].get('result', '-') if bet_history and bet_history[-1].get('issue') == issue_id else '-'
            
            if 'Thắng' in str(last_result):
                print(f"{C.SUCCESS}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
                print(f"{C.SUCCESS}║{C.RESET}  {C.ERROR}☠️  {C.BOLD}SÁT THỦ: {room_name:20}{C.RESET}                                       {C.SUCCESS}║{C.RESET}")
                print(f"{C.SUCCESS}║{C.RESET}  {C.SUCCESS}✓ {C.BOLD}KẾT QUẢ: THẮNG!{C.RESET}                                                       {C.SUCCESS}║{C.RESET}")
                print(f"{C.SUCCESS}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
            elif 'Thua' in str(last_result):
                print(f"{C.ERROR}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
                print(f"{C.ERROR}║{C.RESET}  {C.ERROR}☠️  {C.BOLD}SÁT THỦ: {room_name:20}{C.RESET}                                       {C.ERROR}║{C.RESET}")
                print(f"{C.ERROR}║{C.RESET}  {C.ERROR}✖ {C.BOLD}KẾT QUẢ: THUA!{C.RESET}                                                        {C.ERROR}║{C.RESET}")
                print(f"{C.ERROR}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
            else:
                print(f"{C.WARNING}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
                print(f"{C.WARNING}║{C.RESET}  {C.ERROR}☠️  {C.BOLD}SÁT THỦ: {room_name:20}{C.RESET}                                       {C.WARNING}║{C.RESET}")
                print(f"{C.WARNING}║{C.RESET}  {C.MUTED}... KHÔNG CƯỢC VÁN NÀY ...{C.RESET}                                                {C.WARNING}║{C.RESET}")
                print(f"{C.WARNING}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
    
    else:
        print(f"{C.MUTED}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.MUTED}║{C.RESET}  {C.MUTED}⏳ CHỜ VÁN MỚI...{C.RESET}                                                          {C.MUTED}║{C.RESET}")
        print(f"{C.MUTED}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")

def display_room_status():
    print()
    print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}🚪 TRẠNG THÁI CÁC PHÒNG{C.RESET}                                                      {C.PRIMARY}║{C.RESET}")
    print(f"{C.PRIMARY}╠══════════════════════════════════════════════════════════════════════════════╣{C.RESET}")
    
    for i, r in enumerate(ROOM_ORDER):
        st = room_state.get(r, {})
        stats = room_stats.get(r, {})
        players = st.get("players", 0)
        bet_val = st.get('bet', 0) or 0
        
        room_name = ROOM_NAMES.get(r, f"Phòng {r}")
        
        max_players = max([room_state.get(x, {}).get("players", 0) for x in ROOM_ORDER] + [1])
        player_bar = get_progress_bar(players, max_players, 15)
        
        status_icons = []
        status_color = C.MUTED
        
        if killed_room is not None and int(r) == int(killed_room):
            status_icons.append(f"{C.ERROR}☠ SÁT THỦ{C.RESET}")
            status_color = C.ERROR
        
        if prediction_locked and predicted_room is not None and int(r) == int(predicted_room):
            if settings.get("algo") == "Hoá Thần":
                 status_icons.append(f"{C.ORANGE}✓ CHỐT{C.RESET}")
                 status_color = C.ORANGE
            else:
                status_icons.append(f"{C.SUCCESS}✓ CHỐT{C.RESET}")
                status_color = C.SUCCESS
        elif not prediction_locked and settings.get("algo") == "Hoá Thần" and predicted_room is not None and int(r) == int(predicted_room):
            status_icons.append(f"{C.ORANGE} RANDOM{C.RESET}")
            status_color = C.ORANGE
        
        
        kills = stats.get("kills", 0)
        survives = stats.get("survives", 0)
        total_rounds = kills + survives
        kill_rate = (kills / total_rounds * 100) if total_rounds > 0 else 0
        
        status_str = " ".join(status_icons) if status_icons else f"{C.MUTED}━{C.RESET}"
        
        bet_str = f"{bet_val:,}" if bet_val < 10000 else f"{bet_val/1000:.1f}K"
        
        print(f"{C.PRIMARY}║{C.RESET} {status_color}[{r}]{C.RESET} {C.ACCENT}{room_name:18}{C.RESET} {C.INFO}{player_bar}{C.RESET} {C.INFO}{players:2}👤{C.RESET} {C.WARNING}{bet_str:>7}{C.RESET} {status_str:20} {C.PRIMARY}║{C.RESET}")
    
    print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")

def display_recent_bets():
    print()
    print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}📜 LỊCH SỬ 5 CƯỢC GẦN NHẤT ({ASSET_TYPE}){C.RESET}                                      {C.PRIMARY}║{C.RESET}")
    print(f"{C.PRIMARY}╠══════════════════════════════════════════════════════════════════════════════╣{C.RESET}")
    
    last5 = list(bet_history)[-5:]
    if not last5:
        print(f"{C.PRIMARY}║{C.RESET}  {C.MUTED}Chưa có lịch sử cược{C.RESET}                                                        {C.PRIMARY}║{C.RESET}")
    else:
        for b in reversed(last5):
            issue_num = b.get('issue', '-')
            room_num = b.get('room', '-')
            room_name = ROOM_NAMES.get(room_num, f"Phòng {room_num}")
            amt = b.get('amount', 0)
            res = str(b.get('result', '-'))
            algo = str(b.get('algo', '-'))[:10]
            
            if res.lower().startswith('thắng') or res.lower().startswith('win'):
                res_color = C.SUCCESS
                res_icon = "✓"
                res_text = "THẮNG"
            elif res.lower().startswith('thua') or res.lower().startswith('lose'):
                res_color = C.ERROR
                res_icon = "✖"
                res_text = "THUA "
            else:
                res_color = C.WARNING
                res_icon = "⏳"
                res_text = "ĐANG"
            
            print(f"{C.PRIMARY}║{C.RESET} {C.MUTED}#{issue_num:<6}{C.RESET} {C.ACCENT}{room_name:18}{C.RESET} {C.INFO}{amt:>8,.2f}{C.RESET} {res_color}{res_icon} {res_text}{C.RESET} {C.MUTED}{algo:>10}{C.RESET} {C.PRIMARY}║{C.RESET}")
    
    print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")

def display_status_loop():
    last_update = 0
    frame = 0
    
    while not stop_flag:
        now = time.time()
        
        if now - last_update >= 0.2:
            os.system("cls" if os.name == "nt" else "clear")
            
            display_status_header()
            display_game_status()
            display_room_status()
            display_recent_bets()
            
            print()
            print_line('═', 80, C.MUTED)
            
            frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            spinner = frames[frame % len(frames)]
            
            net_status = f"{C.SUCCESS}✓ ONLINE{C.RESET}" if check_internet_connection(timeout=0.5) else f"{C.ERROR}✖ OFFLINE{C.RESET}"
            
            print(f"{C.MUTED}  {spinner} Đang chạy...  {C.PRIMARY}│{C.RESET}  {C.MUTED}Nhấn {C.WARNING}Ctrl+C{C.MUTED} để dừng{C.RESET} {C.PRIMARY}│{C.RESET} {net_status}")
            print_line('═', 80, C.MUTED)
            
            last_update = now
            frame += 1
        
        time.sleep(0.01) 

def prompt_settings():
    global base_bet, multiplier, run_mode, bet_rounds_before_skip, current_bet, pause_after_losses, profit_target, stop_when_profit_reached, stop_loss_target, stop_when_loss_reached, settings, random_bet_enabled, algo7_skip_first_round
    
    os.system("cls" if os.name == "nt" else "clear")
    print()
    print_line('═', 80, C.PRIMARY)
    print(f"{C.BOLD}{C.GRAD1}                    ⚙️  CẤU HÌNH TOOL VTH{C.RESET}")
    print_line('═', 80, C.PRIMARY)
    print()
    
    print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}CHỌN THUẬT TOÁN{C.RESET}                                                   {C.PRIMARY}║{C.RESET}")
    print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
    print()
    
    algos = [
        ("1", "LUYỆN KHÍ", "CHO MẤY THẰNG ÍT BUILD", C.INFO),
        ("2", "TRÚC CƠ", "BUILD VỪA", C.SUCCESS),
        ("3", "TINH ANH", "build nhiều", C.WARNING),
        ("4", "Đỉnh cấp", "99% con bạc dừng lại trước khi thắng lớn", C.ERROR),
        ("5", "Hoá thần", "len cơn thiếu build ", C.ORANGE),
        ("6", "NHẬP MA", "RƠI VÀO MA ĐẠO", C.ACCENT),
        ("7", "NHẬP MÔN", "BOOS", C.SECONDARY),
        ("8", SPECIAL_MODE_KEY, f"Áp dụng cho phòng extern {SPECIAL_EXTERNAL_ROOM_ID}", C.ERROR)
    ]
    
    for num, name, desc, color in algos:
        if num == "5":
            print(f"{C.ORANGE}[{num}]{C.RESET} {C.ORANGE}{name:16}{C.RESET} {C.MUTED}━ {desc}{C.RESET}")
        else:
            print(f"{color}[{num}]{C.RESET} {C.ACCENT}{name:16}{C.RESET} {C.MUTED}━ {desc}{C.RESET}")
    print()
    
    tt5_choice_color = C.ORANGE
    
    alg = input(f"{C.PRIMARY}➜ {C.BOLD}Chọn thuật toán (1-8, mặc định 1):{C.RESET} {tt5_choice_color}").strip() or "1"
    
    try:
        alg_map = {"1": "LUYỆN KHÍ", "2": "TRÚC CƠ", "3": "TINH ANH", "4": "Đỉnh cấp", "5": "Hoá Thần", "6": "NHẬP MA", "7": "NHẬP MÔN", "8": SPECIAL_MODE_KEY}
        settings["algo"] = alg_map.get(alg, "HOÀNG")
        print(f"    {C.SUCCESS}✓ Đã chọn: {settings['algo']}{C.RESET}")
    except Exception:
        settings["algo"] = "HOÀNG"
        print(f"    {C.WARNING}⚠ Dùng mặc định: HOÀNG {C.RESET}")
    
    try:
        _init_formulas(settings["algo"])
    except Exception:
        pass
    print()
    
    global ASSET_TYPE 
    print()
    print_line('─', 80, C.MUTED)
    print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}CHỌN LOẠI TIỀN CƯỢC{C.RESET}                                              {C.PRIMARY}║{C.RESET}")
    print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
    print()
    print(f"{C.PRIMARY}[1] Cược bằng {C.ACCENT}BUILD{C.RESET} (Mặc định)")
    print(f"{C.PRIMARY}[2] Cược bằng {C.SUCCESS}USDT{C.RESET}")
    print()
    asset_choice = input(f"{C.PRIMARY}➜ {C.BOLD}Lựa chọn (1-2, mặc định 1):{C.RESET} {C.SUCCESS}").strip() or "1"
    if asset_choice == "2":
        ASSET_TYPE = "USDT"
        print(f"    {C.SUCCESS}✓ Đã chọn cược bằng USDT{C.RESET}")
    else:
        ASSET_TYPE = "BUILD"
        print(f"    {C.SUCCESS}✓ Đã chọn cược bằng BUILD{C.RESET}")
    print()
    
    
    if settings.get("algo") == "Hoá Thần":
        random_bet_enabled = True
        bet_rounds_before_skip = 5 
        multiplier = 2.0 
        base_bet = 1.0
        current_bet = base_bet
        
        asset_balance = current_usdt if ASSET_TYPE == "USDT" else current_build
        
        print(f"{C.ORANGE}➜ {C.BOLD}CẤU HÌNH MẶC ĐỊNH TT5:{C.RESET}")
        print(f"{C.ORANGE}  ✓ {C.RESET}Cược ngẫu nhiên (tối đa {asset_balance} {ASSET_TYPE}, có lớn có nhỏ){C.RESET}")
        print(f"{C.ORANGE}  ✓ {C.RESET}Nghỉ 1 phiên sau mỗi 5 phiên{C.RESET}")
        print(f"{C.ORANGE}  ✓ {C.RESET}Thua: x2 hệ số nhân{C.RESET}")
        print_line('═', 80, C.ORANGE)
        
    else:
        print_line('─', 80, C.MUTED)
        
        if settings.get("algo") == "Theo sát thủ":
             algo7_skip_first_round = True
             print(f"{C.ACCENT}➜ {C.BOLD}LƯU Ý TT7:{C.RESET} {C.ACCENT}TT7 sẽ nghỉ ván đầu để xác định sát thủ.{C.RESET}")
             print()

        print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}📌 CẤU HÌNH ĐẶT CƯỢC{C.RESET}                                                 {C.PRIMARY}║{C.RESET}")
        print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
        print()
        
        base = input(f"{C.PRIMARY}[1] {C.BOLD}Số {ASSET_TYPE} đặt mỗi ván:{C.RESET} {C.SUCCESS}").strip() or "1"
        try:
            base_bet = float(base)
            print(f"    {C.SUCCESS}✓ Đã đặt: {base_bet} {ASSET_TYPE}{C.RESET}")
        except Exception:
            base_bet = 1.0
            print(f"    {C.WARNING}⚠ Dùng mặc định: 1 {ASSET_TYPE}{C.RESET}")
        print()
        
        m = input(f"{C.PRIMARY}[2] {C.BOLD}Số nhân sau khi thua (ví dụ: 2):{C.RESET} {C.SUCCESS}").strip() or "2"
        try:
            multiplier = float(m)
            print(f"    {C.SUCCESS}✓ Đã đặt: x{multiplier}{C.RESET}")
        except Exception:
            multiplier = 2.0
            print(f"    {C.WARNING}⚠ Dùng mặc định: x2{C.RESET}")
        current_bet = base_bet
        print()
        
        print_line('─', 80, C.MUTED)
        print()
        
        if settings.get("algo") in ["LUYỆN KHÍ", "TINH ANH"]:
            print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
            print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}🎲 CƯỢC NGẪU NHIÊN (Chỉ Đỉnh cấp++, TINH ANH){C.RESET}                      {C.PRIMARY}║{C.RESET}")
            print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
            print()
            ans = input(f"{C.WARNING}Có cược ngẫu nhiên ko? Tool cược hết đéo chịu trách nhiệm (y/n):{C.RESET} ").strip().lower() or 'n'
            if ans == 'y':
                random_bet_enabled = True
                print(f"{C.SUCCESS}✓ Đã bật cược ngẫu nhiên{C.RESET}")
                
                print_line('═', 80, C.PRIMARY)
                print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
                print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}🎲 HỎI LẠI LẦN CUỐI{C.RESET}               {C.PRIMARY}║{C.RESET}")
                print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
                print()
                ans_final = input(f"{C.WARNING}Tool nó tất tay mà mất đéo chịu trách nhiệm đâu đấy (y/n):{C.RESET} ").strip().lower() or 'n'
                if ans_final != 'y':
                    random_bet_enabled = False
                    print(f"{C.MUTED}○ Đã tắt cược ngẫu nhiên{C.RESET}")
                
            else:
                random_bet_enabled = False
                print(f"{C.MUTED}○ Đã tắt cược ngẫu nhiên{C.RESET}")
            print_line('═', 80, C.PRIMARY)
        else:
            random_bet_enabled = False 

        
        print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}⚡ CẤU HÌNH NÂNG CAO{C.RESET}                                                  {C.PRIMARY}║{C.RESET}")
        print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
        print()
        
        s = input(f"{C.PRIMARY}[3] {C.BOLD}Chống soi - Sau bao nhiêu ván thì nghỉ 1 ván (0=tắt):{C.RESET} {C.SUCCESS}").strip() or "0"
        try:
            bet_rounds_before_skip = int(s)
            if bet_rounds_before_skip > 0:
                print(f"    {C.SUCCESS}✓ Sẽ nghỉ sau mỗi {bet_rounds_before_skip} ván{C.RESET}")
            else:
                print(f"    {C.MUTED}○ Tắt chế độ chống soi{C.RESET}")
        except Exception:
            bet_rounds_before_skip = 0
            print(f"    {C.MUTED}○ Tắt chế độ chống soi{C.RESET}")
        print()
        
        pl = input(f"{C.PRIMARY}[4] {C.BOLD}Nếu thua thì nghỉ bao nhiêu ván (0=tắt):{C.RESET} {C.SUCCESS}").strip() or "0"
        try:
            pause_after_losses = int(pl)
            if pause_after_losses > 0:
                print(f"    {C.SUCCESS}✓ Sẽ nghỉ {pause_after_losses} ván sau mỗi lần thua{C.RESET}")
            else:
                print(f"    {C.MUTED}○ Không nghỉ khi thua{C.RESET}")
        except Exception:
            pause_after_losses = 0
            print(f"    {C.MUTED}○ Không nghỉ khi thua{C.RESET}")
        print()
        
        print_line('─', 80, C.MUTED)
        print()
    
    print(f"{C.PRIMARY}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
    print(f"{C.PRIMARY}║{C.RESET} {C.BOLD}🎯 MỤC TIÊU & GIỚI HẠN{C.RESET}                                               {C.PRIMARY}║{C.RESET}")
    print(f"{C.PRIMARY}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
    print()
    
    pt = input(f"{C.PRIMARY}[5] {C.BOLD}Mục tiêu lãi ({ASSET_TYPE}, Enter=bỏ qua):{C.RESET} {C.SUCCESS}").strip()
    try:
        if pt and pt.strip() != "":
            profit_target = float(pt)
            stop_when_profit_reached = True
            print(f"    {C.SUCCESS}✓ Sẽ dừng khi đạt {profit_target} {ASSET_TYPE}{C.RESET}")
        else:
            profit_target = None
            stop_when_profit_reached = False
            print(f"    {C.MUTED}○ Không giới hạn mục tiêu{C.RESET}")
    except Exception:
        profit_target = None
        stop_when_profit_reached = False
        print(f"    {C.MUTED}○ Không giới hạn mục tiêu{C.RESET}")
    print()
    
    sl = input(f"{C.PRIMARY}[6] {C.BOLD}Cắt lỗ tại ({ASSET_TYPE}, Enter=bỏ qua):{C.RESET} {C.SUCCESS}").strip()
    try:
        if sl and sl.strip() != "":
            stop_loss_target = float(sl)
            stop_when_loss_reached = True
            print(f"    {C.ERROR}✓ Sẽ dừng khi còn {stop_loss_target} {ASSET_TYPE}{C.RESET}")
        else:
            stop_loss_target = None
            stop_when_loss_reached = False
            print(f"    {C.MUTED}○ Không cắt lỗ{C.RESET}")
    except Exception:
        stop_loss_target = None
        stop_when_loss_reached = False
        print(f"    {C.MUTED}○ Không cắt lỗ{C.RESET}")
    print()
    
    print_line('═', 80, C.SUCCESS)
    print()
    print(f"{C.SUCCESS}{C.BOLD}✓ ĐÃ CẤU HÌNH XONG!{C.RESET}")
    print()
    
    input(f"{C.PRIMARY}➜ {C.BOLD}Nhấn ENTER để bắt đầu...{C.RESET} {C.SUCCESS}")
    run_mode = "AUTO"

def start_threads():
    threading.Thread(target=start_ws, daemon=True).start()
    threading.Thread(target=monitor_loop, daemon=True).start()

def parse_login():
    global USER_ID, SECRET_KEY
    LINK_FILE = 'Es_link.json'
    saved_link = None
    link = None

    os.system("cls" if os.name == "nt" else "clear")
    print()
    print_line('═', 80, C.PRIMARY)
    print(f"{C.BOLD}{C.GRAD1}                    🔐 ĐĂNG NHẬP VÀO HỆ THỐNG{C.RESET}")
    print_line('═', 80, C.PRIMARY)
    print()
    
    if os.path.exists(LINK_FILE):
        try:
            with open(LINK_FILE, 'r') as f:
                data = json.load(f)
                saved_link = data.get('link')
        except Exception:
            pass

    use_saved = False
    if saved_link:
        print(f"{C.INFO}Tìm thấy link đã lưu: {C.MUTED}{saved_link[:50]}...{C.RESET}")
        q = input(f"{C.WARNING}Sử dụng lại link này không? (y/n): {C.RESET}").strip().lower()
        if q == 'y':
            link = saved_link
            use_saved = True

    if not use_saved:
        print(f"{C.INFO}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.INFO}║{C.RESET} {C.BOLD}📌 HƯỚNG DẪN LẤY LINK:{C.RESET}                                                        {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}                                                                              {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}  {C.MUTED}1.{C.RESET} Truy cập {C.ACCENT}xworld.info{C.RESET}                                                  {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}  {C.MUTED}2.{C.RESET} Tìm và vào trò chơi {C.SUCCESS}Vua Thoát Hiểm{C.RESET}                                     {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}  {C.MUTED}3.{C.RESET} Nhấn vào {C.WARNING}CHƠI NGAY{C.RESET}                                                       {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}  {C.MUTED}4.{C.RESET} Sao chép {C.ACCENT}LINK{C.RESET} trên thanh địa chỉ trình duyệt                             {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}                                                                              {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}  {C.WARNING}⚠️  LƯU Ý: Phải dùng trình duyệt web (Chrome, Edge, Safari, Firefox){C.RESET}       {C.INFO}║{C.RESET}")
        print(f"{C.INFO}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
        print()
        
        link = input(f"{C.PRIMARY}➜ {C.BOLD}Dán link vào đây:{C.RESET} {C.SUCCESS}").strip()
        print()
    
    if not link:
        print(f"{C.ERROR}✖ Bạn chưa nhập link. Tool sẽ thoát.{C.RESET}")
        time.sleep(2)
        sys.exit(1)
    
    try:
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        if 'userId' in params:
            USER_ID = int(params.get('userId')[0])
        SECRET_KEY = params.get('secretKey', [None])[0]
        
        if not USER_ID or not SECRET_KEY:
            raise ValueError("Link thiếu userId hoặc secretKey")
            
        print(f"{C.SUCCESS}✓ Đăng nhập thành công!{C.RESET}")
        print(f"{C.INFO}  User ID: {C.ACCENT}{USER_ID}{C.RESET}")
        print()
        
        if not use_saved:
            s = input(f"{C.INFO}Bạn có muốn lưu link này cho lần sau không? (y/n): {C.RESET}").strip().lower()
            if s == 'y':
                with open(LINK_FILE, 'w') as f:
                    json.dump({'link': link}, f)
                print(f"{C.SUCCESS}✓ Đã lưu link!{C.RESET}")
        
        time.sleep(1)
        
    except Exception as e:
        print(f"{C.ERROR}✖ Link không hợp lệ hoặc sai định dạng!{C.RESET}")
        print(f"{C.MUTED}  Lỗi: {e}{C.RESET}")
        print()
        log_debug(f"parse_login err: {e}")
        time.sleep(2)
        sys.exit(1)

def main_game():
    try:
        main()
    except Exception as e:
        print(f"{C.ERROR}Lỗi nghiêm trọng trong quá trình kiểm tra key: {e}{C.RESET}")
        sys.exit(1)
    
    parse_login()
    
    os.system("cls" if os.name == "nt" else "clear")
    print()
    print_line('═', 80, C.PRIMARY)
    print(f"{C.BOLD}{C.GRAD1}                    ⚡ ĐANG TẢI DỮ LIỆU...{C.RESET}")
    print_line('═', 80, C.PRIMARY)
    print()
    
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    for i in range(10): 
        sys.stdout.write(f"\r{C.INFO}  {frames[i % len(frames)]} Đang kết nối với server...{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
    print()
    
    print(f"\n{C.INFO}💰 Đang lấy số dư tài khoản...{C.RESET}")
    try:
        fetch_balances_3games(params={"userId": str(USER_ID)} if USER_ID else None)
        if current_build is not None or current_usdt is not None or current_world is not None:
            print(f"{C.SUCCESS}✓ Đã lấy số dư:{C.RESET}")
            if current_build is not None:
                print(f"    {C.ACCENT}BUILD: {C.BOLD}{current_build:,.4f}{C.RESET}")
            if current_usdt is not None:
                print(f"    {C.ACCENT}USDT:  {C.BOLD}{current_usdt:,.4f}{C.RESET}")
            if current_world is not None:
                print(f"    {C.ACCENT}WORLD: {C.BOLD}{current_world:,.4f}{C.RESET}")
        else:
            print(f"{C.WARNING}⚠ Không lấy được số dư{C.RESET}")
    except Exception as e:
        print(f"{C.WARNING}⚠ Lỗi: {e}{C.RESET}")
    
    time.sleep(1)
    
    prompt_settings()
    
    apply_theme()
    
    show_main_banner() 
    
    os.system("cls" if os.name == "nt" else "clear")
    print()
    print_line('═', 80, C.SUCCESS)
    print(f"{C.BOLD}{C.SUCCESS}                    🚀 ĐANG KHỞI ĐỘNG TOOL...{C.RESET}")
    print_line('═', 80, C.SUCCESS)
    print()
    
    print(f"{C.INFO}[1/3]{C.RESET} Khởi tạo WebSocket...")
    time.sleep(0.5)
    print(f"{C.SUCCESS}      ✓ Hoàn thành{C.RESET}")
    
    print(f"{C.INFO}[2/3]{C.RESET} Kết nối với server...")
    start_threads()
    time.sleep(1)
    print(f"{C.SUCCESS}      ✓ Hoàn thành{C.RESET}")
    
    print(f"{C.INFO}[3/3]{C.RESET} Khởi động giao diện...")
    time.sleep(0.5)
    print(f"{C.SUCCESS}      ✓ Hoàn thành{C.RESET}")
    
    print()
    print(f"{C.SUCCESS}✓ Tool đã sẵn sàng!{C.RESET}")
    time.sleep(2)
    
    try:
        display_status_loop()
    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        print()
        print_line('═', 80, C.PRIMARY)
        print(f"{C.BOLD}{C.PRIMARY}                    👋 CẢM ƠN ĐÃ SỬ DỤNG TOOL!{C.RESET}")
        print_line('═', 80, C.PRIMARY)
        print()
        
        print(f"{C.INFO}╔══════════════════════════════════════════════════════════════════════════════╗{C.RESET}")
        print(f"{C.INFO}║{C.RESET} {C.BOLD}THỐNG KÊ PHIÊN CHƠI{C.RESET}                                                       {C.INFO}║{C.RESET}")
        print(f"{C.INFO}╠══════════════════════════════════════════════════════════════════════════════╣{C.RESET}")
        
        total = len(bet_history)
        wins = len([b for b in bet_history if b.get('result') == 'Thắng'])
        losses = len([b for b in bet_history if b.get('result') == 'Thua'])
        win_rate = (wins / total * 100) if total > 0 else 0
        
        print(f"{C.INFO}║{C.RESET}  {C.BOLD}Tổng số ván:{C.RESET} {C.ACCENT}{total}{C.RESET}                                                          {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}  {C.SUCCESS}Thắng: {wins}{C.RESET} {C.MUTED}│{C.RESET} {C.ERROR}Thua: {losses}{C.RESET} {C.MUTED}│{C.RESET} {C.WARNING}Tỷ lệ: {win_rate:.1f}%{C.RESET}                                  {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}  {C.SUCCESS}Chuỗi thắng tốt nhất: {C.BOLD}{max_win_streak}{C.RESET}                                              {C.INFO}║{C.RESET}")
        print(f"{C.INFO}║{C.RESET}  {C.ERROR}Chuỗi thua dài nhất: {C.BOLD}{max_lose_streak}{C.RESET}                                               {C.INFO}║{C.RESET}")
        
        pnl_color = C.SUCCESS if cumulative_profit > 0 else (C.ERROR if cumulative_profit < 0 else C.WARNING)
        pnl_symbol = "↑" if cumulative_profit > 0 else ("↓" if cumulative_profit < 0 else "→")
        print(f"{C.INFO}║{C.RESET}  {C.BOLD}Tổng lãi/lỗ ({ASSET_TYPE}):{C.RESET} {pnl_color}{pnl_symbol} {C.BOLD}{cumulative_profit:+,.4f}{C.RESET}                                  {C.INFO}║{C.RESET}")
        
        print(f"{C.INFO}╚══════════════════════════════════════════════════════════════════════════════╝{C.RESET}")
        print()
        print(f"{C.MUTED}Tool được phát triển bởi {C.ACCENT}/DUY HOÀNG TU TIÊN{C.RESET}")
        print()
        try:
            sys.exit(0)
        except SystemExit:
            raise

if __name__ == "__main__":
    main_game()