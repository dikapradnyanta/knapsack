"""
greedy_solver.py
Algoritma Greedy untuk 0/1 Knapsack Problem.
Strategi: urutkan barang berdasar nilai tertinggi, lalu masukkan jika masih muat.
Batasan: berat (kg) dan/atau volume (cm³) — dapat dinonaktifkan.
"""

import logging
from dp_solver import Item, KnapsackResult

log = logging.getLogger(__name__)


def solve_knapsack_greedy(
    items: list[Item],
    max_weight: float = float("inf"),
    max_volume: int = 2**31,
    use_weight: bool = True,
    use_volume: bool = True,
) -> KnapsackResult:
    """
    Selesaikan 0/1 Knapsack dengan Greedy (urutkan nilai desc → masukkan jika muat).

    Catatan: Greedy tidak menjamin solusi optimal, namun sangat cepat (O(n log n)).

    Args:
        items:      Daftar barang.
        max_weight: Kapasitas berat (kg). Diabaikan jika use_weight=False.
        max_volume: Kapasitas volume (cm³). Diabaikan jika use_volume=False.
        use_weight: Jika False, constraint berat tidak digunakan.
        use_volume: Jika False, constraint volume tidak digunakan.

    Returns:
        KnapsackResult berisi selected, total_value, total_weight, total_volume.
    """
    log.debug(
        "solve_knapsack_greedy: %d barang, W=%.1f (%s), V=%d (%s)",
        len(items), max_weight, "aktif" if use_weight else "nonaktif",
        max_volume, "aktif" if use_volume else "nonaktif",
    )

    if not items:
        return {"selected": [], "total_value": 0, "total_weight": 0.0, "total_volume": 0}

    # Urutkan berdasarkan nilai tertinggi (greedy choice)
    sorted_items = sorted(items, key=lambda it: it["value"], reverse=True)

    selected: list[Item] = []
    rem_w = max_weight if use_weight else float("inf")
    rem_v = max_volume if use_volume else 2**31

    for it in sorted_items:
        w_fits = (it["weight"] <= rem_w) if use_weight else True
        v_fits = (it["volume"] <= rem_v) if use_volume else True

        if w_fits and v_fits:
            selected.append(it)
            rem_w -= it["weight"]
            rem_v -= it["volume"]
            log.debug("Greedy pilih '%s' (nilai=%d)", it["name"], it["value"])

    selected_names = [it["name"] for it in selected]
    total_w   = sum(it["weight"] for it in selected)
    total_v   = sum(it["volume"] for it in selected)
    total_val = sum(it["value"]  for it in selected)

    log.info(
        "Greedy → terpilih=%s, nilai=%d, berat=%.2fkg, vol=%dcm³",
        selected_names, total_val, total_w, total_v,
    )
    return {
        "selected":     selected_names,
        "total_value":  total_val,
        "total_weight": round(total_w, 2),
        "total_volume": int(total_v),
    }
