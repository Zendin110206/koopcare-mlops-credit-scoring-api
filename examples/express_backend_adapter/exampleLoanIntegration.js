import { assertModelReady, predictCreditRisk } from './mlScoringClient.js';
import {
  buildLoanAiAssessmentRecord,
  buildPredictionPayload,
} from './loanAiMapping.js';

export const scoreLoanApplication = async ({
  loanId,
  applicationData,
  saveAiAssessment,
  mlClientOptions = {},
}) => {
  await assertModelReady(mlClientOptions);

  const requestPayload = buildPredictionPayload(applicationData);
  const prediction = await predictCreditRisk(requestPayload, mlClientOptions);
  const aiAssessmentRecord = buildLoanAiAssessmentRecord({
    loanId,
    requestPayload,
    prediction,
  });

  if (typeof saveAiAssessment === 'function') {
    await saveAiAssessment(aiAssessmentRecord);
  }

  return aiAssessmentRecord;
};

