"""
main.py
GUI Knapsack Solver — Dynamic Programming / Brute Force / Greedy
Gaya Visual: Neobrutalism
"""

import csv
import logging
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import pygame
    _PYGAME_OK = True
except ImportError:
    _PYGAME_OK = False

from quiz_popup import QuizPopup
from dp_solver import solve_knapsack, Item
from bf_solver import solve_knapsack_bf
from greedy_solver import solve_knapsack_greedy

# ─────────────────────────────────────────────────────────────────
# Logging Setup  (ubah level ke DEBUG untuk output verbose)
# ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)-8s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Palet Warna & Font  (ubah di sini untuk eksperimen desain)
# ─────────────────────────────────────────────────────────────────

C: dict[str, str] = {
    "bg":        "#FAFAF8",
    "black":     "#000000",
    "yellow":    "#FFDE59",
    "pink":      "#EF4444",
    "blue":      "#3B82F6",
    "lime":      "#B8FF57",
    "white":     "#FFFFFF",
    "gray":      "#D0D0D0",
    "dark_gray": "#555555",
}

FONTS: dict[str, tuple] = {
    "title":  ("Space Grotesk", 20, "bold"),
    "head":   ("Space Grotesk", 14, "bold"),
    "body":   ("Inter", 11),
    "body_b": ("Inter", 11, "bold"),
    "small":  ("Inter", 9),
    "btn":    ("Space Grotesk", 12, "bold"),
    "btn_sm": ("Space Grotesk", 10, "bold"),
}


# ─────────────────────────────────────────────────────────────────
# Widget Factory  (neo-brutalism helpers)
# ─────────────────────────────────────────────────────────────────

def neo_frame(parent: tk.Widget, bg: str = C["white"]) -> tk.Frame:
    """Frame dengan border hitam tebal dan hard shadow."""
    outer = tk.Frame(parent, bg=C["black"])
    inner = tk.Frame(outer, bg=bg, highlightbackground=C["black"], highlightthickness=2, padx=16, pady=16)
    inner.pack(padx=(0, 6), pady=(0, 6), fill="both", expand=True)
    # Simpan referensi outer agar bisa di-pack/grid dari luar
    inner._outer = outer  # type: ignore[attr-defined]
    return inner


def neo_label(parent: tk.Widget, text: str, font=None,
              bg: str = C["bg"], fg: str = C["black"], **kw) -> tk.Label:
    return tk.Label(parent, text=text, font=font or FONTS["body"],
                    bg=bg, fg=fg, **kw)


def neo_entry(parent: tk.Widget, textvariable: tk.StringVar,
              width: int = 14, bg: str = C["white"]) -> tk.Frame:
    """Entry dengan border hitam dan hard shadow 2px."""
    shadow = tk.Frame(parent, bg=C["black"])
    entry_frame = tk.Frame(shadow, bg=bg, highlightbackground=C["black"], highlightthickness=2)
    entry_frame.pack(padx=(0, 2), pady=(0, 2), fill="both", expand=True)
    
    tk.Entry(
        entry_frame,
        textvariable=textvariable,
        width=width,
        font=FONTS["body"],
        bg=bg, fg=C["black"],
        insertbackground=C["black"],
        relief="flat", bd=2,
        highlightthickness=0,
    ).pack(padx=2, pady=2)
    return shadow


def neo_button(parent: tk.Widget, text: str, color: str,
               command, font_key: str = "btn", icon_type: str = "",
               padx: int = 16, pady: int = 8) -> tk.Frame:
    """Tombol bergaya neobrutalism universal dengan vector icon opsional."""
    shadow = tk.Frame(parent, bg=C["black"])
    
    face = tk.Frame(shadow, bg=color, highlightthickness=2, highlightbackground=C["black"], cursor="hand2")
    face.pack(fill="both", expand=True, padx=(0, 4), pady=(0, 4))
    
    inner = tk.Frame(face, bg=color, cursor="hand2")
    inner.pack(expand=True, padx=padx, pady=pady)
    
    canvas = None
    if icon_type:
        canvas = tk.Canvas(inner, bg=color, width=20, height=20, bd=0, highlightthickness=0, cursor="hand2")
        canvas.pack(side="left", padx=(0, 6))
        
    text_id = tk.Label(inner, text=text, font=FONTS[font_key], bg=color, fg=C["black"], cursor="hand2")
    text_id.pack(side="left")

    def draw_icon(state="normal"):
        if not canvas: return
        canvas.delete("icon")
        cx, cy = 10, 10
        if icon_type == "reset":
            r = 6
            canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=30, extent=270, style="arc", outline=C["black"], width=2, tags="icon")
            canvas.create_polygon(cx+r-1, cy-3, cx+r+5, cy-1, cx+r+1, cy+4, fill=C["black"], tags="icon")
        elif icon_type == "mute":
            # Geser speaker ke kiri (x: 3 s/d 12) agar X dan gelombang muat di kanan (x: 14 s/d 19)
            canvas.create_polygon(3, 7, 7, 7, 12, 3, 12, 17, 7, 13, 3, 13, fill=color, outline=C["black"], width=2, tags="icon")
            if state == "muted":
                # Coret speaker dengan satu garis miring (slash) yang tebal
                canvas.create_line(14, 2, 2, 18, fill=C["black"], width=3, tags="icon")
            else:
                canvas.create_arc(10, 6, 16, 14, start=-60, extent=120, style="arc", outline=C["black"], width=2, tags="icon")
                canvas.create_arc(6, 2, 20, 18, start=-60, extent=120, style="arc", outline=C["black"], width=2, tags="icon")
        elif icon_type == "plus":
            canvas.create_line(cx, cy-6, cx, cy+6, fill=C["black"], width=2, tags="icon")
            canvas.create_line(cx-6, cy, cx+6, cy, fill=C["black"], width=2, tags="icon")
        elif icon_type == "import":
            canvas.create_line(cx, cy-6, cx, cy+2, fill=C["black"], width=2, tags="icon")
            canvas.create_polygon(cx-4, cy, cx+4, cy, cx, cy+5, fill=C["black"], tags="icon")
            canvas.create_line(cx-6, cy+6, cx+6, cy+6, fill=C["black"], width=2, tags="icon")
        elif icon_type == "export":
            canvas.create_line(cx, cy+2, cx, cy-6, fill=C["black"], width=2, tags="icon")
            canvas.create_polygon(cx-4, cy-2, cx+4, cy-2, cx, cy-7, fill=C["black"], tags="icon")
            canvas.create_line(cx-6, cy+6, cx+6, cy+6, fill=C["black"], width=2, tags="icon")
        elif icon_type == "trash":
            canvas.create_rectangle(cx-4, cy-2, cx+4, cy+6, outline=C["black"], width=2, tags="icon")
            canvas.create_line(cx-6, cy-2, cx+6, cy-2, fill=C["black"], width=2, tags="icon")
            canvas.create_line(cx-2, cy-5, cx+2, cy-5, fill=C["black"], width=2, tags="icon")
        elif icon_type == "lightning":
            canvas.create_polygon(cx+2, cy-7, cx-4, cy+1, cx+1, cy+1, cx-2, cy+7, cx+4, cy-1, cx-1, cy-1, fill=color, outline=C["black"], width=2, tags="icon")
        elif icon_type == "eye":
            canvas.create_arc(cx-8, cy-4, cx+8, cy+6, start=0, extent=180, style="arc", outline=C["black"], width=2, tags="icon")
            canvas.create_arc(cx-8, cy-4, cx+8, cy+6, start=180, extent=180, style="arc", outline=C["black"], width=2, tags="icon")
            if state == "closed":
                canvas.create_line(cx-7, cy-3, cx+7, cy+5, fill=C["black"], width=2, tags="icon")
            else:
                canvas.create_oval(cx-2, cy-1, cx+2, cy+3, fill=C["black"], tags="icon")

    draw_icon("unmuted" if icon_type == "mute" else "normal")

    def on_press(e):
        if shadow._state == "normal": face.pack_configure(padx=(4, 0), pady=(4, 0))
    def on_release(e):
        if shadow._state == "normal":
            face.pack_configure(padx=(0, 4), pady=(0, 4))
            command()

    elements = [face, inner, text_id]
    if canvas: elements.append(canvas)
    for el in elements:
        el.bind("<ButtonPress-1>", on_press)
        el.bind("<ButtonRelease-1>", on_release)
        
    class _BtnProxy:
        pass
    proxy = _BtnProxy()
    
    def config_proxy(**kwargs):
        if "text" in kwargs:
            text_id.configure(text=kwargs["text"])
        if "state" in kwargs:
            shadow._state = kwargs["state"]
            if kwargs["state"] == "disabled":
                text_id.configure(fg=C["dark_gray"])
            else:
                text_id.configure(fg=C["black"])
            
    proxy.config = config_proxy
    shadow._btn = proxy
    shadow._draw_icon = draw_icon
    shadow._state = "normal"
    
    return shadow


