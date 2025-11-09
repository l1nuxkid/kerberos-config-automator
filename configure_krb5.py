#!/usr/bin/env python3
"""

██╗░░░░░░░███╗░░███╗░░██╗██╗░░░██╗██╗░░██╗██╗░░██╗██╗██████╗░
██║░░░░░░████║░░████╗░██║██║░░░██║╚██╗██╔╝██║░██╔╝██║██╔══██╗
██║░░░░░██╔██║░░██╔██╗██║██║░░░██║░╚███╔╝░█████═╝░██║██║░░██║
██║░░░░░╚═╝██║░░██║╚████║██║░░░██║░██╔██╗░██╔═██╗░██║██║░░██║
███████╗███████╗██║░╚███║╚██████╔╝██╔╝╚██╗██║░╚██╗██║██████╔╝
╚══════╝╚══════╝╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝╚═════╝░


Kerberos Configuration Script for Active Directory Environments

This script configures /etc/krb5.conf for Kerberos authentication with tools like:
- evil-winrm
- impacket tools
- bloodhound-python
- etc.


Features:
- Automatic backup of existing configuration
- Proper Kerberos settings for AD environments
- Support for both DNS and IP-based KDC configuration
- Validation and testing

Usage examples:
  python3 configure_krb5.py nanocorp.htb dc01
  python3 configure_krb5.py -k 10.129.11.92 nanocorp.htb dc01
  python3 configure_krb5.py --ip-kdc 10.129.11.92 nanocorp.htb dc01
"""

import os
import sys
import argparse
from pathlib import Path
import shutil
from datetime import datetime
import subprocess


def get_config(domain_fqdn: str, dc_name: str, kdc_ip: str = None):
    """Generate krb5.conf configuration"""
    
    if kdc_ip:
        # Use IP address directly
        kdc_host = kdc_ip
        admin_server = kdc_ip
    else:
        # Use DNS name
        kdc_host = f"{dc_name.lower()}.{domain_fqdn.lower()}"
        admin_server = f"{dc_name.lower()}.{domain_fqdn.lower()}"
    
    return f"""[libdefaults]
    default_realm = {domain_fqdn.upper()}
    dns_lookup_realm = false
    dns_lookup_kdc = {'false' if kdc_ip else 'true'}
    ticket_lifetime = 24h
    renew_lifetime = 7d
    forwardable = true
    proxiable = true
    rdns = false

[realms]
    {domain_fqdn.upper()} = {{
        kdc = {kdc_host}
        admin_server = {admin_server}
    }}

[domain_realm]
    {domain_fqdn.lower()} = {domain_fqdn.upper()}
    .{domain_fqdn.lower()} = {domain_fqdn.upper()}
"""


def backup_existing_config():
    """Backup existing krb5.conf if it exists"""
    krb5_path = Path("/etc/krb5.conf")
    if krb5_path.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"/etc/krb5.conf.backup.{timestamp}"
        shutil.copy2(krb5_path, backup_name)
        print(f"[+] Backed up existing config to {backup_name}")
        return backup_name
    return None


def check_permissions():
    """Check if we have write permissions to /etc/krb5.conf"""
    krb5_path = Path("/etc/krb5.conf")
    if krb5_path.exists():
        if not os.access(krb5_path, os.W_OK):
            return False
    else:
        etc_dir = Path("/etc")
        if not os.access(etc_dir, os.W_OK):
            return False
    return True


