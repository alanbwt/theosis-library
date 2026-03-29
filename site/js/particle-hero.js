/**
 * Theosis Library — ASCII Art Portrait
 * Exact port of scipython.com/blog/ascii-art/ technique.
 * White ASCII characters on black background.
 */

(function () {
  'use strict';

  var container = document.getElementById('particle-hero');
  if (!container) return;

  var IMAGE_SRC = '/assets/christ-portrait.jpg';
  var ASCII_WIDTH = 160; // characters wide — increase for more detail
  var CONTRAST = 10;

  // Exact density string from scipython
  var density = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'.          ';
  // Trim by contrast (contrast=10 keeps almost all)
  density = density.substring(0, density.length - 11 + CONTRAST);
  var n = density.length;

  // Build a <pre> element with the ASCII art (not canvas — actual text)
  var pre = document.createElement('pre');
  pre.className = 'ascii-art';
  container.appendChild(pre);

  var img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = function () {
    renderASCII(img);

    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () { renderASCII(img); }, 300);
    });
  };
  img.src = IMAGE_SRC;

  function renderASCII(img) {
    // Responsive width: more chars on bigger screens
    var cw = container.clientWidth;
    var width = cw > 900 ? 200 : cw > 600 ? 160 : cw > 400 ? 120 : 90;

    // Calculate height with 0.5 aspect correction for character cells
    var r = img.height / img.width;
    var height = Math.floor(width * r * 0.5);

    // Sample the image at ASCII resolution
    var sCanvas = document.createElement('canvas');
    var sCtx = sCanvas.getContext('2d');
    sCanvas.width = width;
    sCanvas.height = height;
    sCtx.imageSmoothingEnabled = true;
    sCtx.imageSmoothingQuality = 'high';
    sCtx.drawImage(img, 0, 0, width, height);
    var data = sCtx.getImageData(0, 0, width, height).data;

    // Build ASCII string exactly like the Python version
    var lines = [];
    for (var y = 0; y < height; y++) {
      var line = '';
      for (var x = 0; x < width; x++) {
        var i = (y * width + x) * 4;
        var gray = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
        var k = Math.floor(gray / 256 * n);
        // n-1-k: dark pixels -> dense chars ($@B), bright pixels -> sparse chars (.  )
        var charIdx = n - 1 - k;
        if (charIdx < 0) charIdx = 0;
        if (charIdx >= n) charIdx = n - 1;
        line += density[charIdx];
      }
      lines.push(line);
    }

    pre.textContent = lines.join('\n');
  }
})();
