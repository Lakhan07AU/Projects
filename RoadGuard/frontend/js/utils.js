/* RoadGuard AI - utilities: formatting, badges, toasts, states */
const UTILS = (() => {
  const SEVERITY_LABELS = { LOW: "Low", MEDIUM: "Medium", HIGH: "High", CRITICAL: "Critical" };
  const STATUS_LABELS = {
    SUBMITTED: "Submitted", AI_ANALYZED: "AI Analyzed", PENDING_VERIFICATION: "Pending Verification",
    VERIFIED: "Verified", PRIORITIZED: "Prioritized", ASSIGNED: "Assigned",
    IN_PROGRESS: "In Progress", COMPLETED: "Completed", CITIZEN_VERIFICATION: "Citizen Verification",
    CLOSED: "Closed", REJECTED: "Rejected",
  };

  function esc(value) {
    if (value === null || value === undefined) return "";
    return String(value).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  function fmtINR(value) {
    const n = Number(value || 0);
    return "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 0 });
  }

  function fmtNum(value, digits = 1) {
    const n = Number(value || 0);
    return n.toLocaleString("en-IN", { maximumFractionDigits: digits });
  }

  function fmtDate(value) {
    if (!value) return "-";
    return new Date(value).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
  }

  function severityBadge(sev) {
    const label = SEVERITY_LABELS[sev] || sev;
    return `<span class="badge-sev sev-${esc(sev)}">${esc(label)}</span>`;
  }

  function priorityBadge(pri) {
    const map = { LOW: "st-CLOSED", MEDIUM: "st-PENDING_VERIFICATION", HIGH: "st-VERIFIED", CRITICAL: "st-REJECTED" };
    return `<span class="badge-status ${map[pri] || "badge-status"}">${esc(pri || "-")}</span>`;
  }

  function statusBadge(st) {
    const label = STATUS_LABELS[st] || st || "-";
    return `<span class="badge-status st-${esc(st)}">${esc(label)}</span>`;
  }

  function confidencePct(v) {
    return (Number(v || 0) * 100).toFixed(1) + "%";
  }

  function toast(message, type = "success") {
    const colors = { success: "#16a34a", danger: "#dc2626", warning: "#d97706", info: "#2563eb" };
    const el = document.createElement("div");
    el.style.cssText = `position:fixed;top:16px;right:16px;z-index:3000;background:${colors[type]||colors.info};
      color:#fff;padding:12px 18px;border-radius:10px;box-shadow:0 6px 20px rgba(0,0,0,.2);font-weight:600;
      max-width:360px;font-size:.9rem;`;
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(() => { el.style.opacity = "0"; el.style.transition = "opacity .3s"; }, 3500);
    setTimeout(() => el.remove(), 4000);
  }

  function showLoading(containerId, label = "Loading...") {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `<div class="text-center py-4 text-muted"><div class="spinner-border text-primary"></div>
      <div class="mt-2">${esc(label)}</div></div>`;
  }

  function emptyState(containerId, title = "Nothing here yet", sub = "") {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `<div class="empty-state"><i class="bi bi-inbox"></i>
      <strong>${esc(title)}</strong>${sub ? `<div class="text-muted-sm">${esc(sub)}</div>` : ""}</div>`;
  }

  function errorState(containerId, message) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `<div class="alert alert-danger">${esc(message || "Something went wrong")}</div>`;
  }

  function spinnerButton(btn, loading = true, label = "Please wait...") {
    if (!btn) return;
    if (loading) {
      btn.dataset.original = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>${esc(label)}`;
    } else {
      btn.disabled = false;
      btn.innerHTML = btn.dataset.original || btn.innerHTML;
    }
  }

  return {
    esc, fmtINR, fmtNum, fmtDate, severityBadge, priorityBadge, statusBadge,
    confidencePct, toast, showLoading, emptyState, errorState, spinnerButton,
  };
})();
