from pydantic import BaseModel, Field


class ModelInfoResponse(BaseModel):
    model_loaded: bool = Field(
        description="Whether the expected model artifact is available and valid."
    )
    model_name: str = Field(description="Expected prototype model name.")
    model_version: str = Field(description="Configured model version label.")
    model_path: str = Field(description="Configured model artifact path.")
    threshold: float = Field(
        description=(
            "Classification threshold reported from the artifact when valid, "
            "otherwise from configuration."
        )
    )
    features_count: int = Field(
        description=(
            "Number of input features reported from the artifact when valid, "
            "otherwise from configuration."
        )
    )
    artifact_status: str = Field(
        description="Human-readable status of the local model artifact."
    )
    artifact_keys: list[str] = Field(
        default_factory=list,
        description="Keys found in the model artifact when it can be inspected.",
    )
    artifact_error: str | None = Field(
        default=None,
        description="Artifact loading or validation error when inspection fails.",
    )
    metadata_source: str = Field(
        description="Where the endpoint metadata currently comes from."
    )
    note: str = Field(description="Operational note for API users.")
