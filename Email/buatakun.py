import requests
import hashlib
import time

# =========================
# CONFIG
# =========================
API_KEY = "YOUR_RAPIDAPI_KEY"
API_HOST = "privatix-temp-mail-v1.p.rapidapi.com"
BASE_URL = f"https://{API_HOST}/request"
headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}


# =========================
# 1. AMBIL DOMAIN TEMP MAIL
# =========================
def get_domains():
    url = f"{BASE_URL}/domains"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print("Gagal mengambil domain:", response.text)
        return []


# =========================
# 2. GENERATE EMAIL RANDOM
# =========================
def generate_email():
    domains = get_domains()
    if not domains:
        return None

    blocked_domains = ['cevipsa.com', 'mister-mail.com', '10minutemail.com']
    safe_domains = [d for d in domains if d.strip('@') not in blocked_domains]
    
    if not safe_domains:
        print("[!] Peringatan: Tidak ada domain aman tersedia.")
        safe_domains = domains

    import random
    domain = random.choice(safe_domains)
    username = f"user{int(time.time())}{random.randint(10,99)}"

    if domain.startswith("@"):
        email = f"{username}{domain}"
    else:
        email = f"{username}@{domain}"

    print(f"Email berhasil dibuat: {email}")
    return email


# =========================
# 3. HASH EMAIL (MD5)
# API ini butuh email dalam bentuk MD5
# =========================
def email_to_md5(email):
    return hashlib.md5(email.encode()).hexdigest()


# =========================
# 4. CEK EMAIL MASUK
# =========================
def check_inbox(email):
    email_hash = email_to_md5(email)

    url = f"{BASE_URL}/mail/id/{email_hash}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            mails = response.json()
            return mails
        except:
            return []
    else:
        print("Gagal cek inbox:", response.text)
        return []


# =========================
# 5. AMBIL OTP DARI EMAIL
# =========================
def extract_otp(mail_list):
    if not isinstance(mail_list, list):
        return None

    for mail in mail_list:
        if not isinstance(mail, dict):
            continue
        subject = mail.get("mail_subject", "")
        text = mail.get("mail_text_only", "")

        print("\n=== EMAIL MASUK ===")
        print("Subject:", subject)
        print("Isi:", text)
        import re
        otp = re.findall(r"\b\d{4,8}\b", text)

        if otp:
            print("\nOTP ditemukan:", otp[0])
            return otp[0]

    print("OTP belum ditemukan.")
    return None


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    email = generate_email()

    if email:
        print("\nGunakan email ini untuk daftar akun:")
        print(email)

        print("\nMenunggu email masuk...")

        while True:
            inbox = check_inbox(email)

            if inbox:
                otp = extract_otp(inbox)
                if otp:
                    print("\nSELESAI - OTP:", otp)
                    break

            print("Belum ada email, cek lagi 10 detik...")
            time.sleep(10)
