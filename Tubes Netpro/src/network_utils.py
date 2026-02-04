# network_utils.py
# Utilitas jaringan untuk WiFi Scanner
# Dibuat oleh Zidan Ardiansyah

import subprocess
import platform
import socket
import re
import urllib.request
import json


def get_os_type():
    """Mendapatkan tipe OS"""
    return platform.system()


def check_wifi_adapter():
    """Memeriksa status adapter WiFi"""
    os_type = get_os_type()
    
    try:
        if os_type == "Windows":
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True, text=True, encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if "State" in result.stdout:
                if "connected" in result.stdout.lower():
                    return "connected", "WiFi Terhubung"
                else:
                    return "disconnected", "WiFi Tidak Terhubung"
            else:
                return "not_found", "Adapter Tidak Ditemukan"
        return "unknown", "Unknown"
    except:
        return "error", "Error Memeriksa Status"


def scan_wifi_networks():
    """Melakukan scanning jaringan WiFi"""
    os_type = get_os_type()
    networks = []
    
    try:
        if os_type == "Windows":
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                capture_output=True, text=True, encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_network = {}
                
                for line in lines:
                    line = line.strip()
                    
                    if line.startswith('SSID') and 'BSSID' not in line:
                        if current_network and 'SSID' in current_network:
                            networks.append(current_network)
                        ssid = line.split(':', 1)[1].strip() if ':' in line else ""
                        current_network = {'SSID': ssid if ssid else "Hidden Network"}
                    
                    elif 'Authentication' in line and ':' in line:
                        current_network['Security'] = line.split(':', 1)[1].strip()
                    
                    elif 'Signal' in line and ':' in line:
                        signal_str = line.split(':', 1)[1].strip().replace('%', '')
                        try:
                            signal = int(signal_str)
                            current_network['Signal'] = signal
                            current_network['Level'] = get_signal_level(signal)
                        except:
                            current_network['Signal'] = 0
                            current_network['Level'] = "Unknown"
                    
                    elif 'BSSID' in line and ':' in line:
                        bssid_parts = line.split(':', 1)
                        if len(bssid_parts) > 1:
                            current_network['BSSID'] = bssid_parts[1].strip()
                    
                    elif 'Radio type' in line or 'Channel' in line:
                        if 'Radio type' in line and ':' in line:
                            radio = line.split(':', 1)[1].strip()
                            if '802.11n' in radio or '802.11g' in radio or '802.11b' in radio:
                                current_network['Band'] = "2.4 GHz"
                            elif '802.11ac' in radio or '802.11ax' in radio or '802.11a' in radio:
                                current_network['Band'] = "5 GHz"
                            else:
                                current_network['Band'] = radio
                
                if current_network and 'SSID' in current_network:
                    networks.append(current_network)
                    
    except Exception as e:
        print(f"Error scanning: {e}")
    
    return networks


def get_signal_level(signal_percentage):
    """Mengubah persentase sinyal menjadi level"""
    if signal_percentage >= 80:
        return "🟢 Excellent"
    elif signal_percentage >= 60:
        return "🔵 Good"
    elif signal_percentage >= 40:
        return "🟡 Fair"
    elif signal_percentage >= 20:
        return "🟠 Weak"
    else:
        return "🔴 Very Weak"


def check_if_connected(ssid):
    """Check if connected to specific SSID"""
    os_type = get_os_type()
    
    try:
        if os_type == "Windows":
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True, text=True, encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = result.stdout
            if 'State' in output and 'connected' in output.lower():
                ssid_match = re.search(r'SSID\s+:\s+(.+)', output)
                if ssid_match:
                    connected_ssid = ssid_match.group(1).strip()
                    return ssid.lower() == connected_ssid.lower()
        return False
    except:
        return False


def get_ip_info(ssid):
    """Mendapatkan informasi IP"""
    os_type = get_os_type()
    
    ip_info = {
        'local_ip': 'Tidak terdeteksi',
        'public_ip': 'Tidak terdeteksi',
        'gateway': 'Tidak terdeteksi',
        'dns': 'Tidak terdeteksi',
        'mac': 'Tidak terdeteksi',
        'subnet': 'Tidak terdeteksi',
        'connected': False
    }
    
    try:
        ip_info['connected'] = check_if_connected(ssid)
        
        # Local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_info['local_ip'] = s.getsockname()[0]
            s.close()
        except:
            try:
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                if local_ip != "127.0.0.1":
                    ip_info['local_ip'] = local_ip
            except:
                pass
        
        # Public IP
        try:
            with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=3) as response:
                data = json.loads(response.read().decode())
                ip_info['public_ip'] = data.get('ip', 'Tidak terdeteksi')
        except:
            pass
        
        # Network details (Windows)
        if os_type == "Windows":
            try:
                result = subprocess.run(
                    ['ipconfig', '/all'],
                    capture_output=True, text=True, encoding='utf-8',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                output = result.stdout
                
                # Gateway
                gateway_match = re.search(r'Default Gateway[\s\.]+:\s+([\d\.]+)', output)
                if gateway_match:
                    ip_info['gateway'] = gateway_match.group(1)
                
                # Subnet
                subnet_match = re.search(r'Subnet Mask[\s\.]+:\s+([\d\.]+)', output)
                if subnet_match:
                    ip_info['subnet'] = subnet_match.group(1)
                
                # DNS
                dns_match = re.search(r'DNS Servers[\s\.]+:\s+([\d\.]+)', output)
                if dns_match:
                    ip_info['dns'] = dns_match.group(1)
                
                # MAC
                mac_match = re.search(r'Physical Address[\s\.]+:\s+([\w\-]+)', output)
                if mac_match:
                    ip_info['mac'] = mac_match.group(1).replace('-', ':')
                    
            except:
                pass
                
    except:
        pass
    
    return ip_info


def connect_to_network(ssid):
    """Mencoba connect ke jaringan WiFi"""
    os_type = get_os_type()
    
    if os_type == "Windows":
        try:
            # Cek apakah profil sudah ada
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profile', ssid],
                capture_output=True, text=True, encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                # Profil ada, langsung connect
                connect_result = subprocess.run(
                    ['netsh', 'wlan', 'connect', f'name={ssid}'],
                    capture_output=True, text=True, encoding='utf-8',
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if connect_result.returncode == 0:
                    return True, f"Berhasil terhubung ke {ssid}"
                else:
                    return False, f"Gagal terhubung ke {ssid}"
            else:
                return False, f"Profil untuk '{ssid}' tidak ditemukan.\nSilakan hubungkan secara manual."
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    return False, "OS tidak didukung"
