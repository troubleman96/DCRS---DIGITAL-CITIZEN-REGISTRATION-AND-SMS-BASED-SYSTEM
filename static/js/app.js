/* Lodrick DCRS — App JS */

(function () {
  // ── Theme ──────────────────────────────────────────────────────────────
  const THEME_KEY = "dcrs_theme";

  function getTheme() {
    return localStorage.getItem(THEME_KEY) ||
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
    document.querySelectorAll("[data-theme-toggle]").forEach(btn => {
      const icon = btn.querySelector("i");
      const label = btn.querySelector(".theme-label");
      if (icon) {
        icon.className = theme === "dark" ? "bi bi-sun" : "bi bi-moon";
      }
      if (label) {
        label.textContent = theme === "dark" ? "Light" : "Dark";
      }
      btn.setAttribute("title", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
    });
  }

  // Apply theme before paint (no flash)
  applyTheme(getTheme());

  document.addEventListener("DOMContentLoaded", () => {
    // Re-apply to sync icons
    applyTheme(getTheme());

    // Theme toggle buttons
    document.querySelectorAll("[data-theme-toggle]").forEach(btn => {
      btn.addEventListener("click", () => {
        const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        applyTheme(next);
      });
    });

    // ── Sidebar ─────────────────────────────────────────────────────────
    const shell    = document.getElementById("appShell");
    const overlay  = document.getElementById("sidebarOverlay");
    const hamburger = document.querySelector("[data-sidebar-toggle]");

    function openSidebar() {
      shell.classList.add("sidebar-open");
      if (overlay) overlay.classList.add("visible");
    }
    function closeSidebar() {
      shell.classList.remove("sidebar-open");
      if (overlay) overlay.classList.remove("visible");
    }

    if (hamburger) hamburger.addEventListener("click", () => {
      shell.classList.contains("sidebar-open") ? closeSidebar() : openSidebar();
    });

    if (overlay) overlay.addEventListener("click", closeSidebar);

    // ── Active sidebar link ──────────────────────────────────────────────
    const currentPath = window.location.pathname;
    document.querySelectorAll(".sidebar-link").forEach(link => {
      const href = link.getAttribute("href");
      if (href && href !== "/" && currentPath.startsWith(href)) {
        link.classList.add("active");
      }
    });

    // ── Auto-dismiss alerts ──────────────────────────────────────────────
    document.querySelectorAll(".alert[data-autodismiss]").forEach(el => {
      setTimeout(() => {
        el.style.opacity = "0";
        el.style.transition = "opacity 0.4s";
        setTimeout(() => el.remove(), 400);
      }, 4000);
    });
  });
})();
