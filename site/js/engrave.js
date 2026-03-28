/**
 * Theosis Library — Engraving renderer
 * Converts the portrait into a black-and-white woodcut/engraving style
 * using layered hatching, crosshatching, and stippling.
 * Renders once to a static <img>.
 */

(function () {
  'use strict';

  var target = document.getElementById('hero-engraving');
  if (!target) return;

  var img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = function () { render(img); };
  img.src = '/assets/christ-portrait.jpg';

  function render(sourceImg) {
    // Output dimensions — high-res for sharp lines
    var maxW = 1200;
    var aspect = sourceImg.height / sourceImg.width;
    var W = maxW;
    var H = Math.round(W * aspect);

    // Sample canvas for brightness data
    var sCanvas = document.createElement('canvas');
    var sCtx = sCanvas.getContext('2d');
    sCanvas.width = W;
    sCanvas.height = H;
    sCtx.drawImage(sourceImg, 0, 0, W, H);
    var imgData = sCtx.getImageData(0, 0, W, H).data;

    // Also create a blurred version for smoother hatching
    var bCanvas = document.createElement('canvas');
    var bCtx = bCanvas.getContext('2d');
    bCanvas.width = W;
    bCanvas.height = H;
    bCtx.filter = 'blur(3px)';
    bCtx.drawImage(sourceImg, 0, 0, W, H);
    var blurData = bCtx.getImageData(0, 0, W, H).data;

    // Output canvas
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    canvas.width = W;
    canvas.height = H;

    // White background
    ctx.fillStyle = '#faf8f4';
    ctx.fillRect(0, 0, W, H);

    function getBrightness(data, x, y) {
      x = Math.max(0, Math.min(W - 1, Math.round(x)));
      y = Math.max(0, Math.min(H - 1, Math.round(y)));
      var i = (y * W + x) * 4;
      return (0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]) / 255;
    }

    function getBlurBrightness(x, y) {
      return getBrightness(blurData, x, y);
    }

    // Edge detection (Sobel) for contour lines
    function getEdge(x, y) {
      var gx = -getBrightness(imgData, x - 1, y - 1) - 2 * getBrightness(imgData, x - 1, y) - getBrightness(imgData, x - 1, y + 1)
             + getBrightness(imgData, x + 1, y - 1) + 2 * getBrightness(imgData, x + 1, y) + getBrightness(imgData, x + 1, y + 1);
      var gy = -getBrightness(imgData, x - 1, y - 1) - 2 * getBrightness(imgData, x, y - 1) - getBrightness(imgData, x + 1, y - 1)
             + getBrightness(imgData, x - 1, y + 1) + 2 * getBrightness(imgData, x, y + 1) + getBrightness(imgData, x + 1, y + 1);
      return Math.sqrt(gx * gx + gy * gy);
    }

    ctx.lineCap = 'round';

    // ─── Layer 1: Primary hatching (roughly 30°) ───────────
    drawHatchLayer(ctx, 30, 3.5, 0.15, 0.7);

    // ─── Layer 2: Cross-hatching (120°) for mid-darks ──────
    drawHatchLayer(ctx, 120, 4, 0.0, 0.55);

    // ─── Layer 3: Tertiary hatching (75°) for darkest ──────
    drawHatchLayer(ctx, 75, 4.5, 0.0, 0.38);

    // ─── Layer 4: Near-horizontal (165°) for deepest darks ─
    drawHatchLayer(ctx, 165, 5, 0.0, 0.22);

    // ─── Layer 5: Stippling for texture in mid-tones ───────
    drawStipple(ctx);

    // ─── Layer 6: Edge contour lines ───────────────────────
    drawEdges(ctx);

    function drawHatchLayer(c, angleDeg, baseSpacing, brightnessThreshold, darknessThreshold) {
      var angle = angleDeg * Math.PI / 180;
      var cos = Math.cos(angle);
      var sin = Math.sin(angle);

      // Perpendicular direction for line spacing
      var perpX = -sin;
      var perpY = cos;

      // Line direction
      var dirX = cos;
      var dirY = sin;

      // Diagonal of canvas
      var diag = Math.sqrt(W * W + H * H);

      // Draw parallel lines across entire canvas
      var spacing = baseSpacing;
      var numLines = Math.ceil(diag / spacing) + 10;

      c.strokeStyle = '#1a1a1a';

      for (var li = -numLines; li <= numLines; li++) {
        // Origin point along perpendicular axis, centered on canvas
        var ox = W / 2 + perpX * li * spacing;
        var oy = H / 2 + perpY * li * spacing;

        // Start and end of line across canvas
        var sx = ox - dirX * diag;
        var sy = oy - dirY * diag;

        // Walk along the line in small steps, drawing segments only where dark enough
        var stepSize = 2;
        var totalSteps = Math.ceil(diag * 2 / stepSize);
        var drawing = false;
        var segStartX, segStartY;

        for (var s = 0; s <= totalSteps; s++) {
          var px = sx + dirX * s * stepSize;
          var py = sy + dirY * s * stepSize;

          // Skip if outside canvas
          if (px < -5 || px > W + 5 || py < -5 || py > H + 5) {
            if (drawing) {
              finishSegment(c, segStartX, segStartY, px - dirX * stepSize, py - dirY * stepSize);
              drawing = false;
            }
            continue;
          }

          var brightness = getBlurBrightness(px, py);
          var darkness = 1 - brightness;

          // Only draw where dark enough for this layer
          var shouldDraw = darkness > darknessThreshold && brightness < (1 - brightnessThreshold);

          if (shouldDraw && !drawing) {
            drawing = true;
            segStartX = px;
            segStartY = py;
          } else if (!shouldDraw && drawing) {
            finishSegment(c, segStartX, segStartY, px, py);
            drawing = false;
          }
        }
        if (drawing) {
          finishSegment(c, segStartX, segStartY,
            sx + dirX * totalSteps * stepSize,
            sy + dirY * totalSteps * stepSize);
        }
      }
    }

    function finishSegment(c, x1, y1, x2, y2) {
      // Vary line weight based on local darkness
      var mx = (x1 + x2) / 2;
      var my = (y1 + y2) / 2;
      var darkness = 1 - getBlurBrightness(mx, my);
      var weight = 0.4 + darkness * 1.2;
      c.lineWidth = weight;
      c.globalAlpha = 0.6 + darkness * 0.4;

      c.beginPath();
      c.moveTo(x1, y1);

      // Add very subtle waviness for hand-engraved feel
      var dx = x2 - x1;
      var dy = y2 - y1;
      var len = Math.sqrt(dx * dx + dy * dy);
      if (len > 8) {
        var steps = Math.ceil(len / 6);
        for (var i = 1; i <= steps; i++) {
          var t = i / steps;
          var px = x1 + dx * t;
          var py = y1 + dy * t;
          // Tiny perpendicular wobble
          var wobble = Math.sin(t * 12 + mx * 0.1) * 0.3;
          var nx = -dy / len;
          var ny = dx / len;
          c.lineTo(px + nx * wobble, py + ny * wobble);
        }
      } else {
        c.lineTo(x2, y2);
      }
      c.stroke();
      c.globalAlpha = 1;
    }

    function drawStipple(c) {
      c.fillStyle = '#1a1a1a';
      var dotCount = 50000;
      for (var i = 0; i < dotCount; i++) {
        var x = Math.random() * W;
        var y = Math.random() * H;
        var brightness = getBlurBrightness(x, y);
        var darkness = 1 - brightness;

        // Stipple primarily in mid-dark areas
        if (darkness > 0.25 && Math.random() < darkness * darkness * 0.7) {
          var r = 0.3 + darkness * 0.8;
          c.globalAlpha = 0.3 + darkness * 0.5;
          c.beginPath();
          c.arc(x, y, r, 0, Math.PI * 2);
          c.fill();
        }
      }
      c.globalAlpha = 1;
    }

    function drawEdges(c) {
      c.strokeStyle = '#111';
      c.lineWidth = 0.8;
      c.globalAlpha = 0.5;

      // Walk the image and draw short edge segments
      var step = 2;
      for (var y = step; y < H - step; y += step) {
        for (var x = step; x < W - step; x += step) {
          var edge = getEdge(x, y);
          if (edge > 0.25) {
            var brightness = getBlurBrightness(x, y);
            // Stronger edges in darker areas
            var alpha = Math.min(edge * (1.5 - brightness), 0.7);
            if (alpha > 0.15) {
              c.globalAlpha = alpha;
              c.beginPath();
              c.arc(x, y, 0.5, 0, Math.PI * 2);
              c.fill();
            }
          }
        }
      }
      c.globalAlpha = 1;
    }

    // Convert canvas to image and insert
    var output = document.createElement('img');
    output.src = canvas.toDataURL('image/png');
    output.alt = 'Christ portrait rendered in engraving style';
    output.className = 'hero-engraving-img';
    target.appendChild(output);
    target.classList.add('loaded');
  }
})();
