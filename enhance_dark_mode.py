import re

file_path = r'c:\Users\Amit kumar gupta\Downloads\AgriVisionAi-main\AgriVisionAi-main\templates\core\home.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Enhance transitions for navbar, cards, and step cards
content = content.replace('.navbar {\n    width: 100%;', '.navbar {\n    width: 100%;\n    transition: background 0.3s ease, border-color 0.3s ease;')
content = content.replace('.feature-card {\n    border: 1px solid rgba(0,0,0,0.05);\n    background: var(--card-bg);\n    border-radius: 24px;\n    padding: 25px;\n    transition: .25s ease;', 
                        '.feature-card {\n    border: 1px solid var(--border-color);\n    background: var(--card-bg);\n    border-radius: 24px;\n    padding: 25px;\n    transition: background 0.3s ease, transform 0.25s ease, box-shadow 0.25s ease, border-color 0.3s ease;')

# Ensure hero gradient transitions
content = content.replace('linear-gradient(180deg, var(--hero-gradient-1) 0%, var(--hero-gradient-2) 100%);', 
                        'linear-gradient(180deg, var(--hero-gradient-1) 0%, var(--hero-gradient-2) 100%);\n    transition: background 0.3s ease;')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Enhanced CSS transitions for dark mode")
