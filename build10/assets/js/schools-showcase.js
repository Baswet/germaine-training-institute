/*==================================================
    GERMAINE — SCHOOLS SHOWCASE renderer
    Builds the premium glass hero + card grid straight
    from window.SCHOOL_DATA / window.SCHOOL_ORDER
    (assets/js/school-data.js), so counts, images and
    "Browse Programmes" links always match the real
    per-school pages — nothing here is hard-coded.
==================================================*/
(function () {
  const mountHero = document.getElementById('gssHeroContent');
  const mountGrid = document.getElementById('gssGrid');
  if (!mountHero || !mountGrid) return;

  const DATA = window.SCHOOL_DATA || {};
  const ORDER = window.SCHOOL_ORDER || Object.keys(DATA);

  const capSVG   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10 12 5 2 10l10 5 10-5Z"/><path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5"/></svg>`;
  const tagSVG   = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.6 12.6 12 21.2 2.8 12A2 2 0 0 1 2 10.6V4a2 2 0 0 1 2-2h6.6a2 2 0 0 1 1.4.6l8.6 8.6a2 2 0 0 1 0 2.8Z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>`;
  const clockSVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/></svg>`;
  const checkSVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12.5 11.2 15 15 9.5"/><circle cx="12" cy="12" r="9"/></svg>`;
  const arrowSVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M13 5l7 7-7 7"/></svg>`;

  // ---- helpers derived from real programme data (nothing invented) ----
  function uniqueLevels(programmes) {
    const seen = [];
    (programmes || []).forEach(p => {
      if (p.level && !seen.includes(p.level)) seen.push(p.level);
    });
    return seen.slice(0, 2).join(' • ') || 'Programmes';
  }

  function commonEntry(programmes) {
    const counts = {};
    (programmes || []).forEach(p => {
      if (!p.entry) return;
      counts[p.entry] = (counts[p.entry] || 0) + 1;
    });
    let best = null, bestCount = 0;
    Object.keys(counts).forEach(k => {
      if (counts[k] > bestCount) { best = k; bestCount = counts[k]; }
    });
    return best || 'Varies by programme';
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

  // ---- hero ----
  const totalProgrammes = ORDER.reduce((sum, key) => sum + (DATA[key] && DATA[key].count ? DATA[key].count : 0), 0);
  mountHero.innerHTML = `
    <div class="gss-eyebrow-row">
      <span class="gss-line"></span>
      <span class="gss-kicker">Germaine Training Institute</span>
      <span class="gss-line"></span>
    </div>
    <h2 class="gss-title">OUR SCHOOLS</h2>
    <p class="gss-subtitle">Explore ${ORDER.length} Schools with ${totalProgrammes}+ Programmes designed for your future.</p>
  `;

  // ---- grid ----
  mountGrid.innerHTML = ORDER.map(key => {
    const s = DATA[key];
    if (!s) return '';
    const img = s.image || 'assets/images/schools/ict-about-hero.webp';
    const count = s.count || (s.programmes ? s.programmes.length : 0);
    return `
      <a href="${s.url || '#'}" class="gss-card" aria-label="${s.label}">
        <div class="gss-photo" style="background-image:url('${img}')"></div>
        <div class="gss-overlay"></div>
        <div class="gss-glass"></div>
        <div class="gss-shine"></div>
        <div class="gss-content">
          <div class="gss-thumb-wrap">
            <div class="gss-thumb" style="background-image:url('${img}')"></div>
          </div>
          <span class="gss-badge">${capSVG}${count} Programmes</span>
          <h3 class="gss-name">School of ${s.label}</h3>
          <div class="gss-pills">
            <span class="gss-pill">${tagSVG}${uniqueLevels(s.programmes)}</span>
            <span class="gss-pill">${clockSVG}${durationRange(s.programmes)}</span>
            <span class="gss-pill">${checkSVG}${commonEntry(s.programmes)}</span>
          </div>
          <span class="gss-cta">Browse Programmes ${arrowSVG}</span>
        </div>
      </a>
    `;
  }).join('');

  // ---- ambient particles ----
  function seedParticles(container, count) {
    if (!container) return;
    for (let i = 0; i < count; i++) {
      const p = document.createElement('span');
      p.className = 'gss-particle';
      p.style.left = (Math.random() * 100) + '%';
      p.style.top = (Math.random() * 100) + '%';
      p.style.animationDuration = (45 + Math.random() * 35) + 's';
      p.style.animationDelay = (Math.random() * 30) + 's';
      container.appendChild(p);
    }
  }
  seedParticles(document.getElementById('gssParticles'), 26);
  seedParticles(document.getElementById('gssHeroParticles'), 5);
})();
