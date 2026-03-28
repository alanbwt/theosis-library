/**
 * Theosis Library — High-fidelity 3D particle portrait
 * WebGL-rendered point cloud with depth, lighting, and perspective.
 */

(function () {
  'use strict';

  var canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  var gl = canvas.getContext('webgl', { antialias: true, alpha: true });
  if (!gl) return;

  // ─── Shaders ─────────────────────────────────────────────

  var vertSrc = [
    'attribute vec3 aPos;',
    'attribute float aBright;',
    'attribute float aPhase;',
    'attribute float aSize;',
    'uniform float uTime;',
    'uniform mat4 uProj;',
    'uniform mat4 uView;',
    'uniform vec2 uMouse;',
    'uniform float uMouseActive;',
    'uniform float uFade;',
    'uniform float uDpr;',
    'varying float vAlpha;',
    'varying float vBright;',
    '',
    'void main() {',
    '  float t = uTime;',
    '  // Organic drift per-particle',
    '  float dx = sin(t * 0.4 + aPhase) * 0.003;',
    '  float dy = cos(t * 0.3 + aPhase * 1.3) * 0.002;',
    '  float dz = sin(t * 0.25 + aPhase * 0.7) * 0.004;',
    '',
    '  vec3 pos = aPos + vec3(dx, dy, dz);',
    '',
    '  // Mouse repulsion in screen space after projection',
    '  vec4 projected = uProj * uView * vec4(pos, 1.0);',
    '  vec2 ndc = projected.xy / projected.w;',
    '  vec2 diff = ndc - uMouse;',
    '  float dist = length(diff);',
    '  float radius = 0.15;',
    '  if (dist < radius && uMouseActive > 0.5) {',
    '    float force = (1.0 - dist / radius) * 0.08;',
    '    vec2 push = normalize(diff) * force;',
    '    pos.x += push.x;',
    '    pos.y += push.y;',
    '    pos.z += (1.0 - dist / radius) * 0.03;',
    '  }',
    '',
    '  gl_Position = uProj * uView * vec4(pos, 1.0);',
    '',
    '  // Depth-based size: closer = bigger',
    '  float depth = gl_Position.w;',
    '  gl_PointSize = aSize * uDpr * (1.8 / depth);',
    '',
    '  // Alpha from brightness and depth',
    '  float depthFade = smoothstep(2.5, 0.8, depth);',
    '  vAlpha = (0.15 + aBright * 0.85) * depthFade * uFade;',
    '  vBright = aBright;',
    '}'
  ].join('\n');

  var fragSrc = [
    'precision mediump float;',
    'varying float vAlpha;',
    'varying float vBright;',
    '',
    'void main() {',
    '  // Soft circular particle',
    '  vec2 c = gl_PointCoord - 0.5;',
    '  float d = length(c);',
    '  if (d > 0.5) discard;',
    '  float soft = 1.0 - smoothstep(0.2, 0.5, d);',
    '',
    '  // Monochrome: dark particles on light bg',
    '  float lum = 0.12 + (1.0 - vBright) * 0.06;',
    '  gl_FragColor = vec4(lum, lum, lum, vAlpha * soft);',
    '}'
  ].join('\n');

  function compileShader(src, type) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.error(gl.getShaderInfoLog(s));
      return null;
    }
    return s;
  }

  var vs = compileShader(vertSrc, gl.VERTEX_SHADER);
  var fs = compileShader(fragSrc, gl.FRAGMENT_SHADER);
  var prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  gl.useProgram(prog);

  var aPos = gl.getAttribLocation(prog, 'aPos');
  var aBright = gl.getAttribLocation(prog, 'aBright');
  var aPhase = gl.getAttribLocation(prog, 'aPhase');
  var aSize = gl.getAttribLocation(prog, 'aSize');
  var uTime = gl.getUniformLocation(prog, 'uTime');
  var uProj = gl.getUniformLocation(prog, 'uProj');
  var uView = gl.getUniformLocation(prog, 'uView');
  var uMouse = gl.getUniformLocation(prog, 'uMouse');
  var uMouseActive = gl.getUniformLocation(prog, 'uMouseActive');
  var uFade = gl.getUniformLocation(prog, 'uFade');
  var uDpr = gl.getUniformLocation(prog, 'uDpr');

  // ─── State ───────────────────────────────────────────────

  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var particleCount = 0;
  var animId = null;
  var startTime = 0;
  var mouse = { x: 0, y: 0, active: false };
  var cameraAngle = 0;
  var FADE_DURATION = 3000;

  // ─── Matrix helpers (no dependencies) ────────────────────

  function perspective(fov, aspect, near, far) {
    var f = 1.0 / Math.tan(fov / 2);
    var nf = 1 / (near - far);
    return new Float32Array([
      f / aspect, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (far + near) * nf, -1,
      0, 0, 2 * far * near * nf, 0
    ]);
  }

  function lookAt(eye, center, up) {
    var zx = eye[0] - center[0], zy = eye[1] - center[1], zz = eye[2] - center[2];
    var zl = 1 / Math.sqrt(zx * zx + zy * zy + zz * zz);
    zx *= zl; zy *= zl; zz *= zl;
    var xx = up[1] * zz - up[2] * zy;
    var xy = up[2] * zx - up[0] * zz;
    var xz = up[0] * zy - up[1] * zx;
    var xl = 1 / Math.sqrt(xx * xx + xy * xy + xz * xz);
    xx *= xl; xy *= xl; xz *= xl;
    var yx = zy * xz - zz * xy;
    var yy = zz * xx - zx * xz;
    var yz = zx * xy - zy * xx;
    return new Float32Array([
      xx, yx, zx, 0,
      xy, yy, zy, 0,
      xz, yz, zz, 0,
      -(xx * eye[0] + xy * eye[1] + xz * eye[2]),
      -(yx * eye[0] + yy * eye[1] + yz * eye[2]),
      -(zx * eye[0] + zy * eye[1] + zz * eye[2]),
      1
    ]);
  }

  // ─── Build particles from image ─────────────────────────

  function loadImage(src, cb) {
    var img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function () { cb(img); };
    img.src = src;
  }

  function buildParticles(img) {
    var sampleCanvas = document.createElement('canvas');
    var sctx = sampleCanvas.getContext('2d');

    // Sample at high resolution
    var sampleW = Math.min(img.width, 800);
    var sampleH = Math.round(sampleW * (img.height / img.width));
    sampleCanvas.width = sampleW;
    sampleCanvas.height = sampleH;
    sctx.drawImage(img, 0, 0, sampleW, sampleH);
    var data = sctx.getImageData(0, 0, sampleW, sampleH).data;

    var positions = [];
    var brightnesses = [];
    var phases = [];
    var sizes = [];

    // Aspect ratio of image
    var aspect = sampleW / sampleH;

    // Sample every pixel at gap=1 for high density, gap=2 for medium
    var gap = sampleW > 600 ? 2 : 2;

    for (var y = 0; y < sampleH; y += gap) {
      for (var x = 0; x < sampleW; x += gap) {
        var i = (y * sampleW + x) * 4;
        var r = data[i], g = data[i + 1], b = data[i + 2];
        var bright = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

        // Skip very bright pixels (background)
        if (bright > 0.82) continue;

        // Normalize to centered coordinates [-1, 1] range
        var nx = (x / sampleW - 0.5) * 2 * aspect * 0.55;
        var ny = -(y / sampleH - 0.5) * 2 * 0.55;

        // Depth from brightness: darker = closer (face pops forward)
        var darkness = 1 - bright;
        var nz = darkness * 0.15 - 0.05;

        // Add slight random jitter for organic feel
        nx += (Math.random() - 0.5) * 0.003;
        ny += (Math.random() - 0.5) * 0.003;
        nz += (Math.random() - 0.5) * 0.01;

        positions.push(nx, ny, nz);
        brightnesses.push(darkness);
        phases.push(Math.random() * Math.PI * 2);

        // Size varies: darker areas get slightly larger particles
        var sz = 2.0 + darkness * 3.0;
        // Add some randomness
        sz *= 0.8 + Math.random() * 0.4;
        sizes.push(sz);
      }
    }

    particleCount = positions.length / 3;

    // Upload buffers
    var posBuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, posBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 3, gl.FLOAT, false, 0, 0);

    var brightBuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, brightBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(brightnesses), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(aBright);
    gl.vertexAttribPointer(aBright, 1, gl.FLOAT, false, 0, 0);

    var phaseBuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, phaseBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(phases), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(aPhase);
    gl.vertexAttribPointer(aPhase, 1, gl.FLOAT, false, 0, 0);

    var sizeBuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, sizeBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(sizes), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(aSize);
    gl.vertexAttribPointer(aSize, 1, gl.FLOAT, false, 0, 0);
  }

  // ─── Resize ──────────────────────────────────────────────

  function resize() {
    var rect = canvas.parentElement.getBoundingClientRect();
    var w = rect.width;
    var h = rect.height;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    gl.viewport(0, 0, canvas.width, canvas.height);
  }

  // ─── Render loop ─────────────────────────────────────────

  function draw(timestamp) {
    if (!startTime) startTime = timestamp;
    var elapsed = timestamp - startTime;
    var fade = Math.min(elapsed / FADE_DURATION, 1);
    fade = fade * fade * (3 - 2 * fade); // smoothstep

    var t = timestamp * 0.001;

    var rect = canvas.parentElement.getBoundingClientRect();
    var w = rect.width;
    var h = rect.height;

    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    // Very slow camera orbit: subtle 3D reveal
    cameraAngle = Math.sin(t * 0.06) * 0.12;
    var camDist = 1.5;
    var eyeX = Math.sin(cameraAngle) * camDist;
    var eyeZ = Math.cos(cameraAngle) * camDist;
    var eyeY = Math.sin(t * 0.04) * 0.03;

    var projMat = perspective(Math.PI / 4.5, w / h, 0.1, 10);
    var viewMat = lookAt([eyeX, eyeY, eyeZ], [0, 0, 0], [0, 1, 0]);

    gl.uniformMatrix4fv(uProj, false, projMat);
    gl.uniformMatrix4fv(uView, false, viewMat);
    gl.uniform1f(uTime, t);
    gl.uniform1f(uFade, fade);
    gl.uniform1f(uDpr, dpr);

    // Mouse in NDC
    if (mouse.active) {
      var mx = (mouse.x / w) * 2 - 1;
      var my = -((mouse.y / h) * 2 - 1);
      gl.uniform2f(uMouse, mx, my);
      gl.uniform1f(uMouseActive, 1.0);
    } else {
      gl.uniform1f(uMouseActive, 0.0);
    }

    gl.drawArrays(gl.POINTS, 0, particleCount);

    animId = requestAnimationFrame(draw);
  }

  // ─── Events ──────────────────────────────────────────────

  canvas.addEventListener('mousemove', function (e) {
    var rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
    mouse.active = true;
  });

  canvas.addEventListener('mouseleave', function () {
    mouse.active = false;
  });

  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resize, 100);
  });

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
      if (animId) cancelAnimationFrame(animId);
      animId = null;
    } else if (!animId && particleCount > 0) {
      animId = requestAnimationFrame(draw);
    }
  });

  // ─── Init ────────────────────────────────────────────────

  loadImage('/assets/christ-portrait.jpg', function (img) {
    resize();
    buildParticles(img);
    animId = requestAnimationFrame(draw);
  });

})();
