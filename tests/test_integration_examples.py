from pathlib import Path


ADAPTER_DIR = Path("examples/express_backend_adapter")


def test_express_backend_adapter_example_files_exist() -> None:
    assert (ADAPTER_DIR / "README.md").exists()
    assert (ADAPTER_DIR / "mlScoringClient.js").exists()
    assert (ADAPTER_DIR / "loanAiMapping.js").exists()
    assert (ADAPTER_DIR / "exampleLoanIntegration.js").exists()


def test_ml_scoring_client_documents_core_ml_api_calls() -> None:
    client = (ADAPTER_DIR / "mlScoringClient.js").read_text(encoding="utf-8")

    assert "ML_API_BASE_URL" in client
    assert "/health" in client
    assert "/model-info" in client
    assert "/predict" in client
    assert "ml_model_not_ready" in client
    assert "ml_api_timeout" in client


def test_loan_ai_mapping_preserves_score_direction() -> None:
    mapper = (ADAPTER_DIR / "loanAiMapping.js").read_text(encoding="utf-8")

    assert "REQUIRED_ML_REQUEST_FIELDS" in mapper
    assert "ML_RESPONSE_STORAGE_FIELDS" in mapper
    assert "prob_default" in mapper
    assert "eligibility_score" in mapper
    assert "1 - Number(probDefault)" in mapper
    assert "MissingMlPayloadFieldError" in mapper


def test_team_integration_contract_links_backend_adapter() -> None:
    contract = Path("docs/team_integration_contract.md").read_text(encoding="utf-8")

    assert "examples/express_backend_adapter/" in contract
    assert "ML_API_BASE_URL" in contract
    assert "eligibility_score = round((1 - prob_default) * 100)" in contract
    assert "Do not store `prob_default * 100` as `ai_score`" in contract
