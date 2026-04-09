/**
 * Theosis Library — Crumbling Corinthian Columns
 * Inspired by Gibbon "Decline & Fall" book spines.
 * Capital intact at TOP. Base intact at BOTTOM.
 * Crumbling progresses from TOP DOWN as you scroll —
 * like the spines going from Vol. I (intact) to Vol. VII (ruins).
 * Scroll back up = column rebuilds.
 */

(function () {
  'use strict';

  if (window.innerWidth < 768) return;

  var isNarrow = window.innerWidth < 1024;
  var COL_W = isNarrow ? 48 : 68;
  var FONT = isNarrow ? 5.5 : 7;
  var LINE_H = FONT * 1.15;

  // ── CAPITAL (Ionic, always at very top) ──
  var CAP = [
    ' ╔════════════════╗ ',
    ' ║████████████████║ ',
    ' ╚════════════════╝ ',
    '╔══════════════════╗',
    '║  ╭(◎)════(◎)╮   ║',
    '║  │ ║║║║║║║║ │   ║',
    '║  ╰─╢║║║║║║╟─╯   ║',
    '╚════╧╧╧╧╧╧╧╧════╝',
    ' ╔════╤╤╤╤╤╤════╗  ',
    ' ║::::║║║║║║::::║  ',
    ' ╚════╧╧╧╧╧╧════╝  ',
  ];

  var CAP_SM = [
    ' ╔══════════╗ ',
    ' ║██████████║ ',
    ' ╚══════════╝ ',
    '╔════════════╗',
    '║ (◎)══(◎)  ║',
    '║  ║║║║║║   ║',
    '╚══╧╧╧╧╧╧══╝',
    ' ╔══╤╤╤╤══╗  ',
    ' ║::║║║║::║  ',
    ' ╚══╧╧╧╧══╝  ',
  ];

  // ── SHAFT variants (intact → crumbling) ──
  var S_INTACT = [
    ' ║ ║║║║║║║║║║ ║ ',
    ' ║ ║║║ ║║ ║║║ ║ ',
    ' ║ ║║║║║║║║║║ ║ ',
    ' ║ ║║ ║║║║ ║║ ║ ',
  ];

  // Cracks appear — jagged lines cutting across the fluting
  var S_CRACKED = [
    ' ║ ║║╲║║║╱║║║ ║ ',
    ' ║ ║║ ╲║╱ ║║║ ║ ',
    ' ║ ║║║╱║╲║║║║ ║ ',
    ' ║ ║╱║║║║║╲║║ ║ ',
  ];

  // Chunks missing — pieces of the column broken away
  var S_BROKEN = [
    ' ║ ║║  ║║  ║║ ║ ',
    ' ║  ║║ ║║ ║║  ║ ',
    '   ║║║ ║║ ║║║   ',
    ' ║  ║  ║║  ║  ║ ',
  ];

  // Major gaps — jagged top of remaining column
  var S_RUINED = [
    '   ║║  ║║  ║║    ',
    '    ║  ║║  ║     ',
    '   ║   ║║   ║    ',
    '    ║  ║    ║    ',
  ];

  // Stumps — barely anything left
  var S_STUMPS = [
    '       ║║        ',
    '    ║  ╎╎  ║     ',
    '       ╎╎        ',
    '    ╎  ╎╎  ╎     ',
  ];

  // Rubble/debris on the ground
  var S_RUBBLE = [
    '   ╎   ..   ╎    ',
    '     .    .       ',
    '  .    ..    .    ',
    '       .     .    ',
  ];

  // ── BASE (always at bottom, intact) ──
  var BASE = [
    ' ╔════╤╤╤╤╤╤════╗  ',
    ' ║::::║║║║║║::::║  ',
    ' ╚════╧╧╧╧╧╧════╝  ',
    '╔══════════════════╗',
    '║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║',
    '╚══════════════════╝',
    '╔══════════════════╗',
    '║██████████████████║',
    '╚══════════════════╝',
  ];

  var BASE_SM = [
    ' ╔══╤╤╤╤══╗  ',
    ' ║::║║║║::║  ',
    ' ╚══╧╧╧╧══╝  ',
    '╔════════════╗',
    '║▓▓▓▓▓▓▓▓▓▓▓║',
    '╚════════════╝',
  ];

  function buildColumn(scrollFrac, totalLines) {
    var cap = isNarrow ? CAP_SM : CAP;
    var bas = isNarrow ? BASE_SM : BASE;
    var lines = [];

    // Capital — crumbles from top as you scroll
    // At scrollFrac 0: full capital visible
    // At scrollFrac 1: capital mostly gone
    var capLinesToShow = Math.max(2, Math.round(cap.length * (1 - scrollFrac * 0.8)));

    // Show remaining capital lines (bottom portion stays longer)
    var capStart = cap.length - capLinesToShow;
    for (var i = capStart; i < cap.length; i++) {
      var line = cap[i];
      // Add damage to upper visible capital lines based on scroll
      if (i < capStart + 3 && scrollFrac > 0.2) {
        var arr = line.split('');
        for (var k = 0; k < arr.length; k++) {
          if (arr[k] !== ' ' && Math.random() < scrollFrac * 0.4) arr[k] = ' ';
        }
        line = arr.join('');
      }
      lines.push(line);
    }

    // Shaft body
    var bodyLines = totalLines - capLinesToShow - bas.length;
    if (bodyLines < 6) bodyLines = 6;

    // The damage zone extends from the TOP of the shaft downward
    // scrollFrac controls how far down the damage reaches
    var damageDepth = Math.floor(bodyLines * scrollFrac * 0.9);
    var intactStart = damageDepth;

    // DAMAGED zone (top of shaft, grows as you scroll)
    for (var d = 0; d < damageDepth; d++) {
      var depthFrac = d / Math.max(damageDepth, 1); // 0=near capital, 1=near intact
      var patterns, pat;

      if (depthFrac < 0.15) {
        // Near top: complete rubble
        patterns = S_RUBBLE;
      } else if (depthFrac < 0.3) {
        // Stumps
        patterns = S_STUMPS;
      } else if (depthFrac < 0.5) {
        // Major ruin
        patterns = S_RUINED;
      } else if (depthFrac < 0.7) {
        // Broken chunks
        patterns = S_BROKEN;
      } else {
        // Cracked — transition to intact
        patterns = S_CRACKED;
      }

      pat = patterns[d % patterns.length];
      // Extra randomization
      var arr2 = pat.split('');
      for (var n = 0; n < arr2.length; n++) {
        if (arr2[n] !== ' ' && Math.random() < (1 - depthFrac) * 0.15) arr2[n] = ' ';
      }
      lines.push(arr2.join(''));
    }

    // INTACT zone (bottom of shaft, shrinks as you scroll)
    var intactLines = bodyLines - damageDepth;
    for (var j = 0; j < intactLines; j++) {
      lines.push(S_INTACT[j % S_INTACT.length]);
    }

    // Base — always intact
    for (var b = 0; b < bas.length; b++) lines.push(bas[b]);

    return lines.join('\n');
  }

  function createColumn(side) {
    var wrap = document.createElement('div');
    wrap.style.cssText = [
      'position: fixed',
      'top: 0',
      side + ': 0',
      'width: ' + COL_W + 'px',
      'height: 100vh',
      'z-index: 100',
      'pointer-events: none',
      'background: #0c0a08',
      'overflow: hidden',
    ].join(';');

    var pre = document.createElement('pre');
    pre.style.cssText = [
      'color: #c4a858',
      'font-family: "Courier New", Courier, monospace',
      'font-size: ' + FONT + 'px',
      'line-height: ' + LINE_H + 'px',
      'white-space: pre',
      'margin: 0',
      'padding: 2px 0',
      'width: 100%',
      'text-align: center',
      'opacity: 0.9',
      side === 'right' ? 'transform: scaleX(-1)' : '',
    ].join(';');

    wrap.appendChild(pre);
    return { wrap: wrap, pre: pre };
  }

  var left = createColumn('left');
  var right = createColumn('right');
  document.body.appendChild(left.wrap);
  document.body.appendChild(right.wrap);

  document.body.style.paddingLeft = COL_W + 'px';
  document.body.style.paddingRight = COL_W + 'px';

  var totalLines = Math.floor(window.innerHeight / LINE_H);

  function update() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var docHeight = Math.max(document.body.scrollHeight - window.innerHeight, 1);
    var frac = Math.min(scrollTop / docHeight, 1);
    var text = buildColumn(frac, totalLines);
    left.pre.textContent = text;
    right.pre.textContent = text;
  }

  update();

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      requestAnimationFrame(function () { update(); ticking = false; });
      ticking = true;
    }
  });

  window.addEventListener('resize', function () {
    if (window.innerWidth < 768) {
      left.wrap.style.display = 'none';
      right.wrap.style.display = 'none';
      document.body.style.paddingLeft = '';
      document.body.style.paddingRight = '';
    } else {
      left.wrap.style.display = '';
      right.wrap.style.display = '';
      document.body.style.paddingLeft = COL_W + 'px';
      document.body.style.paddingRight = COL_W + 'px';
      totalLines = Math.floor(window.innerHeight / LINE_H);
      update();
    }
  });
})();
