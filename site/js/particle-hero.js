/**
 * Theosis Library — Illuminated Glyph Hero
 * Public-domain artworks pre-rendered to density frames (data/ascii-frames.json),
 * drawn on canvas as Greek uncial letters lit in gold: a portrait written in
 * the alphabet of the manuscripts. Light follows the cursor; frames cycle with
 * a scribal "rewrite" transition.
 */
(function () {
  'use strict';
  var container = document.getElementById('particle-hero');
  if (!container) return;

  var HOLD = 4200, TRANSITION = 1800;
  // Density ramp used when the frames were generated (dark → light).
  // Generator ramp: index 0 = darkest pixel, last = brightest.
  var RAMP = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ';
  var DENS = {};
  for (var r = 0; r < RAMP.length; r++) DENS[RAMP[r]] = r / (RAMP.length - 1);  // brightness
  // Uncial glyph buckets by weight (light → heavy).
  var GLYPHS = [
    '·', '.', '˙', 'ι', 'ϲ', 'ο', 'τ', 'ε', 'υ', 'ν', 'α', 'κ', 'η', 'ρ', 'χ', 'λ', 'π', 'δ', 'μ', 'ω', 'θ', 'φ', 'ψ', 'ξ', 'Ω', 'Θ', 'Ψ', 'Φ', 'Ξ', 'Δ', 'Μ', 'Ω'
  ];

  var canvas = document.createElement('canvas');
  canvas.className = 'glyph-hero';
  container.appendChild(canvas);
  var ctx = canvas.getContext('2d');

  var CELL_H = 1.62;  // generator assumed glyphs ~1.6x taller than wide
  var frames = [], idx = 0, cols = 0, rows = 0, cell = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
  var isMobile = window.innerWidth < 600;
  var cur = null, target = null, mix = 1, tStart = 0, timings = null, holdTimer = null;
  var mouse = { x: -1, y: -1, on: false };
  var phase = null;

  function densities(frame) {
    var lines = isMobile ? frame.mobile : frame.desktop;
    cols = isMobile ? frame.cols_mobile : frame.cols_desktop;
    rows = lines.length;
    var out = new Float32Array(cols * rows);
    for (var y = 0; y < rows; y++) {
      var line = lines[y];
      for (var x = 0; x < cols; x++) {
        var ch = line[x] || ' ';
        var d = DENS[ch];
        out[y * cols + x] = d === undefined ? 0.5 : Math.pow(d, 1.1);
      }
    }
    return out;
  }

  function resize() {
    var w = container.clientWidth || 500;
    cell = w / cols;
    var h = cell * CELL_H * rows;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.font = (cell * 1.45) + 'px "Gentium Plus", "Cardo", "Palatino Linotype", Georgia, serif';
    ctx.textBaseline = 'middle';
    ctx.textAlign = 'center';
  }

  function gold(d, glow) {
    // deep bronze → gold → pale illumination
    var t = Math.min(1, d * 1.15 + glow * 0.4);
    var r = Math.round(60 + 195 * Math.pow(t, 0.7));
    var g = Math.round(34 + 186 * Math.pow(t, 1.0));
    var b = Math.round(8 + 130 * Math.pow(t, 1.9));
    return 'rgb(' + r + ',' + g + ',' + b + ')';
  }

  function draw(now) {
    var w = canvas.width / dpr, h = canvas.height / dpr;
    ctx.fillStyle = '#050403';
    ctx.fillRect(0, 0, w, h);
    // vignette + faint parchment glow at the centre
    var vg = ctx.createRadialGradient(w / 2, h / 2, h * 0.15, w / 2, h / 2, h * 0.8);
    vg.addColorStop(0, 'rgba(90,60,20,0.18)');
    vg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = vg; ctx.fillRect(0, 0, w, h);

    var cx = mouse.on ? mouse.x : w / 2 + Math.sin(now / 2600) * w * 0.28;
    var cy = mouse.on ? mouse.y : h / 2 + Math.cos(now / 3400) * h * 0.22;
    var radius = Math.max(w, h) * 0.32;

    for (var y = 0; y < rows; y++) {
      for (var x = 0; x < cols; x++) {
        var i = y * cols + x;
        var d = cur[i];
        if (target && mix < 1) {
          var p = mix - timings[i];
          if (p > 0.12) d = target[i];
          else if (p > 0) d = Math.random();  // scribal scramble
        }
        if (d < 0.04) continue;
        var px = x * cell + cell / 2, py = (y + 0.5) * cell * CELL_H;
        var dx = px - cx, dy = py - cy;
        var dist = Math.sqrt(dx * dx + dy * dy);
        var glow = Math.max(0, 1 - dist / radius);
        var shimmer = 0.85 + 0.15 * Math.sin(now / 900 + phase[i]);
        ctx.fillStyle = gold(d * shimmer, glow * glow);
        var gi = Math.min(GLYPHS.length - 1, Math.floor(d * GLYPHS.length + (glow > 0.6 ? 2 : 0)));
        ctx.fillText(GLYPHS[gi], px, py);
      }
    }
  }

  function loop(now) {
    if (target && mix < 1) {
      mix = Math.min(1, (now - tStart) / TRANSITION);
      if (mix >= 1) { cur = target; target = null; holdTimer = setTimeout(next, HOLD); }
    }
    draw(now);
    requestAnimationFrame(loop);
  }

  function next() {
    idx = (idx + 1) % frames.length;
    target = densities(frames[idx]);
    timings = new Float32Array(cols * rows);
    for (var i = 0; i < timings.length; i++) {
      // sweep top-left → bottom-right like a pen moving across the page
      var x = i % cols, y = Math.floor(i / cols);
      timings[i] = ((x / cols) * 0.5 + (y / rows) * 0.5) * 0.7 + Math.random() * 0.18;
    }
    mix = 0; tStart = performance.now();
  }

  container.addEventListener('mousemove', function (e) {
    var rct = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rct.left; mouse.y = e.clientY - rct.top; mouse.on = true;
  });
  container.addEventListener('mouseleave', function () { mouse.on = false; });
  container.addEventListener('touchmove', function (e) {
    var t = e.touches[0], rct = canvas.getBoundingClientRect();
    mouse.x = t.clientX - rct.left; mouse.y = t.clientY - rct.top; mouse.on = true;
  }, { passive: true });
  window.addEventListener('resize', function () { if (cols) resize(); });

  fetch('/data/ascii-frames.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      frames = data;
      if (!frames.length) return;
      idx = 0;
      cur = new Float32Array(0);
      target = densities(frames[0]);
      cur = new Float32Array(cols * rows);
      phase = new Float32Array(cols * rows);
      for (var i = 0; i < phase.length; i++) phase[i] = Math.random() * 6.283;
      timings = new Float32Array(cols * rows);
      for (var j = 0; j < timings.length; j++) {
        var x = j % cols, y = Math.floor(j / cols);
        timings[j] = ((x / cols) * 0.5 + (y / rows) * 0.5) * 0.7 + Math.random() * 0.18;
      }
      resize();
      mix = 0; tStart = performance.now();
      requestAnimationFrame(loop);
    })
    .catch(function (err) { console.error('hero frames failed', err); });
})();
