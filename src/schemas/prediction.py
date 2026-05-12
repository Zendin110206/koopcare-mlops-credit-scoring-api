from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code_gender": "M",
                "name_income_type": "Working",
                "name_education_type": "Secondary / secondary special",
                "name_family_status": "Married",
                "occupation_type": "Laborers",
                "flag_own_car": "N",
                "flag_own_realty": "Y",
                "cnt_children": 0,
                "cnt_fam_members": 2.0,
                "amt_income_total": 135000.0,
                "amt_credit": 568800.0,
                "amt_annuity": 20560.5,
                "amt_goods_price": 450000.0,
                "days_birth": -19241,
                "days_employed": -2329.0,
                "days_last_phone_change": -1740.0,
                "ext_source_1": 0.5,
                "ext_source_2": 0.6,
                "ext_source_3": 0.4,
            }
        }
    )

    code_gender: str = Field(
        min_length=1,
        description="Applicant gender code from the prototype dataset.",
        examples=["M"],
    )
    name_income_type: str = Field(
        min_length=1,
        description="Applicant income type.",
        examples=["Working"],
    )
    name_education_type: str = Field(
        min_length=1,
        description="Applicant education type.",
        examples=["Secondary / secondary special"],
    )
    name_family_status: str = Field(
        min_length=1,
        description="Applicant family status.",
        examples=["Married"],
    )
    occupation_type: str = Field(
        min_length=1,
        description="Applicant occupation type.",
        examples=["Laborers"],
    )
    flag_own_car: Literal["Y", "N"] = Field(
        description="Whether the applicant owns a car.",
        examples=["N"],
    )
    flag_own_realty: Literal["Y", "N"] = Field(
        description="Whether the applicant owns real estate/property.",
        examples=["Y"],
    )
    cnt_children: int = Field(
        ge=0,
        description="Number of children.",
        examples=[0],
    )
    cnt_fam_members: float = Field(
        ge=1,
        description="Number of family members.",
        examples=[2.0],
    )
    amt_income_total: float = Field(
        gt=0,
        description="Applicant total income amount.",
        examples=[135000.0],
    )
    amt_credit: float = Field(
        gt=0,
        description="Requested credit amount.",
        examples=[568800.0],
    )
    amt_annuity: float = Field(
        gt=0,
        description="Loan annuity amount.",
        examples=[20560.5],
    )
    amt_goods_price: float = Field(
        gt=0,
        description="Goods price amount.",
        examples=[450000.0],
    )
    days_birth: int = Field(
        lt=0,
        description=(
            "Applicant birth offset in days. Home Credit style data stores this "
            "as a negative number before the application date."
        ),
        examples=[-19241],
    )
    days_employed: float = Field(
        description=(
            "Employment duration offset in days. Negative values are expected "
            "for normal records; anomaly values may be handled later."
        ),
        examples=[-2329.0],
    )
    days_last_phone_change: float = Field(
        le=0,
        description="Days since the applicant last changed phone number.",
        examples=[-1740.0],
    )
    ext_source_1: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="External source score 1. Optional because real BMT users may not have this feature.",
        examples=[0.5],
    )
    ext_source_2: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="External source score 2. Optional because real BMT users may not have this feature.",
        examples=[0.6],
    )
    ext_source_3: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="External source score 3. Optional because real BMT users may not have this feature.",
        examples=[0.4],
    )

    @field_validator(
        "code_gender",
        "name_income_type",
        "name_education_type",
        "name_family_status",
        "occupation_type",
        mode="before",
    )
    @classmethod
    def strip_text_fields(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value


class PredictionResponse(BaseModel):
    ai_recommendation: Literal["LAYAK", "TIDAK_LAYAK"] = Field(
        description="AI recommendation derived from probability and threshold."
    )
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Human-readable risk level."
    )
    prob_default: float = Field(
        ge=0,
        le=1,
        description="Predicted probability of default risk.",
    )
    threshold: float = Field(
        ge=0,
        le=1,
        description="Threshold used to convert probability into recommendation.",
    )
    confidence: float = Field(
        ge=0,
        le=1,
        description="Simple confidence score for the recommendation.",
    )
    model_name: str = Field(description="Model name used for prediction.")
    model_version: str = Field(description="Model version label used for prediction.")
    human_review_required: bool = Field(
        default=True,
        description="Whether cooperative officer review is required.",
    )
    final_decision: None = Field(
        default=None,
        description="Final financing decision remains outside the AI API.",
    )
    note: str = Field(description="Decision-support disclaimer.")
