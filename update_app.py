import sys

with open('frontend/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Chat bubbles colors
content = content.replace('background:#2E7D32; color:white;', 'background:#000000; color:white;')

# Chart.js colors
content = content.replace('backgroundColor: [\n          "#2E7D32", "#4CAF50", "#FF6F00", "#FFA000", "#81C784"\n        ]', 'backgroundColor: [\n          "#000000", "#333333", "#666666", "#999999", "#CCCCCC"\n        ]')
content = content.replace('backgroundColor: "#4CAF50"', 'backgroundColor: "#555555"')

# Confetti colors
content = content.replace("colors: ['#2E7D32', '#4CAF50', '#FF6F00', '#FFA000']", "colors: ['#000000', '#333333', '#888888', '#FFFFFF']")

# Cursor tracking logic
cursor_logic = """
// ─────────────────────────────────────────
// BLOCK 8 — CURSOR TRAIL
// ─────────────────────────────────────────
const cursorTrail = document.getElementById("cursor-trail");
if (cursorTrail) {
  let mouseX = 0, mouseY = 0;
  let trailX = 0, trailY = 0;

  window.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  // Add hover class when hovering over interactive elements
  const interactables = document.querySelectorAll('a, button, input, textarea');
  interactables.forEach(el => {
    el.addEventListener('mouseenter', () => cursorTrail.classList.add('hovered'));
    el.addEventListener('mouseleave', () => cursorTrail.classList.remove('hovered'));
  });

  function animateCursor() {
    // Smooth interpolation (easing)
    trailX += (mouseX - trailX) * 0.2;
    trailY += (mouseY - trailY) * 0.2;

    cursorTrail.style.transform = `translate(${trailX}px, ${trailY}px) translate(-50%, -50%)`;
    requestAnimationFrame(animateCursor);
  }
  animateCursor();
}
"""

if 'BLOCK 8 — CURSOR TRAIL' not in content:
    content += "\n" + cursor_logic

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated app.js')
