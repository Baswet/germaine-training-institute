/*==================================================
    GERMAINE — ALUMNI REGISTRATION PAGE
    Floating-label <select> support + form submit handling.
    (Text inputs/textareas use pure-CSS :not(:placeholder-shown)
    — only <select> needs a JS-driven "has-value" class.)
==================================================*/
(function () {
    "use strict";

    var selects = document.querySelectorAll(".alu-field select");
    selects.forEach(function (sel) {
        function sync() {
            sel.classList.toggle("has-value", !!sel.value);
        }
        sel.addEventListener("change", sync);
        sync();
    });

    var form = document.getElementById("alumniForm");
    var success = document.getElementById("alumniSuccess");
    var sending = false;
    var status = null;

    if (form) {
        // Claims this form so main.js's generic initForms() catch-all
        // handler backs off instead of resetting the fields and faking
        // a success message before this real handler runs.
        form.setAttribute("data-form-handled", "true");

        status = document.createElement("p");
        status.className = "alu-form-status";
        status.setAttribute("role", "status");
        status.hidden = true;
        status.style.cssText = "margin-top:10px;font-size:0.9em;color:#c0392b;";
        form.appendChild(status);
    }

    if (form && success) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            if (sending) return;

            if (!form.checkValidity()) {
                form.reportValidity();
                return;
            }

            if (!window.GermaineAPI) return;

            // Wired to POST /api/alumni/register (Step 6). "Programme
            // Studied" (#aluProgramme) is DELIBERATELY NOT SENT: Step 2
            // §39 item F documents that this field's options are actually
            // 9 school names + "Germaine AI Bootcamp", not individual
            // programmes, so there is no safe, non-guessed way to map its
            // value to programmes.id. alumni.programme_id is left null on
            // every record created here until that item is resolved.
            var interests = Array.prototype.slice
                .call(form.querySelectorAll('input[name="stayConnected"]:checked'))
                .map(function (el) { return el.value; });

            var payload = {
                full_name: document.getElementById("aluName").value.trim(),
                email: document.getElementById("aluEmail").value.trim(),
                phone: document.getElementById("aluPhone").value.trim(),
                graduation_year: parseInt(document.getElementById("aluGradYear").value, 10) || undefined,
                organisation: document.getElementById("aluEmployer").value.trim() || undefined,
                engagement_interests: interests.length ? interests : undefined,
                consent: document.getElementById("aluConsent").checked,
            };

            sending = true;
            if (status) status.hidden = true;

            window.GermaineAPI.post("/api/alumni/register", payload).then(function (res) {
                sending = false;

                if (res.success) {
                    form.hidden = true;
                    success.hidden = false;
                    var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
                    success.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "center" });
                } else if (status) {
                    var firstFieldError = res.errors && Object.keys(res.errors).length
                        ? res.errors[Object.keys(res.errors)[0]][0]
                        : null;
                    status.textContent = firstFieldError || res.message || "Something went wrong. Please try again.";
                    status.hidden = false;
                }
            });
        });
    }
})();
