"""
dp_solver.py
Algoritma Dynamic Programming untuk Multi-Constraint 0/1 Knapsack Problem.
Batasan: berat (kg) dan volume (cm³).
"""

import logging
from typing import TypedDict

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Type Alias
# ─────────────────────────────────────────────────────────────────

class Item(TypedDict):
    name:   str
    weight: float   # kg
    volume: int     # cm³
    value:  int     # 0–5


class KnapsackResult(TypedDict):
    selected:     list[str]
    total_value:  int
    total_weight: float
    total_volume: int


# ─────────────────────────────────────────────────────────────────
# Konstanta
# ─────────────────────────────────────────────────────────────────

WEIGHT_SCALE    = 10        # 1 unit = 0.1 kg (membuat berat jadi integer)
MAX_VOLUME_CELLS = 50_000   # Batas resolusi volume agar memori terkendali


# ─────────────────────────────────────────────────────────────────
# Fungsi Utama
# ─────────────────────────────────────────────────────────────────

def solve_knapsack(items: list[Item], max_weight: float, max_volume: int) -> KnapsackResult:
    """
    Selesaikan Multi-Constraint 0/1 Knapsack dengan DP.

    Args:
        items:      Daftar barang dengan name, weight, volume, value.
        max_weight: Kapasitas berat tas (kg).
        max_volume: Kapasitas volume tas (cm³).

    Returns:
        KnapsackResult berisi selected, total_value, total_weight, total_volume.
    """
    log.debug("solve_knapsack dipanggil: %d barang, W=%.1fkg, V=%dcm³",
              len(items), max_weight, max_volume)

    _empty: KnapsackResult = {
        "selected": [], "total_value": 0, "total_weight": 0.0, "total_volume": 0
    }

    if not items:
        log.warning("Daftar barang kosong, mengembalikan hasil kosong.")
        return _empty

    n = len(items)
    W = int(round(max_weight * WEIGHT_SCALE))
    V = int(max_volume)

    # Konversi berat ke unit integer
    weights_int = [int(round(item["weight"] * WEIGHT_SCALE)) for item in items]
    volumes_int = [int(item["volume"]) for item in items]
    values      = [int(item["value"])  for item in items]

    log.debug("Berat (unit ×0.1kg): %s", weights_int)
    log.debug("Volume (cm³):        %s", volumes_int)
    log.debug("Nilai:               %s", values)

    # Scale down volume jika terlalu besar untuk memori
    if V > MAX_VOLUME_CELLS:
        volume_scale = V / MAX_VOLUME_CELLS
        V_scaled     = MAX_VOLUME_CELLS
        volumes_scaled = [max(1, int(round(v / volume_scale))) for v in volumes_int]
        log.info("Volume di-scale down: skala=%.2f, V_scaled=%d", volume_scale, V_scaled)
    else:
        volume_scale   = 1.0
        V_scaled       = V
        volumes_scaled = volumes_int

    # ── Inisialisasi tabel DP ──────────────────────────────────
    # dp[i][w][v] = nilai terbaik menggunakan barang 0..i-1
    #               dengan kapasitas berat w dan volume v_scaled
    prev = [[0] * (V_scaled + 1) for _ in range(W + 1)]
    dp_table: list[list[list[int]] | None] = [None] * (n + 1)
    dp_table[0] = [row[:] for row in prev]

    # ── Iterasi DP ────────────────────────────────────────────
    for i in range(1, n + 1):
        wi  = weights_int[i - 1]
        vi  = volumes_scaled[i - 1]
        val = values[i - 1]

        curr = [row[:] for row in prev]

        for w in range(W + 1):
            for v in range(V_scaled + 1):
                if wi <= w and vi <= v:
                    take = prev[w - wi][v - vi] + val
                    if take > curr[w][v]:
                        curr[w][v] = take

        dp_table[i] = curr
        prev = curr
        log.debug("Selesai proses barang [%d] %s → nilai terbaik=%d",
                  i, items[i - 1]["name"], curr[W][V_scaled])

    # ── Backtracking ──────────────────────────────────────────
    selected: list[str] = []
    w, v = W, V_scaled

    for i in range(n, 0, -1):
        if dp_table[i][w][v] != dp_table[i - 1][w][v]:
            name = items[i - 1]["name"]
            selected.append(name)
            w -= weights_int[i - 1]
            v -= volumes_scaled[i - 1]
            log.debug("Backtrack: pilih '%s', sisa W=%d, V=%d", name, w, v)

    selected.reverse()

    # ── Hitung total aktual ───────────────────────────────────
    selected_set = set(selected)
    total_weight = sum(item["weight"] for item in items if item["name"] in selected_set)
    total_volume = sum(item["volume"] for item in items if item["name"] in selected_set)
    total_value  = dp_table[n][W][V_scaled]

    result: KnapsackResult = {
        "selected":     selected,
        "total_value":  total_value,
        "total_weight": round(total_weight, 2),
        "total_volume": total_volume,
    }

    log.info("Hasil DP → terpilih=%s, nilai=%d, berat=%.2fkg, vol=%dcm³",
             selected, total_value, total_weight, total_volume)

    return result
