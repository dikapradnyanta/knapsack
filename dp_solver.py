"""
dp_solver.py
Algoritma Dynamic Programming untuk Multi-Constraint 0/1 Knapsack Problem.
Batasan: berat (kg) dan volume (cm³).
"""

import logging
from typing import TypedDict, Tuple

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
# Helper Functions
# ─────────────────────────────────────────────────────────────────

def _scale_inputs(items: list[Item], max_weight: float, max_volume: int) -> Tuple[int, int, list[int], list[int], list[int]]:
    """Mengubah input float ke int dan melakukan scaling jika volume terlalu besar."""
    W = int(round(max_weight * WEIGHT_SCALE))
    V = int(max_volume)

    weights_int = [int(round(item["weight"] * WEIGHT_SCALE)) for item in items]
    volumes_int = [int(item["volume"]) for item in items]
    values      = [int(item["value"])  for item in items]

    # Scale down volume jika melebihi limit memori
    if V > MAX_VOLUME_CELLS:
        volume_scale = V / MAX_VOLUME_CELLS
        V_scaled     = MAX_VOLUME_CELLS
        volumes_scaled = [max(1, int(round(v / volume_scale))) for v in volumes_int]
        log.info("Volume di-scale down: skala=%.2f, V_scaled=%d", volume_scale, V_scaled)
    else:
        V_scaled       = V
        volumes_scaled = volumes_int

    log.debug("Berat (unit ×0.1kg): %s", weights_int)
    log.debug("Volume (cm³) scaled: %s", volumes_scaled)
    log.debug("Nilai:               %s", values)
    
    return W, V_scaled, weights_int, volumes_scaled, values


def _run_dp(n: int, W: int, V_scaled: int, weights: list[int], volumes: list[int], values: list[int]) -> list[list[list[bool]]]:
    """
    Menjalankan algoritma DP. 
    Hanya menyimpan matrix boolean `keep` untuk menghemat memori, bukan seluruh tabel nilai.
    """
    # dp_table untuk nilai saat ini dan sebelumnya (2D array untuk menghemat RAM)
    prev_val = [[0] * (V_scaled + 1) for _ in range(W + 1)]
    
    # keep_table menyimpan True jika barang i diambil pada state (w, v)
    keep_table = [[[False] * (V_scaled + 1) for _ in range(W + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        wi  = weights[i - 1]
        vi  = volumes[i - 1]
        val = values[i - 1]

        curr_val = [row[:] for row in prev_val]

        for w in range(W + 1):
            for v in range(V_scaled + 1):
                if wi <= w and vi <= v:
                    take = prev_val[w - wi][v - vi] + val
                    if take > curr_val[w][v]:
                        curr_val[w][v] = take
                        keep_table[i][w][v] = True

        prev_val = curr_val
        log.debug("Selesai proses DP barang [%d] -> max val = %d", i, curr_val[W][V_scaled])

    return keep_table


def _backtrack(keep_table: list[list[list[bool]]], items: list[Item], 
               weights: list[int], volumes: list[int], W: int, V_scaled: int) -> list[str]:
    """Menelusuri ulang keep_table untuk mendapatkan barang-barang yang terpilih."""
    selected: list[str] = []
    w, v = W, V_scaled
    n = len(items)

    for i in range(n, 0, -1):
        if keep_table[i][w][v]:
            name = items[i - 1]["name"]
            selected.append(name)
            w -= weights[i - 1]
            v -= volumes[i - 1]
            log.debug("Backtrack: pilih '%s', sisa kapasitas -> W=%d, V=%d", name, w, v)

    selected.reverse()
    return selected


def _calculate_totals(items: list[Item], selected: list[str]) -> KnapsackResult:
    """Menghitung total berat, volume, dan nilai sebenarnya dari barang yang dipilih."""
    selected_set = set(selected)
    
    total_weight = sum(item["weight"] for item in items if item["name"] in selected_set)
    total_volume = sum(item["volume"] for item in items if item["name"] in selected_set)
    total_value  = sum(item["value"]  for item in items if item["name"] in selected_set)

    return {
        "selected":     selected,
        "total_value":  total_value,
        "total_weight": round(total_weight, 2),
        "total_volume": total_volume,
    }


# ─────────────────────────────────────────────────────────────────
# Fungsi Utama Ekspor
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
    log.debug("solve_knapsack dipanggil: %d barang, W=%.1fkg, V=%dcm³", len(items), max_weight, max_volume)

    if not items:
        log.warning("Daftar barang kosong, mengembalikan hasil kosong.")
        return {"selected": [], "total_value": 0, "total_weight": 0.0, "total_volume": 0}

    # 1. Persiapan Data (Scaling)
    W, V_scaled, weights_int, volumes_scaled, values = _scale_inputs(items, max_weight, max_volume)

    # 2. Iterasi DP (Optimasi Memori)
    keep_table = _run_dp(len(items), W, V_scaled, weights_int, volumes_scaled, values)

    # 3. Backtracking Solusi
    selected_names = _backtrack(keep_table, items, weights_int, volumes_scaled, W, V_scaled)

    # 4. Kalkulasi Hasil Aktual
    result = _calculate_totals(items, selected_names)
    
    log.info("Hasil DP → terpilih=%s, nilai=%d, berat=%.2fkg, vol=%dcm³", 
             result["selected"], result["total_value"], result["total_weight"], result["total_volume"])
    
    return result
