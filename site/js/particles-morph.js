/**
 * Theosis Library — Morphing Particle Mosaic
 * Particles form one image, then smoothly drift to form the next.
 * Cycles through: Christ, cuneiform, papyrus, codex.
 */

(function () {
  'use strict';

  var container = document.getElementById('particle-hero');
  if (!container) return;

  var canvas = document.createElement('canvas');
  canvas.className = 'particle-canvas';
  container.appendChild(canvas);
  var ctx = canvas.getContext('2d');

  var images = [
    '/assets/christ-portrait.jpg',
    '/assets/timeline/gilgamesh-tablet.jpg',
    '/assets/timeline/book-of-dead.jpg',
    '/assets/timeline/codex-sinaiticus.jpg'
  ];

  var PARTICLE_COUNT = 8000;
  var SAMPLE_W = 300;
  var LERP_SPEED = 0.03;
  var CYCLE_MS = 6000;
  var PARTICLE_SIZE = 1.5;
  var dpr = Math.min(window.devicePixelRatio || 1, 2);

  var particles = [];
  var imageData = [];
  var currentImage = 0;
  var lastSwitch = 0;
  var animId = null;
  var w = 0, h = 0;

  function resize() {
    var rect = container.getBoundingClientRect();
    w = rect.width;
    h = rect.height;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function sampleImage(img) {
    var sCanvas = document.createElement('canvas');
    var sCtx = sCanvas.getContext('2d');
    var aspect = img.height / img.width;
    var sW = SAMPLE_W;
    var sH = Math.round(sW * aspect);
    sCanvas.width = sW;
    sCanvas.height = sH;
    sCtx.drawImage(img, 0, 0, sW, sH);
    var data = sCtx.getImageData(0, 0, sW, sH).data;

    // Collect dark pixel positions
    var points = [];
    for (var y = 0; y < sH; y += 2) {
      for (var x = 0; x < sW; x += 2) {
        var i = (y * sW + x) * 4;
        var bright = (0.299 * data[i] + 0.587 * data[i+1] + 0.114 * data[i+2]) / 255;
        if (bright < 0.75) {
          var darkness = 1 - bright;
          if (Math.random() < darkness * darkness) {
            points.push({ x: x / sW, y: y / sH, d: darkness });
          }
        }
      }
    }

    // Select PARTICLE_COUNT points
    while (points.length < PARTICLE_COUNT) {
      points.push(points[Math.floor(Math.random() * points.length)]);
    }
    // Shuffle and take
    for (var i = points.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = points[i]; points[i] = points[j]; points[j] = tmp;
    }
    return points.slice(0, PARTICLE_COUNT);
  }

  function loadAllImages(urls, cb) {
    var loaded = 0;
    var imgs = [];
    urls.forEach(function(url, idx) {
      var img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = function() {
        imgs[idx] = img;
        loaded++;
        if (loaded === urls.length) cb(imgs);
      };
      img.onerror = function() {
        // Use a placeholder
        imgs[idx] = imgs[0] || img;
        loaded++;
        if (loaded === urls.length) cb(imgs);
      };
      img.src = url;
    });
  }

  function init(imgs) {
    resize();

    // Sample all images
    imgs.forEach(function(img) {
      imageData.push(sampleImage(img));
    });

    // Initialize particles at first image's positions
    var first = imageData[0];
    var imgAspect = imgs[0].height / imgs[0].width;
    var displayW = Math.min(w * 0.6, 300);
    var displayH = displayW * imgAspect;
    var offsetX = (w - displayW) / 2;
    var offsetY = (h - displayH) / 2;

    for (var i = 0; i < PARTICLE_COUNT; i++) {
      var p = first[i];
      particles.push({
        x: offsetX + p.x * displayW,
        y: offsetY + p.y * displayH,
        tx: offsetX + p.x * displayW,
        ty: offsetY + p.y * displayH,
        size: PARTICLE_SIZE * (0.5 + p.d * 1),
        alpha: 0.3 + p.d * 0.6,
        phase: Math.random() * Math.PI * 2
      });
    }

    lastSwitch = performance.now();
    animId = requestAnimationFrame(draw);
  }

  function setTargets(imgIdx) {
    var points = imageData[imgIdx];
    // Recalculate display dimensions for this image
    // Use container dimensions
    var displayW = Math.min(w * 0.55, 280);
    var displayH = displayW * 1.3; // approximate
    var offsetX = (w - displayW) / 2;
    var offsetY = (h - displayH) / 2;

    for (var i = 0; i < PARTICLE_COUNT; i++) {
      var p = points[i];
      particles[i].tx = offsetX + p.x * displayW + (Math.random() - 0.5) * 2;
      particles[i].ty = offsetY + p.y * displayH + (Math.random() - 0.5) * 2;
      particles[i].alpha = 0.3 + p.d * 0.6;
      particles[i].size = PARTICLE_SIZE * (0.5 + p.d * 1);
    }
  }

  function draw(time) {
    // Check if we should switch images
    if (time - lastSwitch > CYCLE_MS) {
      currentImage = (currentImage + 1) % imageData.length;
      setTargets(currentImage);
      lastSwitch = time;
    }

    ctx.clearRect(0, 0, w, h);

    var t = time * 0.001;
    for (var i = 0; i < particles.length; i++) {
      var p = particles[i];

      // Lerp toward target
      p.x += (p.tx - p.x) * LERP_SPEED;
      p.y += (p.ty - p.y) * LERP_SPEED;

      // Subtle breathing
      var bx = Math.sin(t * 0.3 + p.phase) * 0.5;
      var by = Math.cos(t * 0.25 + p.phase * 1.3) * 0.3;

      ctx.globalAlpha = p.alpha;
      ctx.fillStyle = '#2c2418';
      ctx.beginPath();
      ctx.arc(p.x + bx, p.y + by, p.size, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.globalAlpha = 1;
    animId = requestAnimationFrame(draw);
  }

  // Start
  loadAllImages(images, init);

  var resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      resize();
      if (imageData.length) setTargets(currentImage);
    }, 150);
  });

  document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
      if (animId) cancelAnimationFrame(animId);
      animId = null;
    } else if (!animId && particles.length) {
      lastSwitch = performance.now();
      animId = requestAnimationFrame(draw);
    }
  });
})();
