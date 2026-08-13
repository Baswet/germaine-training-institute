/*==================================================
    GERMAINE — PARTNER WITH US
    Three small, independent modules:
      1. Ambient hero particle field (seeded, CSS-animated)
      2. IntersectionObserver scroll reveals
      3. Partnership inquiry form validation + submission
    Each no-ops cleanly if its mount points are absent.
==================================================*/
(function () {
    "use strict";

    var reduceMotion = window.matchMedia &&
        window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------------------------------------------
       1. AMBIENT PARTICLES
    --------------------------------------------- */
    (function particles() {
        var mount = document.getElementById("pwParticles");
        if (!mount || reduceMotion) return;

        var count = window.innerWidth < 720 ? 14 : 30;
        var frag = document.createDocumentFragment();

        for (var i = 0; i < count; i++) {
            var dot = document.createElement("span");
            var size = (Math.random() * 2.2 + 1.2).toFixed(2);
            dot.style.width = size + "px";
            dot.style.height = size + "px";
            dot.style.left = (Math.random() * 100).toFixed(2) + "%";
            dot.style.top = (Math.random() * 100).toFixed(2) + "%";
            dot.style.animationDuration = (Math.random() * 18 + 16).toFixed(1) + "s";
            dot.style.animationDelay = "-" + (Math.random() * 20).toFixed(1) + "s";
            if (Math.random() > 0.5) dot.style.background = "#EC4899";
            frag.appendChild(dot);
        }
        mount.appendChild(frag);
    })();

    /* ---------------------------------------------
       2. SCROLL REVEALS
    --------------------------------------------- */
    (function reveals() {
        var items = document.querySelectorAll(".pw-reveal");
        if (!items.length) return;

        if (reduceMotion || !("IntersectionObserver" in window)) {
            Array.prototype.forEach.call(items, function (el) { el.classList.add("is-in"); });
            return;
        }

        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-in");
                    io.unobserve(entry.target);
                }
            });
        }, { rootMargin: "0px 0px -12% 0px", threshold: 0.1 });

        Array.prototype.forEach.call(items, function (el) { io.observe(el); });
    })();

    /* ---------------------------------------------
       3. LOGO WALL — duplicate the track so the
          marquee loops seamlessly at -50%
    --------------------------------------------- */
    (function logoWall() {
        var track = document.getElementById("pwLogoTrack");
        if (!track || reduceMotion) return;
        track.innerHTML += track.innerHTML;
    })();

    /* ---------------------------------------------
       4. INQUIRY FORM
    --------------------------------------------- */
    (function inquiryForm() {
        var form = document.getElementById("pwForm");
        var success = document.getElementById("pwSuccess");
        var submit = document.getElementById("pwSubmit");
        if (!form || !success || !submit) return;

        // Claims this form so main.js's generic initForms() catch-all
        // handler backs off instead of resetting the fields and faking
        // a success message before this real handler runs.
        form.setAttribute("data-form-handled", "true");

        var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
        var PHONE_RE = /^[+]?[\d\s()-]{9,20}$/;
        var MIN_MESSAGE = 20;
        var sending = false;

        /* live character counter */
        var message = document.getElementById("pwMessage");
        var counter = document.getElementById("pwCount");
        if (message && counter) {
            message.addEventListener("input", function () {
                counter.textContent = String(message.value.length);
            });
        }

        function errorNode(id) {
            return form.querySelector('.pw-error[data-for="' + id + '"]');
        }

        function setError(field, msg) {
            var node = errorNode(field.id);
            var wrap = field.closest(".pw-field");
            if (wrap) wrap.classList.toggle("has-error", !!msg);
            if (node) {
                node.textContent = msg || "";
                node.classList.toggle("is-shown", !!msg);
            }
            return !msg;
        }

        function validateField(field) {
            var v = (field.value || "").trim();

            if (field.type === "checkbox") {
                return setError(field, field.checked ? "" : "Please confirm your consent before submitting.");
            }
            if (!v) {
                return setError(field, "This field is required.");
            }
            if (field.type === "email" && !EMAIL_RE.test(v)) {
                return setError(field, "Please enter a valid email address.");
            }
            if (field.type === "tel" && !PHONE_RE.test(v)) {
                return setError(field, "Please enter a valid phone number.");
            }
            if (field === message && v.length < MIN_MESSAGE) {
                return setError(field, "Please give us a little more detail (at least " + MIN_MESSAGE + " characters).");
            }
            return setError(field, "");
        }

        var fields = Array.prototype.slice.call(
            form.querySelectorAll("input[required], select[required], textarea[required]")
        );

        /* clear an error as soon as the user starts fixing it */
        fields.forEach(function (field) {
            var evt = field.tagName === "SELECT" || field.type === "checkbox" ? "change" : "input";
            field.addEventListener(evt, function () {
                var wrap = field.closest(".pw-field");
                if ((wrap && wrap.classList.contains("has-error")) ||
                    (field.type === "checkbox")) {
                    validateField(field);
                }
            });
            field.addEventListener("blur", function () { validateField(field); });
        });

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            if (sending) return;

            var firstBad = null;
            fields.forEach(function (field) {
                if (!validateField(field) && !firstBad) firstBad = field;
            });

            if (firstBad) {
                firstBad.focus();
                if (firstBad.scrollIntoView) {
                    firstBad.scrollIntoView({ behavior: "smooth", block: "center" });
                }
                return;
            }

            sending = true;
            submit.disabled = true;
            submit.classList.add("is-loading");
            submit.querySelector(".pw-submit-label").textContent = "Sending…";

            if (!window.GermaineAPI) { sending = false; return; }

            // Wired to POST /api/enquiries/partner-enquiries (Step 6),
            // enquiry_type="partnership" for this page. The backend table
            // has no columns for "Organization Type" or "Partnership
            // Interest" (pwType/pwInterest) — those are folded into the
            // free-text message field rather than silently dropped.
            var org = document.getElementById("pwOrg").value.trim();
            var contact = document.getElementById("pwName").value.trim();
            var email = document.getElementById("pwEmail").value.trim();
            var phone = document.getElementById("pwPhone").value.trim();
            var type = document.getElementById("pwType").value;
            var interest = document.getElementById("pwInterest").value;
            var msg = message.value.trim();

            var messageParts = [];
            if (type) messageParts.push("Organization type: " + type);
            if (interest) messageParts.push("Partnership interest: " + interest);
            if (msg) messageParts.push(msg);

            var payload = {
                organisation: org,
                contact_name: contact,
                email: email,
                phone: phone || undefined,
                enquiry_type: "partnership",
                message: messageParts.join("\n") || undefined,
            };

            window.GermaineAPI.post("/api/enquiries/partner-enquiries", payload).then(function (res) {
                sending = false;
                submit.disabled = false;
                submit.classList.remove("is-loading");
                submit.querySelector(".pw-submit-label").textContent = "Submit Partnership Inquiry";

                if (res.success) {
                    form.hidden = true;
                    success.hidden = false;
                    success.setAttribute("tabindex", "-1");
                    success.focus();
                    if (success.scrollIntoView) {
                        success.scrollIntoView({ behavior: "smooth", block: "center" });
                    }
                } else {
                    var firstFieldError = res.errors && Object.keys(res.errors).length
                        ? res.errors[Object.keys(res.errors)[0]][0]
                        : null;
                    var note = firstFieldError || res.message || "Something went wrong. Please try again.";
                    var errNode = errorNode("pwConsent");
                    if (errNode) {
                        errNode.textContent = note;
                        errNode.classList.add("is-shown");
                    } else {
                        window.alert(note);
                    }
                }
            });
        });
    })();

})();