def test_kerberos_config():
    """Test if Kerberos configuration is working"""
    print("[*] Testing Kerberos configuration...")
    
    tests = [
        ["klist", "-5"],
        ["klist", "-k"]
    ]
    
    for test_cmd in tests:
        try:
            result = subprocess.run(test_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[+] Test passed: {' '.join(test_cmd)}")
            else:
                print(f"[-] Test may have issues with: {' '.join(test_cmd)}")
                if result.stderr:
                    print(f"    Error: {result.stderr.strip()}")
        except Exception as e:
            print(f"[-] Failed to run test {' '.join(test_cmd)}: {e}")


def get_current_config():
    """Display current krb5.conf if it exists"""
    krb5_path = Path("/etc/krb5.conf")
    if krb5_path.exists():
        print("\n[*] Current /etc/krb5.conf:")
        print("-" * 50)
        with open(krb5_path, 'r') as f:
            print(f.read())
        print("-" * 50)


def main():
    parser = argparse.ArgumentParser(
        description="Configure /etc/krb5.conf for Active Directory Kerberos authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {sys.argv[0]} nanocorp.htb dc01
  {sys.argv[0]} -k 10.129.228.72 nanocorp.htb dc01
  {sys.argv[0]} --ip-kdc 10.129.228.72 --test nanocorp.htb dc01
  {sys.argv[0]} --show-current

Common tools that use this configuration:
  • evil-winrm -i <DC_IP> -r <DOMAIN>
  • impacket-getTGT -dc-ip <DC_IP> <DOMAIN>/<USER>
  • bloodhound-python -d <DOMAIN> -k
  • crackmapexec <DC_IP> -k
        """
    )
    parser.add_argument("domain_fqdn", nargs="?", help="Domain FQDN (e.g., nanocorp.htb)")
    parser.add_argument("dc_name", nargs="?", help="Domain Controller Name (e.g., dc01)")
    parser.add_argument("-k", "--ip-kdc", help="Use IP address for KDC instead of DNS name")
    parser.add_argument("-t", "--test", action="store_true", help="Test Kerberos configuration after setup")
    parser.add_argument("--show-current", action="store_true", help="Show current krb5.conf and exit")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()

    # Show current config if requested
    if args.show_current:
        get_current_config()
        sys.exit(0)

    # Validate required arguments
    if not args.domain_fqdn or not args.dc_name:
        parser.print_help()
        print(f"\n[-] Error: domain_fqdn and dc_name are required")
        sys.exit(1)

    # Check permissions
    if not check_permissions():
        print("[*] Root privileges required, requesting sudo...")
        sudo_args = ["sudo", sys.executable] + sys.argv + [os.environ]
        os.execlpe("sudo", *sudo_args)

    # Show current config before changes
    get_current_config()

    # Generate new configuration
    config_data = get_config(args.domain_fqdn, args.dc_name, args.ip_kdc)
    
    print("\n[*] New Configuration:")
    print("=" * 50)
    print(config_data)
    print("=" * 50)

    # Confirmation
    if not args.yes:
        confirm = input("\n[!] This will overwrite /etc/krb5.conf. Continue? [y/N] ")
        if confirm.lower() != 'y':
            print("[!] Aborting")
            sys.exit(1)

    # Backup existing config
    backup_path = backup_existing_config()

    try:
        with open("/etc/krb5.conf", "w") as f:
            f.write(config_data)
        print("[+] /etc/krb5.conf has been successfully configured")
        
        # Test configuration if requested
        if args.test:
            test_kerberos_config()
        
        # Show usage examples
        print("\n[+] Usage examples with the new configuration:")
        print(f"  kinit username@{args.domain_fqdn.upper()}")
        print(f"  evil-winrm -i {args.ip_kdc or args.dc_name + '.' + args.domain_fqdn} -r {args.domain_fqdn}")
        print(f"  impacket-getTGT -dc-ip {args.ip_kdc or args.dc_name + '.' + args.domain_fqdn} {args.domain_fqdn.upper()}/username")
        print(f"  bloodhound-python -d {args.domain_fqdn} -k")
            
    except Exception as e:
        print(f"[-] Error writing configuration: {e}")
        if backup_path:
            print(f"[*] Restoring backup from {backup_path}")
            shutil.copy2(backup_path, "/etc/krb5.conf")
        sys.exit(1)


if __name__ == "__main__":
    main()
