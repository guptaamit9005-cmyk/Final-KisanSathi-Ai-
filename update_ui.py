import re

def update_ui(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update root variables for clean light mode
    root_vars = '''
        :root {
            --primary: #10b981;
            --primary-dark: #059669;
            --primary-light: #d1fae5;
            --secondary: #0f172a;
            --accent: #f59e0b;
            --bg-color: #fafafa;
            --card-bg: #ffffff;
            --text-main: #334155;
            --text-muted: #94a3b8;
            --border-color: #f1f5f9;
            --shadow-sm: 0 4px 20px rgba(0, 0, 0, 0.03);
            --shadow-md: 0 10px 30px rgba(0, 0, 0, 0.05);
            --shadow-hover: 0 20px 40px rgba(16, 185, 129, 0.08);
            --radius-md: 16px;
            --radius-lg: 24px;
            --green: var(--primary);
            --green-dark: var(--primary-dark);
            --green-deep: #06472d;
            --green-soft: #ecfdf5;
            --green-light: #f0fdf4;
            --background: var(--bg-color);
            --white: #ffffff;
            --text: var(--text-main);
            --muted: var(--text-muted);
            --border: var(--border-color);
            --yellow: var(--accent);
            --yellow-soft: #fffbeb;
            --blue: #3b82f6;
            --blue-soft: #eff6ff;
            --orange: #f97316;
            --orange-soft: #fff7ed;
            --red: #ef4444;
            --red-soft: #fef2f2;
        }
    '''
    content = re.sub(r':root\s*\{.*?(?=\})\}', root_vars, content, flags=re.DOTALL)

    # 2. Upgrade font sizes (very small fonts -> legible, crisp)
    content = re.sub(r'font-size:\s*7px;', 'font-size: 11px;', content)
    content = re.sub(r'font-size:\s*8px;', 'font-size: 13px;', content)
    content = re.sub(r'font-size:\s*9px;', 'font-size: 14px;', content)
    content = re.sub(r'font-size:\s*10px;', 'font-size: 15px;', content)
    content = re.sub(r'font-size:\s*11px;', 'font-size: 16px;', content)
    content = re.sub(r'font-size:\s*12px;', 'font-size: 18px;', content)
    content = re.sub(r'font-size:\s*13px;', 'font-size: 20px;', content)
    content = re.sub(r'font-size:\s*14px;', 'font-size: 22px;', content)
    content = re.sub(r'font-size:\s*15px;', 'font-size: 24px;', content)
    content = re.sub(r'font-size:\s*16px;', 'font-size: 26px;', content)
    content = re.sub(r'font-size:\s*17px;', 'font-size: 28px;', content)

    # 3. Add global crisp typography rules
    content = content.replace('body {', 'body {\\n            letter-spacing: -0.01em;\\n            line-height: 1.6;\\n')
    
    # 4. Improve specific spacing
    content = re.sub(r'width: 215px;', 'width: 260px;', content) # wider sidebar
    content = re.sub(r'margin-left: 215px;', 'margin-left: 260px;', content)
    content = re.sub(r'calc\(100% - 215px\)', 'calc(100% - 260px)', content)
    
    # 5. Clean minimalist shadows for cards
    content = re.sub(r'box-shadow:\s*0\s+2px\s+10px\s+rgba.*?;\n', 'box-shadow: var(--shadow-sm);\\n', content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

import glob
for f in glob.glob('c:/Users/Amit kumar gupta/Downloads/AgriVisionAi-main/AgriVisionAi-main/templates/**/*.html', recursive=True):
    if 'core\\\\home.html' not in f and 'base.html' not in f:
        try:
            update_ui(f)
        except Exception as e:
            print(f"Failed on {f}: {e}")

