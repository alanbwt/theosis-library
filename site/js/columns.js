/**
 * Theosis Library — ASCII Art Corinthian Columns
 * Renders decorative columns as ASCII art on left/right viewport edges.
 * Matches the hero art aesthetic. Only on screens >= 1200px.
 */

(function () {
  'use strict';

  if (window.innerWidth < 1200) return;

  // ASCII column components
  var CAPITAL = [
    '    .:|||:.    ',
    '  .:|||||||||:. ',
    ' :{||||||||||||} ',
    ':{||||||||||||||} ',
    ':|||  |||||  |||}',
    ' {|| ||||| ||}  ',
    '  {||||||||||}  ',
    '   {|||||||||}  ',
    '   :{||||||}: ',
    '    :|||||:  ',
    '   .:|||||:.  ',
    '   :|||||||||: ',
    '  ============ ',
  ];

  var SHAFT = [
    '  |||||||||||  ',
    '  ||| ||| ||  ',
    '  |||||||||||  ',
    '  || ||| |||  ',
  ];

  var BASE = [
    '  ============ ',
    '   :|||||:   ',
    '  .::::::::.  ',
    ' .:||||||||||:. ',
    ' ============== ',
    '.:||||||||||||:.',
    '================',
    '||||||||||||||||',
    '================',
  ];

  function createColumn(side) {
    var col = document.createElement('pre');
    col.className = 'ascii-column ascii-column--' + side;
    
    // Build the full column
    var lines = [];
    
    // Capital at top
    for (var i = 0; i < CAPITAL.length; i++) {
      lines.push(CAPITAL[i]);
    }
    
    // Calculate shaft height to fill viewport
    // Approximate: each char line is ~14px at current font size
    var viewH = window.innerHeight;
    var capBaseH = (CAPITAL.length + BASE.length) * 14;
    var shaftLines = Math.max(20, Math.floor((viewH - capBaseH) / 14));
    
    for (var j = 0; j < shaftLines; j++) {
      lines.push(SHAFT[j % SHAFT.length]);
    }
    
    // Base at bottom
    for (var k = 0; k < BASE.length; k++) {
      lines.push(BASE[k]);
    }
    
    col.textContent = lines.join('\n');
    
    col.style.cssText = [
      'position: fixed',
      'top: 0',
      side + ': 0',
      'height: 100vh',
      'z-index: 50',
      'pointer-events: none',
      'color: #8a7e6f',
      'opacity: 0.08',
      'font-family: monospace',
      'font-size: 8px',
      'line-height: 1.0',
      'white-space: pre',
      'overflow: hidden',
      'padding: 0',
      'margin: 0',
      side === 'right' ? 'transform: scaleX(-1)' : '',
    ].join(';');
    
    return col;
  }

  document.body.appendChild(createColumn('left'));
  document.body.appendChild(createColumn('right'));

  // Handle resize
  window.addEventListener('resize', function () {
    var cols = document.querySelectorAll('.ascii-column');
    for (var i = 0; i < cols.length; i++) {
      cols[i].style.display = window.innerWidth >= 1200 ? '' : 'none';
    }
  });
})();
