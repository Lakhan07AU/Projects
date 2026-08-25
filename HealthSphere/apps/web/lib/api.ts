"use client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const ACCESS_KEY = "cg_access";
const REFRESH_KEY = "cg_refresh";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

let refreshing: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) return false;
  if (!refreshing) {
    refreshing = (async () => {
      try {
        const resp = await fetch(`${API_URL}/auth/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refresh }),
        });
        if (!resp.ok) return false;
        const data = await resp.json();
        setTokens(data.access_token, data.refresh_token);
        return true;
      } catch {
        return false;
      } finally {
        refreshing = null;
      }
    })();
  }
  return refreshing;
}

async function parseError(resp: Response): Promise<ApiError> {
  let code = "REQUEST_FAILED";
  let message = `Request failed (${resp.status})`;
  try {
    const body = await resp.json();
    if (body?.error?.code) code = body.error.code;
    if (body?.error?.message) message = body.error.message;
  } catch {
    /* non-JSON error body */
  }
  return new ApiError(code, message, resp.status);
}

export async function api<T = unknown>(
  path: string,
  options: RequestInit = {},
  retry = true,
): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> | undefined),
  };
  const token = getAccessToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const resp = await fetch(`${API_URL}${path}`, { ...options, headers });

  if ((resp.status === 403 || resp.status === 401) && retry && token) {
    // Access token may have expired — attempt silent refresh once.
    const ok = await tryRefresh();
    if (ok) return api<T>(path, options, false);
    clearTokens();
  }

  if (!resp.ok) throw await parseError(resp);
  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

export async function apiUpload<T = unknown>(path: string, file: File, query = ""): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  return api<T>(`${path}${query}`, { method: "POST", body: form });
}

/** Authenticated raw download (endpoints require an Authorization header). */
export async function apiBlob(path: string): Promise<Blob> {
  const headers: Record<string, string> = {};
  const token = getAccessToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const resp = await fetch(`${API_URL}${path}`, { headers });
  if ((resp.status === 403 || resp.status === 401) && token && (await tryRefresh())) {
    return apiBlob(path);
  }
  if (!resp.ok) throw await parseError(resp);
  return resp.blob();
}

/** Trigger a browser download of a fetched blob. */
export function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}
