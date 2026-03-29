/**
 * Theosis Library — ASCII Art Portrait
 * Based on the scipython.com/blog/ascii-art/ technique.
 * Dense character set, inverted brightness mapping, 0.5 aspect correction.
 */

(function () {
  'use strict';

  var container = document.getElementById('particle-hero');
  if (!container) return;

  var canvas = document.createElement('canvas');
  canvas.style.cssText = 'width:100%;height:100%;display:block;border-radius:12px;';
  container.appendChild(canvas);
  var ctx = canvas.getContext('2d');
  if (!ctx) return;

  var IMAGE_SRC = '/assets/christ-portrait.jpg';

  // The exact 70-char density string from scipython, densest to lightest
  var DENSITY = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. ';

  var dpr = Math.min(window.devicePixelRatio || 1, 2);

  function render(img) {
    var cw = container.clientWidth;
    var ch = container.clientHeight;

    canvas.width = cw * dpr;
    canvas.height = ch * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Dark background
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, cw, ch);

    // Font size — smaller = denser = higher fidelity
    var fontSize = cw > 900 ? 7 : cw > 600 ? 6 : cw > 400 ? 5.5 : 5;

    // Measure actual character dimensions
    ctx.font = fontSize + 'px Courier New, Courier, monospace';
    var charW = ctx.measureText('M').width;
    var charH = fontSize * 1.15; // line height

    // How many chars fit in the container
    var cols = Math.floor(cw / charW);
    var rows = Math.floor(ch / charH);

    if (cols < 10 || rows < 10) return;

    // Sample the image at ASCII resolution
    // The 0.5 aspect correction is built into the grid: we use charH which is ~2x charW
    var sCanvas = document.createElement('canvas');
    var sCtx = sCanvas.getContext('2d');
    sCanvas.width = cols;
    sCanvas.height = rows;

    // Enable high-quality downsampling (equivalent to LANCZOS)
    sCtx.imageSmoothingEnabled = true;
    sCtx.imageSmoothingQuality = 'high';

    // Draw image to fill the grid (cover)
    var imgAspect = img.width / img.height;
    var gridAspect = (cols * charW) / (rows * charH);
    var sx, sy, sw, sh;

    if (imgAspect > gridAspect) {
      // Image wider than grid — crop sides
      sh = img.height;
      sw = img.height * gridAspect;
      sx = (img.width - sw) / 2;
      sy = 0;
    } else {
      // Image taller than grid — crop top/bottom
      sw = img.width;
      sh = img.width / gridAspect;
      sx = 0;
      sy = (img.height - sh) / 2;
    }

    sCtx.drawImage(img, sx, sy, sw, sh, 0, 0, cols, rows);
    var data = sCtx.getImageData(0, 0, cols, rows).data;

    var n = DENSITY.length;

    // Set font for rendering
    ctx.font = fontSize + 'px Courier New, Courier, monospace';
    ctx.textBaseline = 'top';

    for (var y = 0; y < rows; y++) {
      for (var x = 0; x < cols; x++) {
        var i = (y * cols + x) * 4;
        var r = data[i], g = data[i + 1], b = data[i + 2];

        // Convert to grayscale
        var gray = 0.299 * r + 0.587 * g + 0.114 * b;

        // Map to character — bright pixel = dense/visible char, dark = sparse/space
        var charIdx = Math.floor(gray / 256 * n);
        if (charIdx >= n) charIdx = n - 1;
        var ch_char = DENSITY[charIdx];

        if (ch_char === ' ' || ch_char === '.' || ch_char === "'") continue;

        // Brighter pixels get more visible characters
        var alpha = 0.4 + (gray / 255) * 0.6;
        ctx.fillStyle = 'rgba(220,220,215,' + alpha.toFixed(2) + ')';
        ctx.fillText(ch_char, x * charW, y * charH);
      }
    }
  }

  var img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = function () {
    render(img);

    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () { render(img); }, 250);
    });
  };
  img.src = IMAGE_SRC;
})();
