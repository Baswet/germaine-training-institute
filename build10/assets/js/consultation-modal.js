/*==================================================
    GERMAINE — "REQUEST A CONSULTATION" MODAL
    Corporate Training page only. Opens/closes the modal and
    submits #cmForm to the real backend (POST
    /api/enquiries/partner-enquiries, enquiry_type="partnership")
    via the shared GermaineAPI client, swapping the form for a
    success card once the request actually succeeds. No-ops if
    the modal markup isn't present on the page.
==================================================*/
(function () {

    function ready(fn) {
        if (document.readyState !== "loading") fn();
        else document.addEventListener("DOMContentLoaded", fn);
    }

    ready(function () {

        var modal = document.getElementById("cmModal");
        if (!modal) return;

        var backdrop = document.getElementById("cmModalBackdrop");
        var closeBtn = document.getElementById("cmModalClose");
        var form = document.getElementById("cmForm");
        var success = document.getElementById("cmSuccess");
        var doneBtn = document.getElementById("cmDoneBtn");
        var triggers = document.querySelectorAll("[data-cm-trigger]");
        var lastFocused = null;

        function openModal(e) {
            if (e) e.preventDefault();
            lastFocused = document.activeElement;
            modal.classList.add("is-open");
            modal.setAttribute("aria-hidden", "false");
            document.body.classList.add("cm-modal-lock");
            var firstField = document.getElementById("cmName");
            if (firstField) {
                window.setTimeout(function () { firstField.focus(); }, 250);
            }
        }

        function closeModal() {
            modal.classList.remove("is-open");
            modal.setAttribute("aria-hidden", "true");
            document.body.classList.remove("cm-modal-lock");
            if (lastFocused && typeof lastFocused.focus === "function") {
                lastFocused.focus();
            }
        }

        function resetModal() {
            if (form) {
                form.reset();
                form.hidden = false;
            }
            if (success) success.hidden = true;
        }

        triggers.forEach(function (t) {
            t.addEventListener("click", openModal);
        });

        if (backdrop) backdrop.addEventListener("click", closeModal);
        if (closeBtn) closeBtn.addEventListener("click", closeModal);

        if (doneBtn) {
            doneBtn.addEventListener("click", function () {
                closeModal();
                window.setTimeout(resetModal, 400);
            });
        }

        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape" && modal.classList.contains("is-open")) {
                closeModal();
            }
        });

        var cmSubmitBtn = form ? form.querySelector(".cm-submit") : null;
        var cmSending = false;
        var cmStatus = null;
        if (form) {
            // Claims this form so main.js's generic initForms() catch-all
            // handler backs off instead of resetting the fields and faking
            // a success message before this real handler runs.
            form.setAttribute("data-form-handled", "true");

            cmStatus = document.createElement("p");
            cmStatus.className = "cm-form-status";
            cmStatus.setAttribute("role", "status");
            cmStatus.hidden = true;
            cmStatus.style.cssText = "margin-top:10px;font-size:0.9em;color:#c0392b;";
            form.appendChild(cmStatus);
        }

        if (form) {
            form.addEventListener("submit", function (e) {
                e.preventDefault();

                if (cmSending) return;

                if (!form.checkValidity()) {
                    form.reportValidity();
                    return;
                }

                if (!window.GermaineAPI) return;

                // Wired to POST /api/enquiries/partner-enquiries (Step 6),
                // enquiry_type="corporate_training" for this page. The
                // backend table has no columns for "Training Area" or
                // "Preferred Consultation Method" — folded into the
                // free-text message field rather than dropped.
                var fullName = document.getElementById("cmName").value.trim();
                var company = document.getElementById("cmCompany").value.trim();
                var workEmail = document.getElementById("cmEmail").value.trim();
                var phone = document.getElementById("cmPhone").value.trim();
                var area = document.getElementById("cmArea").value;
                var method = document.getElementById("cmMethod").value;
                var needs = document.getElementById("cmNeeds").value.trim();

                var messageParts = [];
                if (area) messageParts.push("Training area: " + area);
                if (method) messageParts.push("Preferred consultation method: " + method);
                if (needs) messageParts.push("Training needs: " + needs);

                var payload = {
                    organisation: company,
                    contact_name: fullName,
                    email: workEmail,
                    phone: phone || undefined,
                    enquiry_type: "corporate_training",
                    message: messageParts.join("\n") || undefined,
                };

                cmSending = true;
                if (cmSubmitBtn) cmSubmitBtn.disabled = true;
                if (cmStatus) cmStatus.hidden = true;

                window.GermaineAPI.post("/api/enquiries/partner-enquiries", payload).then(function (res) {
                    cmSending = false;
                    if (cmSubmitBtn) cmSubmitBtn.disabled = false;

                    if (res.success) {
                        form.hidden = true;
                        if (success) success.hidden = false;
                    } else if (cmStatus) {
                        var firstFieldError = res.errors && Object.keys(res.errors).length
                            ? res.errors[Object.keys(res.errors)[0]][0]
                            : null;
                        cmStatus.textContent = firstFieldError || res.message || "Something went wrong. Please try again.";
                        cmStatus.hidden = false;
                    }
                });
            });
        }
    });

})();
