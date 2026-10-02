import re

file_path = r'c:\Users\Amit kumar gupta\Downloads\AgriVisionAi-main\AgriVisionAi-main\templates\core\home.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CSS Variables to support dark mode
css_vars = '''
        :root {
            /* Light Theme Variables */
            --primary: #10b981;
            --primary-dark: #059669;
            --primary-light: #d1fae5;
            --secondary: #0f172a;
            --accent: #f59e0b;
            --bg-color: #fafafa;
            --card-bg: #ffffff;
            --text-main: #334155;
            --text-muted: #94a3b8;
            --border-color: rgba(0,0,0,0.05);
            --shadow-sm: 0 4px 20px rgba(0, 0, 0, 0.03);
            --shadow-md: 0 10px 40px -10px rgba(0,0,0,0.08);
            --green: var(--primary);
            --green-dark: var(--primary-dark);
            --green-light: var(--primary-light);
            --nav-bg: rgba(255,255,255,.92);
            --hero-gradient-1: #fbfdfb;
            --hero-gradient-2: #f3f9f3;
            --feature-icon-bg: #eaf7ed;
            --cta-bg: linear-gradient(120deg, #0d542e, #168044);
            --cta-text: white;
            --footer-bg: #103b24;
            --footer-text: #d3e6d8;
        }

        [data-theme="dark"] {
            /* Dark Theme Variables */
            --primary: #34d399;
            --primary-dark: #10b981;
            --primary-light: rgba(52, 211, 153, 0.15);
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #cbd5e1;
            --border-color: rgba(255,255,255,0.1);
            --shadow-sm: 0 4px 20px rgba(0, 0, 0, 0.2);
            --shadow-md: 0 10px 40px -10px rgba(0,0,0,0.3);
            --nav-bg: rgba(15, 23, 42, 0.92);
            --hero-gradient-1: #0f172a;
            --hero-gradient-2: #1e293b;
            --feature-icon-bg: rgba(52, 211, 153, 0.1);
            --cta-bg: linear-gradient(120deg, #064e3b, #065f46);
            --cta-text: #f8fafc;
            --footer-bg: #020617;
            --footer-text: #94a3b8;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            transition: background-color 0.3s ease, color 0.3s ease;
        }
'''
content = re.sub(r':root\s*\{[^}]+\}', css_vars, content, count=1)

# Replace specific hardcoded colors to use variables
content = content.replace('background: rgba(255,255,255,.92);', 'background: var(--nav-bg);')
content = content.replace('background: white;', 'background: var(--card-bg);')
content = content.replace('color: #123a24;', 'color: var(--text-main);')
content = content.replace('color: #63766a;', 'color: var(--text-muted);')
content = content.replace('color: #143c25;', 'color: var(--text-main);')
content = content.replace('color: #17452a;', 'color: var(--text-main);')
content = content.replace('linear-gradient(180deg, #fbfdfb 0%, #f3f9f3 100%)', 'linear-gradient(180deg, var(--hero-gradient-1) 0%, var(--hero-gradient-2) 100%)')
content = content.replace('background: var(--green-light);', 'background: var(--feature-icon-bg);')

# 2. Add Theme Toggle Button to nav-actions
theme_toggle = '''<button id="theme-toggle" class="btn btn-outline" style="padding: 10px; border-radius: 50%; width: 45px; height: 45px; display: grid; place-items: center; border-color: var(--border-color); color: var(--text-main);" aria-label="Toggle Dark Mode">
                <svg id="theme-icon-light" style="display: none; width: 20px; height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                <svg id="theme-icon-dark" style="display: block; width: 20px; height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>
            </button>'''

if 'id="theme-toggle"' not in content:
    content = content.replace('<div class="nav-actions">', f'<div class="nav-actions">\n            {theme_toggle}')

# 3. Add Theme Toggle JS logic
theme_script = '''
<!-- THEME TOGGLE LOGIC -->
<script>
    const themeToggleBtn = document.getElementById('theme-toggle');
    const iconLight = document.getElementById('theme-icon-light');
    const iconDark = document.getElementById('theme-icon-dark');
    
    // Check saved theme
    const savedTheme = localStorage.getItem('ks-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        iconLight.style.display = 'block';
        iconDark.style.display = 'none';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        iconLight.style.display = 'none';
        iconDark.style.display = 'block';
    }
    
    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        if (currentTheme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('ks-theme', 'light');
            iconLight.style.display = 'none';
            iconDark.style.display = 'block';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('ks-theme', 'dark');
            iconLight.style.display = 'block';
            iconDark.style.display = 'none';
        }
    });
</script>
'''
if 'id="theme-toggle"' in content and 'THEME TOGGLE LOGIC' not in content:
    content = content.replace('</body>', theme_script + '\n</body>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Added dark mode support and theme toggle")
