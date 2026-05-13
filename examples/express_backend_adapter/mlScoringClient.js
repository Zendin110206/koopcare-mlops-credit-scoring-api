const DEFAULT_ML_API_BASE_URL = 'http://127.0.0.1:8000';
const DEFAULT_TIMEOUT_MS = 5000;

export class MlApiError extends Error {
  constructor(message, { status = null, code = 'ml_api_error', detail = null } = {}) {
    super(message);
    this.name = 'MlApiError';
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}

const getBaseUrl = (baseUrl = process.env.ML_API_BASE_URL) => {
  return (baseUrl || DEFAULT_ML_API_BASE_URL).replace(/\/+$/, '');
};

const parseJsonSafely = async (response) => {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
};

const requestJson = async (
  path,
  {
    method = 'GET',
    body = null,
    baseUrl,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    fetchImpl = globalThis.fetch,
  } = {},
) => {
  if (typeof fetchImpl !== 'function') {
    throw new MlApiError(
      'No fetch implementation is available. Use Node.js 18+ or inject fetchImpl.',
      { code: 'fetch_unavailable' },
    );
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  const url = `${getBaseUrl(baseUrl)}${path}`;

  try {
    const response = await fetchImpl(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: body === null ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
    const parsedBody = await parseJsonSafely(response);

    if (!response.ok) {
      const detail = parsedBody?.detail || parsedBody;
      const code = detail?.error || `ml_api_http_${response.status}`;
      const message = detail?.message || `ML API request failed with HTTP ${response.status}.`;

      throw new MlApiError(message, {
        status: response.status,
        code,
        detail,
      });
    }

    return parsedBody;
  } catch (error) {
    if (error instanceof MlApiError) {
      throw error;
    }

    if (error?.name === 'AbortError') {
      throw new MlApiError('ML API request timed out.', {
        code: 'ml_api_timeout',
      });
    }

    throw new MlApiError(`Unable to reach ML API: ${error.message}`, {
      code: 'ml_api_unreachable',
      detail: error,
    });
  } finally {
    clearTimeout(timeout);
  }
};

export const getMlHealth = (options = {}) => {
  return requestJson('/health', options);
};

export const getModelInfo = (options = {}) => {
  return requestJson('/model-info', options);
};

export const assertModelReady = async (options = {}) => {
  const modelInfo = await getModelInfo(options);

  if (
    modelInfo?.model_loaded !== true
    || modelInfo?.artifact_status !== 'available'
    || modelInfo?.metadata_source !== 'artifact'
  ) {
    throw new MlApiError('ML model is not ready for prediction.', {
      code: 'ml_model_not_ready',
      detail: modelInfo,
    });
  }

  return modelInfo;
};

export const predictCreditRisk = (payload, options = {}) => {
  return requestJson('/predict', {
    ...options,
    method: 'POST',
    body: payload,
  });
};

