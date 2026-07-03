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

##  Overview

This project focuses on understanding and implementing the **Encrypted User Information (EUI)** system that Xiaomi uses to protect sensitive registration data. The bulk account registration capability is simply a practical application of this encryption knowledge.

---

##  Core Technical Implementation

### Hybrid Encryption System

| Component | Algorithm | Purpose |
|-----------|-----------|---------|
|  **Key Exchange** | RSA-1024 | Encrypts randomly generated AES keys using Xiaomi's public key |
|  **Data Encryption** | AES-CBC | Encrypts sensitive user data (email, password) with random 16-byte keys |
|  **Protocol Format** | EUI Header | `{RSA_encrypted_AES_key}.{Base64_field_names}` |

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
<summary> <b>Click to see encryption workflow</b></summary>

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

##  Features

<table>
<tr>
<td width="50%">

###  Encryption & Security
-  Full implementation of Xiaomi's EUI encryption protocol
-  RSA PKCS1_v1_5 padding implementation
-  AES-CBC mode with custom IV
-  Device fingerprinting generation
-  Browser fingerprint evasion using curl-cffi

</td>
<td width="50%">

###  Automation Capabilities
-  Automated captcha solving (Image OCR + hCaptcha)
-  Temporary email integration via RapidAPI
-  OTP extraction and verification
-  Multi-threaded account creation (3 threads)
-  Automatic proxy rotation on IP blocks
-  Cookie session management

</td>
</tr>
</table>

###  API Endpoints Used

```
┌────────────────────────────────────────────────────────────────────────┐
│ Endpoint                                            │ Purpose          │
├────────────────────────────────────────────────────────────────────────┤
│ global.account.xiaomi.com/pass/sendEmailRegTicket  │ Registration     │
│ global.account.xiaomi.com/pass/verifyEmailRegTicket│ OTP Verification │
│ account.xiaomi.com/pass/serviceLogin               │ Mi Store Sync    │
│ go.buy.mi.co.id/id/app/userprofile                 │ Profile Check    │
└────────────────────────────────────────────────────────────────────────┘
```

---

##  Technical Stack

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/xiaomi-account-encryption-protocol.git
cd xiaomi-account-encryption-protocol

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

<table>
<tr>
<td align="center" width="25%">
<img src="https://raw.githubusercontent.com/psf/requests/main/ext/requests-logo.png" width="60"><br>
<b>requests</b><br>
<sub>HTTP client</sub>
</td>
<td align="center" width="25%">
<img src="https://avatars.githubusercontent.com/u/110098278" width="60"><br>
<b>curl-cffi</b><br>
<sub>Browser impersonation</sub>
</td>
<td align="center" width="25%">
<img src="https://www.pycryptodome.org/en/latest/_static/pycryptodome_logo.png" width="60"><br>
<b>pycryptodome</b><br>
<sub>RSA/AES operations</sub>
</td>
<td align="center" width="25%">
<img src="https://core.telegram.org/file/464001863/110f3/I47qTXAD9Z4.120010/e0ea04f66357b640ec" width="60"><br>
<b>pyTelegramBotAPI</b><br>
<sub>Notifications (optional)</sub>
</td>
</tr>
</table>

---

##  Configuration

Before running, configure your API credentials:

<details open>
<summary><b>1️. Temp Mail API (RapidAPI)</b></summary>

Edit `Email/buatakun.py`:
```python
API_KEY = "YOUR_RAPIDAPI_KEY"  # Line 8
```

