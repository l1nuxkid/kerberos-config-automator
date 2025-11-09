# 🔐 Kerberos Configuration Automator

A Python script to automatically generate and configure `/etc/krb5.conf` for Active Directory environments during penetration testing and red team engagements.

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)

## 🚀 Features

- **Automated Configuration**: Generates proper `krb5.conf` for Kerberos authentication
- **Multiple Deployment Options**: Supports both DNS names and direct IP addresses
- **Safe Operations**: Automatically backs up existing configuration before changes
- **Validation Tools**: Built-in testing to verify Kerberos configuration
- **Tool Integration**: Optimized for common AD exploitation tools

## 🛠️ Supported Tools

- **evil-winrm** - Kerberos authentication for WinRM
- **Impacket Suite** - getTGT, GetUserSPNs, etc.
- **BloodHound Python** - Kerberos-based enumeration
- **CrackMapExec** - Kerberos attacks
- **And more** - Any tool that uses Kerberos authentication

## 📥 Installation

```bash
git clone https://github.com/l1nuxkid/kerberos-config-automator.git
cd kerberos-config-automator
chmod +x configure_krb5.py


## 📥 Usage

python3 configure_krb5.py nanocorp.htb dc01



## 👤 Author
l1nuxkid

GitHub: @l1nuxkid


