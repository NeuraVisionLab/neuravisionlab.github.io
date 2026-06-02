/* NeuraVision Research Lab — site interactions (vanilla, no dependencies) */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- adaptive header (transparent over the dark band, solid after) */
  var header = document.querySelector(".site-header");
  var topDark = document.querySelector(".hero, .subhero");
  if (header) {
    if (topDark && "IntersectionObserver" in window) {
      // header is "on-dark" while any of the dark hero/sub-hero sits behind it;
      // it becomes the solid "is-stuck" bar once that band scrolls past the header.
      var hio = new IntersectionObserver(function (entries) {
        var over = entries[0].isIntersecting;
        header.classList.toggle("on-dark", over);
        header.classList.toggle("is-stuck", !over);
      }, { rootMargin: "-72px 0px 0px 0px", threshold: 0 });
      hio.observe(topDark);
    } else {
      var fb = function () {
        header.classList.remove("on-dark");
        header.classList.toggle("is-stuck", (window.scrollY || 0) > 8);
      };
      window.addEventListener("scroll", fb, { passive: true });
      fb();
    }
  }

  /* ---------- mobile drawer (focus-trapped dialog) ------------------- */
  var toggle = document.querySelector(".nav-toggle");
  var drawer = document.querySelector(".nav-drawer");
  var overlay = document.querySelector(".drawer-overlay");
  var lastFocus = null;
  function focusables() {
    return drawer ? drawer.querySelectorAll('a[href], button:not([disabled])') : [];
  }
  function openDrawer() {
    if (!drawer) return;
    lastFocus = document.activeElement;
    drawer.classList.add("open");
    if (overlay) overlay.classList.add("open");
    document.body.style.overflow = "hidden";
    toggle.setAttribute("aria-expanded", "true");
    var f = focusables();
    if (f.length) f[0].focus();
  }
  function closeDrawer() {
    if (!drawer) return;
    drawer.classList.remove("open");
    if (overlay) overlay.classList.remove("open");
    document.body.style.overflow = "";
    toggle.setAttribute("aria-expanded", "false");
    if (lastFocus) lastFocus.focus();
  }
  if (toggle) toggle.addEventListener("click", function () {
    drawer.classList.contains("open") ? closeDrawer() : openDrawer();
  });
  if (overlay) overlay.addEventListener("click", closeDrawer);
  var closeBtn = document.querySelector(".drawer-close");
  if (closeBtn) closeBtn.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", function (e) {
    if (!drawer || !drawer.classList.contains("open")) return;
    if (e.key === "Escape") { closeDrawer(); return; }
    if (e.key === "Tab") {
      var f = focusables(); if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  if (drawer) drawer.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", closeDrawer); });

  /* ---------- scroll reveal ------------------------------------------ */
  var reveals = document.querySelectorAll("[data-reveal]");
  if (reveals.length && "IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-visible"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- count-up vital stats ----------------------------------- */
  var counters = document.querySelectorAll("[data-count]");
  function countUp(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    if (reduceMotion) { el.textContent = target.toLocaleString(); return; }
    var start = null, dur = 1000;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(eased * target).toLocaleString();
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if (counters.length) {
    if ("IntersectionObserver" in window) {
      var co = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { if (en.isIntersecting) { countUp(en.target); co.unobserve(en.target); } });
      }, { threshold: 0.5 });
      counters.forEach(function (el) { co.observe(el); });
    } else { counters.forEach(countUp); }
  }

  /* ---------- publications filter ------------------------------------ */
  var pubList = document.querySelector("[data-pub-list]");
  if (pubList) {
    var pills = document.querySelectorAll(".filter-pill");
    var rows = pubList.querySelectorAll(".pub-row");
    var countEl = document.querySelector("[data-pub-count]");
    var totalEl = document.querySelector("[data-pub-total]");
    var total = rows.length;
    if (totalEl) totalEl.textContent = total;

    function applyFilter(key, val) {
      var shown = 0;
      rows.forEach(function (r) {
        var match = (key === "all") || (r.getAttribute("data-" + key) || "").split(" ").indexOf(val) !== -1;
        r.classList.toggle("is-hidden", !match);
        if (match) shown++;
      });
      // hide empty year groups
      document.querySelectorAll("[data-year-group]").forEach(function (g) {
        var vis = g.querySelectorAll(".pub-row:not(.is-hidden)").length;
        g.style.display = vis ? "" : "none";
      });
      if (countEl) countEl.textContent = shown;
    }
    pills.forEach(function (p) {
      p.addEventListener("click", function () {
        pills.forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        p.setAttribute("aria-pressed", "true");
        applyFilter(p.getAttribute("data-filter"), p.getAttribute("data-value") || "");
      });
    });
  }

  /* ---------- theme toggle ------------------------------------------- */
  var themeBtn = document.querySelector(".theme-toggle");
  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }
  if (themeBtn) {
    themeBtn.setAttribute("aria-pressed", String(currentTheme() === "dark"));
    themeBtn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("nv-theme", next); } catch (e) {}
      themeBtn.setAttribute("aria-pressed", String(next === "dark"));
    });
  }

  /* ---------- mouse-driven graph parallax (the constellation follows) - */
  if (!reduceMotion && window.matchMedia("(pointer:fine)").matches) {
    document.querySelectorAll(".hero, .subhero").forEach(function (hero) {
      var motif = hero.querySelector(".constellation");
      var visual = hero.querySelector(".hero-visual");
      if (!motif && !visual) return;
      var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
      function loop() {
        cx += (tx - cx) * 0.08; cy += (ty - cy) * 0.08;
        if (motif) motif.style.transform = "translate(" + (cx * 36).toFixed(1) + "px," + (cy * 36).toFixed(1) + "px)";
        if (visual) visual.style.transform = "translate(" + (cx * -16).toFixed(1) + "px," + (cy * -16).toFixed(1) + "px)";
        if (Math.abs(tx - cx) > 0.0005 || Math.abs(ty - cy) > 0.0005) { raf = requestAnimationFrame(loop); }
        else { raf = null; }
      }
      function kick() { if (!raf) raf = requestAnimationFrame(loop); }
      hero.addEventListener("pointermove", function (e) {
        var r = hero.getBoundingClientRect();
        tx = (e.clientX - r.left) / r.width - 0.5;
        ty = (e.clientY - r.top) / r.height - 0.5;
        kick();
      });
      hero.addEventListener("pointerleave", function () { tx = 0; ty = 0; kick(); });
    });
  }

  /* ---------- hero canvas: interactive node graph that follows the mouse */
  var heroCanvas = document.querySelector(".hero-canvas");
  if (heroCanvas && heroCanvas.getContext && !reduceMotion) {
    var hctx = heroCanvas.getContext("2d");
    var heroEl = heroCanvas.closest(".hero");
    var DPR = Math.min(window.devicePixelRatio || 1, 2);
    var cw = 0, ch = 0, count = 0, maxDist = 150, infl = 220;
    var pts = [], mx = -9999, my = -9999, hover = false, hraf = null;
    var rnd = function (a, b) { return a + Math.random() * (b - a); };

    function seed() {
      pts = [];
      for (var i = 0; i < count; i++) {
        pts.push({ x: rnd(0, cw), y: rnd(0, ch), vx: rnd(-0.25, 0.25), vy: rnd(-0.25, 0.25), r: rnd(1.1, 3.2) });
      }
    }
    function sizeCanvas() {
      var r = heroEl.getBoundingClientRect();
      cw = Math.max(1, r.width); ch = Math.max(1, r.height);
      heroCanvas.width = Math.round(cw * DPR); heroCanvas.height = Math.round(ch * DPR);
      hctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      count = Math.round(Math.min(70, Math.max(24, cw * ch / 18000)));
      maxDist = Math.min(165, Math.max(108, cw / 9));
      infl = Math.min(260, Math.max(150, cw / 5));
      if (pts.length !== count) seed();
    }
    function frame() {
      hctx.clearRect(0, 0, cw, ch);
      var i, j, p, q, dx, dy, d, sp;
      for (i = 0; i < pts.length; i++) {
        p = pts[i];
        p.x += p.vx; p.y += p.vy;
        if (hover) {
          dx = mx - p.x; dy = my - p.y; d = Math.hypot(dx, dy);
          if (d < infl && d > 0.5) { var f = (1 - d / infl) * 0.045; p.vx += (dx / d) * f; p.vy += (dy / d) * f; }
        }
        p.vx *= 0.985; p.vy *= 0.985;
        p.vx += rnd(-0.01, 0.01); p.vy += rnd(-0.01, 0.01);
        sp = Math.hypot(p.vx, p.vy);
        if (sp > 1.4) { p.vx = p.vx / sp * 1.4; p.vy = p.vy / sp * 1.4; }
        if (p.x < 0) { p.x = 0; p.vx = Math.abs(p.vx); } else if (p.x > cw) { p.x = cw; p.vx = -Math.abs(p.vx); }
        if (p.y < 0) { p.y = 0; p.vy = Math.abs(p.vy); } else if (p.y > ch) { p.y = ch; p.vy = -Math.abs(p.vy); }
      }
      for (i = 0; i < pts.length; i++) {
        p = pts[i];
        for (j = i + 1; j < pts.length; j++) {
          q = pts[j]; dx = p.x - q.x; dy = p.y - q.y; d = Math.hypot(dx, dy);
          if (d < maxDist) {
            hctx.strokeStyle = "rgba(40,181,96," + (0.42 * (1 - d / maxDist)).toFixed(3) + ")";
            hctx.lineWidth = 1;
            hctx.beginPath(); hctx.moveTo(p.x, p.y); hctx.lineTo(q.x, q.y); hctx.stroke();
          }
        }
      }
      for (i = 0; i < pts.length; i++) {
        p = pts[i]; var near = false;
        if (hover) {
          dx = mx - p.x; dy = my - p.y; d = Math.hypot(dx, dy);
          if (d < infl) {
            near = true;
            hctx.strokeStyle = "rgba(52,196,108," + (0.5 * (1 - d / infl)).toFixed(3) + ")";
            hctx.lineWidth = 1;
            hctx.beginPath(); hctx.moveTo(p.x, p.y); hctx.lineTo(mx, my); hctx.stroke();
          }
        }
        hctx.beginPath(); hctx.arc(p.x, p.y, p.r * (near ? 1.6 : 1), 0, 6.2832);
        hctx.fillStyle = near ? "rgba(107,240,173,0.95)" : "rgba(52,196,108,0.72)";
        hctx.fill();
      }
      hraf = requestAnimationFrame(frame);
    }
    heroEl.addEventListener("pointermove", function (e) {
      var r = heroEl.getBoundingClientRect(); mx = e.clientX - r.left; my = e.clientY - r.top; hover = true;
    });
    heroEl.addEventListener("pointerleave", function () { hover = false; mx = my = -9999; });
    var rt; window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(sizeCanvas, 150); });
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) { if (hraf) { cancelAnimationFrame(hraf); hraf = null; } }
      else if (!hraf) { hraf = requestAnimationFrame(frame); }
    });
    sizeCanvas(); hraf = requestAnimationFrame(frame);
  }
})();
