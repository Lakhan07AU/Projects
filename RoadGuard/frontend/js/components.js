/* RoadGuard AI - reusable layout components: public navbar, dashboard sidebar,
   top bar, footer and demo banner. */

const COMPONENTS = (() => {
  function demoBanner() {
    if (document.getElementById("demo-banner")) return;
    const div = document.createElement("div");
    div.id = "demo-banner";
    div.className = "demo-banner";
    div.innerHTML = '<i class="bi bi-lightning-charge-fill me-1"></i>Demo Mode: AI results are simulated for demonstration';
    document.body.prepend(div);
  }

  function publicNavbar(active = "") {
    const { right, user } = AUTH.publicNavItems();
    const links = [
      { href: "/index.html", label: "Home", key: "home" },
      { href: "/map.html", label: "Road Map", key: "map" },
      { href: "/complaints.html", label: "My Complaints", key: "complaints", authOnly: true },
      { href: "/report.html", label: "Report a Pothole", key: "report", authOnly: true, strong: true },
    ];

    const mid = links
      .filter((l) => !l.authOnly || user)
      .map((l) => {
        const cls = ["nav-link", active === l.key ? "active" : ""].join(" ");
        return `<li class="nav-item"><a class="${cls}" href="${l.href}">${l.label}</a></li>`;
      })
      .join("");

    const rightHtml = right
      .map((r) =>
        r.btn
          ? `<a class="btn btn-accent btn-sm ms-2" href="${r.href}"><i class="bi ${r.icon} me-1"></i>${r.label}</a>`
          : `<a class="nav-link ms-1" href="${r.href}"><i class="bi ${r.icon || ""} me-1"></i>${r.label}</a>`
      )
      .join("");

    const container = document.getElementById("navbar");
    if (!container) return;
    container.innerHTML = `
      <nav class="navbar navbar-expand-lg rg-navbar">
        <div class="container">
          <a class="navbar-brand rg-brand" href="/index.html">
            <i class="bi bi-shield-fill-check me-2"></i>RoadGuard AI
            <small>DETECT &middot; REPORT &middot; PRIORITIZE &middot; REPAIR</small>
          </a>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#rgNav">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="rgNav">
            <ul class="navbar-nav ms-auto align-items-lg-center">
              ${mid}
              ${user ? `<li class="nav-item ms-2"><a class="btn btn-outline-light btn-sm" href="/notifications.html"><i class="bi bi-bell me-1"></i></a></li>
                <li class="nav-item dropdown">
                  <a class="nav-link dropdown-toggle" data-bs-toggle="dropdown">${UTILS.esc(user.name)}</a>
                  <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="/profile.html"><i class="bi bi-person me-2"></i>Profile</a></li>
                    <li><a class="dropdown-item" href="/complaints.html"><i class="bi bi-list-check me-2"></i>My Complaints</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><button class="dropdown-item text-danger" onclick="AUTH.logout()"><i class="bi bi-box-arrow-right me-2"></i>Logout</button></li>
                  </ul>
                </li>` : rightHtml}
            </ul>
          </div>
        </div>
      </nav>`;
  }

  function sidebar(items, active) {
    const container = document.getElementById("sidebar");
    if (container) {
      const user = AUTH.getUser();
      container.innerHTML = `
      <aside class="rg-sidebar" id="rgSidebar">
        <div class="brand-box">
          <a href="/index.html" class="rg-brand text-decoration-none">
            <i class="bi bi-shield-fill-check me-2"></i>RoadGuard AI
          </a>
          <div class="text-white-50" style="font-size:.75rem;">${UTILS.esc(user ? AUTH.ROLE_LABELS[user.role] : "")}</div>
        </div>
        <ul class="side-nav">
          ${items
            .map((i) => `<li><a class="${active === i.key ? "active" : ""}" href="${i.href}"><i class="bi ${i.icon}"></i>${i.label}</a></li>`)
            .join("")}
        </ul>
        <div class="side-foot">
          <div>Logged in as <strong>${UTILS.esc(user ? user.name : "-")}</strong></div>
          <a class="text-decoration-none" style="color:#93c5fd;" href="#" onclick="AUTH.logout()">Logout</a>
        </div>
      </aside>`;
    }

    const title = document.getElementById("pageTitle");
    if (title) title.textContent = active;
    const user = AUTH.getUser();
    const badge = document.getElementById("topbarUser");
    if (badge && user) badge.textContent = AUTH.ROLE_LABELS[user.role] || user.role;
  }

  function endSidebar() { /* layout is fully owned by the page; nothing to close */ }

  function footer() {
    const el = document.getElementById("footer");
    if (!el) return;
    el.innerHTML = `
      <footer class="rg-footer">
        <div class="container">
          <div class="row g-4">
            <div class="col-md-4">
              <div class="rg-brand">RoadGuard AI</div>
              <div class="mt-1">Detect. Report. Prioritize. Repair.</div>
              <p class="mt-2 mb-0" style="font-size:.85rem;">AI-powered road infrastructure management platform.</p>
            </div>
            <div class="col-md-4">
              <strong>Platform</strong>
              <ul class="list-unstyled mt-2">
                <li><a href="/report.html">Report a Pothole</a></li>
                <li><a href="/map.html">Public Road Map</a></li>
                <li><a href="/login.html">Government Portal</a></li>
              </ul>
            </div>
            <div class="col-md-4">
              <strong>Note</strong>
              <p class="mt-2" style="font-size:.85rem;">All AI results in demo mode are simulated. Estimates are preliminary and require official engineering verification.</p>
            </div>
          </div>
          <hr style="border-color:rgba(255,255,255,.15);">
          <div class="text-center" style="font-size:.8rem;">&copy; 2026 RoadGuard AI &middot; Detect. Report. Prioritize. Repair.</div>
        </div>
      </footer>`;
  }

  return { demoBanner, publicNavbar, sidebar, endSidebar, footer };
})();
