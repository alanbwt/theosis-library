/**
 * Theosis Library — Crumbling Corinthian Columns
 * Award-winning ASCII art columns that crumble as you scroll.
 * Wider, more detailed, unmistakably columns.
 * Black background with warm gold ASCII characters.
 */

(function () {
  'use strict';

  var isMobile = window.innerWidth < 768;
  if (isMobile) return; // Skip on mobile — too narrow to look good

  var isTablet = window.innerWidth < 1024;
  var COL_W = isTablet ? 50 : 72;
  var FONT = isTablet ? 6 : 7;
  var LINE_H = FONT * 1.15;

  // Detailed Ionic capital — unmistakably a column
  var CAPITAL = [
    '  ╔══════════════╗  ',
    '  ║██████████████║  ',
    '  ╚══════════════╝  ',
    ' ╔════════════════╗ ',
    ' ║  ╭──────────╮  ║ ',
    ' ║ ╭╯ (◎)  (◎) ╰╮ ║ ',
    ' ║ │  ╭──────╮  │ ║ ',
    ' ║ ╰╮ │||||||│ ╭╯ ║ ',
    ' ║  ╰─┤||||||├─╯  ║ ',
    ' ║    │||||||│    ║ ',
    ' ║    ╰──┬┬──╯    ║ ',
    ' ╚═══════╧╧═══════╝ ',
    '  ┌──────┤├──────┐  ',
    '  │::::::││::::::│  ',
    '  └──────┤├──────┘  ',
  ];

  // Narrower capital for tablet
  var CAPITAL_SM = [
    ' ╔══════════╗ ',
    ' ║██████████║ ',
    ' ╚══════════╝ ',
    '╔════════════╗',
    '║ ╭(◎)  (◎)╮ ║',
    '║ │ ││││││ │ ║',
    '║ ╰─┤││││├─╯ ║',
    '╚════╧╧╧╧════╝',
    ' ┌───┤├───┐ ',
    ' │:::││:::│ ',
    ' └───┤├───┘ ',
  ];

  var SHAFT = [
    '  │║│║│║││║│║│║│  ',
    '  │║│║│║││║│║│║│  ',
    '  │║│║│ ││ │║│║│  ',
    '  │║│║│║││║│║│║│  ',
  ];

  var SHAFT_SM = [
    ' │║│║││║│║│ ',
    ' │║│ ││ │║│ ',
    ' │║│║││║│║│ ',
    ' │║│║││║│║│ ',
  ];

  // Damaged variants
  var SHAFT_WORN = [
    '  │║│ │ ││ │ │║│  ',
    '  │║│║│ ││║│║│║│  ',
    '  │ │║│║││║│║│ │  ',
    '  │║│ │ ││ │║│║│  ',
  ];

  var SHAFT_CRACKED = [
    '  │ │  ╲││╱  │ │  ',
    '  │║│   ││   │║│  ',
    '  │ │  ╱││╲  │ │  ',
    '  │ │   ││   │ │  ',
  ];

  var SHAFT_BREAKING = [
    '  │ │   ╎╎   │    ',
    '     │  ╎╎  │     ',
    '  │     ╎╎    │   ',
    '    │   ╎╎   │    ',
  ];

  var SHAFT_RUBBLE = [
    '   ╎    ╎╎        ',
    '        ╎╎   ╎    ',
    '  ╎     ╎         ',
    '     ╎       ╎    ',
  ];

  var SHAFT_DUST = [
    '   ·    ·    ·    ',
    '      ·      ·    ',
    '  ·       ·       ',
    '        ·     ·   ',
  ];

  // Column base
  var BASE = [
    '  ┌──────┤├──────┐  ',
    '  │::::::││::::::│  ',
    '  └──────┤├──────┘  ',
    ' ╔═══════╤╤═══════╗ ',
    ' ║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║ ',
    ' ╚═══════════════╝  ',
    '╔══════════════════╗',
    '║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║',
    '╚══════════════════╝',
  ];

  var BASE_SM = [
    ' ┌───┤├───┐ ',
    ' │:::││:::│ ',
    ' └───┤├───┘ ',
    '╔════╤╤════╗',
    '║▓▓▓▓▓▓▓▓▓▓║',
    '╚══════════╝',
  ];

  function buildColumn(scrollFrac, totalLines) {
    var cap = isTablet ? CAPITAL_SM : CAPITAL;
    var sh = isTablet ? SHAFT_SM : SHAFT;
    var bas = isTablet ? BASE_SM : BASE;
    var lines = [];

    // Capital
    for (var i = 0; i < cap.length; i++) lines.push(cap[i]);

    var bodyLines = totalLines - cap.length - bas.length;
    if (bodyLines < 10) bodyLines = 10;

    var intactEnd = Math.floor(bodyLines * Math.max(0.05, 1 - scrollFrac * 0.95));
    var crumbleLines = bodyLines - intactEnd;

    // Intact shaft
    for (var j = 0; j < intactEnd; j++) {
      var line = sh[j % sh.length];
      // Slight wear near transition
      if (j > intactEnd - 4 && scrollFrac > 0.15) {
        var arr = line.split('');
        for (var k = 0; k < arr.length; k++) {
          if ((arr[k] === '║' || arr[k] === '│') && Math.random() < 0.12 * scrollFrac) arr[k] = ' ';
        }
        line = arr.join('');
      }
      lines.push(line);
    }

    // Crumbling zone
    for (var m = 0; m < crumbleLines; m++) {
      var frac = m / Math.max(crumbleLines, 1);
      var patterns = [SHAFT_WORN, SHAFT_CRACKED, SHAFT_BREAKING, SHAFT_RUBBLE, SHAFT_DUST];
      var idx = Math.min(Math.floor(frac * patterns.length), patterns.length - 1);
      var pattern = patterns[idx];
      var line2 = pattern[m % pattern.length];
      // Extra randomization
      var arr2 = line2.split('');
      for (var n = 0; n < arr2.length; n++) {
        if (arr2[n] !== ' ' && Math.random() < frac * 0.3) arr2[n] = ' ';
      }
      lines.push(arr2.join(''));
    }

    // Base
    for (var b = 0; b < bas.length; b++) lines.push(bas[b]);

    return lines.join('\n');
  }

  function createColumn(side) {
    var wrap = document.createElement('div');
    wrap.className = 'ascii-col-wrap ascii-col--' + side;
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
      'color: #b8a070',
      'font-family: "Courier New", Courier, monospace',
      'font-size: ' + FONT + 'px',
      'line-height: ' + LINE_H + 'px',
      'white-space: pre',
      'margin: 0',
      'padding: 2px 0',
      'width: 100%',
      'text-align: center',
      'opacity: 0.85',
      side === 'right' ? 'transform: scaleX(-1)' : '',
    ].join(';');

    wrap.appendChild(pre);
    return { wrap: wrap, pre: pre };
  }

  var left = createColumn('left');
  var right = createColumn('right');
  document.body.appendChild(left.wrap);
  document.body.appendChild(right.wrap);

  // Add body padding so content doesn't go under columns
  document.body.style.paddingLeft = COL_W + 'px';
  document.body.style.paddingRight = COL_W + 'px';

  var totalLines = Math.floor(window.innerHeight / LINE_H);

  function updateColumns() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var docHeight = Math.max(document.body.scrollHeight - window.innerHeight, 1);
    var scrollFrac = Math.min(scrollTop / docHeight, 1);
    var text = buildColumn(scrollFrac, totalLines);
    left.pre.textContent = text;
    right.pre.textContent = text;
  }

  updateColumns();

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      requestAnimationFrame(function () {
        updateColumns();
        ticking = false;
      });
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
      updateColumns();
    }
  });
})();
