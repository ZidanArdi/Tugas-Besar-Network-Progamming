# wifi_scanner_gui.py
# WiFi Scanner dengan GUI Modern dan Elegan
# Dibuat oleh Zidan Ardiansyah

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime

# Import modul lokal
from config import COLORS, APP_CONFIG
from ui_components import (
    ModernTooltip, AnimatedProgressBar, 
    create_rounded_button, create_stat_card,
    show_toast, copy_to_clipboard
)
from network_utils import (
    check_wifi_adapter, scan_wifi_networks, 
    get_ip_info, connect_to_network, get_signal_level
)


class WiFiScannerGUI:
    """Aplikasi WiFi Scanner dengan GUI Modern"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(APP_CONFIG['title'])
        self.root.geometry(APP_CONFIG['geometry'])
        self.root.minsize(APP_CONFIG['min_width'], APP_CONFIG['min_height'])
        self.root.resizable(True, True)
        
        self.networks = []
        self.sort_column = None
        self.sort_reverse = False
        self.auto_refresh = False
        self.auto_refresh_interval = APP_CONFIG['auto_refresh_interval']
        self.colors = COLORS
        
        # Setup aplikasi
        self.setup_style()
        self.build_ui()
        self.setup_events()
        self.refresh_status()
        
    def setup_style(self):
        """Setup style modern"""
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Style Treeview
        style.configure("Modern.Treeview",
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_medium'],
                       borderwidth=0, font=("Segoe UI", 10))
        
        style.configure("Modern.Treeview.Heading",
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_secondary'],
                       borderwidth=0, font=("Segoe UI Semibold", 10))
        
        style.map("Modern.Treeview",
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')])
        
        style.map("Modern.Treeview.Heading",
                 background=[('active', self.colors['primary'])])
        
    def build_ui(self):
        """Membangun antarmuka pengguna"""
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        self._build_header(main_container)
        self._build_controls(main_container)
        self._build_stats(main_container)
        self._build_table(main_container)
        self._build_footer(main_container)
        
    def _build_header(self, parent):
        """Build header section"""
        header = tk.Frame(parent, bg=self.colors['bg_light'], height=120)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Left - Logo dan Title
        left = tk.Frame(header, bg=self.colors['bg_light'])
        left.pack(side=tk.LEFT, padx=30, pady=20)
        
        tk.Label(left, text="📡", font=("Segoe UI Emoji", 36),
                bg=self.colors['bg_light']).pack(side=tk.LEFT, padx=(0, 15))
        
        title_box = tk.Frame(left, bg=self.colors['bg_light'])
        title_box.pack(side=tk.LEFT)
        
        tk.Label(title_box, text="WiFi Scanner Pro",
                font=("Segoe UI", 24, "bold"),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_light']).pack(anchor="w")
        
        tk.Label(title_box, text="Network Programming • Advanced WiFi Analysis Tool",
                font=("Segoe UI", 11), fg=self.colors['text_secondary'],
                bg=self.colors['bg_light']).pack(anchor="w")
        
        # Right - Status
        right = tk.Frame(header, bg=self.colors['bg_light'])
        right.pack(side=tk.RIGHT, padx=30, pady=20)
        
        status_frame = tk.Frame(right, bg=self.colors['bg_light'])
        status_frame.pack(anchor="e")
        
        self.status_dot = tk.Label(status_frame, text="●", font=("Segoe UI", 14),
                                   fg=self.colors['text_muted'], bg=self.colors['bg_light'])
        self.status_dot.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Memeriksa status...")
        tk.Label(status_frame, textvariable=self.status_var,
                font=("Segoe UI", 11), fg=self.colors['text_secondary'],
                bg=self.colors['bg_light']).pack(side=tk.LEFT, padx=(5, 0))
        
        self.timestamp_var = tk.StringVar(value="")
        tk.Label(right, textvariable=self.timestamp_var,
                font=("Segoe UI", 9), fg=self.colors['text_muted'],
                bg=self.colors['bg_light']).pack(anchor="e", pady=(5, 0))
        
    def _build_controls(self, parent):
        """Build control panel"""
        control = tk.Frame(parent, bg=self.colors['bg_dark'], padx=30, pady=20)
        control.pack(fill=tk.X)
        
        # Left - Tombol utama
        left = tk.Frame(control, bg=self.colors['bg_dark'])
        left.pack(side=tk.LEFT)
        
        self.scan_btn_frame = create_rounded_button(
            left, "Mulai Scanning", self.start_scanning,
            self.colors['primary'], self.colors['primary_hover'], icon="🔍")
        self.scan_btn_frame.pack(side=tk.LEFT, padx=(0, 10))
        self.scan_btn = self.scan_btn_frame.winfo_children()[0]
        
        create_rounded_button(left, "Refresh", self.refresh_status,
            self.colors['success'], "#34d399", icon="🔄").pack(side=tk.LEFT, padx=(0, 10))
        
        export_btn = create_rounded_button(left, "Export", self.export_results,
            self.colors['secondary'], "#67e8f9", fg_color=self.colors['bg_dark'])
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        ModernTooltip(export_btn, "Export hasil scan ke file TXT atau CSV")
        
        # Right - Filter dan Auto Refresh
        right = tk.Frame(control, bg=self.colors['bg_dark'])
        right.pack(side=tk.RIGHT)
        
        # Filter
        filter_frame = tk.Frame(right, bg=self.colors['card'], padx=2, pady=2)
        filter_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(filter_frame, text="🔎", font=("Segoe UI Emoji", 12),
                bg=self.colors['card'], fg=self.colors['text_muted']).pack(side=tk.LEFT, padx=(10, 5))
        
        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(filter_frame, textvariable=self.filter_var,
                                    font=("Segoe UI", 10), bg=self.colors['card'],
                                    fg=self.colors['text_primary'],
                                    insertbackground=self.colors['text_primary'],
                                    relief="flat", width=20)
        self.filter_entry.pack(side=tk.LEFT, padx=5, pady=8)
        self.filter_entry.insert(0, "Filter jaringan...")
        self.filter_entry.bind('<FocusIn>', lambda e: self.filter_entry.delete(0, tk.END) 
                               if self.filter_entry.get() == "Filter jaringan..." else None)
        self.filter_entry.bind('<FocusOut>', lambda e: self.filter_entry.insert(0, "Filter jaringan...") 
                               if not self.filter_entry.get() else None)
        
        # Auto Refresh toggle
        auto_frame = tk.Frame(right, bg=self.colors['card'], padx=15, pady=10)
        auto_frame.pack(side=tk.LEFT)
        
        tk.Label(auto_frame, text="Auto Refresh", font=("Segoe UI", 10),
                bg=self.colors['card'], fg=self.colors['text_secondary']).pack(side=tk.LEFT, padx=(0, 10))
        
        self.toggle_btn = tk.Label(auto_frame, text="○", font=("Segoe UI", 20),
                                  fg=self.colors['text_muted'], bg=self.colors['card'], cursor="hand2")
        self.toggle_btn.pack(side=tk.LEFT)
        self.toggle_btn.bind('<Button-1>', self.toggle_auto_refresh)
        ModernTooltip(auto_frame, "Auto refresh setiap 10 detik")
        
        # Progress bar
        progress_container = tk.Frame(parent, bg=self.colors['bg_dark'], padx=30)
        progress_container.pack(fill=tk.X)
        self.progress = AnimatedProgressBar(progress_container, height=4, width=100)
        self.progress.pack(fill=tk.X)
        
    def _build_stats(self, parent):
        """Build stats cards"""
        stats = tk.Frame(parent, bg=self.colors['bg_dark'], padx=30, pady=15)
        stats.pack(fill=tk.X)
        
        cards = tk.Frame(stats, bg=self.colors['bg_dark'])
        cards.pack(fill=tk.X)
        
        self.total_card = create_stat_card(cards, "Total Jaringan", "0", "📊", self.colors['primary'])
        self.total_card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        self.secure_card = create_stat_card(cards, "Jaringan Aman", "0", "🔒", self.colors['success'])
        self.secure_card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        self.open_card = create_stat_card(cards, "Jaringan Terbuka", "0", "🔓", self.colors['warning'])
        self.open_card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        self.best_signal_card = create_stat_card(cards, "Sinyal Terkuat", "N/A", "📶", self.colors['secondary'])
        self.best_signal_card.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
    def _build_table(self, parent):
        """Build results table"""
        results = tk.Frame(parent, bg=self.colors['bg_dark'], padx=30, pady=10)
        results.pack(fill=tk.BOTH, expand=True)
        
        table_container = tk.Frame(results, bg=self.colors['border'], padx=1, pady=1)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        table_inner = tk.Frame(table_container, bg=self.colors['bg_medium'])
        table_inner.pack(fill=tk.BOTH, expand=True)
        
        columns = ('No', 'SSID', 'Signal', 'Level', 'Security', 'BSSID', 'Band')
        self.tree = ttk.Treeview(table_inner, columns=columns, show='headings', 
                                style="Modern.Treeview", height=12)
        
        headings = [('No', 'No.', 50), ('SSID', '📡 Nama Jaringan', 200),
                   ('Signal', '📶 Sinyal', 100), ('Level', '📊 Level', 100),
                   ('Security', '🔒 Keamanan', 120), ('BSSID', '🏷️ BSSID', 150),
                   ('Band', '📻 Band', 80)]
        
        for col, heading, width in headings:
            self.tree.heading(col, text=heading, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, anchor=tk.CENTER if col != 'SSID' else tk.W)
        
        scrollbar = ttk.Scrollbar(table_inner, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _build_footer(self, parent):
        """Build footer"""
        footer = tk.Frame(parent, bg=self.colors['bg_light'], height=60)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        center = tk.Frame(footer, bg=self.colors['bg_light'])
        center.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(center, text=f"📡 Dibuat oleh {APP_CONFIG['author']} | Network Programming | Tugas Besar © {APP_CONFIG['year']}",
                font=("Segoe UI Semibold", 11), fg=self.colors['text_secondary'],
                bg=self.colors['bg_light']).pack(expand=True)
        
        tk.Label(center, text="💡 Double-click pada jaringan untuk melihat detail IP Address",
                font=("Segoe UI", 9), fg=self.colors['text_muted'],
                bg=self.colors['bg_light']).pack(pady=(0, 10))
        
    def setup_events(self):
        """Setup event handlers"""
        self.tree.bind('<Double-Button-1>', self.on_item_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.filter_var.trace('w', self.filter_networks)
        
    # ==================== EVENT HANDLERS ====================
    
    def sort_by_column(self, column):
        """Sort tabel berdasarkan kolom"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        items = [(self.tree.set(item, column), item) for item in self.tree.get_children('')]
        
        if column in ['Signal', 'No']:
            try:
                items.sort(key=lambda x: int(x[0].replace('%', '').replace('N/A', '0')), 
                          reverse=self.sort_reverse)
            except:
                items.sort(reverse=self.sort_reverse)
        else:
            items.sort(reverse=self.sort_reverse)
        
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
            
    def filter_networks(self, *args):
        """Filter jaringan"""
        filter_text = self.filter_var.get().lower()
        if filter_text in ["filter jaringan...", ""]:
            self.display_results()
            return
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, network in enumerate(self.networks, 1):
            ssid = network.get('SSID', 'Unknown').lower()
            security = network.get('Security', 'Unknown').lower()
            if filter_text in ssid or filter_text in security:
                self._add_network_to_tree(i, network)
    
    def toggle_auto_refresh(self, event=None):
        """Toggle auto refresh"""
        self.auto_refresh = not self.auto_refresh
        if self.auto_refresh:
            self.toggle_btn.configure(text="●", fg=self.colors['success'])
            self.auto_refresh_scan()
        else:
            self.toggle_btn.configure(text="○", fg=self.colors['text_muted'])
    
    def auto_refresh_scan(self):
        """Auto refresh scanning"""
        if self.auto_refresh:
            self.start_scanning()
            self.root.after(self.auto_refresh_interval, self.auto_refresh_scan)
    
    def show_context_menu(self, event):
        """Context menu saat klik kanan"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = tk.Menu(self.root, tearoff=0, bg=self.colors['card'], 
                          fg=self.colors['text_primary'], font=("Segoe UI", 10))
            menu.add_command(label="📋 Lihat Detail", command=lambda: self.on_item_double_click(None))
            menu.add_command(label="🔗 Connect", command=self.connect_to_selected)
            menu.add_separator()
            menu.add_command(label="📄 Copy SSID", command=self.copy_selected_ssid)
            menu.add_command(label="📄 Copy BSSID", command=self.copy_selected_bssid)
            menu.tk_popup(event.x_root, event.y_root)
    
    def on_item_double_click(self, event):
        """Handle double click"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        ssid, signal, security, bssid, band = values[1], values[2], values[4], values[5], values[6]
        ip_info = get_ip_info(ssid)
        self.show_network_details(ssid, signal, security, bssid, band, ip_info)
    
    # ==================== ACTIONS ====================
    
    def refresh_status(self):
        """Refresh status adapter"""
        status, message = check_wifi_adapter()
        self.status_var.set(message)
        
        color_map = {'connected': self.colors['success'], 'disconnected': self.colors['warning'],
                    'not_found': self.colors['danger'], 'error': self.colors['danger']}
        self.status_dot.configure(fg=color_map.get(status, self.colors['text_muted']))
    
    def start_scanning(self):
        """Mulai scanning"""
        self.scan_btn.configure(text="⏳ Scanning...")
        self.progress.start()
        self.status_var.set("Sedang Scanning...")
        self.status_dot.configure(fg=self.colors['warning'])
        
        thread = threading.Thread(target=self._do_scan)
        thread.daemon = True
        thread.start()
    
    def _do_scan(self):
        """Proses scanning di thread terpisah"""
        self.networks = scan_wifi_networks()
        self.root.after(0, self.display_results)
        self.root.after(0, self._scanning_complete)
    
    def _scanning_complete(self):
        """Ketika scanning selesai"""
        self.progress.stop()
        self.scan_btn.configure(text="🔍 Mulai Scanning")
        self.refresh_status()
        self.timestamp_var.set(f"Terakhir scan: {datetime.now().strftime('%H:%M:%S')}")
        
        if not self.auto_refresh:
            show_toast(self.root, f"✓ Ditemukan {len(self.networks)} jaringan WiFi", 
                      self.colors['success'])
    
    def display_results(self):
        """Menampilkan hasil scan"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update stats
        total = len(self.networks)
        secure = sum(1 for n in self.networks if 'WPA' in n.get('Security', ''))
        open_nets = sum(1 for n in self.networks if 'Open' in n.get('Security', ''))
        best_signal = max((n.get('Signal', 0) for n in self.networks), default=0)
        
        self.total_card.value_label.configure(text=str(total))
        self.secure_card.value_label.configure(text=str(secure))
        self.open_card.value_label.configure(text=str(open_nets))
        self.best_signal_card.value_label.configure(text=f"{best_signal}%")
        
        for i, network in enumerate(self.networks, 1):
            self._add_network_to_tree(i, network)
        
        # Configure tags
        tags_map = {'excellent': '#064e3b', 'good': '#1e3a5f', 'fair': '#713f12',
                   'weak': '#7f1d1d', 'veryweak': '#374151'}
        for tag, color in tags_map.items():
            self.tree.tag_configure(tag, background=color)
    
    def _add_network_to_tree(self, index, network):
        """Menambahkan jaringan ke tree"""
        ssid = network.get('SSID', 'Unknown')
        signal = f"{network.get('Signal', 0)}%"
        level = network.get('Level', 'Unknown')
        security = network.get('Security', 'Unknown')
        bssid = network.get('BSSID', 'N/A')
        band = network.get('Band', 'N/A')
        
        tag_map = {'Excellent': 'excellent', 'Good': 'good', 'Fair': 'fair', 
                  'Weak': 'weak', 'Very': 'veryweak'}
        tags = ('veryweak',)
        for key, tag in tag_map.items():
            if key in level:
                tags = (tag,)
                break
        
        self.tree.insert('', 'end', values=(index, ssid, signal, level, security, bssid, band), tags=tags)
    
    def export_results(self):
        """Export hasil scan"""
        if not self.networks:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk di-export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")],
            title="Export Hasil Scan")
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.csv'):
                    f.write("No,SSID,Signal,Level,Security,BSSID,Band\n")
                    for i, n in enumerate(self.networks, 1):
                        f.write(f"{i},{n.get('SSID','')},{n.get('Signal',0)}%,{n.get('Level','')},{n.get('Security','')},{n.get('BSSID','')},{n.get('Band','')}\n")
                else:
                    f.write("=" * 70 + "\n")
                    f.write(f"           WiFi Scanner Pro - Hasil Scan\n")
                    f.write(f"           Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 70 + "\n\n")
                    for i, n in enumerate(self.networks, 1):
                        f.write(f"[{i}] {n.get('SSID','')}\n")
                        f.write(f"    Sinyal: {n.get('Signal',0)}% | Level: {n.get('Level','')}\n")
                        f.write(f"    Keamanan: {n.get('Security','')} | BSSID: {n.get('BSSID','')}\n")
                        f.write("-" * 50 + "\n")
                    f.write(f"\nTotal: {len(self.networks)} jaringan | Dibuat oleh: {APP_CONFIG['author']}\n")
            
            messagebox.showinfo("Berhasil", f"Export berhasil ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {str(e)}")
    
    def connect_to_selected(self):
        """Connect ke jaringan terpilih"""
        selected = self.tree.selection()
        if not selected:
            return
        
        ssid = self.tree.item(selected[0])['values'][1]
        success, message = connect_to_network(ssid)
        
        if success:
            messagebox.showinfo("Berhasil", message)
        else:
            messagebox.showwarning("Info", message)
    
    def copy_selected_ssid(self):
        """Copy SSID"""
        selected = self.tree.selection()
        if selected:
            copy_to_clipboard(self.root, self.tree.item(selected[0])['values'][1], self.colors)
    
    def copy_selected_bssid(self):
        """Copy BSSID"""
        selected = self.tree.selection()
        if selected:
            copy_to_clipboard(self.root, self.tree.item(selected[0])['values'][5], self.colors)
    
    def show_network_details(self, ssid, signal, security, bssid, band, ip_info):
        """Menampilkan detail jaringan"""
        detail = tk.Toplevel(self.root)
        detail.title(f"Detail: {ssid}")
        detail.geometry("550x650")
        detail.resizable(False, False)
        detail.configure(bg=self.colors['bg_dark'])
        detail.transient(self.root)
        detail.grab_set()
        
        # Center
        detail.update_idletasks()
        x = (detail.winfo_screenwidth() // 2) - 275
        y = (detail.winfo_screenheight() // 2) - 325
        detail.geometry(f"550x650+{x}+{y}")
        
        # Header
        header = tk.Frame(detail, bg=self.colors['primary'], height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_content = tk.Frame(header, bg=self.colors['primary'])
        header_content.pack(expand=True)
        
        tk.Label(header_content, text=f"📡 {ssid}", font=("Segoe UI", 18, "bold"),
                fg="white", bg=self.colors['primary']).pack(pady=(20, 5))
        
        status_text = "✅ Terhubung" if ip_info['connected'] else "⚪ Tidak Terhubung"
        status_bg = self.colors['success'] if ip_info['connected'] else self.colors['text_muted']
        
        status_frame = tk.Frame(header_content, bg=status_bg, padx=15, pady=3)
        status_frame.pack()
        tk.Label(status_frame, text=status_text, font=("Segoe UI", 10),
                fg="white", bg=status_bg).pack()
        
        # Content
        content = tk.Frame(detail, bg=self.colors['bg_dark'], padx=25, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Network Info
        self._create_info_section(content, "Informasi Jaringan", [
            ("SSID", ssid), ("Kekuatan Sinyal", signal), ("Keamanan", security),
            ("BSSID", bssid), ("Band", band)])
        
        # IP Info
        self._create_info_section(content, "Informasi IP Address", [
            ("IP Lokal", ip_info['local_ip']), ("IP Publik", ip_info['public_ip']),
            ("Gateway", ip_info['gateway']), ("Subnet Mask", ip_info['subnet']),
            ("DNS Server", ip_info['dns']), ("MAC Address", ip_info['mac'])], show_copy=True)
        
        # Buttons
        btn_frame = tk.Frame(content, bg=self.colors['bg_dark'])
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        create_rounded_button(btn_frame, "Tutup", detail.destroy,
            self.colors['text_muted'], self.colors['border']).pack(side=tk.RIGHT)
    
    def _create_info_section(self, parent, title, data, show_copy=False):
        """Membuat section info"""
        section = tk.Frame(parent, bg=self.colors['card'], padx=15, pady=15)
        section.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(section, text=title, font=("Segoe UI Semibold", 11),
                fg=self.colors['text_primary'], bg=self.colors['card']).pack(anchor="w", pady=(0, 10))
        
        for label, value in data:
            row = tk.Frame(section, bg=self.colors['card'])
            row.pack(fill=tk.X, pady=3)
            
            tk.Label(row, text=f"{label}:", font=("Segoe UI", 10),
                    fg=self.colors['text_muted'], bg=self.colors['card'],
                    width=15, anchor="w").pack(side=tk.LEFT)
            
            tk.Label(row, text=value, font=("Segoe UI", 10),
                    fg=self.colors['text_primary'], bg=self.colors['card']).pack(side=tk.LEFT, padx=(10, 0))
            
            if show_copy and value != "Tidak terdeteksi":
                copy_btn = tk.Label(row, text="📋", font=("Segoe UI Emoji", 10),
                                   fg=self.colors['text_secondary'], bg=self.colors['card'], cursor="hand2")
                copy_btn.pack(side=tk.RIGHT)
                copy_btn.bind('<Button-1>', lambda e, v=value: copy_to_clipboard(self.root, v, self.colors))


def main():
    root = tk.Tk()
    app = WiFiScannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()