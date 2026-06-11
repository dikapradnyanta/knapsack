"""
bf_solver.py
Algoritma Brute Force untuk 0/1 Knapsack Problem.
Batasan: berat (kg) dan/atau volume (cm³) — dapat dinonaktifkan.
"""

import logging
from itertools import combinations
from dp_solver import Item, KnapsackResult

log = logging.getLogger(__name__)


def solve_knapsack_bf(
    items: list[Item],
    max_weight: float = float("inf"),
    max_volume: int = 2**31,
    use_weight: bool = True,
    use_volume: bool = True,
) -> KnapsackResult:
    """
    Selesaikan 0/1 Knapsack dengan Brute Force (enumerasi semua subset).

    Args:
        items:      Daftar barang.
        max_weight: Kapasitas berat (kg). Diabaikan jika use_weight=False.
        max_volume: Kapasitas volume (cm³). Diabaikan jika use_volume=False.
        use_weight: Jika False, constraint berat tidak digunakan.
        use_volume: Jika False, constraint volume tidak digunakan.

    Returns:
        KnapsackResult berisi selected, total_value, total_weight, total_volume.

    Peringatan: Eksponensial O(2^n). Hanya praktis untuk n ≤ 20.
    """
    log.debug(
        "solve_knapsack_bf: %d barang, W=%.1f (%s), V=%d (%s)",
        len(items), max_weight, "aktif" if use_weight else "nonaktif",
        max_volume, "aktif" if use_volume else "nonaktif",
    )

    if not items:
        return {"selected": [], "total_value": 0, "total_weight": 0.0, "total_volume": 0}

    n = len(items)
    best_val = -1
    best_subset: tuple[Item, ...] = ()

    # Iterasi semua 2^n subset
    for r in range(n + 1):
        for subset in combinations(items, r):
            total_w   = sum(it["weight"] for it in subset)
            total_v   = sum(it["volume"] for it in subset)
            total_val = sum(it["value"]  for it in subset)

            w_ok = (total_w <= max_weight) if use_weight else True
            v_ok = (total_v <= max_volume) if use_volume else True

            if w_ok and v_ok and total_val > best_val:
                best_val = total_val
                best_subset = subset

    selected_names = [it["name"] for it in best_subset]
    total_w   = sum(it["weight"] for it in best_subset)
    total_v   = sum(it["volume"] for it in best_subset)

    log.info(
        "BF → terpilih=%s, nilai=%d, berat=%.2fkg, vol=%dcm³",
        selected_names, best_val, total_w, total_v,
    )
    return {
        "selected":     selected_names,
        "total_value":  best_val if best_val >= 0 else 0,
        "total_weight": round(total_w, 2),
        "total_volume": int(total_v),
    }
