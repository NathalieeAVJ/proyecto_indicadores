const BASE_URL = 'http://localhost:8000/api/v1/';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const body = options.body;
  
  // Robust check for FormData
  const isFormData = body && (
    body instanceof FormData || 
    (body.constructor && body.constructor.name === 'FormData') ||
    typeof body.append === 'function' ||
    Object.prototype.toString.call(body) === '[object FormData]'
  );

  const headers = {
    ...(token && { 'Authorization': `Token ${token}` }),
    ...options.headers,
  };

  // If it IS FormData, MUST NOT have a Content-Type manual header
  if (isFormData) {
    delete headers['Content-Type'];
    delete headers['content-type'];
  } else if (!headers['Content-Type'] && !headers['content-type'] && options.method !== 'GET') {
    headers['Content-Type'] = 'application/json';
  }

  const url = options.baseURL ? `${options.baseURL}${path}` : `${BASE_URL}${path}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(errorData.detail || response.statusText);
    error.status = response.status;
    error.data = errorData;
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
}

const api = {
  get: (url, options) => request(url, { ...options, method: 'GET' }),
  post: (url, body, options = {}) => {
    const isFormData = body && (body instanceof FormData || body.constructor?.name === 'FormData' || typeof body.append === 'function');
    return request(url, { ...options, method: 'POST', body: isFormData ? body : JSON.stringify(body) });
  },
  put: (url, body, options = {}) => {
    const isFormData = body && (body instanceof FormData || body.constructor?.name === 'FormData' || typeof body.append === 'function');
    return request(url, { ...options, method: 'PUT', body: isFormData ? body : JSON.stringify(body) });
  },
  patch: (url, body, options = {}) => {
    const isFormData = body && (body instanceof FormData || body.constructor?.name === 'FormData' || typeof body.append === 'function');
    return request(url, { ...options, method: 'PATCH', body: isFormData ? body : JSON.stringify(body) });
  },
  delete: (url, options) => request(url, { ...options, method: 'DELETE' }),
};

export default api;
