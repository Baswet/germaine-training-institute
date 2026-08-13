/*==================================================
    GERMAINE — NEWSLETTER FORM (Step 6)
    Shared handler for every ".newsletter-form" instance
    sitewide (footer subscribe box, 10 pages), plus
    apply.html's differently-styled ".ap-connect-form"
    "Stay Updated" box, which is the same email-subscribe
    form under a page-specific class (its own dedicated CSS
    in apply-page.css depends on that class name, so the
    class itself is left alone — only this selector list was
    extended, so the existing look is untouched). Step 9 fix:
    apply.html's box never had ANY dedicated handler before —
    it was previously left to main.js's generic fake-success
    fallback and never reached the real backend. Wires both to
    POST /api/enquiries/newsletter-subscriptions via the shared
    GermaineAPI client. Discovers forms purely by class and tag
    structure (email input + submit button), identical across
    every occurrence.
==================================================*/
(function () {
    "use strict";

    function ready(fn) {
        if (document.readyState !== "loading") fn();
        else document.addEventListener("DOMContentLoaded", fn);
    }

    ready(function () {
        var forms = document.querySelectorAll(".newsletter-form, .ap-connect-form");
        if (!forms.length || !window.GermaineAPI) return;

        Array.prototype.forEach.call(forms, function (form) {
            var input = form.querySelector('input[type="email"]');
            var button = form.querySelector('button[type="submit"], button:not([type])');
            if (!input || !button) return;

            // Claims this form so main.js's generic initForms() catch-all
            // handler backs off instead of resetting the fields and faking
            // a success message before this real handler runs.
            form.setAttribute("data-form-handled", "true");

            var buttonLabel = button.textContent;
            var sending = false;

            // Small status line appended after the form — the newsletter
            // box has no existing note element, so this is the minimal
            // addition needed to surface success/error state without
            // altering the section's layout or styling.
            var status = document.createElement("p");
            status.className = "newsletter-status";
            status.setAttribute("role", "status");
            status.hidden = true;
            status.style.margin = "8px 0 0";
            status.style.fontSize = "0.85em";
            form.insertAdjacentElement("afterend", status);

            function showStatus(message, isError) {
                status.textContent = message;
                status.hidden = false;
                status.style.color = isError ? "#c0392b" : "";
            }

            form.addEventListener("submit", function (e) {
                e.preventDefault();
                if (sending) return;

                var email = input.value.trim();
                if (!form.checkValidity()) {
                    form.reportValidity();
                    return;
                }

                sending = true;
                button.disabled = true;
                button.textContent = "Subscribing…";
                status.hidden = true;

                window.GermaineAPI.post("/api/enquiries/newsletter-subscriptions", {
                    email: email,
                    source_page: window.location.pathname.split("/").pop() || "unknown",
                    consent: true,
                }).then(function (res) {
                    sending = false;
                    button.disabled = false;
                    button.textContent = buttonLabel;

                    if (res.success) {
                        form.reset();
                        showStatus(res.message || "You're subscribed — thank you.", false);
                    } else {
                        var firstFieldError = res.errors && Object.keys(res.errors).length
                            ? res.errors[Object.keys(res.errors)[0]][0]
                            : null;
                        showStatus(firstFieldError || res.message || "Something went wrong. Please try again.", true);
                    }
                });
            });
        });
    });
})();
