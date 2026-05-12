import math

import pytest

from src.services.model_service import (
    build_prediction_response,
    calculate_confidence,
    get_ai_recommendation,
    get_risk_level,
)


MODEL_NAME = "XGBoost"
MODEL_VERSION = "koopcare-xgboost-v1"
THRESHOLD = 0.6660796


def test_get_ai_recommendation_returns_layak_below_threshold() -> None:
    assert get_ai_recommendation(0.2911, THRESHOLD) == "LAYAK"


def test_get_ai_recommendation_returns_tidak_layak_at_or_above_threshold() -> None:
    assert get_ai_recommendation(THRESHOLD, THRESHOLD) == "TIDAK_LAYAK"
    assert get_ai_recommendation(0.8, THRESHOLD) == "TIDAK_LAYAK"


def test_get_risk_level_uses_threshold_bands() -> None:
    assert get_risk_level(0.2, THRESHOLD) == "LOW"
    assert get_risk_level(THRESHOLD * 0.75, THRESHOLD) == "MEDIUM"
    assert get_risk_level(THRESHOLD, THRESHOLD) == "HIGH"


def test_calculate_confidence_uses_distance_from_threshold() -> None:
    expected = abs(0.2911 - THRESHOLD) / max(THRESHOLD, 1 - THRESHOLD)

    assert math.isclose(calculate_confidence(0.2911, THRESHOLD), expected)


def test_build_prediction_response_returns_decision_support_payload() -> None:
    response = build_prediction_response(
        prob_default=0.2911,
        threshold=THRESHOLD,
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
    )

    assert response.ai_recommendation == "LAYAK"
    assert response.risk_level == "LOW"
    assert response.prob_default == 0.2911
    assert response.threshold == 0.66608
    assert response.confidence == round(calculate_confidence(0.2911, THRESHOLD), 6)
    assert response.model_name == MODEL_NAME
    assert response.model_version == MODEL_VERSION
    assert response.human_review_required is True
    assert response.final_decision is None
    assert "Final financing decision" in response.note


@pytest.mark.parametrize("prob_default", [-0.1, 1.1])
def test_decision_helpers_reject_invalid_probability(prob_default: float) -> None:
    with pytest.raises(ValueError, match="prob_default"):
        get_ai_recommendation(prob_default, THRESHOLD)


@pytest.mark.parametrize("threshold", [-0.1, 1.1])
def test_decision_helpers_reject_invalid_threshold(threshold: float) -> None:
    with pytest.raises(ValueError, match="threshold"):
        get_risk_level(0.5, threshold)
