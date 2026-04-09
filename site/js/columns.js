/**
 * Theosis Library — Crumbling Corinthian Columns
 * Gibbon "Decline & Fall" style: column snaps off from the top.
 * At scroll=0: full column with capital.
 * As you scroll: capital vanishes, top becomes a jagged broken edge
 * that descends lower and lower. Base always intact.
 * Like Vols I→VII of the Gibbon spines.
 */

(function () {
  'use strict';

  if (window.innerWidth < 768) return;

  var isNarrow = window.innerWidth < 1024;
  var COL_W = isNarrow ? 48 : 68;
  var FONT = isNarrow ? 5.5 : 7;
  var LINE_H = FONT * 1.15;
  var GOLD = '#c4a858';

  // ── Full intact capital ──
  var CAP = [
    ' ╔════════════════╗ ',
    ' ║████████████████║ ',
    ' ╚══╤══════════╤══╝ ',
    '╔═══╧══════════╧═══╗',
    '║ ╭(◎)══════(◎)╮  ║',
    '║ │ ║║║║║║║║║║ │  ║',
    '║ ╰─╢║║║║║║║║╟─╯  ║',
    '╚═══╤╤╤╤╤╤╤╤╤╤═══╝',
    '  ╔═╧╧╧╧╧╧╧╧╧╧═╗  ',
    '  ║::║║║║║║║║::║  ',
    '  ╚═╤╤╤╤╤╤╤╤╤╤═╝  ',
  ];

  // ── Intact shaft line patterns ──
  var SHAFT = [
    '  ║ ║║║║║║║║║║ ║  ',
    '  ║ ║║║ ║║ ║║║ ║  ',
    '  ║ ║║║║║║║║║║ ║  ',
    '  ║ ║║ ║║║║ ║║ ║  ',
  ];

  // ── Jagged break edge patterns (the irregular top of a snapped column) ──
  // These represent the ragged broken-off top, read top-to-bottom
  var JAGGED_TOP = [
    '        .  ,       ',
    '    ,  .    . ,    ',
    '   ╎.  ╎  ╎  .╎   ',
    '   ╎║  ╎║ ║╎  ║   ',
    '  ╎║║╎ ║║ ║║ ╎║╎  ',
    '  ║║║║╎║║ ║║╎║║║  ',
    '  ║║║║║║║╎║║║║║║  ',
    '  ║ ║║║║║║║║║║ ║  ',
  ];

  // ── Base (always intact) ──
  var BASE = [
    '  ╔═╤╤╤╤╤╤╤╤╤╤═╗  ',
    '  ║::║║║║║║║║::║  ',
    '  ╚═╧╧╧╧╧╧╧╧╧╧═╝  ',
    '╔══════════════════╗',
    '║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║',
    '╚══════════════════╝',
    '╔══════════════════╗',
    '║██████████████████║',
    '╚══════════════════╝',
  ];

  function buildColumn(scrollFrac, totalLines) {
    var lines = [];
    var baseH = BASE.length;
    var bodyLines = totalLines - baseH;
    if (bodyLines < 10) bodyLines = 10;

    // How much of the column is destroyed (from top)
    // scrollFrac 0 = full column, 1 = only base + short stump
    var destroyedLines = Math.floor(bodyLines * scrollFrac * 0.85);
    var remainingBody = bodyLines - destroyedLines;

    // Fill destroyed zone with empty space (black background shows)
    for (var e = 0; e < destroyedLines; e++) {
      lines.push('                    ');
    }

    if (scrollFrac < 0.05) {
      // Nearly no scroll: show full capital + shaft
      // Undo empty lines
      lines = [];
      for (var ci = 0; ci < CAP.length; ci++) lines.push(CAP[ci]);
      var shaftCount = bodyLines - CAP.length;
      for (var si = 0; si < shaftCount; si++) {
        lines.push(SHAFT[si % SHAFT.length]);
      }
    } else {
      // Capital is gone. Show jagged broken top edge, then intact shaft below.
      // The jagged edge is ~6-8 lines of transition from rubble → intact

      var jaggedH = Math.min(JAGGED_TOP.length, remainingBody);
      for (var ji = 0; ji < jaggedH; ji++) {
        var jline = JAGGED_TOP[ji];
        // Extra randomization on the very top lines
        if (ji < 3) {
          var arr = jline.split('');
          for (var k = 0; k < arr.length; k++) {
            if (arr[k] !== ' ' && Math.random() < 0.3) arr[k] = ' ';
          }
          jline = arr.join('');
        }
        lines.push(jline);
      }

      // Intact shaft fills the rest
      var intactCount = remainingBody - jaggedH;
      for (var ii = 0; ii < intactCount; ii++) {
        lines.push(SHAFT[ii % SHAFT.length]);
      }
    }

    // Base always at bottom
    for (var b = 0; b < baseH; b++) lines.push(BASE[b]);

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
      'color: ' + GOLD,
      'font-family: "Courier New", Courier, monospace',
      'font-size: ' + FONT + 'px',
      'line-height: ' + LINE_H + 'px',
      'white-space: pre',
      'margin: 0',
      'padding: 0',
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