# ─────────────────────────────────────────────────────────────────
# Aplikasi Utama
# ─────────────────────────────────────────────────────────────────

class KnapsackApp(tk.Tk):

    # ── Init ──────────────────────────────────────────────────

    def __init__(self) -> None:
        super().__init__()
        self.title("📦 Knapsack Solver — Dynamic Programming")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.minsize(900, 700)

        self.items: list[Item] = []

        # State untuk musik
        self.music_muted: bool = False

        # State untuk Reveal feature
        self.last_result: dict | None = None
        self.last_active_items: list[Item] | None = None
        self.last_max_w: float = 0.0
        self.last_max_v: int = 0
        self.is_revealed: bool = False

        self._init_vars()
        self._build_ui()
        self._init_music()
        self._center_window(1100, 780)
        log.info("Aplikasi dimulai.")

    def _init_music(self) -> None:
        """Inisialisasi pygame mixer dan mulai musik latar secara otomatis."""
        if not _PYGAME_OK:
            log.warning("pygame tidak tersedia, fitur musik dinonaktifkan.")
            return
        try:
            pygame.mixer.init()
            music_path = os.path.join(os.path.dirname(__file__), "bgm.mp3")
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)  # loop selamanya
            self.music_muted = False
            log.info("Musik latar diputar.")
        except Exception as e:
            log.warning("Gagal memuat musik: %s", e)
            self.music_muted = True
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        """Hentikan mixer sebelum keluar agar tidak ada thread yang tersisa."""
        if _PYGAME_OK:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception:
                pass
        self.destroy()

    # ── Variabel Input ────────────────────────────────────────

    def _init_vars(self) -> None:
        """Inisialisasi semua StringVar dan trace otomatis."""
        # Input barang
        self.var_name   = tk.StringVar()
        self.var_weight = tk.StringVar()
        self.var_p      = tk.StringVar()
        self.var_l      = tk.StringVar()
        self.var_t      = tk.StringVar()

        # Input kapasitas tas
        self.var_cap_w  = tk.StringVar()
        self.var_cap_p  = tk.StringVar()
        self.var_cap_l  = tk.StringVar()
        self.var_cap_t  = tk.StringVar()

        # Checkbox aktifkan/nonaktifkan batasan
        self.var_use_weight = tk.BooleanVar(value=True)
        self.var_use_volume = tk.BooleanVar(value=True)

        # Trace volume otomatis
        for v in (self.var_p, self.var_l, self.var_t):
            v.trace_add("write", self._on_item_dim_changed)
        for v in (self.var_cap_p, self.var_cap_l, self.var_cap_t):
            v.trace_add("write", self._on_cap_dim_changed)

        # Trace checkbox → update meter
        self.var_use_weight.trace_add("write", lambda *_: self._on_constraint_toggle())
        self.var_use_volume.trace_add("write", lambda *_: self._on_constraint_toggle())

    # ── Posisi Window ─────────────────────────────────────────

    def _center_window(self, w: int, h: int) -> None:
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ─────────────────────────────────────────────────────────
    # UI Builder
    # ─────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()

        # Build result panel first and pack it at the bottom so it's never pushed off-screen
        self._build_result_panel()

        body = tk.Frame(self, bg=C["bg"])
        body.pack(side="top", fill="both", expand=True, padx=10, pady=8)
        body.columnconfigure(0, weight=0, minsize=200)
        body.columnconfigure(1, weight=1)
        body.columnconfigure(2, weight=0, minsize=220)
        body.rowconfigure(0, weight=1)

        self._build_input_panel(body)
        self._build_list_panel(body)
        self._build_right_panel(body)

    def _build_header(self) -> None:
        hdr = tk.Frame(self, bg=C["yellow"])
        hdr.pack(fill="x")
        tk.Frame(hdr, height=4, bg=C["black"]).pack(fill="x", side="bottom")

        neo_label(hdr, "📦  KNAPSACK SOLVER",
                  font=FONTS["title"], bg=C["yellow"]).pack(
                      side="left", padx=20, pady=14)
        neo_label(hdr, "Dynamic Programming  ·  Multi-Constraint 0/1",
                  font=("Arial", 11, "italic"), bg=C["yellow"],
                  fg=C["dark_gray"]).pack(side="left", padx=4)
        neo_button(hdr, "RESET", C["pink"], self._reset,
                   font_key="btn_sm", icon_type="reset", padx=10, pady=6).pack(
                       side="right", padx=(0, 6), pady=10)
        self.btn_music = neo_button(hdr, "MUTE", C["gray"], self._toggle_music,
                                    font_key="btn_sm", icon_type="mute", padx=10, pady=6)
        self.btn_music.pack(side="right", padx=(0, 6), pady=10)
        if not _PYGAME_OK:
            self.btn_music._btn.config(state="disabled")

    # ── Panel Input Barang ────────────────────────────────────

    def _build_input_panel(self, parent: tk.Frame) -> None:
        inner = neo_frame(parent, bg=C["blue"])
        inner._outer.grid(row=0, column=0, sticky="nsew", padx=(0, 6), pady=4)

        neo_label(inner, "INPUT BARANG", font=FONTS["head"],
                  bg=C["blue"]).pack(anchor="w", pady=(0, 8))
        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=(0, 10))

        self._labeled_entry(inner, "Nama Barang",  self.var_name,   C["blue"])
        self._labeled_entry(inner, "Berat (kg)",   self.var_weight, C["blue"])

        # Dimensi P × L × T
        neo_label(inner, "Dimensi (cm)", font=FONTS["body_b"],
                  bg=C["blue"]).pack(anchor="w", pady=(8, 2))

        dim_row = tk.Frame(inner, bg=C["blue"])
        dim_row.pack(fill="x", pady=2)
        for var, lbl in [(self.var_p, "P"), (self.var_l, "L"), (self.var_t, "T")]:
            cell = tk.Frame(dim_row, bg=C["blue"])
            cell.pack(side="left", padx=(0, 6))
            neo_label(cell, lbl, font=FONTS["small"], bg=C["blue"]).pack(anchor="w")
            neo_entry(cell, textvariable=var, width=6).pack()

        vol_row = tk.Frame(inner, bg=C["blue"])
        vol_row.pack(fill="x", pady=(6, 0))
        neo_label(vol_row, "Volume:", font=FONTS["body_b"], bg=C["blue"]).pack(side="left")
        self._lbl_item_vol = neo_label(vol_row, "belum diisi", bg=C["blue"],
                                        fg=C["dark_gray"])
        self._lbl_item_vol.pack(side="left", padx=6)

        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=10)
        neo_button(inner, "INPUT BARANG", C["pink"],
                   self._add_item, icon_type="plus").pack(pady=4)

    def _labeled_entry(self, parent: tk.Widget, label: str,
                        var: tk.StringVar, bg: str) -> None:
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=4)
        neo_label(row, label + ":", font=FONTS["body_b"], bg=bg).pack(anchor="w")
        neo_entry(row, textvariable=var, width=22).pack(fill="x")

    # ── Panel Daftar Barang ───────────────────────────────────

    def _build_list_panel(self, parent: tk.Frame) -> None:
        inner = neo_frame(parent, bg=C["white"])
        inner._outer.grid(row=0, column=1, sticky="nsew", padx=6, pady=4)

        neo_label(inner, "DAFTAR BARANG", font=FONTS["head"],
                  bg=C["white"]).pack(anchor="w", pady=(0, 8))
        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=(0, 6))

        self._setup_treeview(inner)
        
        btn_row = tk.Frame(inner, bg=C["white"])
        btn_row.pack(fill="x", pady=(8, 0))
        
        neo_button(btn_row, "IMPORT CSV", C["blue"],
                   self._import_csv, font_key="btn_sm",
                   icon_type="import", padx=10, pady=6).pack(side="left", padx=(0, 4))
        
        neo_button(btn_row, "EXPORT CSV", C["yellow"],
                   self._export_csv, font_key="btn_sm",
                   icon_type="export", padx=10, pady=6).pack(side="left", padx=4)
        
        neo_button(btn_row, "HAPUS", C["gray"],
                   self._delete_item, font_key="btn_sm",
                   icon_type="trash", padx=10, pady=6).pack(side="right", padx=(4, 0))

    def _setup_treeview(self, parent: tk.Widget) -> None:
        wrapper = tk.Frame(parent, bg=C["black"], bd=2)
        wrapper.pack(fill="both", expand=True)

        cols = ("sim", "no", "nama", "berat", "volume", "nilai")
        self.tree = ttk.Treeview(wrapper, columns=cols, show="headings",
                                  height=10, selectmode="browse")

        col_defs = [
            ("sim",    "Sim",       50),
            ("no",     "No",        40),
            ("nama",   "Nama",     130),
            ("berat",  "Berat(kg)", 80),
            ("volume", "Vol(cm³)",  90),
            ("nilai",  "Nilai ★",   80),
        ]
        for col, heading, width in col_defs:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=C["white"], foreground=C["black"],
                         rowheight=28, fieldbackground=C["white"],
                         font=FONTS["body"], borderwidth=0)
        style.configure("Treeview.Heading",
                         background=C["black"], foreground=C["yellow"],
                         font=FONTS["body_b"], borderwidth=0, relief="flat")
        style.map("Treeview",
                  background=[("selected", C["yellow"])],
                  foreground=[("selected", C["black"])])

        scroll = ttk.Scrollbar(wrapper, orient="vertical",
                                command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        scroll.pack(side="right", fill="y", padx=(0, 2), pady=2)

        # Bind event klik untuk checkbox
        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)

    def _on_tree_click(self, event) -> None:
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        col = self.tree.identify_column(event.x)
        if col == "#1":  # Kolom "Sim"
            row_id = self.tree.identify_row(event.y)
            if row_id:
                vals = list(self.tree.item(row_id, "values"))
                idx = int(vals[1]) - 1  # vals[1] is "no"
                
                # Toggle status simulasi
                if vals[0] == "☑":
                    vals[0] = "☐"
                    self.items[idx]["active"] = False
                else:
                    vals[0] = "☑"
                    self.items[idx]["active"] = True
                
                self.tree.item(row_id, values=vals)
                self._update_sim_meters()

    # ── Panel Kanan: Kapasitas + Simulasi ─────────────────────

    def _build_right_panel(self, parent: tk.Frame) -> None:
        inner = neo_frame(parent, bg=C["yellow"])
        inner._outer.grid(row=0, column=2, sticky="nsew", padx=(0, 0), pady=4)

        neo_label(inner, "KAPASITAS TAS", font=FONTS["head"],
                  bg=C["yellow"]).pack(anchor="w", pady=(0, 4))
        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=(0, 10))

        # ── Berat Maks + Checkbox ─────────────────────────────
        w_row = tk.Frame(inner, bg=C["yellow"])
        w_row.pack(fill="x")
        neo_label(w_row, "Berat Maks (kg):", font=FONTS["body_b"],
                  bg=C["yellow"]).pack(side="left")
        self._chk_weight = tk.Checkbutton(
            w_row, text="Aktif", variable=self.var_use_weight,
            bg=C["yellow"], fg=C["black"], selectcolor=C["white"],
            activebackground=C["yellow"], font=FONTS["small"],
            relief="flat", cursor="hand2",
        )
        self._chk_weight.pack(side="right")
        self._entry_cap_w = neo_entry(inner, textvariable=self.var_cap_w, width=10)
        self._entry_cap_w.pack(anchor="w", pady=(2, 8))

        # ── Dimensi Tas + Checkbox ────────────────────────────
        v_row = tk.Frame(inner, bg=C["yellow"])
        v_row.pack(fill="x")
        neo_label(v_row, "Dimensi Tas (cm):", font=FONTS["body_b"],
                  bg=C["yellow"]).pack(side="left")
        self._chk_volume = tk.Checkbutton(
            v_row, text="Aktif", variable=self.var_use_volume,
            bg=C["yellow"], fg=C["black"], selectcolor=C["white"],
            activebackground=C["yellow"], font=FONTS["small"],
            relief="flat", cursor="hand2",
        )
        self._chk_volume.pack(side="right")
        self._frame_dim = tk.Frame(inner, bg=C["yellow"])
        self._frame_dim.pack(anchor="w", pady=(2, 0))
        for var, lbl in [(self.var_cap_p, "P"), (self.var_cap_l, "L"), (self.var_cap_t, "T")]:
            cell = tk.Frame(self._frame_dim, bg=C["yellow"])
            cell.pack(side="left", padx=(0, 4))
            neo_label(cell, lbl, font=FONTS["small"], bg=C["yellow"]).pack(anchor="w")
            neo_entry(cell, textvariable=var, width=5).pack()

        vol_row = tk.Frame(inner, bg=C["yellow"])
        vol_row.pack(fill="x", pady=(6, 0))
        neo_label(vol_row, "Vol Maks:", font=FONTS["body_b"], bg=C["yellow"]).pack(side="left")
        self._lbl_cap_vol = neo_label(vol_row, "belum diisi", bg=C["yellow"], fg=C["dark_gray"])
        self._lbl_cap_vol.pack(side="left", padx=4)

        # ── Simulasi Meter ────────────────────────────────────
        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=(12, 8))
        neo_label(inner, "SIMULASI 🎒", font=FONTS["body_b"],
                  bg=C["yellow"]).pack(anchor="w", pady=(0, 6))

        # Berat meter
        neo_label(inner, "⚖  Berat:", font=FONTS["small"], bg=C["yellow"]).pack(anchor="w")
        self.sim_bar_w = tk.Canvas(inner, bg=C["white"], height=18,
                                   highlightthickness=2, highlightbackground=C["black"])
        self.sim_bar_w.pack(fill="x", pady=(2, 0))
        self.sim_lbl_w = neo_label(inner, "0 kg / — kg", font=FONTS["small"],
                                   bg=C["yellow"], fg=C["dark_gray"])
        self.sim_lbl_w.pack(anchor="w", pady=(2, 8))

        # Volume meter
        neo_label(inner, "📦  Volume:", font=FONTS["small"], bg=C["yellow"]).pack(anchor="w")
        self.sim_bar_v = tk.Canvas(inner, bg=C["white"], height=18,
                                   highlightthickness=2, highlightbackground=C["black"])
        self.sim_bar_v.pack(fill="x", pady=(2, 0))
        self.sim_lbl_v = neo_label(inner, "0 cm³ / — cm³", font=FONTS["small"],
                                   bg=C["yellow"], fg=C["dark_gray"])
        self.sim_lbl_v.pack(anchor="w", pady=(2, 8))

        # Value meter
        self.sim_lbl_val = neo_label(inner, "🏆  Nilai Sim  :  0", font=FONTS["small"],
                                     bg=C["yellow"])
        self.sim_lbl_val.pack(anchor="w", pady=(0, 12))

        # ── Tombol Hitung ─────────────────────────────────────
        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=(0, 8))
        
        btn_row = tk.Frame(inner, bg=C["yellow"])
        btn_row.pack(fill="x", pady=(4, 2))
        
        neo_button(btn_row, "BRUTE FORCE", C["lime"],
                   self._solve_bf, font_key="btn_sm",
                   padx=8, pady=6).pack(side="left", fill="x", expand=True, padx=(0, 2))
        neo_button(btn_row, "GREEDY", C["blue"],
                   self._solve_greedy, font_key="btn_sm",
                   padx=8, pady=6).pack(side="left", fill="x", expand=True, padx=(2, 0))
                   
        neo_button(inner, "SOLUSI OPTIMAL (DP)", C["pink"],
                   self._solve, icon_type="lightning").pack(fill="x", pady=(2, 4))

    # ── Panel Hasil ───────────────────────────────────────────

    def _build_result_panel(self) -> None:
        inner = neo_frame(self, bg=C["lime"])
        inner._outer.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        inner.configure(pady=10)

        header_frame = tk.Frame(inner, bg=C["lime"])
        header_frame.pack(fill="x", anchor="w")
        neo_label(header_frame, "HASIL SOLUSI", font=FONTS["head"],
                  bg=C["lime"]).pack(side="left")
                  
        self.btn_reveal = neo_button(header_frame, "LIHAT SOLUSI", C["yellow"],
                                     self._toggle_reveal, font_key="btn_sm",
                                     icon_type="eye", padx=10, pady=4)
        self.btn_reveal.pack(side="right")
        self.btn_reveal._btn.config(state="disabled")

        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=(4, 8))

        # Frame untuk Text Info
        self.result_info_frame = tk.Frame(inner, bg=C["lime"])
        self.result_info_frame.pack(fill="x", pady=(0, 10))
        
        left_info = tk.Frame(self.result_info_frame, bg=C["lime"])
        left_info.pack(side="left", fill="both", expand=True)
        
        self.lbl_val = neo_label(left_info, "Tekan ⚡ CARI SOLUSI OPTIMAL untuk mulai menghitung.", bg=C["lime"], justify="left")
        self.lbl_val.pack(anchor="w")
        self.lbl_weight = neo_label(left_info, "", bg=C["lime"], justify="left")
        self.lbl_vol = neo_label(left_info, "", bg=C["lime"], justify="left")
        
        right_info = tk.Frame(self.result_info_frame, bg=C["lime"])
        right_info.pack(side="right", fill="y")
        
        self.lbl_time = neo_label(right_info, "", font=FONTS["small"], bg=C["lime"], fg=C["dark_gray"])
        self.lbl_time.pack(side="bottom", anchor="se")
        
        # Bar Kapasitas selalu ada
        self.canvas_vis = tk.Canvas(inner, bg=C["white"], height=30, highlightthickness=2, highlightbackground=C["black"])
        self.canvas_vis.pack(fill="x", pady=(0, 10))

        # Frame untuk Badges (menggunakan Text widget agar otomatis wrap)
        self.lbl_badges_title = neo_label(inner, "Barang yang masuk tas:", bg=C["lime"], font=FONTS["body_b"])
        self.badges_text = tk.Text(inner, bg=C["lime"], bd=0, highlightthickness=0, height=3, wrap="word", state="disabled", font=FONTS["small"])

    # ─────────────────────────────────────────────────────────
    # Trace Callbacks (Volume Otomatis)
    # ─────────────────────────────────────────────────────────

    def _on_item_dim_changed(self, *_) -> None:
        vol = self._parse_volume(self.var_p, self.var_l, self.var_t)
        self._lbl_item_vol.config(
            text=f"{vol:,} cm³" if vol else "— cm³",
            fg=C["black"] if vol else C["dark_gray"],
        )

    def _on_cap_dim_changed(self, *_) -> None:
        vol = self._parse_volume(self.var_cap_p, self.var_cap_l, self.var_cap_t)
        self._lbl_cap_vol.config(
            text=f"{vol:,} cm³" if vol else "— cm³",
            fg=C["black"] if vol else C["dark_gray"],
        )
        # Refresh simulasi meter karena max kapasitas bisa berubah
        self._update_sim_meters()

    @staticmethod
    def _parse_volume(vp: tk.StringVar, vl: tk.StringVar,
                      vt: tk.StringVar) -> int:
        """Hitung volume dari tiga StringVar. Return 0 jika input invalid."""
        try:
            p, l, t = float(vp.get()), float(vl.get()), float(vt.get())
            return int(p * l * t) if p > 0 and l > 0 and t > 0 else 0
        except ValueError:
            return 0

    # ─────────────────────────────────────────────────────────
    # Action Handlers
    # ─────────────────────────────────────────────────────────

    def _add_item(self) -> None:
        """Validasi input, buka kuis, simpan barang."""
        name   = self.var_name.get().strip()
        weight = self.var_weight.get().strip()
        volume = self._parse_volume(self.var_p, self.var_l, self.var_t)

        if not name:
            messagebox.showwarning("Input Kurang", "Nama barang tidak boleh kosong.")
            return
        try:
            w = float(weight)
            assert w > 0
        except (ValueError, AssertionError):
            messagebox.showwarning("Input Salah",
                                   "Berat harus berupa angka positif.")
            return
        if volume <= 0:
            messagebox.showwarning("Input Kurang",
                                   "Masukkan dimensi barang (P, L, T) dengan benar.")
            return

        log.debug("Membuka kuis untuk barang '%s' (%.1fkg, %dcm³)",
                  name, w, volume)

        popup = QuizPopup(self, name)
        self.wait_window(popup)

        if popup.result is None:
            log.debug("Kuis dibatalkan, barang tidak ditambahkan.")
            return

        item: Item = {"name": name, "weight": w, "volume": volume,
                       "value": popup.result, "active": False}  # default: tidak dicentang
        self.items.append(item)
        log.info("Barang ditambahkan: %s", item)

        stars = "★" * popup.result + "☆" * (5 - popup.result)
        self.tree.insert("", "end", values=(
            "☐", len(self.items), name, f"{w}", f"{volume:,}", stars,
        ))

        # Reset field input barang
        for var in (self.var_name, self.var_weight,
                    self.var_p, self.var_l, self.var_t):
            var.set("")

    def _delete_item(self) -> None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Pilih Barang",
                                "Pilih barang yang ingin dihapus.")
            return

        idx = self.tree.index(sel[0])
        removed = self.items.pop(idx)
        self.tree.delete(sel[0])
        log.info("Barang dihapus: %s", removed)

        # Renumber
        for i, iid in enumerate(self.tree.get_children()):
            vals = list(self.tree.item(iid, "values"))
            vals[1] = i + 1
            self.tree.item(iid, values=vals)

    def _import_csv(self) -> None:
        filepath = filedialog.askopenfilename(
            title="Import CSV Barang",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    name = row.get("Nama", "").strip()
                    weight_str = row.get("Berat(kg)", "0")
                    volume_str = row.get("Volume(cm3)", "0")
                    value_str = row.get("Nilai", "0")

                    if not name:
                        continue

                    w = float(weight_str)
                    v = int(volume_str)
                    val = int(value_str)

                    item: Item = {"name": name, "weight": w, "volume": v, "value": val, "active": False}  # default: tidak dicentang
                    self.items.append(item)
                    
                    stars = "★" * val + "☆" * max(0, 5 - val)
                    self.tree.insert("", "end", values=(
                        "☐", len(self.items), name, f"{w}", f"{v:,}", stars,
                    ))
                    count += 1
            log.info("Berhasil import %d barang dari CSV", count)
            messagebox.showinfo("Import Berhasil", f"Berhasil mengimpor {count} barang.")
        except Exception as e:
            log.error("Gagal import CSV: %s", e)
            messagebox.showerror("Error Import", f"Gagal membaca file CSV.\nPastikan format kolom benar: Nama, Berat(kg), Volume(cm3), Nilai.\nDetail: {e}")

    def _export_csv(self) -> None:
        if not self.items:
            messagebox.showwarning("Kosong", "Belum ada barang untuk di-export.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Export CSV Barang",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["Nama", "Berat(kg)", "Volume(cm3)", "Nilai"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for item in self.items:
                    writer.writerow({
                        "Nama": item["name"],
                        "Berat(kg)": item["weight"],
                        "Volume(cm3)": item["volume"],
                        "Nilai": item["value"],
                    })
            log.info("Berhasil export %d barang ke CSV", len(self.items))
            messagebox.showinfo("Export Berhasil", f"Data berhasil disimpan di:\n{filepath}")
        except Exception as e:
            log.error("Gagal export CSV: %s", e)
            messagebox.showerror("Error Export", f"Gagal menyimpan file CSV.\n{e}")

    def _update_sim_meters(self) -> None:
        """Update progress bar simulasi (berat, volume, value) berdasarkan item yang dicentang."""
        sim_items = [it for it in self.items if it.get("active", False)]
        total_w   = sum(it["weight"] for it in sim_items)
        total_v   = sum(it["volume"] for it in sim_items)
        total_val = sum(it["value"]  for it in sim_items)
        max_val   = sum(it["value"]  for it in self.items)

        try:
            max_w = float(self.var_cap_w.get())
        except ValueError:
            max_w = 0
        max_v = self._parse_volume(self.var_cap_p, self.var_cap_l, self.var_cap_t)

        # Update label berat
        if max_w > 0:
            pct_w = min(total_w / max_w, 1.0)
            self.sim_lbl_w.config(text=f"{total_w:.1f} kg / {max_w:.1f} kg  ({pct_w*100:.0f}%)",
                                   fg=C["pink"] if pct_w >= 1.0 else C["black"])
        else:
            pct_w = 0
            self.sim_lbl_w.config(text=f"{total_w:.1f} kg / — kg", fg=C["dark_gray"])

        # Update label volume
        if max_v > 0:
            pct_v = min(total_v / max_v, 1.0)
            self.sim_lbl_v.config(text=f"{total_v:,} cm³ / {max_v:,} cm³  ({pct_v*100:.0f}%)",
                                   fg=C["pink"] if pct_v >= 1.0 else C["black"])
        else:
            pct_v = 0
            self.sim_lbl_v.config(text=f"{total_v:,} cm³ / — cm³", fg=C["dark_gray"])

        # Gambar bar berat
        self.sim_bar_w.update_idletasks()
        cw = self.sim_bar_w.winfo_width() or 180
        ch = int(self.sim_bar_w["height"])
        self.sim_bar_w.delete("all")
        if pct_w > 0:
            bar_color = C["pink"] if pct_w >= 1.0 else C["lime"]
            self.sim_bar_w.create_rectangle(0, 0, cw * pct_w, ch, fill=bar_color, outline="")

        # Gambar bar volume
        self.sim_bar_v.update_idletasks()
        cw = self.sim_bar_v.winfo_width() or 180
        ch = int(self.sim_bar_v["height"])
        self.sim_bar_v.delete("all")
        if pct_v > 0:
            bar_color = C["pink"] if pct_v >= 1.0 else C["blue"]
            self.sim_bar_v.create_rectangle(0, 0, cw * pct_v, ch, fill=bar_color, outline="")

        # Update value
        self.sim_lbl_val.config(text=f"🏆  Nilai Sim  :  {total_val} / {max_val}")

    # ─────────────────────────────────────────────────────────
    # Constraint Toggle Helper
    # ─────────────────────────────────────────────────────────

    def _on_constraint_toggle(self) -> None:
        """Aktifkan/nonaktifkan widget input sesuai checkbox."""
        use_w = self.var_use_weight.get()
        use_v = self.var_use_volume.get()

        state_w = "normal" if use_w else "disabled"
        state_v = "normal" if use_v else "disabled"

        def set_state(widget: tk.Widget, state: str) -> None:
            if isinstance(widget, tk.Entry):
                widget.configure(state=state)
            for child in widget.winfo_children():
                set_state(child, state)

        set_state(self._entry_cap_w, state_w)
        set_state(self._frame_dim, state_v)

        self._update_sim_meters()

    # ─────────────────────────────────────────────────────────
    # Validasi Kapasitas (dengan dukungan checkbox)
    # ─────────────────────────────────────────────────────────

    def _get_capacity(self) -> tuple[float, int] | None:
        """
        Ambil max_w dan max_v sesuai status checkbox.
        Kembalikan None jika ada input wajib yang kosong/salah.
        Return (max_w, max_v) — nilai besar jika constraint dinonaktifkan.
        """
        use_w = self.var_use_weight.get()
        use_v = self.var_use_volume.get()

        if use_w:
            try:
                max_w = float(self.var_cap_w.get())
                assert max_w > 0
            except (ValueError, AssertionError):
                messagebox.showwarning("Input Salah",
                                       "Kapasitas berat tas harus berupa angka positif.")
                return None
        else:
            max_w = float("inf")  # tidak dibatasi

        if use_v:
            max_v = self._parse_volume(self.var_cap_p, self.var_cap_l, self.var_cap_t)
            if max_v <= 0:
                messagebox.showwarning("Input Kurang",
                                       "Masukkan dimensi tas (P, L, T) dengan benar.")
                return None
        else:
            max_v = 2 ** 31  # tidak dibatasi

        return max_w, max_v

    # ─────────────────────────────────────────────────────────
    # Solve Methods
    # ─────────────────────────────────────────────────────────

    def _solve(self) -> None:
        """Cari solusi dengan Dynamic Programming."""
        if not self.items:
            messagebox.showwarning("Kosong", "Belum ada barang di list untuk dihitung.")
            return

        cap = self._get_capacity()
        if cap is None:
            return
        max_w, max_v = cap

        use_w = self.var_use_weight.get()
        use_v = self.var_use_volume.get()

        log.info("Menjalankan DP: %d barang, W=%s kg, V=%s cm³",
                 len(self.items),
                 f"{max_w:.1f}" if use_w else "∞",
                 f"{max_v:,}" if use_v else "∞")

        # DP hanya mendukung nilai integer untuk kapasitas;
        # jika batasan dinonaktifkan, tetapkan nilai besar namun terbatas
        dp_w = max_w if use_w else sum(i["weight"] for i in self.items)
        dp_v = int(max_v) if use_v else sum(i["volume"] for i in self.items)

        start_time = time.perf_counter()
        result = solve_knapsack(self.items, dp_w, dp_v)
        elapsed = time.perf_counter() - start_time
        
        self._display_result(result, max_w, max_v, algo="DP", elapsed=elapsed)

    def _solve_greedy(self) -> None:
        """Cari solusi dengan Greedy."""
        if not self.items:
            messagebox.showwarning("Kosong", "Belum ada barang di list untuk dihitung.")
            return

        cap = self._get_capacity()
        if cap is None:
            return
        max_w, max_v = cap

        use_w = self.var_use_weight.get()
        use_v = self.var_use_volume.get()

        log.info("Menjalankan Greedy: %d barang", len(self.items))
        start_time = time.perf_counter()
        result = solve_knapsack_greedy(
            self.items, max_w, int(max_v), use_weight=use_w, use_volume=use_v
        )
        elapsed = time.perf_counter() - start_time
        self._display_result(result, max_w, max_v, algo="Greedy", elapsed=elapsed)

    def _solve_bf(self) -> None:
        """Cari solusi dengan Brute Force (hanya direkomendasikan ≤ 20 barang)."""
        if not self.items:
            messagebox.showwarning("Kosong", "Belum ada barang di list untuk dihitung.")
            return

        n = len(self.items)
        if n > 20:
            if not messagebox.askyesno(
                "Peringatan Brute Force",
                f"Brute Force akan mengevaluasi 2^{n} = {2**n:,} kombinasi.\n"
                f"Ini mungkin sangat lambat untuk {n} barang.\n\nLanjutkan?"
            ):
                return

        cap = self._get_capacity()
        if cap is None:
            return
        max_w, max_v = cap

        use_w = self.var_use_weight.get()
        use_v = self.var_use_volume.get()

        log.info("Menjalankan Brute Force: %d barang", n)
        start_time = time.perf_counter()
        result = solve_knapsack_bf(
            self.items, max_w, int(max_v), use_weight=use_w, use_volume=use_v
        )
        elapsed = time.perf_counter() - start_time
        self._display_result(result, max_w, max_v, algo="Brute Force", elapsed=elapsed)

    def _display_result(
        self,
        result: dict,
        max_w: float,
        max_v: int,
        algo: str = "DP",
        elapsed: float = 0.0,
    ) -> None:
        """Tampilkan ringkasan hasil ke panel HASIL SOLUSI."""
        # Simpan state untuk reveal
        self.last_result       = result
        self.last_active_items = self.items
        self.last_max_w        = max_w if self.var_use_weight.get() else sum(i["weight"] for i in self.items)
        self.last_max_v        = int(max_v) if self.var_use_volume.get() else sum(i["volume"] for i in self.items)
        self.is_revealed       = False

        # Reset tampilan lama
        for iid in self.tree.get_children():
            self.tree.item(iid, tags=())
        self.canvas_vis.delete("all")
        self.canvas_vis.pack_forget()

        max_val = sum(i["value"] for i in self.items)
        val = result["total_value"]

        self.lbl_weight.pack(anchor="w")
        self.lbl_vol.pack(anchor="w")

        self.lbl_val.config(
            text=f"✅ [{algo}] Kalkulasi selesai! Tekan LIHAT SOLUSI untuk detailnya."
        )
        self.lbl_weight.config(text=f"🏆 Theoretical Max Value : {val} / {max_val}")
        self.lbl_vol.config(text="")
        
        self.lbl_time.config(text=f"⏱ Waktu Eksekusi: {elapsed*1000:.2f} ms")

        self.lbl_badges_title.pack_forget()
        self.badges_text.pack_forget()
        self.badges_text.config(state="normal")
        self.badges_text.delete("1.0", "end")
        self.badges_text.config(state="disabled")

        self.btn_reveal._btn.config(state="normal", text="LIHAT SOLUSI")

    def _toggle_reveal(self) -> None:
        if not self.last_result or not self.last_active_items:
            return
            
        if self.is_revealed:
            self._hide_solution()
        else:
            self._reveal_solution()

    def _hide_solution(self) -> None:
        self.is_revealed = False
        self.btn_reveal._btn.config(text="LIHAT SOLUSI")
        self.btn_reveal._draw_icon("normal")
        for iid in self.tree.get_children():
            self.tree.item(iid, tags=())
        self.canvas_vis.delete("all")
        self.lbl_badges_title.pack_forget()
        self.badges_text.pack_forget()
        self.badges_text.config(state="normal")
        self.badges_text.delete("1.0", "end")
        self.badges_text.config(state="disabled")
            
        if self.last_result and self.last_active_items:
            max_val = sum(i["value"] for i in self.last_active_items)
            val = self.last_result["total_value"]
            self.lbl_val.config(text=f"✅ Kalkulasi selesai! Tekan LIHAT SOLUSI untuk detailnya.")
            self.lbl_weight.config(text=f"🏆 Theoretical Max Value : {val} / {max_val}")
            self.lbl_vol.config(text="")

    def _reveal_solution(self) -> None:
        self.is_revealed = True
        self.btn_reveal._btn.config(text="SEMBUNYIKAN")
        self.btn_reveal._draw_icon("closed")
        
        result     = self.last_result
        items_used = self.last_active_items
        max_w      = self.last_max_w
        max_v      = self.last_max_v

        selected  = result["selected"]

        # Highlight baris terpilih di tabel
        selected_set = set(selected)
        for iid in self.tree.get_children():
            name = self.tree.item(iid, "values")[2]
            self.tree.item(iid, tags=("selected",) if name in selected_set else ())
        self.tree.tag_configure("selected", background=C["lime"])

        self.lbl_badges_title.pack(anchor="w", pady=(0, 4))
        self.badges_text.pack(fill="x", anchor="w")
        self.badges_text.config(state="normal")
        self.badges_text.delete("1.0", "end")
        self.badges_text.config(state="disabled")

        self.update_idletasks()
        self._animate_visualization(selected_set, items_used, max_w, max_v)
        
    def _animate_visualization(self, selected_set: set[str], items_used: list[Item], max_w: float, max_v: float) -> None:
        """Animasi blok-blok barang terpilih yang mengisi bar kapasitas secara sekuensial."""
        self.canvas_vis.delete("all")
        
        # Fallback if winfo_width is not ready
        cw = self.canvas_vis.winfo_width()
        if cw < 10:
            cw = self.winfo_width() - 60
            
        ch = int(self.canvas_vis["height"]) # Use requested height

        chosen = [it for it in items_used if it["name"] in selected_set]
        max_val = sum(i["value"] for i in items_used)
        
        use_w = self.var_use_weight.get()
        use_v = self.var_use_volume.get()

        if not chosen or max_w <= 0:
            self.lbl_val.config(text=f"🏆  Total Nilai     :  0 / {max_val}")
            if use_w:
                self.lbl_weight.config(text=f"⚖️  Total Berat     :  0 kg dari {max_w} kg (0%)")
                self.lbl_weight.pack(anchor="w")
            else:
                self.lbl_weight.pack_forget()

            if use_v:
                self.lbl_vol.config(text=f"📦  Total Volume    :  0 cm³ dari {max_v:,} cm³ (0%)")
                self.lbl_vol.pack(anchor="w")
            else:
                self.lbl_vol.pack_forget()
            return

        colors = [C["blue"], C["yellow"], C["pink"], "#00D2FF", "#A78BFA", "#F87171"]

        # Variabel akumulasi untuk real-time update
        self._anim_val = 0
        self._anim_w = 0.0
        self._anim_vol = 0

        def draw_next(idx: int, x: float) -> None:
            if idx > len(chosen) or not self.is_revealed:
                return
                
            if idx > 0:
                # Tambahkan nilai barang sebelumnya
                prev_it = chosen[idx-1]
                self._anim_val += prev_it["value"]
                self._anim_w += prev_it["weight"]
                self._anim_vol += prev_it["volume"]
                
                # Buat badge block
                color = colors[(idx-1) % len(colors)]
                badge = tk.Frame(self.badges_text, bg=color, highlightthickness=2, highlightbackground=C["black"], padx=6, pady=4)
                tk.Label(badge, text=prev_it["name"], bg=color, fg=C["black"], font=FONTS["small"]).pack()
                
                self.badges_text.config(state="normal")
                self.badges_text.window_create("end", window=badge)
                self.badges_text.insert("end", "  ")
                self.badges_text.config(state="disabled")
            
            # Update teks real-time
            pct_w = (self._anim_w / max_w * 100) if max_w else 0
            pct_v = (self._anim_vol / max_v * 100) if max_v else 0
            
            self.lbl_val.config(text=f"🏆  Total Nilai     :  {self._anim_val} / {max_val}")
            if use_w:
                self.lbl_weight.config(text=f"⚖️  Total Berat     :  {self._anim_w:.1f} kg dari {max_w} kg ({pct_w:.1f}%)")
                self.lbl_weight.pack(anchor="w")
            else:
                self.lbl_weight.pack_forget()
                
            if use_v:
                self.lbl_vol.config(text=f"📦  Total Volume    :  {self._anim_vol:,} cm³ dari {max_v:,} cm³ ({pct_v:.1f}%)")
                self.lbl_vol.pack(anchor="w")
            else:
                self.lbl_vol.pack_forget()

            if idx == len(chosen):
                return # Selesai
                
            it = chosen[idx]
            bw = (it["weight"] / max_w) * cw
            color = colors[idx % len(colors)]
            
            # Gambar block di canvas
            self.canvas_vis.create_rectangle(x, 0, x + bw, ch, fill=color, outline=C["black"], width=2)
            if bw > 40:
                self.canvas_vis.create_text(
                    x + bw / 2, ch / 2,
                    text=f"{it['name']} ({it['weight']}kg)",
                    font=FONTS["small"], fill=C["black"]
                )
                
            self.after(300, lambda nx=x + bw, i=idx + 1: draw_next(i, nx))

        # Mulai animasi
        draw_next(0, 0.0)

    def _reset(self) -> None:
        if self.items and not messagebox.askyesno(
                "Reset", "Hapus semua data dan mulai ulang?"):
            return

        self.items.clear()
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for var in (self.var_name, self.var_weight, self.var_p, self.var_l,
                    self.var_t, self.var_cap_w, self.var_cap_p,
                    self.var_cap_l, self.var_cap_t):
            var.set("")
            
        self.last_result       = None
        self.last_active_items = None
        self.last_max_w        = 0.0
        self.last_max_v        = 0
        self.is_revealed       = False
        self.btn_reveal._btn.config(state="disabled", text="LIHAT SOLUSI")
        self.canvas_vis.delete("all")
        
        self.lbl_badges_title.pack_forget()
        self.badges_text.pack_forget()
        self.badges_text.config(state="normal")
        self.badges_text.delete("1.0", "end")
        self.badges_text.config(state="disabled")
            
        self.lbl_val.config(text="Tekan ⚡ CARI SOLUSI OPTIMAL untuk mulai menghitung.")
        self.lbl_weight.pack_forget()
        self.lbl_vol.pack_forget()
        self.lbl_time.config(text="")
        log.info("Aplikasi di-reset.")


    def _toggle_music(self) -> None:
        """Toggle mute/unmute musik latar."""
        if not _PYGAME_OK:
            return
        try:
            if self.music_muted:
                pygame.mixer.music.set_volume(0.5)
                self.music_muted = False
                self.btn_music._btn.config(text="MUTE")
                self.btn_music._draw_icon("unmuted")
                log.debug("Musik dilanjutkan (unmute).")
            else:
                pygame.mixer.music.set_volume(0.0)
                self.music_muted = True
                self.btn_music._btn.config(text="UNMUTE")
                self.btn_music._draw_icon("muted")
                log.debug("Musik dibisukan (mute).")
        except Exception as e:
            log.warning("Gagal toggle musik: %s", e)


# ─────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = KnapsackApp()
    app.mainloop()
