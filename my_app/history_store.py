import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


_HISTORY_FILE = Path(__file__).resolve().parent / "analysis_history.json"


def _normalize_legacy_entry(day_key: str, payload: Dict) -> Dict:
    return {
        "timestamp": payload.get("updated_at", day_key),
        "date": day_key,
        "mode": payload.get("mode", "legacy"),
        "source": payload.get("source", "historique_legacy"),
        "total_transactions": int(payload.get("transactions", 0) or 0),
        "frauds": int(payload.get("fraudes", 0) or 0),
        "blocked_amount": float(payload.get("montant_bloque", 0.0) or 0.0),
        "mean_probability": float(payload.get("mean_probability", 0.0) or 0.0),
        "max_probability": float(payload.get("max_probability", 0.0) or 0.0),
    }


def load_history() -> List[Dict]:
    if not _HISTORY_FILE.exists():
        return []

    try:
        raw = json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if isinstance(raw, list):
        entries = [entry for entry in raw if isinstance(entry, dict)]
    elif isinstance(raw, dict):
        entries = [_normalize_legacy_entry(key, value) for key, value in raw.items() if isinstance(value, dict)]
    else:
        entries = []

    return sorted(entries, key=lambda entry: str(entry.get("timestamp", "")))


def save_history(entries: List[Dict]) -> None:
    _HISTORY_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def append_history_entry(entry: Dict, keep_last: int = 1000) -> None:
    entries = load_history()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    normalized = {
        "timestamp": timestamp,
        "date": timestamp[:10],
        "mode": entry.get("mode", "inconnu"),
        "source": entry.get("source", "inconnu"),
        "total_transactions": int(entry.get("total_transactions", 0) or 0),
        "frauds": int(entry.get("frauds", 0) or 0),
        "blocked_amount": float(entry.get("blocked_amount", 0.0) or 0.0),
        "mean_probability": float(entry.get("mean_probability", 0.0) or 0.0),
        "max_probability": float(entry.get("max_probability", 0.0) or 0.0),
    }

    entries.append(normalized)
    if keep_last > 0:
        entries = entries[-keep_last:]

    save_history(entries)


def compute_kpis(entries: List[Dict]) -> Dict:
    total_analyses = len(entries)
    total_transactions = sum(int(entry.get("total_transactions", 0) or 0) for entry in entries)
    total_frauds = sum(int(entry.get("frauds", 0) or 0) for entry in entries)
    total_blocked_amount = sum(float(entry.get("blocked_amount", 0.0) or 0.0) for entry in entries)

    fraud_rate = (total_frauds / total_transactions * 100) if total_transactions else 0.0
    avg_blocked_amount = (total_blocked_amount / total_frauds) if total_frauds else 0.0

    return {
        "total_analyses": total_analyses,
        "total_transactions": total_transactions,
        "total_frauds": total_frauds,
        "total_blocked_amount": total_blocked_amount,
        "fraud_rate": fraud_rate,
        "avg_blocked_amount": avg_blocked_amount,
    }
