"""
quiz_popup.py
Pop-up kuis 5 pertanyaan Ya/Tidak untuk menentukan nilai kepentingan barang.
Skor hasil kuis: 0–5 (setiap "Ya" = +1).
Gaya visual: Neobrutalism.
"""

import logging
import tkinter as tk

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Konstanta
# ─────────────────────────────────────────────────────────────────

QUESTIONS: list[str] = [
    "Apakah kamu pakai barang ini\nhampir setiap hari?",
    "Kalau barang ini ketinggalan,\nkamu bakal repot?",
    "Apakah barang ini susah dipinjam\ndari orang lain?",
    "Apakah kamu bakalan kangen barang ini\nkalau tidak dibawa?",
    "Kalau barang ini hilang, kamu perlu\nbeli lagi secepatnya?",
]

# Palet Warna Neobrutalism
COLORS: dict[str, str] = {
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

RESULT_TIERS: list[dict] = [
    {"min": 4, "bg": "#B8FF57", "emoji": "🌟", "label": "Sangat Penting!"},
    {"min": 3, "bg": "#74D7FF", "emoji": "👍", "label": "Cukup Penting"},
    {"min": 2, "bg": "#FFE500", "emoji": "🤔", "label": "Lumayan Perlu"},
    {"min": 0, "bg": "#FF6B9D", "emoji": "😐", "label": "Kurang Penting"},
]


# ─────────────────────────────────────────────────────────────────
# Widget Helpers
# ─────────────────────────────────────────────────────────────────

def _make_neo_button(
    parent: tk.Widget,
    text: str,
    color: str,
    command,
    font_size: int = 13,
    fg: str = None,
) -> tk.Frame:
    """Buat tombol bergaya neobrutalism dengan efek press (hard shadow)."""
    fg_color = fg if fg else COLORS["black"]
    shadow = tk.Frame(parent, bg=COLORS["black"])
    btn = tk.Button(
        shadow,
        text=text,
        bg=color,
        fg=fg_color,
        font=("Space Grotesk", font_size, "bold"),
        relief="flat",
        bd=0,
        padx=20,
        pady=10,
        cursor="hand2",
        activebackground=color,
        activeforeground=fg_color,
        command=command,
        highlightthickness=2,
        highlightbackground=COLORS["black"],
    )
    # Default state: offset hard shadow 4px 4px
    btn.pack(padx=(0, 4), pady=(0, 4))

    # Press animation
    btn.bind("<ButtonPress-1>", lambda _e: btn.pack_configure(padx=(4, 0), pady=(4, 0)))
    btn.bind("<ButtonRelease-1>", lambda _e: btn.pack_configure(padx=(0, 4), pady=(0, 4)))
    
    return shadow


# ─────────────────────────────────────────────────────────────────
# Kelas Pop-up
# ─────────────────────────────────────────────────────────────────

class QuizPopup(tk.Toplevel):
    """
    Modal pop-up kuis penilaian barang.

    Setelah window ditutup:
      - self.result = int (0–5) jika dijawab sampai selesai
      - self.result = None       jika dibatalkan
    """

    # ── Init ──────────────────────────────────────────────────

    def __init__(self, parent: tk.Tk, item_name: str) -> None:
        super().__init__(parent)
        self.item_name = item_name
        self.result: int | None = None

        self._current_q: int       = 0
        self._score:     int       = 0
        self._answers:   list[bool] = []

        self._setup_window()
        self._build_quiz_screen()
        self._render_question()

        self.transient(parent)
        self.grab_set()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        log.debug("QuizPopup dibuka untuk barang '%s'", item_name)

    # ── Window Setup ──────────────────────────────────────────

    def _setup_window(self) -> None:
        self.title("Kuis Nilai Barang")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg"])

        w, h = 480, 420
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    # ── Bangun Layar Kuis ─────────────────────────────────────

    def _build_quiz_screen(self) -> None:
        """Bangun semua widget layar kuis (dipanggil sekali saat init)."""
        self._quiz_frame = tk.Frame(self, bg=COLORS["bg"])
        self._quiz_frame.pack(fill="both", expand=True)

        # Header kuning
        hdr = tk.Frame(self._quiz_frame, bg=COLORS["yellow"],
                       highlightthickness=3, highlightbackground=COLORS["black"])
        hdr.pack(fill="x", padx=4, pady=(4, 0))

        tk.Label(hdr, text="📦  Seberapa penting barang ini?",
                 bg=COLORS["yellow"], fg=COLORS["black"],
                 font=("Space Grotesk", 14, "bold"), pady=12).pack()
        tk.Label(hdr, text=f'"{self.item_name}"',
                 bg=COLORS["yellow"], fg=COLORS["black"],
                 font=("Inter", 11, "italic"), pady=4).pack()

        # Body
        body = tk.Frame(self._quiz_frame, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=16, pady=10)

        self._lbl_progress = tk.Label(body, text="", bg=COLORS["bg"],
                                       fg=COLORS["dark_gray"],
                                       font=("Arial", 10, "bold"))
        self._lbl_progress.pack(anchor="w", pady=(4, 0))

        tk.Frame(body, height=3, bg=COLORS["black"]).pack(fill="x", pady=6)

        # Kotak pertanyaan
        self._lbl_question = tk.Label(
            body, text="",
            bg=COLORS["white"], fg=COLORS["black"],
            font=("Arial", 13, "bold"),
            wraplength=420, justify="center",
            relief="flat", bd=0, padx=16, pady=20,
            highlightthickness=3, highlightbackground=COLORS["black"],
        )
        self._lbl_question.pack(fill="x", pady=8)

        # Tombol Ya / Tidak
        btn_row = tk.Frame(body, bg=COLORS["bg"])
        btn_row.pack(pady=10)
        _make_neo_button(btn_row, "✅  YA",    COLORS["lime"], self._on_yes).pack(side="left", padx=12)
        _make_neo_button(btn_row, "❌  TIDAK", COLORS["pink"], self._on_no ).pack(side="left", padx=12)

        # Dots + skor sementara
        bottom = tk.Frame(body, bg=COLORS["bg"])
        bottom.pack(pady=6)

        self._dots_frame = tk.Frame(bottom, bg=COLORS["bg"])
        self._dots_frame.pack(side="left", padx=8)

        self._lbl_score = tk.Label(bottom, text="Skor sementara: 0",
                                    bg=COLORS["bg"], fg=COLORS["black"],
                                    font=("Arial", 11, "bold"))
        self._lbl_score.pack(side="left", padx=8)

        _make_neo_button(body, "BATAL", COLORS["gray"], self._on_cancel,
                         font_size=9).pack(pady=(4, 0))

    # ── Render Pertanyaan ─────────────────────────────────────

    def _render_question(self) -> None:
        """Perbarui semua widget sesuai pertanyaan saat ini."""
        q_idx = self._current_q
        total = len(QUESTIONS)

        self._lbl_progress.config(text=f"Pertanyaan {q_idx + 1} dari {total}")
        self._lbl_question.config(text=QUESTIONS[q_idx])
        self._lbl_score.config(text=f"Skor sementara: {self._score}")

        # Dots indikator
        for w in self._dots_frame.winfo_children():
            w.destroy()

        dot_colors = {
            "past_yes": COLORS["lime"],
            "past_no":  COLORS["pink"],
            "current":  COLORS["yellow"],
            "future":   COLORS["gray"],
        }
        for i in range(total):
            if i < q_idx:
                color = dot_colors["past_yes"] if self._answers[i] else dot_colors["past_no"]
            elif i == q_idx:
                color = dot_colors["current"]
            else:
                color = dot_colors["future"]

            tk.Label(self._dots_frame, text="●", bg=COLORS["bg"],
                     fg=color, font=("Arial", 18)).pack(side="left", padx=2)

    # ── Event Handlers ────────────────────────────────────────

    def _on_yes(self) -> None:
        log.debug("Q%d '%s' → YA", self._current_q + 1,
                  QUESTIONS[self._current_q].replace("\n", " "))
        self._answers.append(True)
        self._score += 1
        self._advance()

    def _on_no(self) -> None:
        log.debug("Q%d '%s' → TIDAK", self._current_q + 1,
                  QUESTIONS[self._current_q].replace("\n", " "))
        self._answers.append(False)
        self._advance()

    def _advance(self) -> None:
        self._current_q += 1
        if self._current_q >= len(QUESTIONS):
            self._finish()
        else:
            self._render_question()

    # ── Selesai / Batal ───────────────────────────────────────

    def _finish(self) -> None:
        self.result = self._score
        log.info("Kuis selesai untuk '%s': skor=%d, jawaban=%s",
                 self.item_name, self._score, self._answers)
        self._show_result_screen()

    def _show_result_screen(self) -> None:
        """Ganti layar kuis dengan layar hasil akhir."""
        self._quiz_frame.destroy()

        # Tentukan tier berdasarkan skor
        tier = next(t for t in RESULT_TIERS if self._score >= t["min"])
        bg = tier["bg"]
        self.configure(bg=bg)

        frame = tk.Frame(self, bg=bg)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        tk.Label(frame, text=tier["emoji"], bg=bg, font=("Arial", 48)).pack(pady=(20, 0))
        tk.Label(frame, text=tier["label"], bg=bg, fg=COLORS["black"],
                 font=("Arial Black", 18, "bold")).pack()

        stars = "★" * self._score + "☆" * (5 - self._score)
        tk.Label(frame, text=stars, bg=bg, fg=COLORS["black"],
                 font=("Arial", 28)).pack(pady=8)
        tk.Label(frame, text=f"Nilai barang: {self._score} / 5",
                 bg=bg, fg=COLORS["black"], font=("Arial", 14, "bold")).pack()
        tk.Label(frame, text=f'"{self.item_name}"',
                 bg=bg, fg=COLORS["dark_gray"], font=("Arial", 12, "italic")).pack(pady=4)

        tk.Frame(frame, height=3, bg=COLORS["black"]).pack(fill="x", pady=12)

        save_btn = _make_neo_button(frame, "SIMPAN & LANJUT ✔",
                                    COLORS["black"], self._close_ok, font_size=12, fg=COLORS["yellow"])
        save_btn.pack()

    def _close_ok(self) -> None:
        self.grab_release()
        self.destroy()

    def _on_cancel(self) -> None:
        log.debug("QuizPopup dibatalkan untuk barang '%s'", self.item_name)
        self.result = None
        self.grab_release()
        self.destroy()
