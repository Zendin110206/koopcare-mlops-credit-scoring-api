export class MissingMlPayloadFieldError extends Error {
  constructor(missingFields) {
    super(`Missing ML payload fields: ${missingFields.join(', ')}`);
    this.name = 'MissingMlPayloadFieldError';
    this.missingFields = missingFields;
  }
}

export const REQUIRED_ML_REQUEST_FIELDS = [
  'code_gender',
  'name_income_type',
  'name_education_type',
  'name_family_status',
  'occupation_type',
  'flag_own_car',
  'flag_own_realty',
  'cnt_children',
  'cnt_fam_members',
  'amt_income_total',
  'amt_credit',
  'amt_annuity',
  'amt_goods_price',
  'days_birth',
  'days_employed',
  'days_last_phone_change',
  'ext_source_1',
  'ext_source_2',
  'ext_source_3',
];

export const ML_RESPONSE_STORAGE_FIELDS = [
  'ai_recommendation',
  'risk_level',
  'prob_default',
  'threshold',
  'confidence',
  'model_name',
  'model_version',
  'human_review_required',
  'final_decision',
  'note',
];

const isMissing = (value) => (
  value === undefined
  || value === null
  || value === ''
  || (typeof value === 'number' && Number.isNaN(value))
);

const assertRequiredPayloadFields = (payload) => {
  const missingFields = REQUIRED_ML_REQUEST_FIELDS.filter((field) => isMissing(payload[field]));

  if (missingFields.length > 0) {
    throw new MissingMlPayloadFieldError(missingFields);
  }
};

export const buildPredictionPayload = (applicationData) => {
  assertRequiredPayloadFields(applicationData);

  const payload = {
    code_gender: applicationData.code_gender,
    name_income_type: applicationData.name_income_type,
    name_education_type: applicationData.name_education_type,
    name_family_status: applicationData.name_family_status,
    occupation_type: applicationData.occupation_type,
    flag_own_car: applicationData.flag_own_car,
    flag_own_realty: applicationData.flag_own_realty,
    cnt_children: Number(applicationData.cnt_children),
    cnt_fam_members: Number(applicationData.cnt_fam_members),
    amt_income_total: Number(applicationData.amt_income_total),
    amt_credit: Number(applicationData.amt_credit),
    amt_annuity: Number(applicationData.amt_annuity),
    amt_goods_price: Number(applicationData.amt_goods_price),
    days_birth: Number(applicationData.days_birth),
    days_employed: Number(applicationData.days_employed),
    days_last_phone_change: Number(applicationData.days_last_phone_change),
    ext_source_1: Number(applicationData.ext_source_1),
    ext_source_2: Number(applicationData.ext_source_2),
    ext_source_3: Number(applicationData.ext_source_3),
  };

  assertRequiredPayloadFields(payload);

  return payload;
};

export const calculateEligibilityScore = (probDefault) => {
  return Math.round((1 - Number(probDefault)) * 100);
};

export const mapPredictionToLoanAiAssessment = (prediction) => {
  return {
    ai_recommendation: prediction.ai_recommendation,
    risk_level: prediction.risk_level,
    prob_default: Number(prediction.prob_default),
    threshold: Number(prediction.threshold),
    confidence: Number(prediction.confidence),
    model_name: prediction.model_name,
    model_version: prediction.model_version,
    human_review_required: prediction.human_review_required,
    final_decision: prediction.final_decision,
    note: prediction.note,
    eligibility_score: calculateEligibilityScore(prediction.prob_default),
  };
};

export const buildLoanAiAssessmentRecord = ({
  loanId,
  requestPayload,
  prediction,
  scoredAt = new Date(),
}) => {
  return {
    loan_id: loanId,
    ...mapPredictionToLoanAiAssessment(prediction),
    request_payload_json: JSON.stringify(requestPayload),
    response_payload_json: JSON.stringify(prediction),
    scored_at: scoredAt,
  };
};
