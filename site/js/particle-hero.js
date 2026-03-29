/**
 * Theosis Library — Animated ASCII Art Hero
 * Cycles between images with a split-flap scramble transition.
 * Gilgamesh → Jesus → loop
 */

(function () {
  'use strict';

  var container = document.getElementById('particle-hero');
  if (!container) return;

  var IMAGES = [
    '/assets/gilgamesh-statue.jpg',
    '/assets/christ-portrait.jpg'
  ];

  var HOLD_TIME = 6000;       // ms to hold each image
  var TRANSITION_TIME = 1500; // ms for scramble transition
  var SCRAMBLE_CHARS = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ';
  var CONTRAST = 10;

  var density = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'.          ';
  density = density.substring(0, density.length - 11 + CONTRAST);
  var n = density.length;

  var pre = document.createElement('pre');
  pre.className = 'ascii-art';
  container.appendChild(pre);

  var asciiFrames = [];   // pre-rendered ASCII strings per image
  var currentIdx = 0;
  var cols = 0;
  var rows = 0;
  var transitioning = false;

  function imageToASCII(img) {
    var cw = container.clientWidth;
    var ch = container.clientHeight;

    // Calculate how many chars fit in the container exactly
    // Font metrics: char width ≈ fontSize * 0.6, char height ≈ lineHeight
    var fontSize = 3.8;
    var lineHeight = 4.2;
    var charW = fontSize * 0.6 + 0.2; // letter-spacing included
    var charH = lineHeight;

    var width = Math.floor(cw / charW);
    var height = Math.floor(ch / charH);

    cols = width;
    rows = height;

    var sCanvas = document.createElement('canvas');
    var sCtx = sCanvas.getContext('2d');
    sCanvas.width = width;
    sCanvas.height = height;
    sCtx.imageSmoothingEnabled = true;
    sCtx.imageSmoothingQuality = 'high';

    // Draw image to cover the grid — crop from TOP, never stretch
    var imgAspect = img.width / img.height;
    var gridAspect = width / height;
    var sx, sy, sw, sh;

    if (imgAspect > gridAspect) {
      // Image wider than grid — crop sides, keep centered
      sh = img.height;
      sw = img.height * gridAspect;
      sx = (img.width - sw) / 2;
      sy = 0;
    } else {
      // Image taller than grid — crop bottom, keep TOP
      sw = img.width;
      sh = img.width / gridAspect;
      sx = 0;
      sy = 0; // TOP aligned, not centered
    }

    sCtx.drawImage(img, sx, sy, sw, sh, 0, 0, width, height);
    var data = sCtx.getImageData(0, 0, width, height).data;

    // Build flat char array
    var chars = [];
    for (var y = 0; y < height; y++) {
      for (var x = 0; x < width; x++) {
        var i = (y * width + x) * 4;
        var gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
        var k = Math.floor(gray / 256 * n);
        var charIdx = n - 1 - k;
        if (charIdx < 0) charIdx = 0;
        if (charIdx >= n) charIdx = n - 1;
        chars.push(density[charIdx]);
      }
    }
    return chars;
  }

  function charsToString(chars) {
    var lines = [];
    for (var y = 0; y < rows; y++) {
      lines.push(chars.slice(y * cols, (y + 1) * cols).join(''));
    }
    return lines.join('\n');
  }

  function display(chars) {
    pre.textContent = charsToString(chars);
  }

  function scrambleTransition(fromChars, toChars, onComplete) {
    transitioning = true;
    var total = fromChars.length;
    var current = fromChars.slice(); // copy

    // Assign each character a random transition time within the window
    var timings = new Float32Array(total);
    for (var i = 0; i < total; i++) {
      timings[i] = Math.random(); // 0-1, will be scaled to TRANSITION_TIME
    }

    var startTime = performance.now();

    function tick(now) {
      var elapsed = now - startTime;
      var progress = Math.min(elapsed / TRANSITION_TIME, 1.0);
      var changed = false;

      for (var i = 0; i < total; i++) {
        if (current[i] === toChars[i]) continue; // already settled

        if (progress >= timings[i] + 0.15) {
          // Settled on target
          current[i] = toChars[i];
          changed = true;
        } else if (progress >= timings[i]) {
          // Scrambling phase — show random chars
          current[i] = SCRAMBLE_CHARS[Math.floor(Math.random() * SCRAMBLE_CHARS.length)];
          changed = true;
        }
      }

      if (changed || progress < 1.0) {
        display(current);
      }

      if (progress < 1.0) {
        requestAnimationFrame(tick);
      } else {
        display(toChars);
        transitioning = false;
        if (onComplete) onComplete();
      }
    }

    requestAnimationFrame(tick);
  }

  function cycle() {
    var nextIdx = (currentIdx + 1) % asciiFrames.length;
    scrambleTransition(asciiFrames[currentIdx], asciiFrames[nextIdx], function () {
      currentIdx = nextIdx;
      setTimeout(cycle, HOLD_TIME);
    });
  }

  // Load all images, pre-render ASCII, start cycling
  function loadImages(urls, cb) {
    var loaded = 0, imgs = [];
    urls.forEach(function (url, idx) {
      var img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = function () { imgs[idx] = img; loaded++; if (loaded === urls.length) cb(imgs); };
      img.onerror = function () { imgs[idx] = null; loaded++; if (loaded === urls.length) cb(imgs); };
      img.src = url;
    });
  }

  loadImages(IMAGES, function (imgs) {
    imgs.filter(Boolean).forEach(function (img) {
      asciiFrames.push(imageToASCII(img));
    });

    if (!asciiFrames.length) return;

    // Show first image
    display(asciiFrames[0]);
    currentIdx = 0;

    // Start cycling after hold time
    setTimeout(cycle, HOLD_TIME);

    // Re-render on resize
    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        var newFrames = [];
        imgs.filter(Boolean).forEach(function (img) {
          newFrames.push(imageToASCII(img));
        });
        asciiFrames = newFrames;
        display(asciiFrames[currentIdx]);
      }, 300);
    });
  });
})();
