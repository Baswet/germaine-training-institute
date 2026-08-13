/*=========================================================
    GERMAINE — PREMIUM FUTURISTIC THEME
    Global, site-wide script. Runs on every page and
    highlights the last word of main headings with the
    Germaine signature gradient (--pt-word). No existing
    markup, structure or content is changed — only a
    <span> wrapper is added around a heading's last word.

    (Ambient particles / travelling streaks are handled by
    germaine-signature.js so they are not duplicated here.)
=========================================================*/
(function () {
    "use strict";

    /* ---------- gradient-word heading highlight ---------- */
    function findLastTextNode(el) {
        for (var i = el.childNodes.length - 1; i >= 0; i--) {
            var node = el.childNodes[i];
            if (node.nodeType === 3 && node.nodeValue.trim().length > 0) {
                return node;
            }
            if (node.nodeType === 1) {
                var found = findLastTextNode(node);
                if (found) return found;
            }
        }
        return null;
    }

    function highlightLastWord(heading) {
        if (!heading || heading.dataset.ptProcessed) return;
        if (heading.querySelector(".pt-word, .b")) { heading.dataset.ptProcessed = "1"; return; }

        var textNode = findLastTextNode(heading);
        if (!textNode) return;

        var text = textNode.nodeValue;
        var trimmedEnd = text.replace(/\s+$/, "");
        var trailingSpace = text.slice(trimmedEnd.length);
        var lastSpaceIdx = trimmedEnd.lastIndexOf(" ");
        var lastWord = lastSpaceIdx === -1 ? trimmedEnd : trimmedEnd.slice(lastSpaceIdx + 1);
        if (!lastWord || lastWord.length < 2) return;

        var before = lastSpaceIdx === -1 ? "" : trimmedEnd.slice(0, lastSpaceIdx + 1);

        var frag = document.createDocumentFragment();
        if (before) frag.appendChild(document.createTextNode(before));
        var span = document.createElement("span");
        span.className = "pt-word";
        span.textContent = lastWord;
        frag.appendChild(span);
        if (trailingSpace) frag.appendChild(document.createTextNode(trailingSpace));

        textNode.parentNode.replaceChild(frag, textNode);
        heading.dataset.ptProcessed = "1";
    }

    document.querySelectorAll("h1:not(#courseTitle), .section-heading h2").forEach(highlightLastWord);
})();
