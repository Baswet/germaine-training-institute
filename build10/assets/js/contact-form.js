/*==================================================
    GERMAINE — CONTACT FORM (Step 6)
    Wires contact.html's #contact-form to
    POST /api/enquiries/contact-messages via the shared
    GermaineAPI client. No visual changes — reuses the
    existing markup and only toggles disabled/text state
    on the existing submit button plus a small inline
    status line inserted next to the form note.
==================================================*/
(function () {
    "use strict";

    function ready(fn) {
        if (document.readyState !== "loading") fn();
        else document.addEventListener("DOMContentLoaded", fn);
    }

    ready(function () {
        var form = document.getElementById("contact-form");
        if (!form || !window.GermaineAPI) return;

        // Claims this form so main.js's generic initForms() catch-all
        // handler (assets/js/main.js) backs off instead of resetting the
        // fields and faking a success message before this real handler runs.
        form.setAttribute("data-form-handled", "true");

        var submitBtn = form.querySelector(".cu-form-submit");
        var submitLabel = submitBtn ? submitBtn.innerHTML : null;

        // Small status line, inserted once, reused for both error and
        // success messaging — matches the existing .cu-form-note style
        // so nothing about the form's visual design changes.
        var status = document.createElement("p");
        status.className = "cu-form-note cu-form-status";
        status.setAttribute("role", "status");
        status.hidden = true;
        form.appendChild(status);

        function showStatus(message, isError) {
            status.textContent = message;
            status.hidden = false;
            status.style.color = isError ? "#c0392b" : "";
        }

        var sending = false;

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            if (sending) return;

            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            var payload = {
                name: document.getElementById("c-name").value.trim(),
                email: document.getElementById("c-email").value.trim(),
                phone: document.getElementById("c-phone").value.trim() || undefined,
                subject: document.getElementById("c-subject").value.trim() || undefined,
                message: document.getElementById("c-message").value.trim(),
            };

            sending = true;
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = "Sending…";
            }
            status.hidden = true;

            window.GermaineAPI.post("/api/enquiries/contact-messages", payload).then(function (res) {
                sending = false;
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitLabel;
                }

                if (res.success) {
                    form.reset();
                    showStatus(res.message || "Thank you — your message has been sent. We'll get back to you within one business day.", false);
                } else {
                    var firstFieldError = res.errors && Object.keys(res.errors).length
                        ? res.errors[Object.keys(res.errors)[0]][0]
                        : null;
                    showStatus(firstFieldError || res.message || "Something went wrong. Please try again.", true);
                }
            });
        });
    });
})();
