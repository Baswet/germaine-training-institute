/*==================================================
    GERMAINE — "REQUEST OUR GRADUATE PROFILE" MODAL
    Opens/closes the modal, renders Lucide icons, handles
    the file-name preview, and submits #gpForm to the real
    backend (POST /api/enquiries/graduate-requests) via the
    shared GermaineAPI client, swapping the form for a success
    card once the request actually succeeds.

    #ghInlineForm below is dead code: it references an inline
    compact form that no longer exists in graduate-hire.html
    (removed when the FAQ + CTA sections were combined). Its
    getElementById lookup returns null, so that branch never
    runs — left here only as a historical no-op guard rather
    than deleted, since removing it isn't needed to fix any
    live behavior.
==================================================*/

(function () {

    function ready(fn) {
        if (document.readyState !== "loading") fn();
        else document.addEventListener("DOMContentLoaded", fn);
    }

    ready(function () {

        var modal = document.getElementById("gpModal");
        if (!modal) return;

        var backdrop = document.getElementById("gpModalBackdrop");
        var closeBtn = document.getElementById("gpModalClose");
        var form = document.getElementById("gpForm");
        var success = document.getElementById("gpSuccess");
        var doneBtn = document.getElementById("gpDoneBtn");
        var fileInput = document.getElementById("gpFile");
        var fileLabel = document.getElementById("gpFileLabel");
        var triggers = document.querySelectorAll("[data-gp-trigger]");
        var lastFocused = null;

        function renderIcons() {
            if (window.lucide && typeof window.lucide.createIcons === "function") {
                window.lucide.createIcons();
            }
        }

        function openModal(e) {
            if (e) e.preventDefault();
            lastFocused = document.activeElement;
            modal.classList.add("is-open");
            modal.setAttribute("aria-hidden", "false");
            document.body.classList.add("gp-modal-lock");
            renderIcons();
            var firstField = document.getElementById("gpCompany");
            if (firstField) {
                window.setTimeout(function () { firstField.focus(); }, 250);
            }
        }

        function closeModal() {
            modal.classList.remove("is-open");
            modal.setAttribute("aria-hidden", "true");
            document.body.classList.remove("gp-modal-lock");
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
            if (fileLabel) fileLabel.textContent = "PDF, DOC or DOCX — click to upload";
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

        if (fileInput && fileLabel) {
            fileInput.addEventListener("change", function () {
                if (fileInput.files && fileInput.files[0]) {
                    fileLabel.textContent = fileInput.files[0].name;
                } else {
                    fileLabel.textContent = "PDF, DOC or DOCX — click to upload";
                }
            });
        }

        var gpSubmitBtn = form ? form.querySelector(".gp-submit") : null;
        var gpSending = false;
        var gpStatus = null;
        if (form) {
            // Claims this form so main.js's generic initForms() catch-all
            // handler backs off instead of resetting the fields and faking
            // a success message before this real handler runs.
            form.setAttribute("data-form-handled", "true");

            gpStatus = document.createElement("p");
            gpStatus.className = "gp-form-status";
            gpStatus.setAttribute("role", "status");
            gpStatus.hidden = true;
            gpStatus.style.cssText = "margin-top:10px;font-size:0.9em;color:#c0392b;";
            form.appendChild(gpStatus);
        }

        if (form) {
            form.addEventListener("submit", function (e) {
                e.preventDefault();

                if (gpSending) return;

                if (!form.checkValidity()) {
                    form.reportValidity();
                    return;
                }

                if (!window.GermaineAPI) return;

                // Wired to POST /api/enquiries/graduate-requests (Step 6).
                // The backend's graduate_profile_requests table only has
                // employer_name/company/email/phone/role_needed/message —
                // it has no columns for contact person, department, or
                // number of profiles, so those three fields are folded
                // into the free-text "message" field rather than dropped.
                // The optional job-description file upload is NOT sent —
                // no file-upload endpoint exists on the backend.
                var company = document.getElementById("gpCompany").value.trim();
                var contact = document.getElementById("gpContact").value.trim();
                var email = document.getElementById("gpEmail").value.trim();
                var phone = document.getElementById("gpPhone").value.trim();
                var position = document.getElementById("gpPosition").value.trim();
                var dept = document.getElementById("gpDept").value;
                var count = document.getElementById("gpCount").value;
                var desc = document.getElementById("gpDesc").value.trim();

                var messageParts = [];
                if (contact) messageParts.push("Contact person: " + contact);
                if (dept) messageParts.push("Department needed: " + dept);
                if (count) messageParts.push("No. of profiles required: " + count);
                if (desc) messageParts.push("Job description: " + desc);

                var payload = {
                    employer_name: company,
                    email: email,
                    phone: phone || undefined,
                    role_needed: position || undefined,
                    message: messageParts.join("\n") || undefined,
                };

                gpSending = true;
                if (gpSubmitBtn) gpSubmitBtn.disabled = true;
                if (gpStatus) gpStatus.hidden = true;

                window.GermaineAPI.post("/api/enquiries/graduate-requests", payload).then(function (res) {
                    gpSending = false;
                    if (gpSubmitBtn) gpSubmitBtn.disabled = false;

                    if (res.success) {
                        form.hidden = true;
                        if (success) success.hidden = false;
                        renderIcons();
                    } else if (gpStatus) {
                        var firstFieldError = res.errors && Object.keys(res.errors).length
                            ? res.errors[Object.keys(res.errors)[0]][0]
                            : null;
                        gpStatus.textContent = firstFieldError || res.message || "Something went wrong. Please try again.";
                        gpStatus.hidden = false;
                    }
                });
            });
        }

        renderIcons();

        /* ---------- inline compact form (FAQ + Request section) ---------- */
        var inlineForm = document.getElementById("ghInlineForm");
        var inlineSuccess = document.getElementById("ghInlineSuccess");

        if (inlineForm) {
            inlineForm.addEventListener("submit", function (e) {
                e.preventDefault();

                if (!inlineForm.checkValidity()) {
                    inlineForm.reportValidity();
                    return;
                }

                // Simulated submission, same as the modal — swap to the
                // success state until a real backend endpoint exists.
                inlineForm.hidden = true;
                if (inlineSuccess) inlineSuccess.hidden = false;
                renderIcons();
            });
        }
    });

})();
