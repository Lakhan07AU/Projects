/* RoadGuard AI - auth/session management and role-based navigation guards */
const AUTH = (() => {
  const KEY = "rg_user";
  const ROLE_HOME = {
    CITIZEN: "/report.html",
    GOVERNMENT_OFFICIAL: "/government/dashboard.html",
    ADMIN: "/government/dashboard.html",
    REPAIR_TEAM: "/repair-team/dashboard.html",
  };
  const ROLE_LABELS = {
    CITIZEN: "Citizen",
    GOVERNMENT_OFFICIAL: "Government Official",
    ADMIN: "Administrator",
    REPAIR_TEAM: "Repair Team",
  };

  function saveSession(token, user) {
    localStorage.setItem("rg_token", token);
    localStorage.setItem(KEY, JSON.stringify(user));
  }

  function clearSession() {
    localStorage.removeItem("rg_token");
    localStorage.removeItem(KEY);
  }

  function getUser() {
    try { return JSON.parse(localStorage.getItem(KEY)) || null; } catch (e) { return null; }
  }

  function setUser(user) {
    localStorage.setItem(KEY, JSON.stringify(user));
  }

  function isAuthenticated() {
    return Boolean(localStorage.getItem("rg_token") && getUser());
  }

  function homeFor(role) {
    return ROLE_HOME[role] || "/";
  }

  async function login(email, password) {
    const data = await API.post("/auth/login", { email, password });
    saveSession(data.access_token, data.user);
    return data.user;
  }

  async function register(payload) {
    const data = await API.post("/auth/register", payload);
    saveSession(data.access_token, data.user);
    return data.user;
  }

  function logout() {
    clearSession();
    window.location.href = "/index.html";
  }

  function requireAuth(roles = null) {
    if (!isAuthenticated()) {
      window.location.href = "/login.html";
      return false;
    }
    const user = getUser();
    if (roles && !roles.includes(user.role)) {
      window.location.href = homeFor(user.role);
      return false;
    }
    return true;
  }

  // If a logged-in user opens a public-only page, route them to their dashboard.
  function redirectIfLoggedIn() {
    if (isAuthenticated()) {
      const user = getUser();
      window.location.href = homeFor(user.role);
    }
  }

  // Public navbar, aware of the session (from components.js)
  function publicNavItems() {
    const user = getUser();
    if (user) {
      return {
        right: [
          { href: homeFor(user.role), label: "Dashboard" },
          { href: "/notifications.html", label: "Notifications", icon: "bi-bell" },
        ],
        user,
      };
    }
    return {
      right: [
        { href: "/login.html", label: "Login", icon: "bi-box-arrow-in-right" },
        { href: "/register.html", label: "Register", icon: "bi-person-plus", btn: true },
      ],
      user: null,
    };
  }

  return {
    saveSession, clearSession, getUser, setUser, isAuthenticated, homeFor, login, register,
    logout, requireAuth, redirectIfLoggedIn, publicNavItems, ROLE_HOME, ROLE_LABELS,
  };
})();
