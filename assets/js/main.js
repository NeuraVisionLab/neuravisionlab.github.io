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
})();
