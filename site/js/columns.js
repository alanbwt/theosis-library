/**
 * Theosis Library — Crumbling ASCII Columns
 * Gibbon "Decline & Fall" inspired columns that crumble as you scroll.
 * Black background, white ASCII characters — matching hero art style.
 * Works on desktop AND mobile (thinner on mobile).
 * Columns rebuild when scrolling back up.
 */

(function () {
  'use strict';

  var isMobile = window.innerWidth < 768;
  var COL_W = isMobile ? 20 : 40; // px width
  var FONT = isMobile ? 5 : 7;    // px font size
  var CHARS_W = isMobile ? 4 : 6; // chars per line
  var LINE_H = FONT * 1.15;

  // Column components scaled by width
  function capital(w) {
    if (w <= 4) return [
      '.==.',
      '|{}|',
      '|::|',
      '+--+',
    ];
    return [
      '.====.',
      '|{~~}|',
      '|(||)|',
      '| || |',
      '|:||:|',
      '+====+',
    ];
  }

  function shaft(w) {
    if (w <= 4) return [
      '||||',
      '||| ',
      '||||',
      ' |||',
    ];
    return [
      '||||||',
      '||| ||',
      '||||||',
      '|| |||',
    ];
  }

  function rubble(w) {
    if (w <= 4) return [
      ' || ',
      '  | ',
      ' .  ',
      '  . ',
      '.  .',
      ' .. ',
    ];
    return [
      ' ||  |',
      '  | | ',
      ' |    ',
      '   .  ',
      ' .  . ',
      '  ..  ',
      '.   . ',
      '  .   ',
    ];
  }

  function base(w) {
    if (w <= 4) return [
      '.,.,',
      '====',
    ];
    return [
      '.,.,..',
      '.,;:,.',
      '======',
    ];
  }

  // Build column text for a given scroll fraction (0 = top, 1 = bottom)
  function buildColumn(scrollFrac, totalLines) {
    var w = CHARS_W;
    var cap = capital(w);
    var sh = shaft(w);
    var rub = rubble(w);
    var bas = base(w);

    var lines = [];

    // Capital always at top
    for (var i = 0; i < cap.length; i++) lines.push(cap[i]);

    var bodyLines = totalLines - cap.length - bas.length;
    if (bodyLines < 4) bodyLines = 4;

    // The "damage point" moves down as you scroll
    // scrollFrac 0 = fully intact, 1 = fully crumbled
    var intactLines = Math.floor(bodyLines * (1 - scrollFrac * 0.95));
    var crumbleLines = bodyLines - intactLines;

    // Intact shaft
    for (var j = 0; j < intactLines; j++) {
      var line = sh[j % sh.length];
      // Add slight weathering near the transition
      if (j > intactLines - 5 && scrollFrac > 0.1) {
        var arr = line.split('');
        for (var k = 0; k < arr.length; k++) {
          if (arr[k] === '|' && Math.random() < 0.15 * scrollFrac) arr[k] = ' ';
        }
        line = arr.join('');
      }
      lines.push(line);
    }

    // Crumbling zone — transition from shaft to rubble
    for (var m = 0; m < crumbleLines; m++) {
      var frac = m / Math.max(crumbleLines, 1); // 0 at crack, 1 at base
      if (frac < 0.3) {
        // Cracked shaft
        var sline = sh[m % sh.length].split('');
        for (var n = 0; n < sline.length; n++) {
          if (sline[n] === '|' && Math.random() < 0.3 + frac) sline[n] = ' ';
        }
        lines.push(sline.join(''));
      } else if (frac < 0.6) {
        // Breaking
        var bline = sh[m % sh.length].split('');
        for (var p = 0; p < bline.length; p++) {
          if (Math.random() < 0.5 + frac * 0.3) bline[p] = ' ';
          else if (bline[p] === '|' && Math.random() < 0.3) bline[p] = '.';
        }
        lines.push(bline.join(''));
      } else {
        // Rubble/dust
        lines.push(rub[m % rub.length]);
      }
    }

    // Base
    for (var b = 0; b < bas.length; b++) lines.push(bas[b]);

    return lines.join('\n');
  }

  function createColumn(side) {
    var wrap = document.createElement('div');
    wrap.className = 'ascii-col-wrap ascii-col-wrap--' + side;
    wrap.style.cssText = [
      'position: fixed',
      'top: 0',
      side + ': 0',
      'width: ' + COL_W + 'px',
      'height: 100vh',
      'z-index: 100',
      'pointer-events: none',
      'background: #0a0a0a',
      'overflow: hidden',
      'display: flex',
      'align-items: stretch',
    ].join(';');

    var pre = document.createElement('pre');
    pre.style.cssText = [
      'color: #c8b898',
      'font-family: "Courier New", Courier, monospace',
      'font-size: ' + FONT + 'px',
      'line-height: ' + LINE_H + 'px',
      'white-space: pre',
      'margin: 0',
      'padding: 0',
      'width: 100%',
      'text-align: center',
      'opacity: 0.7',
      side === 'right' ? 'transform: scaleX(-1)' : '',
    ].join(';');

    wrap.appendChild(pre);
    return { wrap: wrap, pre: pre };
  }

  var left = createColumn('left');
  var right = createColumn('right');
  document.body.appendChild(left.wrap);
  document.body.appendChild(right.wrap);

  var totalLines = Math.floor(window.innerHeight / LINE_H);

  function updateColumns() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var docHeight = Math.max(document.body.scrollHeight - window.innerHeight, 1);
    var scrollFrac = Math.min(scrollTop / docHeight, 1);

    var text = buildColumn(scrollFrac, totalLines);
    left.pre.textContent = text;
    right.pre.textContent = text;
  }

  // Initial render
  updateColumns();

  // Update on scroll with RAF throttling
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

  // Handle resize
  window.addEventListener('resize', function () {
    totalLines = Math.floor(window.innerHeight / LINE_H);
    updateColumns();
  });
})();
