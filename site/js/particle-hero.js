/**
 * Theosis Library — ASCII Art Portrait
 * Renders source image as dense ASCII characters on dark background.
 * High-res, monochrome, like a terminal art masterpiece.
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

  // ASCII characters from darkest to lightest
  var CHARS = ' .\'`^",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$';

  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var rendered = false;

  function render(img) {
    var cw = container.clientWidth;
    var ch = container.clientHeight;

    canvas.width = cw * dpr;
    canvas.height = ch * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // Dark background
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, cw, ch);

    // Determine font size for density
    // Smaller font = more characters = higher fidelity
    var fontSize = cw > 800 ? 6 : cw > 500 ? 5.5 : 5;
    var charW = fontSize * 0.6;
    var charH = fontSize * 1.0;

    // How many characters fit
    var cols = Math.floor(cw / charW);
    var rows = Math.floor(ch / charH);

    // Sample image at that resolution
    var sCanvas = document.createElement('canvas');
    var sCtx = sCanvas.getContext('2d');
    sCanvas.width = cols;
    sCanvas.height = rows;

    // Draw image centered/cover
    var imgAspect = img.width / img.height;
    var containerAspect = cols / rows * (charH / charW);
    var drawW, drawH, drawX, drawY;

    if (imgAspect > containerAspect) {
      drawH = rows;
      drawW = rows * imgAspect * (charW / charH);
      drawX = (cols - drawW) / 2;
      drawY = 0;
    } else {
      drawW = cols;
      drawH = cols / imgAspect * (charH / charW);
      drawX = 0;
      drawY = (rows - drawH) / 2;
    }

    sCtx.drawImage(img, drawX, drawY, drawW, drawH);
    var data = sCtx.getImageData(0, 0, cols, rows).data;

    // Render ASCII
    ctx.font = fontSize + 'px monospace';
    ctx.textBaseline = 'top';

    for (var y = 0; y < rows; y++) {
      for (var x = 0; x < cols; x++) {
        var i = (y * cols + x) * 4;
        var r = data[i], g = data[i + 1], b = data[i + 2], a = data[i + 3];

        if (a < 10) continue;

        var brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

        // Map brightness to character
        var charIdx = Math.floor(brightness * (CHARS.length - 1));
        var ch_char = CHARS[charIdx];

        if (ch_char === ' ') continue;

        // Use brightness for alpha/intensity
        var intensity = 0.3 + brightness * 0.7;
        ctx.fillStyle = 'rgba(255,255,255,' + intensity + ')';
        ctx.fillText(ch_char, x * charW, y * charH);
      }
    }

    rendered = true;
  }

  function init() {
    var img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      render(img);

      // Re-render on resize
      var resizeTimer;
      window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () { render(img); }, 200);
      });
    };
    img.src = IMAGE_SRC;
  }

  init();
})();
