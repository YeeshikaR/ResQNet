from pathlib import Path
from typing import Any

import joblib

from backend.config import MODEL_PATH, USE_ML_PRIORITY

SEVERITY_POINTS = {'low': 20, 'medium': 50, 'high': 75, 'critical': 100}


def formula_priority(severity: str, people_affected: int) -> float:
    base = SEVERITY_POINTS[severity]
    people_bonus = min(people_affected * 2, 30)
    return float(min(base + people_bonus, 100))


def calculate_priority(severity: str, people_affected: int) -> float:
    if USE_ML_PRIORITY and Path(MODEL_PATH).exists():
        model = joblib.load(MODEL_PATH)
        prediction = model.predict([[SEVERITY_POINTS[severity], people_affected]])[0]
        return float(max(0, min(100, prediction)))
    return formula_priority(severity, people_affected)


def model_status() -> dict[str, Any]:
    return {
        'enabled': USE_ML_PRIORITY,
        'path': str(MODEL_PATH),
        'exists': Path(MODEL_PATH).exists(),
        'active_method': 'ml' if USE_ML_PRIORITY and Path(MODEL_PATH).exists() else 'formula',
    }
