"""
main.py
GUI Knapsack Solver — Dynamic Programming Multi-Constraint
Gaya Visual: Neobrutalism
"""

import csv
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from quiz_popup import QuizPopup
from dp_solver import solve_knapsack, Item

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
               command, font_key: str = "btn",
               padx: int = 16, pady: int = 8) -> tk.Frame:
    """Tombol bergaya neobrutalism dengan shadow efek saat diklik."""
    shadow = tk.Frame(parent, bg=C["black"])
    btn = tk.Button(
        shadow,
        text=text,
        bg=color, fg=C["black"],
        font=FONTS[font_key],
        relief="flat", bd=0, highlightthickness=2, highlightbackground=C["black"],
        padx=padx, pady=pady,
        cursor="hand2",
        activebackground=color, activeforeground=C["black"],
        command=command,
    )
    # Default state: offset hard shadow 4px 4px
    btn.pack(padx=(0, 4), pady=(0, 4))

    # Press animation (geser shadow)
    btn.bind("<ButtonPress-1>",   lambda _e: btn.pack_configure(padx=(4, 0), pady=(4, 0)))
    btn.bind("<ButtonRelease-1>", lambda _e: btn.pack_configure(padx=(0, 4), pady=(0, 4)))

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

        self._init_vars()
        self._build_ui()
        self._center_window(960, 760)
        log.info("Aplikasi dimulai.")

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

        # Trace volume otomatis
        for v in (self.var_p, self.var_l, self.var_t):
            v.trace_add("write", self._on_item_dim_changed)
        for v in (self.var_cap_p, self.var_cap_l, self.var_cap_t):
            v.trace_add("write", self._on_cap_dim_changed)

    # ── Posisi Window ─────────────────────────────────────────

    def _center_window(self, w: int, h: int) -> None:
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ─────────────────────────────────────────────────────────
    # UI Builder
    # ─────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=10, pady=8)
        body.columnconfigure(0, weight=0, minsize=280)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_input_panel(body)
        self._build_list_panel(body)
        self._build_capacity_panel()
        self._build_result_panel()

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
        neo_button(hdr, "🔄 RESET", C["pink"], self._reset,
                   font_key="btn_sm", padx=10, pady=6).pack(
                       side="right", padx=14, pady=10)

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
        self._lbl_item_vol = neo_label(vol_row, "— cm³", bg=C["blue"],
                                        fg=C["dark_gray"])
        self._lbl_item_vol.pack(side="left", padx=6)

        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=10)
        neo_button(inner, "＋ TAMBAH BARANG", C["pink"],
                   self._add_item).pack(pady=4)

    def _labeled_entry(self, parent: tk.Widget, label: str,
                        var: tk.StringVar, bg: str) -> None:
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=4)
        neo_label(row, label + ":", font=FONTS["body_b"], bg=bg).pack(anchor="w")
        neo_entry(row, textvariable=var, width=22).pack(fill="x")

    # ── Panel Daftar Barang ───────────────────────────────────

    def _build_list_panel(self, parent: tk.Frame) -> None:
        inner = neo_frame(parent, bg=C["white"])
        inner._outer.grid(row=0, column=1, sticky="nsew", pady=4)

        neo_label(inner, "DAFTAR BARANG", font=FONTS["head"],
                  bg=C["white"]).pack(anchor="w", pady=(0, 8))
        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=(0, 6))

        self._setup_treeview(inner)
        
        btn_row = tk.Frame(inner, bg=C["white"])
        btn_row.pack(fill="x", pady=(8, 0))
        
        neo_button(btn_row, "📥 IMPORT CSV", C["blue"],
                   self._import_csv, font_key="btn_sm",
                   padx=10, pady=6).pack(side="left", padx=(0, 4))
        
        neo_button(btn_row, "📤 EXPORT CSV", C["yellow"],
                   self._export_csv, font_key="btn_sm",
                   padx=10, pady=6).pack(side="left", padx=4)
        
        neo_button(btn_row, "🗑 HAPUS", C["gray"],
                   self._delete_item, font_key="btn_sm",
                   padx=10, pady=6).pack(side="right", padx=(4, 0))

    def _setup_treeview(self, parent: tk.Widget) -> None:
        wrapper = tk.Frame(parent, bg=C["black"], bd=2)
        wrapper.pack(fill="both", expand=True)

        cols = ("no", "nama", "berat", "volume", "nilai")
        self.tree = ttk.Treeview(wrapper, columns=cols, show="headings",
                                  height=10, selectmode="browse")

        col_defs = [
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

    # ── Panel Kapasitas Tas ───────────────────────────────────

    def _build_capacity_panel(self) -> None:
        inner = neo_frame(self, bg=C["yellow"])
        inner._outer.pack(fill="x", padx=10, pady=(2, 4))

        neo_label(inner, "KAPASITAS TAS", font=FONTS["head"],
                  bg=C["yellow"]).grid(row=0, column=0, sticky="w", pady=(0, 6))
        tk.Frame(inner, height=3, bg=C["black"]).grid(
            row=1, column=0, columnspan=12, sticky="ew", pady=(0, 8))

        # Berat maks
        neo_label(inner, "Berat Maks (kg):", font=FONTS["body_b"],
                  bg=C["yellow"]).grid(row=2, column=0, sticky="w", padx=(0, 6))
        neo_entry(inner, textvariable=self.var_cap_w, width=8).grid(
            row=2, column=1, padx=(0, 20))

        # Dimensi tas
        neo_label(inner, "Dimensi Tas P×L×T (cm):", font=FONTS["body_b"],
                  bg=C["yellow"]).grid(row=2, column=2, sticky="w", padx=(0, 6))
        for i, (var, lbl) in enumerate([(self.var_cap_p, "P"),
                                         (self.var_cap_l, "L"),
                                         (self.var_cap_t, "T")]):
            col = 3 + i * 2
            neo_label(inner, lbl, font=FONTS["small"],
                      bg=C["yellow"]).grid(row=2, column=col, padx=(4, 0))
            neo_entry(inner, textvariable=var, width=6).grid(
                row=2, column=col + 1, padx=(2, 4))

        neo_label(inner, "Vol Maks:", font=FONTS["body_b"],
                  bg=C["yellow"]).grid(row=2, column=9, padx=(10, 4))
        self._lbl_cap_vol = neo_label(inner, "— cm³", bg=C["yellow"],
                                       fg=C["dark_gray"])
        self._lbl_cap_vol.grid(row=2, column=10, sticky="w")

        neo_button(inner, "⚡ HITUNG SOLUSI", C["pink"],
                   self._solve).grid(row=2, column=11, padx=(20, 0), pady=2)

    # ── Panel Hasil ───────────────────────────────────────────

    def _build_result_panel(self) -> None:
        inner = neo_frame(self, bg=C["lime"])
        inner._outer.pack(fill="x", padx=10, pady=(0, 10))
        inner.configure(pady=10)

        neo_label(inner, "HASIL SOLUSI", font=FONTS["head"],
                  bg=C["lime"]).pack(anchor="w")
        tk.Frame(inner, height=3, bg=C["black"]).pack(fill="x", pady=(4, 8))

        self._lbl_result = neo_label(
            inner,
            "Tekan  ⚡ HITUNG SOLUSI  untuk melihat hasil optimal.",
            bg=C["lime"], justify="left",
        )
        self._lbl_result.pack(anchor="w")

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
                       "value": popup.result}
        self.items.append(item)
        log.info("Barang ditambahkan: %s", item)

        stars = "★" * popup.result + "☆" * (5 - popup.result)
        self.tree.insert("", "end", values=(
            len(self.items), name, f"{w}", f"{volume:,}", stars,
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
            vals[0] = i + 1
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

                    item: Item = {"name": name, "weight": w, "volume": v, "value": val}
                    self.items.append(item)
                    
                    stars = "★" * val + "☆" * max(0, 5 - val)
                    self.tree.insert("", "end", values=(
                        len(self.items), name, f"{w}", f"{v:,}", stars,
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

    def _solve(self) -> None:
        if not self.items:
            messagebox.showwarning("Kosong",
                                   "Belum ada barang yang dimasukkan.")
            return

        try:
            max_w = float(self.var_cap_w.get())
            assert max_w > 0
        except (ValueError, AssertionError):
            messagebox.showwarning("Input Salah",
                                   "Kapasitas berat tas harus berupa angka positif.")
            return

        max_v = self._parse_volume(self.var_cap_p, self.var_cap_l, self.var_cap_t)
        if max_v <= 0:
            messagebox.showwarning("Input Kurang",
                                   "Masukkan dimensi tas (P, L, T) dengan benar.")
            return

        log.info("Menjalankan DP: %d barang, W=%.1fkg, V=%dcm³",
                 len(self.items), max_w, max_v)

        result = solve_knapsack(self.items, max_w, max_v)
        self._display_result(result, max_w, max_v)

    def _display_result(self, result: dict, max_w: float, max_v: int) -> None:
        selected    = result["selected"]
        total_val   = result["total_value"]
        total_w     = result["total_weight"]
        total_vol   = result["total_volume"]
        max_val     = sum(i["value"] for i in self.items)

        # Highlight baris terpilih di tabel
        for iid in self.tree.get_children():
            name = self.tree.item(iid, "values")[1]
            self.tree.item(iid, tags=("selected",) if name in selected else ())
        self.tree.tag_configure("selected", background=C["lime"])

        pct_w = (total_w   / max_w  * 100) if max_w  else 0
        pct_v = (total_vol / max_v  * 100) if max_v  else 0
        names = "  ·  ".join(selected) if selected else "(tidak ada)"
        stars = ("★" * total_val + "☆" * max(0, max_val - total_val))[:10]

        self._lbl_result.config(text=(
            f"✅  Barang Terpilih  :  {names}\n\n"
            f"🏆  Total Nilai      :  {total_val} / {max_val}   {stars}\n"
            f"⚖️   Total Berat      :  {total_w} kg  dari  {max_w} kg  "
            f"({pct_w:.1f}%)\n"
            f"📦  Total Volume     :  {total_vol:,} cm³  dari  {max_v:,} cm³  "
            f"({pct_v:.1f}%)"
        ))

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
        self._lbl_result.config(
            text="Tekan  ⚡ HITUNG SOLUSI  untuk melihat hasil optimal.")
        log.info("Aplikasi di-reset.")


# ─────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = KnapsackApp()
    app.mainloop()
