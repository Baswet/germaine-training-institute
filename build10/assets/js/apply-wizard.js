/*==================================================
    GERMAINE TRAINING INSTITUTE
    FULL SCHOLARSHIP APPLICATION FORM (single step)

    Step 9 revision: this was previously a 2-step wizard
    (Next/Previous navigation, a step progress indicator,
    and a separate "Review Your Credentials" screen). All
    of that has been removed per instruction — every field
    from the old Step 1 and Step 2 now lives in one form,
    submitted directly. The DOM ids/classes were kept
    wherever possible so this stays a small, targeted diff
    against the working wizard rather than a rewrite.

    Self-contained. Does not touch main.js / global
    form handling — the form uses plain <div>s, not
    a <form>, so it never collides with initForms().

    Schools & programmes are read directly from
    window.SCHOOL_DATA / window.SCHOOL_ORDER (see
    assets/js/school-data.js), which is generated only
    from the institute's official school documents.
    Nothing here is invented — if a school or programme
    isn't in that file, it will not appear in this form.
    Load school-data.js BEFORE this script.
==================================================*/

(function () {
    "use strict";

    var COUNTIES = ["Mombasa","Kwale","Kilifi","Tana River","Lamu","Taita Taveta","Garissa","Wajir","Mandera",
        "Marsabit","Isiolo","Meru","Tharaka-Nithi","Embu","Kitui","Machakos","Makueni","Nyandarua","Nyeri",
        "Kirinyaga","Murang'a","Kiambu","Turkana","West Pokot","Samburu","Trans Nzoia","Uasin Gishu",
        "Elgeyo-Marakwet","Nandi","Baringo","Laikipia","Nakuru","Narok","Kajiado","Kericho","Bomet","Kakamega",
        "Vihiga","Bungoma","Busia","Siaya","Kisumu","Homa Bay","Migori","Kisii","Nyamira","Nairobi"];

    var MODES = [
        { id: "fulltime", title: "Full Time" },
        { id: "parttime", title: "Part Time" },
        { id: "distance", title: "Virtual / Distance Learning" },
        { id: "talented", title: "Talented Student" }
    ];

    var SCHOOL_ORDER = (window.SCHOOL_ORDER || []).slice();
    var SCHOOL_DATA = window.SCHOOL_DATA || {};

    var state = {
        mode: "", modeLabel: "",
        fullname: "", phone: "", email: "", idnum: "", county: "", gender: "",
        eduLevel: "", kcseGrade: "",
        schoolId: "", schoolName: "",
        programme: "",
        submitted: false
    };

    function $(sel, ctx) { return (ctx || document).querySelector(sel); }
    function $all(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

    document.addEventListener("DOMContentLoaded", function () {
        var wizard = $("#applyWizard");
        if (!wizard) return;

        buildModeSelect();
        buildSchoolSelect();
        buildCounties();
        bindCombobox();
        bindTerms();
        bindSubmit();
    });

    /*========== BUILD STATIC CHOICE UI ==========*/
    function buildModeSelect() {
        var sel = $("#apMode");
        if (!sel) return;
        MODES.forEach(function (m) {
            var opt = document.createElement("option");
            opt.value = m.id;
            opt.textContent = m.title;
            sel.appendChild(opt);
        });
        sel.addEventListener("change", function () {
            var chosen = MODES.filter(function (m) { return m.id === sel.value; })[0];
            state.mode = sel.value;
            state.modeLabel = chosen ? chosen.title : "";
            hideError("apModeError");
        });
    }

    function buildSchoolSelect() {
        var sel = $("#apSchool");
        if (!sel) return;
        SCHOOL_ORDER.forEach(function (id) {
            var s = SCHOOL_DATA[id];
            if (!s) return;
            var opt = document.createElement("option");
            opt.value = id;
            opt.textContent = s.label;
            sel.appendChild(opt);
        });
        sel.addEventListener("change", function () {
            state.schoolId = sel.value;
            state.schoolName = (SCHOOL_DATA[sel.value] || {}).label || "";
            state.programme = "";
            hideError("apSchoolError");
            resetProgrammeCombobox();
        });
    }

    function buildCounties() {
        var sel = $("#apCounty");
        if (!sel) return;
        COUNTIES.forEach(function (c) {
            var opt = document.createElement("option");
            opt.value = c; opt.textContent = c;
            sel.appendChild(opt);
        });
    }

    /*========== PROGRAMME — searchable combobox ==========*/
    function currentSchoolProgrammes() {
        var school = SCHOOL_DATA[state.schoolId];
        return (school && school.programmes) || [];
    }

    function resetProgrammeCombobox() {
        var input = $("#apProgrammeSearch");
        var hidden = $("#apProgramme");
        var hint = $("#apProgrammeHint");
        var list = $("#apProgrammeList");
        if (hidden) hidden.value = "";
        if (list) { list.innerHTML = ""; list.classList.remove("open"); }
        if (!input) return;
        var programmes = currentSchoolProgrammes();
        if (!state.schoolId) {
            input.value = ""; input.disabled = true; input.placeholder = "Choose a school first";
            if (hint) hint.textContent = "Choose a school above first.";
            return;
        }
        input.disabled = false;
        input.value = "";
        if (!programmes.length) {
            input.placeholder = "No programmes listed yet for this school";
            input.disabled = true;
            if (hint) hint.textContent = "Programme listing for " + state.schoolName + " is being finalised — contact admissions on +254 719 488 112.";
            return;
        }
        input.placeholder = "Search " + programmes.length + " programmes…";
        if (hint) hint.textContent = "Programmes offered by " + state.schoolName + ".";
    }

    function renderProgrammeList(query) {
        var list = $("#apProgrammeList");
        if (!list) return;
        var programmes = currentSchoolProgrammes();
        var q = (query || "").trim().toLowerCase();
        var matches = programmes.filter(function (p) { return !q || p.name.toLowerCase().indexOf(q) !== -1; });
        if (!matches.length) {
            list.innerHTML = '<div class="ap-combobox-empty">No programmes match your search.</div>';
        } else {
            list.innerHTML = matches.slice(0, 40).map(function (p) {
                return '<div class="ap-combobox-item" data-name="' + p.name.replace(/"/g, "&quot;") + '">' +
                    '<span>' + p.name + '</span><span class="ap-combo-level">' + p.level + '</span></div>';
            }).join("");
        }
        list.classList.add("open");
        $all(".ap-combobox-item", list).forEach(function (item) {
            item.addEventListener("mousedown", function (e) {
                e.preventDefault();
                var name = item.getAttribute("data-name");
                var input = $("#apProgrammeSearch");
                var hidden = $("#apProgramme");
                if (input) input.value = name;
                if (hidden) hidden.value = name;
                state.programme = name;
                list.classList.remove("open");
                markInvalid("#apProgrammeSearch", false);
            });
        });
    }

    function bindCombobox() {
        var input = $("#apProgrammeSearch");
        var list = $("#apProgrammeList");
        if (!input || !list) return;
        input.addEventListener("focus", function () {
            if (!input.disabled) renderProgrammeList(input.value);
        });
        input.addEventListener("input", function () {
            state.programme = "";
            var hidden = $("#apProgramme");
            if (hidden) hidden.value = "";
            renderProgrammeList(input.value);
        });
        document.addEventListener("click", function (e) {
            if (!list.contains(e.target) && e.target !== input) list.classList.remove("open");
        });
    }

    function bindTerms() {
        var box = $("#apTerms");
        var submitBtn = $("#apSubmitBtn");
        if (!box || !submitBtn) return;
        box.addEventListener("change", function () {
            submitBtn.disabled = !box.checked;
        });
    }

    function bindSubmit() {
        var submitBtn = $("#apSubmitBtn");
        if (submitBtn) submitBtn.addEventListener("click", handleSubmit);
    }

    /*========== VALIDATION ==========*/
    function showError(id) { var el = document.getElementById(id); if (el) el.classList.add("show"); }
    function hideError(id) { var el = document.getElementById(id); if (el) el.classList.remove("show"); }

    function markInvalid(sel, invalid) {
        var el = $(sel);
        if (!el) return;
        el.classList.toggle("input-error", !!invalid);
    }

    /* Single-step form: every previously-per-step validation now runs
       together before submission. Reads current DOM values directly
       (same approach the old validateStep(1) used), marks every invalid
       field, and returns false on the first missing requirement so
       handleSubmit never posts incomplete required information. */
    function validateAll() {
        state.fullname = $("#apFullname").value.trim();
        state.phone = $("#apPhone").value.trim();
        state.email = $("#apEmail").value.trim();
        state.idnum = $("#apIdnum").value.trim();
        state.gender = $("#apGender").value;
        state.county = $("#apCounty").value;
        state.eduLevel = $("#apEduLevel").value;
        state.kcseGrade = $("#apKcseGrade") ? $("#apKcseGrade").value : "";

        markInvalid("#apFullname", !state.fullname);
        markInvalid("#apPhone", !state.phone);
        markInvalid("#apGender", !state.gender);
        markInvalid("#apCounty", !state.county);
        markInvalid("#apEduLevel", !state.eduLevel);

        var modeOk = !!state.mode;
        if (!modeOk) showError("apModeError"); else hideError("apModeError");

        var schoolOk = !!state.schoolId;
        if (!schoolOk) showError("apSchoolError"); else hideError("apSchoolError");

        markInvalid("#apProgrammeSearch", !state.programme);

        var personalOk = !!(state.fullname && state.phone &&
            state.gender && state.county && state.eduLevel);

        return personalOk && modeOk && schoolOk && !!state.programme;
    }

    /*========== SUBMIT ==========*/
    /* Wired to the real backend (Step 9 fix — this previously posted to a
       hardcoded, non-existent external URL in no-cors mode and always showed
       the success state regardless of outcome, so nothing was ever saved and
       failures were invisible). Uses window.GermaineAPI (assets/js/api-client.js),
       the same client every other integrated form on the site already uses. */

    function showSubmitError(message) {
        var el = document.getElementById("apSubmitError");
        if (el) el.textContent = message;
        showError("apSubmitError");
    }

    function setSubmitting(isSubmitting) {
        var btn = $("#apSubmitBtn");
        if (!btn) return;
        btn.disabled = isSubmitting;
        btn.textContent = isSubmitting ? "Submitting…" : "Submit Application";
    }

    function showSuccess() {
        state.submitted = true;
        var panel = $('.ap-step-panel[data-step="1"]');
        $all(".ap-fieldset-head, .ap-compact-grid, .ap-combobox, .ap-terms, #apModeError, #apSchoolError", panel).forEach(function (el) {
            el.style.display = "none";
        });
        hideError("apSubmitError");
        var success = $("#apSuccess");
        if (success) success.classList.add("active");
        var stepNav = $(".ap-step-nav");
        if (stepNav) stepNav.style.display = "none";
    }

    function handleSubmit() {
        if (!validateAll()) return;

        var termsBox = $("#apTerms");
        if (termsBox && !termsBox.checked) return;

        hideError("apSubmitError");

        if (!window.GermaineAPI) {
            showSubmitError("We couldn't reach the server. Please check your connection and try again.");
            return;
        }

        setSubmitting(true);

        // The form only ever knows the school's slug and the programme's
        // display name (from school-data.js) — never a database id — so the
        // numeric programme_id the backend requires is looked up here via the
        // same public catalogue endpoint the rest of the site already uses,
        // matched on an exact name. Nothing is invented: if no exact match is
        // found, the submission is stopped and a real error is shown instead
        // of a fabricated id.
        window.GermaineAPI.get("/api/programmes", { school: state.schoolId, q: state.programme, per_page: 50 })
            .then(function (res) {
                var items = (res.success && res.data && res.data.items) || [];
                var match = items.filter(function (p) { return p.name === state.programme; })[0];
                if (!match) {
                    setSubmitting(false);
                    showSubmitError("We couldn't match \"" + state.programme + "\" to a programme on file. Please re-select your programme and try again.");
                    return null;
                }
                return match.id;
            })
            .then(function (programmeId) {
                if (!programmeId) return; // error already shown above

                var payload = {
                    full_name: state.fullname,
                    email: state.email,
                    phone: "254" + state.phone,
                    national_id: state.idnum || undefined,
                    gender: state.gender || undefined,
                    county: state.county || undefined,
                    education_level: state.eduLevel || undefined,
                    kcse_grade: state.kcseGrade || undefined,
                    programme_id: programmeId,
                    application_type: "scholarship",
                    consent: true
                };

                return window.GermaineAPI.post("/api/admissions/applications", payload).then(function (res) {
                    setSubmitting(false);
                    if (!res.success) {
                        var fieldErrors = res.errors && Object.keys(res.errors).map(function (k) { return res.errors[k][0]; });
                        showSubmitError((fieldErrors && fieldErrors[0]) || res.message || "We couldn't submit your application. Please check your details and try again.");
                        return;
                    }
                    showSuccess();
                });
            })
            .catch(function () {
                setSubmitting(false);
                showSubmitError("We couldn't reach the server. Please check your connection and try again.");
            });
    }

})();
