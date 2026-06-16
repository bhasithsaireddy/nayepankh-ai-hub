import sys
import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Tailwind script block removal
content = re.sub(r'<script>\s*tailwind\.config = \{.*?\n\s*\}\s*</script>', '', content, flags=re.DOTALL)

# Hex colors
content = content.replace('#2E7D32', '#000000')  # Main Green -> Black
content = content.replace('#4CAF50', '#FFFFFF')  # Light Green -> White
content = content.replace('#1B5E20', '#111111')  # Dark Green -> Dark Gray
content = content.replace('#388E3C', '#222222')  # Mid Green -> Gray
content = content.replace('#FF6F00', '#333333')  # Orange -> Dark Gray
content = content.replace('#FFD54F', '#CCCCCC')  # Yellow/Orange -> Light Gray

# Tailwind classes
content = content.replace('hover:text-green-700', 'hover:text-gray-900')
content = content.replace('hover:text-green-400', 'hover:text-white')
content = content.replace('hover:text-green-200', 'hover:text-gray-400')
content = content.replace('text-green-100', 'text-gray-300')
content = content.replace('text-green-200', 'text-gray-300')
content = content.replace('focus:ring-green-700', 'focus:ring-gray-900')

# Cursor trail element
if '<div id="cursor-trail"></div>' not in content:
    content = content.replace('<body class="bg-white text-gray-900 font-sans">', '<body class="bg-white text-gray-900 font-sans">\n<div id="cursor-trail"></div>')

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated index.html')
