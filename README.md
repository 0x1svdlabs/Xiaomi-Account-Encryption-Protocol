<div align="center">

```
██╗  ██╗██╗ █████╗  ██████╗ ███╗   ███╗██╗      █████╗  ██████╗ ██████╗ ██████╗ ██╗   ██╗███╗   ██╗████████╗
╚██╗██╔╝██║██╔══██╗██╔═══██╗████╗ ████║██║     ██╔══██╗██╔════╝██╔════╝██╔═══██╗██║   ██║████╗  ██║╚══██╔══╝
 ╚███╔╝ ██║███████║██║   ██║██╔████╔██║██║     ███████║██║     ██║     ██║   ██║██║   ██║██╔██╗ ██║   ██║  
 ██╔██╗ ██║██╔══██║██║   ██║██║╚██╔╝██║██║     ██╔══██║██║     ██║     ██║   ██║██║   ██║██║╚██╗██║   ██║ 
██╔╝ ██╗██║██║  ██║╚██████╔╝██║ ╚═╝ ██║██║     ██║  ██║╚██████╗╚██████╗╚██████╔╝╚██████╔╝██║ ╚████║   ██║  
╚═╝  ╚═╝╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝ 

███████╗███╗   ██╗ ██████╗██████╗ ██╗   ██╗██████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██╔════╝████╗  ██║██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
█████╗  ██╔██╗ ██║██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║██║   ██║██╔██╗ ██║
██╔══╝  ██║╚██╗██║██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║██║   ██║██║╚██╗██║
███████╗██║ ╚████║╚██████╗██║  ██║   ██║   ██║        ██║   ██║╚██████╔╝██║ ╚████║
╚══════╝╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

██████╗ ██████╗  ██████╗ ████████╗ ██████╗  ██████╗ ██████╗ ██╗     
██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝██╔═══██╗██║     
██████╔╝██████╔╝██║   ██║   ██║   ██║   ██║██║     ██║   ██║██║     
██╔═══╝ ██╔══██╗██║   ██║   ██║   ██║   ██║██║     ██║   ██║██║     
██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╗╚██████╔╝███████╗
╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝

by 0x1svd.labs
```

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Educational-orange.svg)]()
[![Security](https://img.shields.io/badge/security-research-red.svg)]()

**Implementation of Xiaomi's Encrypted User Information (EUI) Protocol**

*Demonstrates hybrid RSA-1024 + AES-CBC encryption, device fingerprinting, and automated captcha solving*

**For Educational and Security Research Purposes**

---

</div>

## 📋 Overview

This project focuses on understanding and implementing the **Encrypted User Information (EUI)** system that Xiaomi uses to protect sensitive registration data. The bulk account registration capability is simply a practical application of this encryption knowledge.

---

## 🔐 Core Technical Implementation

### Hybrid Encryption System

| Component | Algorithm | Purpose |
|-----------|-----------|---------|
| 🔑 **Key Exchange** | RSA-1024 | Encrypts randomly generated AES keys using Xiaomi's public key |
| 🛡️ **Data Encryption** | AES-CBC | Encrypts sensitive user data (email, password) with random 16-byte keys |
| 📦 **Protocol Format** | EUI Header | `{RSA_encrypted_AES_key}.{Base64_field_names}` |

### Extracted Public Key

```python
PUBLIC_KEY_EUI = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCYEVrK/4Mahiv0pUJgTybx4J9P
5dUT/Y0PuwMbk+gMU+jrZnBiXGv6/hCH1avIhoBcE535F8nJQQN3UavZdFkYidso
XuEnat3+eVTp3FslyhRwIBDF09v4vDhRtxFOT+R7uH7h/mzmyA2/+lfIMWGIrffX
prYizbV76+YQKhoqFQIDAQAB
-----END PUBLIC KEY-----"""
```

<details>
<summary>🔍 <b>Click to see encryption workflow</b></summary>

```python
# Step 1: Generate random AES key (16 bytes)
aes_key = ''.join(random.choice(chars) for _ in range(16))

# Step 2: Encrypt AES key with RSA public key
rsa_cipher = PKCS1_v1_5.new(RSA.import_key(PUBLIC_KEY_EUI))
encrypted_aes_key = rsa_cipher.encrypt(base64.b64encode(aes_key.encode()))

# Step 3: Encrypt user data with AES-CBC
cipher = AES.new(aes_key.encode(), AES.MODE_CBC, iv=b"0102030405060708")
encrypted_data = cipher.encrypt(pad(user_data.encode(), AES.block_size))

# Step 4: Build EUI header
eui_header = f"{base64(encrypted_aes_key)}.{base64(field_names)}"
```

</details>

---

## Features

**Encryption & Security:**
- Full implementation of Xiaomi's EUI encryption protocol
- RSA PKCS1_v1_5 padding implementation
- AES-CBC mode with custom IV
- Device fingerprinting generation
- Browser fingerprint evasion using curl-cffi

**Automation Capabilities:**
- Automated captcha solving (Image OCR + hCaptcha)
- Temporary email integration via RapidAPI
- OTP extraction and verification
- Multi-threaded account creation
- Automatic proxy rotation on IP blocks
- Cookie session management

**API Endpoints Used:**
- `global.account.xiaomi.com/pass/sendEmailRegTicket` - Registration
- `global.account.xiaomi.com/pass/verifyEmailRegTicket` - OTP Verification
- `account.xiaomi.com/pass/serviceLogin` - Mi Store Sync
- `go.buy.mi.co.id/id/app/userprofile` - Profile Verification

## Technical Stack

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `requests` - HTTP client
- `curl_cffi` - Browser impersonation
- `pycryptodome` - RSA/AES cryptographic operations
- `pyTelegramBotAPI` - Telegram notifications (optional)

## Configuration

Before running, configure your API credentials:

### 1. Temp Mail API (RapidAPI)
Edit `Email/buatakun.py`:
```python
API_KEY = "YOUR_RAPIDAPI_KEY"  # Line 8
```
Get your key from: https://rapidapi.com/Privatix/api/temp-mail

### 2. CapSolver API
Edit `Register/register.py`:
```python
api_key = "YOUR_CAPSOLVER_API_KEY"  # Line 29
```
Get your key from: https://capsolver.com

### 3. Proxy Configuration (Optional)
Edit `Register/register.py`:
```python
proxy_url = "http://USER:PASS@IP:PORT"  # Line 269
```
Residential proxies recommended for avoiding IP blocks.

## Usage

Run the main registration script:

```bash
python Register/register.py
```

The script will:
1. Prompt for the number of accounts to create
2. Generate temporary emails automatically
3. Encrypt credentials using the EUI protocol
4. Solve captchas automatically
5. Verify OTP from email
6. Save successful cookies to `Cookies/cookies.json`

**Multi-threading:** Uses 3 concurrent threads by default for optimal performance.

## Project Structure

```
.
├── Email/
│   └── buatakun.py          # Temp email generation & OTP extraction
├── Register/
│   └── register.py          # Main registration & encryption logic
├── Cookies/
│   └── cookies.json         # Saved account cookies
├── requirements.txt
└── README.md
```

## Security Mechanisms Bypassed

- ✅ Device fingerprinting
- ✅ Image CAPTCHA (via CapSolver OCR)
- ✅ hCaptcha (site key: `6LeBM0ocAAAAAEwYcFUjtxpVbs-0rnbSVXBBXmh4`)
- ✅ Rate limiting (via proxy rotation)
- ✅ IP blocking detection

## Educational Purpose

This project is for **educational and research purposes** to understand:
- Client-side encryption implementation
- Hybrid cryptographic systems (RSA + AES)
- API reverse engineering methodologies
- Browser automation and fingerprint evasion

The extracted `PUBLIC_KEY_EUI` and encryption protocol can be used for legitimate integrations with Xiaomi's account system.

## Disclaimer

This tool is intended for educational purposes and authorized security research only. Users are responsible for compliance with Xiaomi's Terms of Service and applicable laws. The authors assume no liability for misuse.

## License

MIT License - Use at your own risk.
