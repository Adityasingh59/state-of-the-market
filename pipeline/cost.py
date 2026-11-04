"""Cost tracker with a hard spend cap.

Every call goes through `reserve()` first: it adds a worst-case estimate for the
call to the running total and refuses if that would pass the budget. After the
call, `settle()` swaps the estimate for the real cost from `response.usage` and
writes a ledger line. The ledger persists across runs and steps, so the cap
covers the whole project, not one script.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass

from . import config


class BudgetExceeded(RuntimeError):
    pass


def _price(model: str) -> tuple[float, float, float, float]:
    return config.PRICES.get(model, config.UNKNOWN_MODEL_PRICE)


def usage_cost(usage, default_model: str) -> float:
    """USD cost of one response's usage block.

    With server-side fallback, `usage.iterations` splits tokens by the model
    that produced them; price each part at its own model's rate.
    """
    parts = []
    for it in getattr(usage, "iterations", None) or []:
        if getattr(it, "input_tokens", None) is None:
            continue
        parts.append((getattr(it, "model", None) or default_model, it))
    if not parts:
        parts = [(default_model, usage)]

    total = 0.0
    for model, u in parts:
        p_in, p_out, p_cr, p_cw = _price(str(model))
        total += (
            (u.input_tokens or 0) * p_in
            + (u.output_tokens or 0) * p_out
            + (getattr(u, "cache_read_input_tokens", 0) or 0) * p_cr
            + (getattr(u, "cache_creation_input_tokens", 0) or 0) * p_cw
        ) / 1_000_000
    return total


def worst_case_cost(model: str, input_tokens_est: int, max_tokens: int) -> float:
    """Upper bound for one call: all input uncached-or-written, full max_tokens."""
    p_in, p_out, _, p_cw = _price(model)
    return (input_tokens_est * max(p_in, p_cw) + max_tokens * p_out) / 1_000_000


@dataclass
class Reservation:
    amount: float
    model: str


class CostTracker:
    def __init__(self, budget: float = config.BUDGET_USD):
        self.budget = budget
        self._lock = threading.Lock()
        self.spent = self._load_spent()
        self.reserved = 0.0

    @staticmethod
    def _load_spent() -> float:
        if not config.COST_LEDGER.exists():
            return 0.0
        total = 0.0
        with open(config.COST_LEDGER, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    total += json.loads(line)["cost_usd"]
        return total

    def remaining(self) -> float:
        with self._lock:
            return self.budget - self.spent - self.reserved

    def reserve(self, model: str, input_tokens_est: int, max_tokens: int) -> Reservation:
        amount = worst_case_cost(model, input_tokens_est, max_tokens)
        with self._lock:
            if self.spent + self.reserved + amount > self.budget:
                raise BudgetExceeded(
                    f"Stopping: spent ${self.spent:.2f} + in-flight ${self.reserved:.2f} "
                    f"+ next call up to ${amount:.2f} would pass the ${self.budget:.2f} cap."
                )
            self.reserved += amount
        return Reservation(amount, model)

    def release(self, r: Reservation) -> None:
        """Call when a request failed before producing billable usage."""
        with self._lock:
            self.reserved -= r.amount

    def settle(self, r: Reservation, response, step: str, note: str = "") -> float:
        cost = usage_cost(response.usage, getattr(response, "model", None) or r.model)
        u = response.usage
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "step": step,
            "requested_model": r.model,
            "served_model": getattr(response, "model", None),
            "input_tokens": u.input_tokens,
            "output_tokens": u.output_tokens,
            "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
            "stop_reason": getattr(response, "stop_reason", None),
            "cost_usd": round(cost, 6),
            "note": note,
        }
        with self._lock:
            self.reserved -= r.amount
            self.spent += cost
            config.COST_LEDGER.parent.mkdir(parents=True, exist_ok=True)
            with open(config.COST_LEDGER, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        return cost


def summary() -> None:
    """Print spend by step: `python -m pipeline.cost`."""
    if not config.COST_LEDGER.exists():
        print("No API calls logged yet.")
        return
    by_step: dict[str, list[float]] = {}
    with open(config.COST_LEDGER, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                by_step.setdefault(e["step"], []).append(e["cost_usd"])
    total = 0.0
    print(f"{'step':<14}{'calls':>7}{'USD':>10}")
    for step, costs in by_step.items():
        total += sum(costs)
        print(f"{step:<14}{len(costs):>7}{sum(costs):>10.2f}")
    print(f"{'total':<14}{'':>7}{total:>10.2f}   (cap ${config.BUDGET_USD:.2f}, "
          f"left ${config.BUDGET_USD - total:.2f})")


if __name__ == "__main__":
    summary()
