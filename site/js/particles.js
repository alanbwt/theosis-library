/**
 * Theosis Library — Particle portrait animation
 * Renders an image as a field of drifting particles on canvas.
 * Monochrome, subtle, meditative.
 */

(function () {
  'use strict';

  var canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  var ctx = canvas.getContext('2d');
  var particles = [];
  var animId = null;
  var time = 0;
  var imgData = null;
  var imgW = 0;
  var imgH = 0;
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var mouse = { x: -9999, y: -9999 };
  var MOUSE_RADIUS = 60;

  // Configuration
  var SAMPLE_GAP = 3;         // pixel gap when sampling image
  var PARTICLE_SIZE = 1.2;    // base radius
  var DRIFT_SPEED = 0.0004;   // how fast particles breathe
  var DRIFT_AMOUNT = 1.8;     // max pixel drift
  var FADE_IN_DURATION = 2500;
  var startTime = 0;

  function resize() {
    var rect = canvas.parentElement.getBoundingClientRect();
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    if (imgData) buildParticles();
  }

  function loadImage(src, cb) {
    var img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      var offscreen = document.createElement('canvas');
      var octx = offscreen.getContext('2d');

      // Size to fit canvas container
      var container = canvas.parentElement.getBoundingClientRect();
      var scale = Math.min(container.width / img.width, container.height / img.height);
      imgW = Math.floor(img.width * scale);
      imgH = Math.floor(img.height * scale);

      offscreen.width = imgW;
      offscreen.height = imgH;
      octx.drawImage(img, 0, 0, imgW, imgH);
      imgData = octx.getImageData(0, 0, imgW, imgH);
      cb();
    };
    img.src = src;
  }

  function getBrightness(x, y) {
    if (x < 0 || x >= imgW || y < 0 || y >= imgH) return 255;
    var i = (y * imgW + x) * 4;
    var r = imgData.data[i];
    var g = imgData.data[i + 1];
    var b = imgData.data[i + 2];
    return 0.299 * r + 0.587 * g + 0.114 * b;
  }

  function buildParticles() {
    particles = [];
    var container = canvas.parentElement.getBoundingClientRect();
    var cw = container.width;
    var ch = container.height;

    // Centre the image in the canvas
    var offsetX = (cw - imgW) / 2;
    var offsetY = (ch - imgH) / 2;

    // Responsive gap: tighter on larger screens
    var gap = cw > 800 ? SAMPLE_GAP : cw > 500 ? 4 : 5;

    for (var y = 0; y < imgH; y += gap) {
      for (var x = 0; x < imgW; x += gap) {
        var brightness = getBrightness(x, y);

        // Skip very bright pixels (background)
        if (brightness > 200) continue;

        // Darker pixels get larger, more opaque particles
        var norm = 1 - brightness / 255;
        var alpha = norm * 0.85 + 0.05;
        var size = PARTICLE_SIZE * (0.5 + norm * 0.8);

        particles.push({
          x: offsetX + x,
          y: offsetY + y,
          baseX: offsetX + x,
          baseY: offsetY + y,
          size: size,
          alpha: alpha,
          // Each particle gets a unique phase for organic motion
          phase: Math.random() * Math.PI * 2,
          speed: DRIFT_SPEED * (0.7 + Math.random() * 0.6),
          drift: DRIFT_AMOUNT * (0.6 + Math.random() * 0.8)
        });
      }
    }
  }

  function draw(timestamp) {
    if (!startTime) startTime = timestamp;
    var elapsed = timestamp - startTime;
    var fadeAlpha = Math.min(elapsed / FADE_IN_DURATION, 1);
    // Ease in
    fadeAlpha = fadeAlpha * fadeAlpha * (3 - 2 * fadeAlpha);

    time = timestamp;

    var container = canvas.parentElement.getBoundingClientRect();
    var cw = container.width;
    var ch = container.height;

    ctx.clearRect(0, 0, cw, ch);

    for (var i = 0; i < particles.length; i++) {
      var p = particles[i];

      // Gentle organic drift
      var dx = Math.sin(time * p.speed + p.phase) * p.drift;
      var dy = Math.cos(time * p.speed * 0.7 + p.phase + 1.3) * p.drift * 0.6;

      p.x = p.baseX + dx;
      p.y = p.baseY + dy;

      // Mouse repulsion
      var mx = p.x - mouse.x;
      var my = p.y - mouse.y;
      var dist = Math.sqrt(mx * mx + my * my);
      if (dist < MOUSE_RADIUS) {
        var force = (1 - dist / MOUSE_RADIUS) * 8;
        p.x += (mx / dist) * force;
        p.y += (my / dist) * force;
      }

      var a = p.alpha * fadeAlpha;
      ctx.globalAlpha = a;
      ctx.fillStyle = '#2a2a2a';
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.globalAlpha = 1;
    animId = requestAnimationFrame(draw);
  }

  function onMouseMove(e) {
    var rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  }

  function onMouseLeave() {
    mouse.x = -9999;
    mouse.y = -9999;
  }

  // Init
  loadImage('/assets/christ-portrait.jpg', function () {
    resize();
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseleave', onMouseLeave);
    animId = requestAnimationFrame(draw);
  });

  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      resize();
    }, 150);
  });

  // Pause when not visible
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
      if (animId) cancelAnimationFrame(animId);
      animId = null;
    } else {
      if (!animId && particles.length) {
        animId = requestAnimationFrame(draw);
      }
    }
  });
})();
