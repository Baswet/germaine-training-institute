/*==================================================
    GERMAINE — SCHOOLS DASHBOARD renderer
    Builds the left navigation table, right overview
    table and live search straight from
    window.SCHOOL_DATA / window.SCHOOL_ORDER
    (assets/js/school-data.js) — the same data source
    that already powers every individual school page.
    Nothing here is hard-coded content; only display
    logic. Clicking a row is a plain <a href> to the
    school's EXISTING page — no in-page loading, no
    modal, no routing changes.
==================================================*/
(function () {
  const rowsMount = document.getElementById('sdRows');
  const overviewMount = document.getElementById('sdOverviewBody');
  const heroStat = document.getElementById('sdHeroSchoolCount');
  const heroStat2 = document.getElementById('sdHeroProgCount');
  const overviewCount = document.getElementById('sdOverviewCount');
  const searchInput = document.getElementById('sdSearchInput');
  const emptyState = document.getElementById('sdEmpty');
  if (!rowsMount) return;

  const DATA = window.SCHOOL_DATA || {};
  const ORDER = window.SCHOOL_ORDER || Object.keys(DATA);

  /* Every school in the current 9-school SCHOOL_ORDER has a real
     count from school-data.js, so no fallback is needed here. */
  const COUNT_FALLBACK = {};

  function uniqueLevels(programmes) {
    const seen = [];
    (programmes || []).forEach(p => {
      if (p.level && !seen.includes(p.level)) seen.push(p.level);
    });
    return seen.slice(0, 2).join(' • ') || 'Diploma • Certificate';
  }

  function durationRange(programmes) {
    let minYears = Infinity, maxYears = 0, found = false;
    (programmes || []).forEach(p => {
      const d = p.duration || '';
      const yearMatch = d.match(/(\d+(\.\d+)?)\s*Year/i);
      const monthMatch = d.match(/(\d+(\.\d+)?)\s*Month/i);
      let years = null;
      if (yearMatch) years = parseFloat(yearMatch[1]);
      else if (monthMatch) years = parseFloat(monthMatch[1]) / 12;
      if (years !== null) {
        found = true;
        minYears = Math.min(minYears, years);
        maxYears = Math.max(maxYears, years);
      }
    });
    if (!found) return 'Varies by level';
    const fmt = n => (Number.isInteger(n) ? n : n.toFixed(1));
    return minYears === maxYears ? `${fmt(minYears)} Years` : `${fmt(minYears)}–${fmt(maxYears)} Years`;
  }

  function schoolCount(key, s) {
    const c = s.count || (s.programmes ? s.programmes.length : 0);
    return c || COUNT_FALLBACK[key] || 0;
  }

  const totalProgrammes = ORDER.reduce((sum, key) => sum + schoolCount(key, DATA[key] || {}), 0);
  if (heroStat) heroStat.textContent = ORDER.length + '+';
  if (heroStat2) heroStat2.textContent = totalProgrammes + '+';
  if (overviewCount) overviewCount.textContent = ORDER.length + ' schools';

  /* ---- left navigation table ---- */
  const rowsHtml = ORDER.map((key, i) => {
    const s = DATA[key];
    if (!s) return '';
    const count = schoolCount(key, s);
    const divider = i < ORDER.length - 1 ? '<div class="sd-row-divider" role="presentation"></div>' : '';
    return `
      <a href="${s.url || '#'}" class="sd-row" data-name="${(s.label || '').toLowerCase()}" data-badge="${(s.badge || '').toLowerCase()}">
        <span class="sd-row-icon"><i class="fa-solid ${s.icon || 'fa-graduation-cap'}"></i></span>
        <span class="sd-row-body">
          <span class="sd-row-name">${s.label}</span>
          <span class="sd-row-meta">${count} Programme${count === 1 ? '' : 's'}</span>
        </span>
        <span class="sd-row-arrow"><i class="fa-solid fa-chevron-right"></i></span>
      </a>
      ${divider}
    `;
  }).join('');
  rowsMount.innerHTML = rowsHtml;

  /* ---- right overview table ---- */
  if (overviewMount) {
    overviewMount.innerHTML = ORDER.map(key => {
      const s = DATA[key];
      if (!s) return '';
      const count = schoolCount(key, s);
      return `
        <tr>
          <td><a href="${s.url || '#'}">${s.label}</a></td>
          <td><span class="sd-count-pill">${count}</span></td>
          <td>${uniqueLevels(s.programmes)}</td>
          <td>${durationRange(s.programmes)}</td>
        </tr>
      `;
    }).join('');
  }

  /* ---- live search filter (left table only) ---- */
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const q = this.value.trim().toLowerCase();
      let visibleCount = 0;
      const rows = rowsMount.querySelectorAll('.sd-row');
      rows.forEach(row => {
        const match = !q || row.dataset.name.includes(q) || row.dataset.badge.includes(q);
        row.style.display = match ? '' : 'none';
        const divider = row.nextElementSibling;
        if (divider && divider.classList.contains('sd-row-divider')) {
          divider.style.display = match ? '' : 'none';
        }
        if (match) visibleCount++;
      });
      if (emptyState) emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    });
  }

  /* ---- ambient hero particles (visual only) ---- */
  const particleHost = document.getElementById('sdHeroParticles');
  if (particleHost) {
    for (let i = 0; i < 16; i++) {
      const p = document.createElement('span');
      p.className = 'sd-particle';
      p.style.left = (Math.random() * 100) + '%';
      p.style.bottom = (Math.random() * 40) + '%';
      p.style.animationDuration = (10 + Math.random() * 10) + 's';
      p.style.animationDelay = (Math.random() * 8) + 's';
      particleHost.appendChild(p);
    }
  }
})();
