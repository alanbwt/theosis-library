/**
 * Theosis Library — Crumbling Corinthian Columns
 * Inspired by the Gibbon "Decline & Fall" book spine columns.
 * ASCII art columns on left/right that progressively crumble as you scroll.
 * Capital intact at top → fragments and rubble at bottom.
 * Only on screens >= 1280px.
 */

(function () {
  'use strict';

  if (window.innerWidth < 1280) return;

  var COL_CHARS = 18; // width in characters
  var CHAR_H = 10;    // approx px per line at font-size 9px
  var COLOR = '#a09078';
  var OPACITY = 0.13;

  // Pristine Ionic/Corinthian capital (top)
  var CAPITAL = [
    '   .========.   ',
    '  /||||||||||\\  ',
    ' /||||||||||||\\  ',
    '|  .--====--. | ',
    '| /  (~~~~)  \\| ',
    '|/  (||||||)  \\',
    '|   (||||||)   |',
    '|    (||||)    |',
    '|     (||)     |',
    '|=====:||:=====|',
    '|:::::::::::::: |',
    '+==============+',
  ];

  // Shaft segments — intact, then progressively damaged
  var SHAFT_INTACT = [
    '| ||| ||| ||| |',
    '| ||| ||| ||| |',
    '| ||| ||| ||| |',
    '| ||| ||| ||| |',
  ];

  var SHAFT_WORN = [
    '| ||  ||| ||| |',
    '| ||| |||  || |',
    '| |||  || ||| |',
    '|  || ||| ||  |',
  ];

  var SHAFT_CRACKED = [
    '| ||   ||  || |',
    '|  ||  |  ||  |',
    '| |  \\  / ||  |',
    '|  |  \\/  |   |',
  ];

  var SHAFT_BREAKING = [
    '|  |    |  |  |',
    '   ||  |   |   ',
    '|  |   |  |   |',
    '   |  |    |   ',
  ];

  var SHAFT_CRUMBLED = [
    '   |    |      ',
    '      |    |   ',
    '  |       |    ',
    '      |        ',
  ];

  var SHAFT_RUBBLE = [
    '  .  ,    .    ',
    '    .   ,   .  ',
    ' ,    .    ,   ',
    '   .    ,      ',
  ];

  var SHAFT_DUST = [
    '  .         .  ',
    '       .       ',
    '  .            ',
    '            .  ',
  ];

  // Base — crumbled remains
  var BASE_RUBBLE = [
    '  .,. .,. .,.  ',
    ' .,:;:.,.:;:,. ',
    '.,;:;:;:;:;:;,.',
    '================',
  ];

  function buildColumn() {
    // Calculate how many lines we need
    var pageH = Math.max(document.body.scrollHeight, window.innerHeight);
    var totalLines = Math.floor(pageH / CHAR_H);

    var lines = [];

    // Capital (always intact)
    for (var i = 0; i < CAPITAL.length; i++) {
      lines.push(CAPITAL[i]);
    }

    var shaftLines = totalLines - CAPITAL.length - BASE_RUBBLE.length;
    if (shaftLines < 10) shaftLines = 10;

    // Divide shaft into zones
    var zone1 = Math.floor(shaftLines * 0.25); // intact
    var zone2 = Math.floor(shaftLines * 0.15); // worn
    var zone3 = Math.floor(shaftLines * 0.15); // cracked
    var zone4 = Math.floor(shaftLines * 0.15); // breaking
    var zone5 = Math.floor(shaftLines * 0.12); // crumbled
    var zone6 = Math.floor(shaftLines * 0.10); // rubble
    var zone7 = shaftLines - zone1 - zone2 - zone3 - zone4 - zone5 - zone6; // dust

    function addZone(pattern, count) {
      for (var j = 0; j < count; j++) {
        var line = pattern[j % pattern.length];
        // Add slight randomness to damaged zones
        if (pattern !== SHAFT_INTACT) {
          var arr = line.split('');
          for (var k = 0; k < arr.length; k++) {
            if (arr[k] === '|' && Math.random() < 0.08) arr[k] = ' ';
            if (arr[k] === ' ' && Math.random() < 0.02) arr[k] = '.';
          }
          line = arr.join('');
        }
        lines.push(line);
      }
    }

    addZone(SHAFT_INTACT, zone1);
    addZone(SHAFT_WORN, zone2);
    addZone(SHAFT_CRACKED, zone3);
    addZone(SHAFT_BREAKING, zone4);
    addZone(SHAFT_CRUMBLED, zone5);
    addZone(SHAFT_RUBBLE, zone6);
    addZone(SHAFT_DUST, zone7);

    // Base rubble
    for (var b = 0; b < BASE_RUBBLE.length; b++) {
      lines.push(BASE_RUBBLE[b]);
    }

    return lines.join('\n');
  }

  function createColumn(side) {
    var pre = document.createElement('pre');
    pre.className = 'ascii-column ascii-column--' + side;
    pre.textContent = buildColumn();

    pre.style.cssText = [
      'position: absolute',
      'top: 0',
      side + ': 0',
      'z-index: 1',
      'pointer-events: none',
      'color: ' + COLOR,
      'opacity: ' + OPACITY,
      'font-family: "Courier New", Courier, monospace',
      'font-size: 9px',
      'line-height: ' + CHAR_H + 'px',
      'white-space: pre',
      'overflow: hidden',
      'padding: 0',
      'margin: 0',
      'width: ' + (COL_CHARS * 5.4) + 'px',
      side === 'right' ? 'transform: scaleX(-1)' : '',
    ].join(';');

    return pre;
  }

  var left = createColumn('left');
  var right = createColumn('right');
  document.body.appendChild(left);
  document.body.appendChild(right);

  // Rebuild on significant page height changes (e.g. dynamic content)
  var lastHeight = document.body.scrollHeight;
  setInterval(function () {
    var h = document.body.scrollHeight;
    if (Math.abs(h - lastHeight) > 200) {
      lastHeight = h;
      left.textContent = buildColumn();
      right.textContent = buildColumn();
    }
  }, 3000);

  // Handle resize
  window.addEventListener('resize', function () {
    var show = window.innerWidth >= 1280;
    left.style.display = show ? '' : 'none';
    right.style.display = show ? '' : 'none';
  });
})();
