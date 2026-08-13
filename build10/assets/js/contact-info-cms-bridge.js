/*
 * Contact Information CMS bridge (Step 7 CMS addition).
 *
 * contact.html repeats the phone/email/WhatsApp/address a few times.
 * Rather than touching the shared, locked site header/footer (out of
 * scope — Step 7 explicitly preserves navigation/chrome unchanged),
 * this bridge updates the two page-specific groups that are unique to
 * this page: the hero "contact hub" icon links, and the Quick Contact
 * Options cards below it. Every field is independently optional and
 * falls back to the existing static value if the admin hasn't set it.
 */
(function () {
    if (!window.GermaineAPI) return;

    var KEYS = ["contact.phone", "contact.email", "contact.whatsapp", "contact.address", "contact.hours"];

    window.GermaineAPI.get("/api/site-content", { keys: KEYS.join(",") }).then(function (res) {
        if (!res || !res.success || !res.data) return;
        var d = res.data;

        var phone = d["contact.phone"];
        var email = d["contact.email"];
        var whatsapp = d["contact.whatsapp"]; // digits only, e.g. "254719488112"
        var address = d["contact.address"];
        var hours = d["contact.hours"];

        function setText(id, value) {
            if (!value) return;
            var el = document.getElementById(id);
            if (el) el.textContent = value;
        }
        function setHref(id, href) {
            if (!href) return;
            var el = document.getElementById(id);
            if (el) el.setAttribute("href", href);
        }

        if (phone) {
            var telHref = "tel:+" + phone.replace(/[^\d]/g, "");
            setHref("cmsHubPhone", telHref);
            setHref("cmsQuickPhoneLink", telHref);
            setText("cmsQuickPhoneLink", phone);
        }
        if (email) {
            var mailHref = "mailto:" + email;
            setHref("cmsHubEmail", mailHref);
            setHref("cmsQuickEmailLink", mailHref);
            setText("cmsQuickEmailLink", email);
        }
        if (whatsapp) {
            var waHref = "https://wa.me/" + whatsapp.replace(/[^\d]/g, "");
            setHref("cmsHubWhatsapp", waHref);
            setHref("cmsQuickWhatsappLink", waHref);
        }
        setText("cmsQuickAddress", address);
        setText("cmsQuickHours", hours);
    }).catch(function () {
        // Silently keep the existing static contact details.
    });
})();
