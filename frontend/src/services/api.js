const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const text = await response.text().catch(() => "");
    let body = {};
    try {
      body = JSON.parse(text || "{}");
    } catch {
      body = {};
    }
    throw new Error(body.detail ?? text ?? `Request failed with ${response.status}`);
  }
  const contentType = response.headers.get("content-type") ?? "";
  const raw = await response.text();
  return contentType.includes("application/json") ? JSON.parse(raw) : raw;
}

export async function uploadRepository(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);
  onProgress?.(30);
  const result = await request("/upload", { method: "POST", body: formData });
  onProgress?.(100);
  return result;
}

export const getAnalysis = (analysisId) => request(`/analysis/${analysisId}`);
export const getGraph = (analysisId) => request(`/analysis/${analysisId}/graph`);
export const getTree = (analysisId) => request(`/analysis/${analysisId}/tree`);
export const getMetrics = (analysisId) => request(`/analysis/${analysisId}/metrics`);
export const searchAnalysis = (analysisId, query) =>
  request(`/analysis/${analysisId}/search?q=${encodeURIComponent(query)}`);
export const exportMermaid = (analysisId) => request(`/export/${analysisId}/mermaid`);

