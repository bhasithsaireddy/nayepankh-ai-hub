import sys

with open('frontend/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('#2E7D32', '#000000')

cursor_css = """
/* ── CURSOR TRAIL ── */
#cursor-trail {
  position: fixed;
  top: 0;
  left: 0;
  width: 32px;
  height: 32px;
  border: 2px solid rgba(0, 0, 0, 0.4);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  z-index: 9999;
  transition: transform 0.1s ease-out, width 0.2s ease, height 0.2s ease, border-color 0.2s ease;
}

body:hover #cursor-trail {
  opacity: 1;
}

/* Add a hover class for when the cursor is over interactive elements */
#cursor-trail.hovered {
  width: 48px;
  height: 48px;
  border-color: rgba(0, 0, 0, 0.8);
  background: rgba(0, 0, 0, 0.05);
}
"""

if '#cursor-trail' not in content:
    content += "\n" + cursor_css

with open('frontend/style.css', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated style.css')
