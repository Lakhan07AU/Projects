/* RoadGuard AI - API client. All backend communication goes through here. */
const API_BASE = (() => {
  const { hostname, port } = window.location;
  const isLocal = hostname === "localhost" || hostname === "127.0.0.1";
  return isLocal && port && port !== "8000" ? "http://localhost:8000" : "";
})();

const API = (() => {
  function getToken() {
    return localStorage.getItem("rg_token") || null;
  }

  async function request(method, path, { body, form, auth = true } = {}) {
    const headers = {};
    const token = getToken();
    if (auth && token) headers["Authorization"] = `Bearer ${token}`;

    let payload;
    if (form) {
      payload = form; // FormData (multipart) - no Content-Type header set manually
    } else if (body !== undefined) {
      headers["Content-Type"] = "application/json";
      payload = JSON.stringify(body);
    }

    const res = await fetch(`${API_BASE}/api${path}`, { method, headers, body: payload });

    if (res.status === 401) {
      clearSession();
      const current = window.location.pathname;
      if (!current.endsWith("login.html")) {
        window.location.href = "/login.html";
      }
      throw new Error("Session expired. Please log in again.");
    }

    const text = await res.text();
    let data = {};
    try { data = text ? JSON.parse(text) : {}; } catch (e) { data = { raw: text }; }

    if (!res.ok) {
      let msg = "Request failed";
      if (typeof data.detail === "string") msg = data.detail;
      else if (Array.isArray(data.detail) && data.detail[0] && data.detail[0].msg) {
        msg = data.detail.map((d) => d.msg).join("; ");
      }
      const err = new Error(msg);
      err.status = res.status;
      throw err;
    }
    return data;
  }

  return {
    get: (p, opts) => request("GET", p, opts),
    post: (p, body, opts) => request("POST", p, { ...opts, body }),
    put: (p, body, opts) => request("PUT", p, { ...opts, body }),
    patch: (p, body) => request("PATCH", p, { body }),
    upload: (p, form) => request("POST", p, { form }),
    token: getToken,
  };
})();
