/* =========================================
   KISANSATHI AI - GLOBAL THEME CONTROLLER
========================================= */

(function () {
    const STORAGE_KEY = "kisansathi-theme";
    const root = document.documentElement;

    function getSavedTheme() {
        try {
            return localStorage.getItem(STORAGE_KEY);
        } catch (error) {
            return null;
        }
    }

    function applyTheme(theme) {
        const selectedTheme = theme === "dark" ? "dark" : "light";

        root.setAttribute("data-theme", selectedTheme);

        const button = document.getElementById("themeToggle");

        if (button) {
            const isDark = selectedTheme === "dark";
            button.textContent = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
            button.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
            button.setAttribute("aria-pressed", String(isDark));
        }
    }

    function toggleTheme() {
        const currentTheme = root.getAttribute("data-theme") || "light";
        const nextTheme = currentTheme === "dark" ? "light" : "dark";

        applyTheme(nextTheme);

        try {
            localStorage.setItem(STORAGE_KEY, nextTheme);
        } catch (error) {
            console.warn("Theme preference could not be saved.", error);
        }
    }

    // Apply saved theme as soon as the script runs.
    applyTheme(getSavedTheme() || "light");

    // Attach click handler after the page DOM is ready.
    document.addEventListener("DOMContentLoaded", function () {
        const button = document.getElementById("themeToggle");

        if (button) {
            button.addEventListener("click", toggleTheme);
            applyTheme(getSavedTheme() || "light");
        } else {
            console.warn("KisanSathi theme button #themeToggle was not found.");
        }
    });
})();