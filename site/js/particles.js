/**
 * Theosis Library — 3D Particle Portrait
 * Three.js InstancedMesh + UnrealBloomPass for cinematic volumetric look.
 */

import * as THREE from 'https://esm.sh/three@0.170.0';
import { OrbitControls } from 'https://esm.sh/three@0.170.0/addons/controls/OrbitControls.js';
import { EffectComposer } from 'https://esm.sh/three@0.170.0/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'https://esm.sh/three@0.170.0/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'https://esm.sh/three@0.170.0/addons/postprocessing/UnrealBloomPass.js';

(function () {
  'use strict';

  var canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  // ─── Config ──────────────────────────────────────────────

  var CONFIG = {
    particleCount: 35000,
    particleSize: 0.12,
    spread: 28,
    depthScale: 6,
    bloomStrength: 1.4,
    bloomRadius: 0.5,
    bloomThreshold: 0,
    rotateSpeed: 0.3,
    hoverAmplitude: 0.04,
    lerpFactor: 0.08,
    fadeInDuration: 3500,
    cameraDistance: 55,
    fogDensity: 0.008
  };

  // ─── Scene setup ─────────────────────────────────────────

  var container = canvas.parentElement;
  var w = container.clientWidth;
  var h = container.clientHeight;
  var dpr = Math.min(window.devicePixelRatio, 2);

  var renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    alpha: false,
    powerPreference: 'high-performance'
  });
  renderer.setSize(w, h);
  renderer.setPixelRatio(dpr);
  renderer.setClearColor(0x0a0a0a, 1);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.2;

  var scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x0a0a0a, CONFIG.fogDensity);

  var camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 500);
  camera.position.set(0, 0, CONFIG.cameraDistance);

  var controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.autoRotate = true;
  controls.autoRotateSpeed = CONFIG.rotateSpeed;
  controls.enablePan = false;
  controls.minDistance = 25;
  controls.maxDistance = 90;

  // ─── Post-processing ────────────────────────────────────

  var composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));

  var bloomPass = new UnrealBloomPass(
    new THREE.Vector2(w, h),
    CONFIG.bloomStrength,
    CONFIG.bloomRadius,
    CONFIG.bloomThreshold
  );
  composer.addPass(bloomPass);

  // ─── Particle system ────────────────────────────────────

  var worldGroup = new THREE.Group();
  scene.add(worldGroup);

  var mesh = null;
  var dummy = new THREE.Object3D();
  var particleData = [];
  var startTime = 0;

  function sampleImage(img) {
    var sCanvas = document.createElement('canvas');
    var sCtx = sCanvas.getContext('2d');

    // Sample at high resolution for faithful reproduction
    var sW = 420;
    var sH = Math.round(sW * (img.height / img.width));
    sCanvas.width = sW;
    sCanvas.height = sH;
    sCtx.drawImage(img, 0, 0, sW, sH);

    var data = sCtx.getImageData(0, 0, sW, sH).data;
    var samples = [];

    for (var y = 0; y < sH; y++) {
      for (var x = 0; x < sW; x++) {
        var i = (y * sW + x) * 4;
        var r = data[i], g = data[i + 1], b = data[i + 2];
        var bright = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

        // Skip bright background
        if (bright > 0.78) continue;

        samples.push({
          x: x,
          y: y,
          brightness: bright,
          darkness: 1 - bright
        });
      }
    }

    // Randomly select particles, weighted toward darker areas
    var selected = [];
    var maxAttempts = CONFIG.particleCount * 4;
    var attempts = 0;

    while (selected.length < CONFIG.particleCount && attempts < maxAttempts) {
      var idx = Math.floor(Math.random() * samples.length);
      var s = samples[idx];
      // Darker pixels more likely to be selected
      if (Math.random() < s.darkness * s.darkness) {
        selected.push(s);
      }
      attempts++;
    }

    // Fill remaining if needed
    while (selected.length < CONFIG.particleCount) {
      selected.push(samples[Math.floor(Math.random() * samples.length)]);
    }

    return { samples: selected, width: sW, height: sH };
  }

  function buildParticles(img) {
    var result = sampleImage(img);
    var samples = result.samples;
    var sW = result.width;
    var sH = result.height;
    var aspect = sW / sH;

    // Geometry: small tetrahedron for faceted sparkle look
    var geo = new THREE.TetrahedronGeometry(CONFIG.particleSize, 0);
    var mat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      transparent: false
    });

    mesh = new THREE.InstancedMesh(geo, mat, CONFIG.particleCount);
    mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    mesh.instanceColor = new THREE.InstancedBufferAttribute(
      new Float32Array(CONFIG.particleCount * 3), 3
    );
    mesh.instanceColor.setUsage(THREE.DynamicDrawUsage);

    var color = new THREE.Color();

    for (var i = 0; i < CONFIG.particleCount; i++) {
      var s = samples[i];

      // Map to 3D centered coordinates
      var nx = (s.x / sW - 0.5) * CONFIG.spread * aspect;
      var ny = -(s.y / sH - 0.5) * CONFIG.spread;
      var nz = s.darkness * CONFIG.depthScale + (Math.random() - 0.5) * 0.5;

      // Slight positional jitter for organic feel
      nx += (Math.random() - 0.5) * 0.15;
      ny += (Math.random() - 0.5) * 0.15;

      // Warm monochrome: dark amber to pale gold based on brightness
      // Darker areas: warm amber (saturated), lighter areas: pale cream
      var hue = 0.08 + s.darkness * 0.02; // amber range
      var sat = 0.2 + s.darkness * 0.5;
      var lum = 0.4 + s.darkness * 0.45;
      color.setHSL(hue, sat, lum);

      particleData.push({
        targetX: nx,
        targetY: ny,
        targetZ: nz,
        currentX: nx + (Math.random() - 0.5) * 40,
        currentY: ny + (Math.random() - 0.5) * 40,
        currentZ: nz + (Math.random() - 0.5) * 40,
        seed: Math.random() * Math.PI * 2,
        speed: 0.5 + Math.random() * 0.5,
        scale: 0.6 + s.darkness * 0.8 + Math.random() * 0.3
      });

      // Set initial transform (will be overridden in animation)
      dummy.position.set(particleData[i].currentX, particleData[i].currentY, particleData[i].currentZ);
      dummy.scale.setScalar(particleData[i].scale);
      dummy.rotation.set(Math.random() * 6.28, Math.random() * 6.28, 0);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
      mesh.setColorAt(i, color);
    }

    mesh.instanceMatrix.needsUpdate = true;
    mesh.instanceColor.needsUpdate = true;

    worldGroup.add(mesh);
  }

  // ─── Animation loop ─────────────────────────────────────

  function animate(timestamp) {
    if (!startTime) startTime = timestamp;
    var elapsed = timestamp - startTime;
    var fade = Math.min(elapsed / CONFIG.fadeInDuration, 1);
    fade = fade * fade * (3 - 2 * fade); // smoothstep easing

    var time = timestamp * 0.001;

    if (mesh) {
      // Lerp factor increases during fade-in for dramatic assembly effect
      var currentLerp = CONFIG.lerpFactor * (0.3 + fade * 0.7);

      for (var i = 0; i < CONFIG.particleCount; i++) {
        var p = particleData[i];

        // Lerp toward target position
        p.currentX += (p.targetX - p.currentX) * currentLerp;
        p.currentY += (p.targetY - p.currentY) * currentLerp;
        p.currentZ += (p.targetZ - p.currentZ) * currentLerp;

        // Subtle hover animation once assembled
        var hover = Math.sin(time * p.speed + p.seed) * CONFIG.hoverAmplitude * fade;
        var hoverX = Math.cos(time * p.speed * 0.7 + p.seed * 1.3) * CONFIG.hoverAmplitude * 0.5 * fade;

        dummy.position.set(
          p.currentX + hoverX,
          p.currentY + hover,
          p.currentZ + Math.sin(time * 0.3 + p.seed * 2.1) * CONFIG.hoverAmplitude * 0.3 * fade
        );
        dummy.scale.setScalar(p.scale * (0.85 + Math.sin(time * 0.8 + p.seed) * 0.15));
        dummy.rotation.x = time * 0.1 + p.seed;
        dummy.rotation.y = time * 0.15 + p.seed * 0.5;
        dummy.updateMatrix();
        mesh.setMatrixAt(i, dummy.matrix);
      }
      mesh.instanceMatrix.needsUpdate = true;
    }

    controls.update();
    composer.render();
    requestAnimationFrame(animate);
  }

  // ─── Resize ──────────────────────────────────────────────

  function resize() {
    var cw = container.clientWidth;
    var ch = container.clientHeight;
    camera.aspect = cw / ch;
    camera.updateProjectionMatrix();
    renderer.setSize(cw, ch);
    composer.setSize(cw, ch);
    bloomPass.resolution.set(cw, ch);
  }

  window.addEventListener('resize', function () {
    resize();
  });

  // ─── Init ────────────────────────────────────────────────

  var img = new Image();
  img.crossOrigin = 'anonymous';
  img.onload = function () {
    buildParticles(img);
    requestAnimationFrame(animate);
  };
  img.src = '/assets/christ-portrait.jpg';

})();