**Get your key:** [RapidAPI - Privatix Temp Mail](https://rapidapi.com/Privatix/api/temp-mail)

</details>

<details open>
<summary><b>2️. CapSolver API</b></summary>

Edit `Register/register.py`:
```python
api_key = "YOUR_CAPSOLVER_API_KEY"  # Line 29
```

**Get your key:** [CapSolver Official](https://capsolver.com)

</details>

<details>
<summary><b>3️. Proxy Configuration (Optional)</b></summary>

Edit `Register/register.py`:
```python
proxy_url = "http://USER:PASS@IP:PORT"  # Line 269
```

**Recommended:** Residential proxies for avoiding IP blocks

</details>

---

##  Usage

### Quick Start

```bash
python Register/register.py
```

### Workflow Process

```
╔════════════════════════════════════════════════════════════════════╗
║                     REGISTRATION WORKFLOW                          ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Step 1  →  Generate temporary email via RapidAPI                 ║
║              ↓                                                     ║
║  Step 2  →  Encrypt credentials using EUI protocol                ║
║              ↓                                                     ║
║  Step 3  →  Send registration request to Xiaomi                   ║
║              ↓                                                     ║
║  Step 4  →  Solve captcha automatically (OCR/hCaptcha)            ║
║              ↓                                                     ║
║  Step 5  →  Extract OTP from temporary email                      ║
║              ↓                                                     ║
║  Step 6  →  Verify OTP and finalize registration                  ║
║              ↓                                                     ║
║  Step 7  →  Initialize Mi Store session                           ║
║              ↓                                                     ║
║  Step 8  →  Save cookies to Cookies/cookies.json                  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

### Performance Features

| Feature | Description |
|---------|-------------|
|  **Multi-threading** | 3 concurrent threads for optimal performance |
|  **Auto-retry** | Automatic proxy rotation on IP blocks |
|  **Session storage** | Successful accounts saved to JSON |
|  **Progress tracking** | Real-time success/failure counter |

---

##  Project Structure

```
xiaomi-account-encryption-protocol/
│
├──  Email/
│   └── buatakun.py                  # Temp email generation & OTP extraction
│                                    # Functions: generate_email(), check_inbox(), extract_otp()
│
├──  Register/
│   └── register.py                  # Main registration & EUI encryption logic
│                                    # Functions: encrypt_eui(), register_account(), verify_otp()
│                                    # Lines: 484 | Core: RSA-AES implementation
│
├──  Cookies/
│   └── cookies.json                 # Saved account session cookies
│                                    # Format: [{"cookie": {...}}, ...]
│
├──  requirements.txt              # Python dependencies
└──  README.md                     # This file
```

<details>
<summary>📊 <b>Code Statistics</b></summary>

| File | Lines | Functions | Purpose |
|------|-------|-----------|---------|
| `Email/buatakun.py` | 136 | 6 | Email & OTP handling |
| `Register/register.py` | 484 | 12 | Encryption & Registration |
| **Total** | **620** | **18** | **Full automation** |

</details>

---

##  Security Mechanisms Bypassed

<table>
<tr>
<td align="center" width="20%">
<img src="https://img.icons8.com/fluency/96/fingerprint.png" width="50"><br>
<b>Device Fingerprinting</b><br>
<sub> MD5 hash generation</sub>
</td>
<td align="center" width="20%">
<img src="https://img.icons8.com/fluency/96/captcha.png" width="50"><br>
<b>Image CAPTCHA</b><br>
<sub> CapSolver OCR</sub>
</td>
<td align="center" width="20%">
<img src="https://img.icons8.com/fluency/96/bot.png" width="50"><br>
<b>hCaptcha</b><br>
<sub> Automated solving</sub>
</td>
<td align="center" width="20%">
<img src="https://img.icons8.com/fluency/96/clock.png" width="50"><br>
<b>Rate Limiting</b><br>
<sub> Proxy rotation</sub>
</td>
<td align="center" width="20%">
<img src="https://img.icons8.com/fluency/96/block.png" width="50"><br>
<b>IP Blocking</b><br>
<sub> Auto-switch proxy</sub>
</td>
</tr>
</table>

**hCaptcha Site Key:** `6LeBM0ocAAAAAEwYcFUjtxpVbs-0rnbSVXBBXmh4`

---

##  Educational Purpose

<div align="center">

```
╔═══════════════════════════════════════════════════════════════════╗
║                    LEARNING OBJECTIVES                            ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║      Client-side encryption implementation                        ║
║      → Understanding how web services protect user data           ║
║                                                                   ║
║      Hybrid cryptographic systems (RSA + AES)                     ║
║      → Real-world encryption pattern analysis                     ║
║                                                                   ║
║      API reverse engineering methodologies                        ║
║      → Understanding proprietary protocols                        ║
║                                                                   ║
║      Browser automation & fingerprint evasion                     ║
║      → Anti-bot bypass techniques                                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

</div>

**Note:** The extracted `PUBLIC_KEY_EUI` and encryption protocol can be used for legitimate integrations with Xiaomi's account system.

---

## !!! Disclaimer !!!

<div align="center">

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                      !!!  IMPORTANT NOTICE  !!!                       ║
║                                                                       ║
║  ┌─────────────────────────────────────────────────────────────────┐  ║
║  │                                                                 │  ║
║  │  This tool is intended for EDUCATIONAL PURPOSES and             │  ║
║  │  AUTHORIZED SECURITY RESEARCH only.                             │  ║
║  │                                                                 │  ║
║  │  Users are responsible for compliance with:                     │  ║
║  │  • Xiaomi's Terms of Service                                    │  ║
║  │  • Applicable local and international laws                      │  ║
║  │  • Ethical security research guidelines                         │  ║
║  │                                                                 │  ║
║  │  The authors assume NO LIABILITY for:                           │  ║
║  │  • Misuse of this software                                      │  ║
║  │  • Any damages resulting from its use                           │  ║
║  │  • Violation of third-party terms of service                    │  ║
║  │                                                                 │  ║
║  │  By using this software, you agree to use it RESPONSIBLY        │  ║
║  │  and in accordance with all applicable laws and regulations.    │  ║
║  │                                                                 │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
```

</div>

---

##  License

<div align="center">

### MIT License

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Copyright (c) 2026 0x1svd.labs                                     │
│                                                                     │
│  Permission is hereby granted, free of charge, to any person        │
│  obtaining a copy of this software and associated documentation     │
│  files (the "Software"), to deal in the Software without            │
│  restriction, including without limitation the rights to use,       │
│  copy, modify, merge, publish, distribute, sublicense, and/or       │
│  sell copies of the Software, and to permit persons to whom the     │
│  Software is furnished to do so, subject to the following           │
│  conditions:                                                        │
│                                                                     │
│  The above copyright notice and this permission notice shall be     │
│  included in all copies or substantial portions of the Software.    │
│                                                                     │
│  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,    │
│  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES    │
│  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND           │
│  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT        │
│  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,       │
│  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING       │
│  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR      │
│  OTHER DEALINGS IN THE SOFTWARE.                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Use at your own risk**

</div>

---

<div align="center">

##  Connect & Support

[![GitHub](https://img.shields.io/badge/GitHub-0x1svd.labs-181717?style=for-the-badge&logo=github)](https://github.com/0x1svd)
[![Email](https://img.shields.io/badge/Email-Contact-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:syaiyesmom.it@gmail.com)
[![Website](https://img.shields.io/badge/Website-0x1svd.labs-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white)]([https://0x1svd.labs](https://0x1svdlabs.viadar.my.id/))

---

###  Found this useful?

 **Star this repository** if you found it helpful!

 **Fork it** to create your own version

 **Report issues** to help improve the project

---

```
███████╗███╗   ██╗     ██╗ ██████╗ ██╗   ██╗    ██╗  ██╗ █████╗  ██████╗██╗  ██╗██╗███╗   ██╗ ██████╗ 
██╔════╝████╗  ██║     ██║██╔═══██╗╚██╗ ██╔╝    ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██║████╗  ██║██╔════╝ 
█████╗  ██╔██╗ ██║     ██║██║   ██║ ╚████╔╝     ███████║███████║██║     █████╔╝ ██║██╔██╗ ██║██║  ███╗
██╔══╝  ██║╚██╗██║██   ██║██║   ██║  ╚██╔╝      ██╔══██║██╔══██║██║     ██╔═██╗ ██║██║╚██╗██║██║   ██║
███████╗██║ ╚████║╚█████╔╝╚██████╔╝   ██║       ██║  ██║██║  ██║╚██████╗██║  ██╗██║██║ ╚████║╚██████╔╝
╚══════╝╚═╝  ╚═══╝ ╚════╝  ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
```

**Made with ❤️ for the Security Research Community**

*Last Updated: July 2026*

</div>
