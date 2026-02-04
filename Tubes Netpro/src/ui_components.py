# ui_components.py
# Komponen UI untuk WiFi Scanner
# Dibuat oleh Zidan Ardiansyah

import tkinter as tk
from config import COLORS, PROGRESS_COLORS


class ModernTooltip:
    """Tooltip modern dengan animasi"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind('<Enter>', self.show)
        self.widget.bind('<Leave>', self.hide)
    
    def show(self, event=None):
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.attributes('-alpha', 0.95)
        
        frame = tk.Frame(self.tooltip, bg="#1a1a2e", relief="solid", bd=1)
        frame.pack()
        
        label = tk.Label(frame, text=self.text, 
                        bg="#1a1a2e", fg="#eef2ff",
                        font=("Segoe UI", 9), padx=10, pady=5)
        label.pack()
    
    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class AnimatedProgressBar(tk.Canvas):
    """Progress bar dengan animasi gradient"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(highlightthickness=0, bg="#1e1e3f")
        self.gradient_offset = 0
        self.is_running = False
        self.colors = PROGRESS_COLORS
        
    def start(self):
        self.is_running = True
        self.animate()
    
    def stop(self):
        self.is_running = False
        self.delete("all")
    
    def animate(self):
        if not self.is_running:
            return
        
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Animasi gradient bergerak
        bar_width = 150
        x = (self.gradient_offset % (width + bar_width)) - bar_width
        
        # Draw gradient bar
        for i in range(bar_width):
            ratio = i / bar_width
            color_index = int(ratio * (len(self.colors) - 1))
            color = self.colors[min(color_index, len(self.colors) - 1)]
            self.create_rectangle(x + i, 0, x + i + 1, height, fill=color, outline="")
        
        self.gradient_offset += 5
        self.after(30, self.animate)


def create_rounded_button(parent, text, command, bg_color, hover_color, 
                          fg_color="white", width=None, icon=None):
    """Membuat tombol dengan efek hover modern"""
    frame = tk.Frame(parent, bg=parent.cget('bg'))
    
    btn_text = f"{icon} {text}" if icon else text
    
    btn = tk.Label(frame, text=btn_text,
                  font=("Segoe UI Semibold", 10),
                  fg=fg_color, bg=bg_color,
                  padx=20, pady=10,
                  cursor="hand2")
    btn.pack(fill=tk.BOTH, expand=True)
    
    if width:
        btn.configure(width=width)
    
    def on_enter(e):
        btn.configure(bg=hover_color)
    
    def on_leave(e):
        btn.configure(bg=bg_color)
    
    def on_click(e):
        command()
    
    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)
    btn.bind('<Button-1>', on_click)
    
    return frame


def create_stat_card(parent, title, value, icon, accent_color):
    """Membuat card statistik"""
    card = tk.Frame(parent, bg=COLORS['card'], padx=20, pady=15)
    
    # Header dengan icon
    header = tk.Frame(card, bg=COLORS['card'])
    header.pack(fill=tk.X)
    
    icon_label = tk.Label(header, text=icon,
                         font=("Segoe UI Emoji", 16),
                         bg=COLORS['card'])
    icon_label.pack(side=tk.LEFT)
    
    title_label = tk.Label(header, text=title,
                          font=("Segoe UI", 10),
                          fg=COLORS['text_muted'],
                          bg=COLORS['card'])
    title_label.pack(side=tk.LEFT, padx=(10, 0))
    
    # Value
    value_label = tk.Label(card, text=value,
                          font=("Segoe UI", 24, "bold"),
                          fg=accent_color,
                          bg=COLORS['card'])
    value_label.pack(anchor="w", pady=(10, 0))
    
    # Simpan referensi ke value label
    card.value_label = value_label
    
    return card


def show_toast(root, message, bg_color, duration=2000):
    """Menampilkan toast notification"""
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes('-topmost', True)
    toast.attributes('-alpha', 0.95)
    
    x = root.winfo_rootx() + root.winfo_width() // 2 - 150
    y = root.winfo_rooty() + 130
    toast.geometry(f"300x50+{x}+{y}")
    
    frame = tk.Frame(toast, bg=bg_color)
    frame.pack(fill=tk.BOTH, expand=True)
    
    tk.Label(frame, text=message,
            font=("Segoe UI Semibold", 11),
            fg="white", bg=bg_color).pack(expand=True)
    
    toast.after(duration, toast.destroy)


def copy_to_clipboard(root, text, colors):
    """Copy text to clipboard dengan toast notification"""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        
        toast = tk.Toplevel(root)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        toast.attributes('-alpha', 0.9)
        
        x = root.winfo_rootx() + root.winfo_width() // 2 - 100
        y = root.winfo_rooty() + root.winfo_height() - 80
        toast.geometry(f"200x40+{x}+{y}")
        
        frame = tk.Frame(toast, bg=colors['success'])
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="✓ Disalin ke clipboard!",
                font=("Segoe UI", 10),
                fg="white", bg=colors['success']).pack(expand=True)
        
        toast.after(1500, toast.destroy)
    except:
        pass
