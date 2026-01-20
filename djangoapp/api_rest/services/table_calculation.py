from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class TableType:
    name: str
    min_capacity: int
    max_capacity: int
    available_quantity: int
    accepts_junction: bool = True


@dataclass(frozen=True)
class Allocation:
    counts: Dict[str, int]
    tables_used: int
    min_total: int
    max_total: int
    waste: int


def best_allocation(
    people: int,
    types: List[TableType],
    *,
    allow_mix_only_if_junction: bool = True,
    preserve_small_tables: bool = True,
) -> Optional[Allocation]:
    if people <= 0:
        return None

    types = [t for t in types if t.available_quantity > 0]
    if not types:
        return None

    # 1) tenta caber em 1 mesa (melhor UX)
    single_candidates: List[Tuple[int, int, TableType]] = []
    for t in types:
        if t.min_capacity <= people <= t.max_capacity and t.available_quantity >= 1:
            waste = t.max_capacity - people
            single_candidates.append((waste, t.max_capacity, t))

    if single_candidates:
        _, _, best = sorted(single_candidates, key=lambda x: (x[0], x[1]))[0]
        return Allocation(
            counts={best.name: 1},
            tables_used=1,
            min_total=best.min_capacity,
            max_total=best.max_capacity,
            waste=best.max_capacity - people,
        )

    # 2) múltiplas mesas (junção)
    candidates = (
        [t for t in types if t.accepts_junction]
        if allow_mix_only_if_junction
        else types
    )
    if not candidates:
        return None

    candidates.sort(key=lambda t: t.max_capacity, reverse=True)

    best_max = candidates[0].max_capacity
    k_min = (people + best_max - 1) // best_max
    k_max = sum(t.available_quantity for t in candidates)

    overall_max = max(t.max_capacity for t in candidates)
    penalty = {
        t.name: (overall_max - t.max_capacity + 1) if preserve_small_tables else 0
        for t in candidates
    }

    # vamos guardar:
    # - best_key só com números (comparável)
    # - best_payload com os dados (dict, totais)
    best_key: Optional[Tuple[int, int, int]] = None  # (tables_used, waste, penalty_sum)
    best_counts: Optional[Dict[str, int]] = None
    best_totals: Optional[Tuple[int, int]] = None  # (min_total, max_total)

    def dfs(
        i: int,
        remaining_tables: int,
        counts: Dict[str, int],
        min_total: int,
        max_total: int,
        pen_sum: int,
        k_target: int,
    ):
        nonlocal best_key, best_counts, best_totals

        # prune seguro: mesmo com o melhor max, não chega
        if max_total + remaining_tables * best_max < people:
            return

        if i == len(candidates):
            if remaining_tables != 0:
                return
            if not (min_total <= people <= max_total):
                return

            waste = max_total - people
            key = (k_target, waste, pen_sum)
            if best_key is None or key < best_key:
                best_key = key
                best_counts = dict(counts)
                best_totals = (min_total, max_total)
            return

        t = candidates[i]
        take_max = min(t.available_quantity, remaining_tables)

        for x in range(take_max, -1, -1):
            if x:
                counts[t.name] = x
            else:
                counts.pop(t.name, None)

            dfs(
                i + 1,
                remaining_tables - x,
                counts,
                min_total + x * t.min_capacity,
                max_total + x * t.max_capacity,
                pen_sum + x * penalty[t.name],
                k_target,
            )

    for k in range(k_min, k_max + 1):
        best_key = None
        best_counts = None
        best_totals = None

        dfs(0, k, {}, 0, 0, 0, k)

        if best_key is not None and best_counts is not None and best_totals is not None:
            min_total, max_total = best_totals
            tables_used, waste, _ = best_key
            return Allocation(
                counts=best_counts,
                tables_used=tables_used,
                min_total=min_total,
                max_total=max_total,
                waste=waste,
            )

    return None


if __name__ == "__main__":
    table_types = [
        TableType("Mesa 2", 1, 2, 8, accepts_junction=True),
        TableType("Mesa 4", 3, 4, 6, accepts_junction=True),
        TableType("Mesa 6", 5, 6, 2, accepts_junction=True),
    ]

    print(best_allocation(16, types=table_types))
