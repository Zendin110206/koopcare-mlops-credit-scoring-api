from pathlib import Path


CI_WORKFLOW_PATH = Path(".github/workflows/ci.yml")
REVIEWER_QUICKSTART_PATH = Path("docs/reviewer_quickstart.md")


def test_ci_workflow_exists_and_runs_core_checks() -> None:
    workflow = CI_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "actions/checkout@v6" in workflow
    assert "actions/setup-python@v6" in workflow
    assert 'python-version: "3.12"' in workflow
    assert "python -m pip install -r requirements.txt" in workflow
    assert "python -m pip check" in workflow
    assert "python -m compileall -q src tests" in workflow
    assert "python -m pytest" in workflow


def test_ci_workflow_runs_on_main_push_and_pull_request() -> None:
    workflow = CI_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "push:" in workflow
    assert "pull_request:" in workflow
    assert "- main" in workflow


def test_reviewer_quickstart_documents_demo_paths() -> None:
    guide = REVIEWER_QUICKSTART_PATH.read_text(encoding="utf-8")

    assert "local API testing" in guide
    assert "Docker" in guide
    assert "Public URL Deployment" in guide
    assert "models/best_model.pkl" in guide
    assert "POST /predict" in guide
    assert "AI recommendation" in guide
