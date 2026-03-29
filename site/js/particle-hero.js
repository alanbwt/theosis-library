/**
 * Theosis Library — High-fidelity particle portrait
 * Pure WebGL (no Three.js) for maximum compatibility.
 * Full-color, brightness-mapped depth, soft particles, bloom-like glow.
 * Falls back to static image if WebGL unavailable.
 */

(function () {
  'use strict';

  var container = document.getElementById('particle-hero');
  if (!container) return;

  var IMAGES = [
    '/assets/christ-portrait.jpg',
    '/assets/timeline/gilgamesh-tablet.jpg',
    '/assets/timeline/book-of-dead.jpg',
    '/assets/timeline/codex-sinaiticus.jpg'
  ];

  var isMobile = window.innerWidth < 768;
  var SAMPLE_W = isMobile ? 250 : 500;
  var MAX_PARTICLES = isMobile ? 60000 : 200000;
  var MORPH_INTERVAL = 8000;
  var SPREAD = isMobile ? 120 : 200;
  var DEPTH = 30;

  // Try WebGL, fallback to static image
  var canvas = document.createElement('canvas');
  var gl = canvas.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false });

  if (!gl) {
    // Fallback: show a static image
    var img = document.createElement('img');
    img.src = IMAGES[0];
    img.alt = 'Ancient manuscripts';
    img.style.cssText = 'width:100%;height:100%;object-fit:cover;border-radius:12px;';
    container.appendChild(img);
    return;
  }

  canvas.style.cssText = 'width:100%;height:100%;display:block;border-radius:12px;';
  container.appendChild(canvas);

  // --- Shaders ---
  var VERT = [
    'attribute vec3 aPos;',
    'attribute vec3 aColor;',
    'attribute float aSize;',
    'attribute vec3 aTarget;',
    'attribute vec3 aTargetColor;',
    'attribute float aTargetSize;',
    'attribute float aRand;',
    '',
    'uniform float uTime;',
    'uniform float uMorph;',
    'uniform float uAspect;',
    'uniform float uScale;',
    '',
    'varying vec3 vColor;',
    'varying float vAlpha;',
    '',
    'void main() {',
    '  vec3 pos = mix(aPos, aTarget, uMorph);',
    '  vec3 col = mix(aColor, aTargetColor, uMorph);',
    '  float sz = mix(aSize, aTargetSize, uMorph);',
    '',
    '  // Breathing',
    '  float t = uTime * 0.4 + aRand * 6.28;',
    '  pos.x += sin(t) * 0.6;',
    '  pos.y += cos(t * 0.7 + 1.3) * 0.4;',
    '  pos.z += sin(t * 0.5 + 2.1) * 0.3;',
    '',
    '  // Simple perspective',
    '  float scale = 300.0 / (300.0 - pos.z);',
    '  vec2 screen = pos.xy * scale;',
    '  screen.x /= uAspect;',
    '',
    '  // Normalize to clip space',
    '  gl_Position = vec4(screen / 150.0, pos.z / 500.0, 1.0);',
    '  gl_PointSize = sz * scale * uScale;',
    '',
    '  vColor = col;',
    '  vAlpha = 0.7 + 0.3 * scale;',
    '}'
  ].join('\n');

  var FRAG = [
    'precision mediump float;',
    'varying vec3 vColor;',
    'varying float vAlpha;',
    '',
    'void main() {',
    '  vec2 c = gl_PointCoord - 0.5;',
    '  float d = length(c);',
    '  if (d > 0.5) discard;',
    '  float alpha = vAlpha * (1.0 - smoothstep(0.15, 0.5, d));',
    '  // Slight glow boost for brighter particles',
    '  float lum = dot(vColor, vec3(0.299, 0.587, 0.114));',
    '  vec3 glow = vColor + vColor * lum * 0.3;',
    '  gl_FragColor = vec4(glow, alpha);',
    '}'
  ].join('\n');

  function compileShader(src, type) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.error('Shader error:', gl.getShaderInfoLog(s));
      return null;
    }
    return s;
  }

  var vs = compileShader(VERT, gl.VERTEX_SHADER);
  var fs = compileShader(FRAG, gl.FRAGMENT_SHADER);
  if (!vs || !fs) return;

  var prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    console.error('Program error:', gl.getProgramInfoLog(prog));
    return;
  }
  gl.useProgram(prog);

  var aPos = gl.getAttribLocation(prog, 'aPos');
  var aColor = gl.getAttribLocation(prog, 'aColor');
  var aSize = gl.getAttribLocation(prog, 'aSize');
  var aTarget = gl.getAttribLocation(prog, 'aTarget');
  var aTargetColor = gl.getAttribLocation(prog, 'aTargetColor');
  var aTargetSize = gl.getAttribLocation(prog, 'aTargetSize');
  var aRand = gl.getAttribLocation(prog, 'aRand');
  var uTime = gl.getUniformLocation(prog, 'uTime');
  var uMorph = gl.getUniformLocation(prog, 'uMorph');
  var uAspect = gl.getUniformLocation(prog, 'uAspect');
  var uScale = gl.getUniformLocation(prog, 'uScale');

  // --- Image sampling ---
  var imageSets = [];
  var particleCount = 0;

  function sampleImage(img) {
    var sc = document.createElement('canvas');
    var sx = sc.getContext('2d');
    var aspect = img.height / img.width;
    var sw = SAMPLE_W;
    var sh = Math.round(sw * aspect);
    sc.width = sw;
    sc.height = sh;
    sx.drawImage(img, 0, 0, sw, sh);
    var data = sx.getImageData(0, 0, sw, sh).data;
    var imgAspect = sw / sh;

    var positions = [], colors = [], sizes = [];

    for (var y = 0; y < sh; y++) {
      for (var x = 0; x < sw; x++) {
        var i = (y * sw + x) * 4;
        var r = data[i] / 255, g = data[i+1] / 255, b = data[i+2] / 255;
        var bright = 0.299 * r + 0.587 * g + 0.114 * b;
        if (bright > 0.9) continue;

        var nx = ((x / sw) - 0.5) * SPREAD * imgAspect;
        var ny = -((y / sh) - 0.5) * SPREAD;
        var nz = (1.0 - bright) * DEPTH - DEPTH * 0.3;

        positions.push(nx, ny, nz);
        colors.push(r, g, b);
        sizes.push(1.0 + (1.0 - bright) * 2.0);
      }
    }

    return { positions: positions, colors: colors, sizes: sizes };
  }

  function normalize(ds, count) {
    var c = ds.positions.length / 3;
    while (ds.positions.length / 3 < count) {
      var idx = Math.floor(Math.random() * c);
      ds.positions.push(ds.positions[idx*3] + (Math.random()-0.5)*2, ds.positions[idx*3+1] + (Math.random()-0.5)*2, ds.positions[idx*3+2]);
      ds.colors.push(ds.colors[idx*3], ds.colors[idx*3+1], ds.colors[idx*3+2]);
      ds.sizes.push(ds.sizes[idx]);
    }
    ds.positions.length = count * 3;
    ds.colors.length = count * 3;
    ds.sizes.length = count;
  }

  // --- Buffers ---
  var posBuf, colorBuf, sizeBuf, targetBuf, targetColorBuf, targetSizeBuf, randBuf;

  function createBuffer(data, attr, size) {
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.DYNAMIC_DRAW);
    if (attr >= 0) {
      gl.enableVertexAttribArray(attr);
      gl.vertexAttribPointer(attr, size, gl.FLOAT, false, 0, 0);
    }
    return buf;
  }

  function updateBuffer(buf, data, attr, size) {
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.DYNAMIC_DRAW);
    if (attr >= 0) {
      gl.enableVertexAttribArray(attr);
      gl.vertexAttribPointer(attr, size, gl.FLOAT, false, 0, 0);
    }
  }

  function buildParticles() {
    var max = 0;
    imageSets.forEach(function(ds) { max = Math.max(max, ds.positions.length / 3); });
    particleCount = Math.min(max, MAX_PARTICLES);
    imageSets.forEach(function(ds) { normalize(ds, particleCount); });

    var first = imageSets[0];
    var second = imageSets[1 % imageSets.length];

    posBuf = createBuffer(first.positions, aPos, 3);
    colorBuf = createBuffer(first.colors, aColor, 3);
    sizeBuf = createBuffer(first.sizes, aSize, 1);
    targetBuf = createBuffer(second.positions, aTarget, 3);
    targetColorBuf = createBuffer(second.colors, aTargetColor, 3);
    targetSizeBuf = createBuffer(second.sizes, aTargetSize, 1);

    var randoms = new Float32Array(particleCount);
    for (var i = 0; i < particleCount; i++) randoms[i] = Math.random();
    randBuf = createBuffer(randoms, aRand, 1);
  }

  // --- State ---
  var currentIdx = 0;
  var morphProgress = 1.0;
  var lastMorphTime = 0;
  var animId = null;

  function setTarget(idx) {
    var ds = imageSets[idx];
    updateBuffer(targetBuf, ds.positions, aTarget, 3);
    updateBuffer(targetColorBuf, ds.colors, aTargetColor, 3);
    updateBuffer(targetSizeBuf, ds.sizes, aTargetSize, 1);
    morphProgress = 0;
  }

  function completeMorph() {
    var ds = imageSets[currentIdx];
    updateBuffer(posBuf, ds.positions, aPos, 3);
    updateBuffer(colorBuf, ds.colors, aColor, 3);
    updateBuffer(sizeBuf, ds.sizes, aSize, 1);
  }

  // --- Resize ---
  function resize() {
    var w = container.clientWidth;
    var h = container.clientHeight;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform1f(uAspect, w / h);
    gl.uniform1f(uScale, dpr * (isMobile ? 0.7 : 1.0));
  }

  // --- Render ---
  function draw(time) {
    var t = time * 0.001;
    gl.uniform1f(uTime, t);

    // Morph
    if (morphProgress < 1.0) {
      morphProgress = Math.min(morphProgress + 0.012, 1.0);
      var s = morphProgress * morphProgress * (3 - 2 * morphProgress);
      gl.uniform1f(uMorph, s);
      if (morphProgress >= 1.0) {
        completeMorph();
        gl.uniform1f(uMorph, 0);
      }
    }

    if (time - lastMorphTime > MORPH_INTERVAL && morphProgress >= 1.0) {
      currentIdx = (currentIdx + 1) % imageSets.length;
      setTarget(currentIdx);
      lastMorphTime = time;
    }

    // Clear to parchment
    gl.clearColor(0.957, 0.929, 0.894, 1.0); // #f4ede4
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

    gl.drawArrays(gl.POINTS, 0, particleCount);

    animId = requestAnimationFrame(draw);
  }

  // --- Init ---
  function loadImages(urls, cb) {
    var loaded = 0, imgs = [];
    urls.forEach(function(url, idx) {
      var img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = function() { imgs[idx] = img; loaded++; if (loaded === urls.length) cb(imgs); };
      img.onerror = function() { imgs[idx] = null; loaded++; if (loaded === urls.length) cb(imgs); };
      img.src = url;
    });
  }

  loadImages(IMAGES, function(imgs) {
    imgs.filter(Boolean).forEach(function(img) {
      imageSets.push(sampleImage(img));
    });
    if (!imageSets.length) return;

    resize();
    buildParticles();
    lastMorphTime = performance.now();
    animId = requestAnimationFrame(draw);
  });

  window.addEventListener('resize', function() {
    resize();
  });

  document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
      if (animId) cancelAnimationFrame(animId);
      animId = null;
    } else if (!animId && particleCount > 0) {
      lastMorphTime = performance.now();
      animId = requestAnimationFrame(draw);
    }
  });
})();
