import re

file_path = r'c:\Users\Amit kumar gupta\Downloads\AgriVisionAi-main\AgriVisionAi-main\templates\core\home.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all occurrences of messed up font sizes with professional ones
content = re.sub(r'font-size:\s*21px;', 'font-size: 15px;', content)
content = re.sub(r'font-size:\s*23px;', 'font-size: 18px;', content)
content = re.sub(r'font-size:\s*22px;', 'font-size: 16px;', content)
content = re.sub(r'font-size:\s*26px;', 'font-size: 18px;', content)
content = re.sub(r'font-size:\s*24px;', 'font-size: 15px;', content)
content = re.sub(r'font-size:\s*25px;', 'font-size: 22px;', content)
content = re.sub(r'font-size:\s*28px;', 'font-size: 20px;', content)
content = re.sub(r'font-size:\s*20px;', 'font-size: 15px;', content)
content = re.sub(r'font-size:\s*19px;', 'font-size: 16px;', content)
content = re.sub(r'font-size:\s*43px;', 'font-size: 32px;', content)
content = re.sub(r'font-size:11.5px;', 'font-size: 12px;', content)

# We also need to fix padding and layout to be ultra premium
content = content.replace('background: white;', 'background: var(--card-bg);')
content = content.replace('border: 1px solid var(--border);', 'border: 1px solid rgba(0,0,0,0.05);')
content = content.replace('box-shadow: var(--shadow);', 'box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);')
content = content.replace('border-radius: 20px;', 'border-radius: 24px;')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated home UI")
