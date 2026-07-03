from curl_cffi import requests as cffi_requests
import requests
import time
import json
import base64
import os
import sys
import random
import string
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Email.buatakun import generate_email, check_inbox, extract_otp

try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5, AES
    from Crypto.Util.Padding import pad
except ImportError:
    print("\n[!] Error: Library 'pycryptodome' belum terinstall.")
    print("[!] Jalankan perintah ini di terminal: pip install pycryptodome\n")
    sys.exit()

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

api_key = "YOUR_CAPSOLVER_API_KEY"
site_key = "6LeBM0ocAAAAAEwYcFUjtxpVbs-0rnbSVXBBXmh4"
site_url = "https://global.account.xiaomi.com/fe/service/register?_locale=id_ID&_uRegion=ID"

PUBLIC_KEY_EUI = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCYEVrK/4Mahiv0pUJgTybx4J9P
5dUT/Y0PuwMbk+gMU+jrZnBiXGv6/hCH1avIhoBcE535F8nJQQN3UavZdFkYidso
XuEnat3+eVTp3FslyhRwIBDF09v4vDhRtxFOT+R7uH7h/mzmyA2/+lfIMWGIrffX
prYizbV76+YQKhoqFQIDAQAB
-----END PUBLIC KEY-----"""

def generate_device_fingerprint():
    return hashlib.md5(str(time.time() + random.random()).encode()).hexdigest()

def encrypt_eui(data_dict):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    aes_key_str = ''.join(random.choice(chars) for _ in range(16))
    key_b64 = base64.b64encode(aes_key_str.encode()).decode()
    rsa_key = RSA.import_key(PUBLIC_KEY_EUI)
    rsa_cipher = PKCS1_v1_5.new(rsa_key)
    rsa_encrypted = rsa_cipher.encrypt(key_b64.encode())
    eui_prefix = base64.b64encode(rsa_encrypted).decode()
    fields = ",".join(data_dict.keys())
    eui_suffix = base64.b64encode(fields.encode()).decode()
    eui_header = f"{eui_prefix}.{eui_suffix}"
    iv = b"0102030405060708"
    encrypted_params = {}
    for k, v in data_dict.items():
        cipher = AES.new(aes_key_str.encode(), AES.MODE_CBC, iv)
        ct_bytes = cipher.encrypt(pad(v.encode(), AES.block_size))
        encrypted_params[k] = base64.b64encode(ct_bytes).decode()
    return eui_header, encrypted_params

import threading
file_lock = threading.Lock()

def save_new_cookie(cookie_dict):
    cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Cookies', 'cookies.json')
    cookie_obj = {str(k): str(v) for k, v in cookie_dict.items()}
    with file_lock:
        data = []
        if os.path.exists(cookie_path):
            try:
                with open(cookie_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []
        
        data.append({"cookie": cookie_obj})
        
        with open(cookie_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    print(f"\n[+] Akun baru berhasil dicatat di Cookies/cookies.json")

def solve_image_captcha(session, captcha_url):
    import threading
    thread_id = threading.get_ident()
    captcha_path = f"Register/captcha_{thread_id}.jpg"
    
    try:
        print(f"[{thread_id}] [*] Mendownload gambar captcha...")
        if captcha_url.startswith('/'):
            captcha_url = 'https://global.account.xiaomi.com' + captcha_url
            
        img_resp = session.get(captcha_url, timeout=30)
        if len(img_resp.content) < 100:
            print(f"[{thread_id}] [-] Gambar captcha terlalu kecil atau gagal download.")
            return None
            
        with open(captcha_path, "wb") as f:
            f.write(img_resp.content)
        print(f"[{thread_id}] [*] Gambar captcha disimpan ke {captcha_path} ({len(img_resp.content)} bytes)")
            
        img_base64 = base64.b64encode(img_resp.content).decode()
        
        print(f"[{thread_id}] [*] Menyelesaikan captcha gambar via CapSolver...", flush=True)
        payload = {
            "clientKey": api_key,
            "task": {
                "type": "ImageToTextTask",
                "body": img_base64,
                "module": "common"
            }
        }
        
        res = requests.post("https://api.capsolver.com/createTask", json=payload, timeout=30)
        create_resp = res.json()
        print(f"[DEBUG] CapSolver create response: {json.dumps(create_resp)}", flush=True)
        
        if create_resp.get("status") == "ready":
            text = create_resp.get("solution", {}).get("text")
            print(f"[+] Captcha gambar terpecahkan (langsung): {text}", flush=True)
            return text
            
        task_id = create_resp.get("taskId")
        if not task_id:
            print(f"[-] Gagal membuat task captcha gambar: {create_resp}", flush=True)
            return None
            
        print(f"[*] Task created: {task_id}, menunggu hasil...", flush=True)
        time.sleep(1)
        
        while True:
            status_res = requests.post("https://api.capsolver.com/getTaskResult", json={
                "clientKey": api_key,
                "taskId": task_id
            }, timeout=30)
            resp = status_res.json()
            print(f"[DEBUG] CapSolver task result: {json.dumps(resp)}", flush=True)
            status = resp.get("status")
            
            if status == "ready":
                text = resp.get("solution", {}).get("text")
                print(f"[+] Captcha gambar terpecahkan: {text}", flush=True)
                return text
            if status == "failed":
                print(f"[-] CapSolver gagal: {resp.get('errorDescription')}", flush=True)
                return None
            if resp.get("errorId") and resp.get("errorId") != 0:
                print(f"[-] CapSolver error ({resp.get('errorCode')}): {resp.get('errorDescription')}", flush=True)
                return None
                
            print(f"[*] Menunggu captcha (status: {status})...", flush=True)
            time.sleep(1)
    except Exception as e:
        print(f"[-] Error solve_image_captcha: {e}")
        return None

def init_mistore_session(session, user_agent, reg_data):
    print("[*] Melakukan sinkronisasi akun (Ritual Login)...")
    try:
        headers = {'User-Agent': user_agent}
        sync_url = reg_data.get('user_synced_url')
        if sync_url:
            print("[*] Menjalankan User Sync...")
            session.get(sync_url, headers=headers, timeout=30)

        login_url = reg_data.get('location')
        if not login_url:
            login_url = "https://account.xiaomi.com/pass/serviceLogin?sid=mi_eshop_id&_locale=id_ID"
        
        print(f"[*] Mengambil tiket Mi Store via: {login_url}")
        session.get(login_url, headers=headers, timeout=30)

        session.get("https://www.mi.co.id/id/", headers=headers, timeout=30)

        check = session.get("https://go.buy.mi.co.id/id/app/userprofile", headers=headers, timeout=30)
        if check.json().get('data', {}).get('profile'):
            print("[+] Ritual Selesai! Sesi Mi Store sekarang AKTIF.")
            return True
        else:
            print("[-] Ritual Selesai, tapi sesi belum aktif (profile masih null).")
            return False
            
    except Exception as e:
        print(f"[-] Gagal melakukan ritual: {e}")
        return False

def verify_otp(session, email, password, clean_referer, eui_header, fingerprint, user_agent):
    print("[*] Menunggu email masuk untuk mengambil OTP...")
    
    headers = {
        'authority': 'global.account.xiaomi.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://global.account.xiaomi.com',
        'referer': clean_referer,
        'user-agent': user_agent,
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'priority': 'u=1, i',
        'eui': eui_header, 
    }

    max_retry = 12
    for i in range(max_retry):
        inbox = check_inbox(email)
        if inbox:
            otp = extract_otp(inbox)
            if otp:
                print(f"[+] OTP ditemukan: {otp}. Melakukan finalisasi pendaftaran...")
                
                new_eui_header, enc_params = encrypt_eui({'email': email, 'password': password})
                headers['eui'] = new_eui_header
                
                final_data = {
                    'ticket': otp,
                    'region': 'ID',
                    'email': enc_params['email'],
                    'env': 'web',
                    'qs': '?sid=mi_overseaid_new',
                    'isAcceptLicense': 'true',
                    'sid': 'mi_overseaid_new',
                    'password': enc_params['password'],
                    'policyName': 'globalmiaccount',
                    'callback': '',
                    'deviceFingerprint': fingerprint
                }
                
                final_res = session.post(
                    'https://global.account.xiaomi.com/pass/verifyEmailRegTicket',
                    headers=headers,
                    data=final_data,
                    timeout=30
                )
                
                final_content = final_res.text.replace("&&&START&&&", "")
                print(f"[DEBUG] Final Response: {final_content}")
                
                if '"result":"ok"' in final_content or '"code":0' in final_content:
                    print(f"\n[SUCCESS] AKUN BERHASIL DIBUAT!")
                    print(f"Email: {email}")
                    print(f"Pass: {password}")
                    try:
                        reg_data = json.loads(final_content)
                    except:
                        reg_data = {}

                    init_mistore_session(session, user_agent, reg_data)
                    all_cookies = session.cookies.get_dict()
                    if all_cookies:
                        save_new_cookie(all_cookies)
                    return True
                else:
                    print(f"[-] Gagal finalisasi akun: {final_content}")
                    return False
        
        print(f"[*] Belum ada email ({i+1}/{max_retry}), cek lagi 2 detik...", flush=True)
        time.sleep(2)
    
    print("[-] Timeout: OTP tidak ditemukan di email.")
    return False

def register_account(email, password, proxy_session_id=None):
    proxy_url = "http://YOUR_PROXY_USER:YOUR_PROXY_PASS@YOUR_PROXY_IP:PORT"
    eui_header, enc_params = encrypt_eui({
        'email': email,
        'password': password
    })
    
    fingerprint = generate_device_fingerprint()
    print(f"[*] Fingerprint Perangkat: {fingerprint}")
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    ]
    ua = random.choice(user_agents)

    session_args = {'impersonate': 'chrome'}
    if proxy_session_id:
        rotated_proxy = f"http://24122004-session-{proxy_session_id}:24122004@pool1.mymiyel.site:3010"
        session_args['proxies'] = {"http": rotated_proxy, "https": rotated_proxy}
        print(f"[PROX] Menggunakan Proxy Residential (Session: {proxy_session_id})...")

    session = cffi_requests.Session(**session_args)

    clean_referer = "https://global.account.xiaomi.com/fe/service/register?region=ID&sid=mi_overseaid_new&_locale=id_ID"
    
    print("[*] Menginisialisasi session dan cookies dasar...")
    try:
        session.get("https://global.account.xiaomi.com/", timeout=15)
        time.sleep(random.uniform(1, 2))
        session.get(clean_referer, timeout=15)
    except Exception as e:
        if proxy_session_id: print(f"[!] Proxy Error: {e}")
        pass
    
    headers = {
        'authority': 'global.account.xiaomi.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://global.account.xiaomi.com',
        'referer': clean_referer,
        'user-agent': ua,
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'priority': 'u=1, i',
        'eui': eui_header, 
    }
    
    data = {
        'email': enc_params['email'],
        'password': enc_params['password'],
        'region': 'ID',
        'sid': 'mi_overseaid_new',
        'icode': '',
    }
    
    print(f"[*] Mencoba mendaftarkan email: {email}")
    print(f"[*] Mengirim permintaan awal...")
    
    try:
        max_captcha_retry = 5
        retry_count = 0
        
        while retry_count < max_captcha_retry:
            retry_count += 1
            response = session.post(
                'https://global.account.xiaomi.com/pass/sendEmailRegTicket',
                headers=headers,
                data=data,
                timeout=30
            )
            
            resp_text = response.text.replace("&&&START&&&", "")
            res_json = json.loads(resp_text)

            if res_json.get("code") == 87001:
                captcha_url = res_json.get("captchaUrl")
                if not captcha_url:
                    print(f"[-] Gagal mendapatkan URL captcha baru: {res_json}")
                    return None

                print(f"[!] Xiaomi meminta verifikasi captcha (Percobaan Akun {retry_count}/{max_captcha_retry}).", flush=True)

                for solve_retry in range(1, 13):
                    print(f"[*] Mencoba memecahkan gambar captcha yang sama (Percobaan OCR {solve_retry}/12)...", flush=True)
                    icode = solve_image_captcha(session, captcha_url)
                    
                    if icode:
                        data['icode'] = icode
                        response = session.post(
                            'https://global.account.xiaomi.com/pass/sendEmailRegTicket',
                            headers=headers,
                            data=data,
                            timeout=30
                        )
                        resp_text = response.text.replace("&&&START&&&", "")
                        res_json = json.loads(resp_text)
                        
                        if res_json.get("code") != 87001:
                            break
                        else:
                            print(f"[-] Kode captcha salah/ditolak. Mengulang OCR...", flush=True)
                    else:
                        print(f"[-] Gagal mendapatkan solusi dari CapSolver.")

                if res_json.get("code") == 87001:
                    print(f"[!] Gagal menembus captcha setelah 12x percobaan OCR. Meminta gambar baru...", flush=True)
                    continue
            
            if res_json.get("result") == "ok":
                print(f"[+] OTP Berhasil dikirim ke {email}!", flush=True)
                return verify_otp(session, email, password, clean_referer, eui_header, fingerprint, ua)
            else:
                desc = res_json.get('description', 'Unknown error')
                print(f"[-] Gagal mengirim OTP: {desc}", flush=True)
                if "请求被拒绝" in desc:
                    print("[!] Terdeteksi blokir IP! Mengaktifkan rotasi proxy untuk percobaan berikutnya...")
                    return "RETRY_WITH_PROXY"
                return None
        
        print(f"[-] Gagal mengirim OTP setelah {max_captcha_retry} percobaan captcha.")
        return None
            
    except Exception as e:
        print(f"[-] Terjadi kesalahan: {e}")
        return None

from concurrent.futures import ThreadPoolExecutor
berhasil_global = 0
percobaan_global = 0
counter_lock = threading.Lock()

def worker_pendaftaran(target_total):
    global berhasil_global, percobaan_global
    thread_id = threading.get_ident()
    current_proxy_session = None
    
    while True:
        with counter_lock:
            if berhasil_global >= target_total:
                break
            percobaan_global += 1
            idx_percobaan = percobaan_global
            
        print(f"\n{'='*50}")
        print(f"[{thread_id}] PERCOBAAN KE-{idx_percobaan} (TOTAL BERHASIL: {berhasil_global}/{target_total})")
        print(f"{'='*50}")
        
        email_baru = generate_email()
        password_baru = "0x1SvdLabs" 
        
        if email_baru:
            res = register_account(email_baru, password_baru, proxy_session_id=current_proxy_session)
            
            if res == True:
                with counter_lock:
                    berhasil_global += 1
                print(f"[{thread_id}] [#] BERHASIL dibuat.")
            elif res == "RETRY_WITH_PROXY":
                print(f"[{thread_id}] [!] IP Terblokir! Melakukan rotasi proxy...")
                current_proxy_session = random.randint(10000, 99999)
                res_retry = register_account(email_baru, password_baru, proxy_session_id=current_proxy_session)
                if res_retry == True:
                    with counter_lock:
                        berhasil_global += 1
                    print(f"[{thread_id}] [#] BERHASIL dibuat via Proxy Baru.")
            else:
                print(f"[{thread_id}] [-] GAGAL.")
        time.sleep(random.uniform(5, 10))

def main_register():
    global berhasil_global, percobaan_global
    print("====================================================")
    print("          XIAOMI AUTO REGISTER BY 0x1Svd.Labs        ")
    print("====================================================")
    cookie_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Cookies', 'cookies.json')
    current_count = 0
    if os.path.exists(cookie_path):
        try:
            with open(cookie_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                current_count = len(data)
        except: current_count = 0

    try:
        jumlah_target = int(input(f"[?] Mau tambah berapa akun? ({current_count} akun di Cookies/cookies.json) : "))
    except ValueError: return
        
    berhasil_global = 0
    percobaan_global = 0
    
    print(f"[*] Memulai pendaftaran dengan 3 thread...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        for _ in range(3):
            executor.submit(worker_pendaftaran, jumlah_target)
            
    print(f"\n[DONE] Target {jumlah_target} akun berhasil terpenuhi.")

    import glob
    print("[*] Membersihkan file captcha temporary...")
    captcha_files = glob.glob("Register/captcha_*.jpg")
    for f in captcha_files:
        try:
            os.remove(f)
        except:
            pass
    print("[+] Selesai. Directory bersih.")

if __name__ == "__main__":
    main_register()
