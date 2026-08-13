/*=========================================================
    GERMAINE TRAINING INSTITUTE — PREMIUM HEADER
    Handles: touch/keyboard support for desktop dropdown &
    mega menus, and keeps --header-height in sync while the
    branding bar shrinks/expands on scroll.

    Note: hover-open/close for dropdowns and the "sticky"
    class on #header are already handled in main.js
    (initDropdownMenus / initStickyHeader). This file only
    adds the behaviour main.js does not cover.
=========================================================*/

(function () {

    var isFinePointer = window.matchMedia &&
        window.matchMedia("(hover: hover) and (pointer: fine)").matches;

    var dropdowns = document.querySelectorAll(".nav-links > li.dropdown");

    dropdowns.forEach(function (dropdown) {

        var trigger = dropdown.querySelector(":scope > a");

        if (!trigger) return;

        trigger.setAttribute("aria-expanded", "false");
        trigger.setAttribute("aria-haspopup", "true");

        function closeDropdown() {
            dropdown.classList.remove("open");
            trigger.setAttribute("aria-expanded", "false");
        }

        function openDropdown() {
            dropdowns.forEach(function (d) {
                if (d !== dropdown) {
                    d.classList.remove("open");
                    var t = d.querySelector(":scope > a");
                    if (t) t.setAttribute("aria-expanded", "false");
                }
            });
            dropdown.classList.add("open");
            trigger.setAttribute("aria-expanded", "true");
        }

        // Touch / no-hover devices: first interaction opens the panel
        // instead of navigating straight through the trigger link.
        trigger.addEventListener("click", function (e) {

            if (!isFinePointer) {

                if (!dropdown.classList.contains("open")) {
                    e.preventDefault();
                    openDropdown();
                }

            }

        });

        // Keyboard support
        trigger.addEventListener("keydown", function (e) {

            if (e.key === "Enter" || e.key === " ") {

                if (!dropdown.classList.contains("open")) {
                    e.preventDefault();
                    openDropdown();
                }

            }

            if (e.key === "Escape") {
                closeDropdown();
                trigger.blur();
            }

        });

        dropdown.addEventListener("keydown", function (e) {

            if (e.key === "Escape") {
                closeDropdown();
                trigger.focus();
            }

        });

    });

    // Close any open dropdown when tapping/clicking outside the nav
    document.addEventListener("click", function (e) {

        if (!e.target.closest(".nav-links > li.dropdown")) {

            dropdowns.forEach(function (d) {
                d.classList.remove("open");
                var t = d.querySelector(":scope > a");
                if (t) t.setAttribute("aria-expanded", "false");
            });

        }

    });

    // Keep the fixed-stack height measurement (used for page-shell
    // offset and side-nav positioning) accurate while the branding
    // bar shrinks/expands as the "sticky" class toggles.
    var lastSticky = null;

    function watchStickyChange() {

        var header = document.getElementById("header");

        if (!header) return;

        var isSticky = header.classList.contains("sticky");

        if (isSticky !== lastSticky) {

            lastSticky = isSticky;

            window.dispatchEvent(new Event("resize"));

        }

    }

    window.addEventListener("scroll", watchStickyChange, { passive: true });

})();
