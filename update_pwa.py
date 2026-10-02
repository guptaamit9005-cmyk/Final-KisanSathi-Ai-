import re

file_path = r'c:\Users\Amit kumar gupta\Downloads\AgriVisionAi-main\AgriVisionAi-main\templates\base.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add manifest
if '<link rel="manifest"' not in content:
    content = content.replace('<head>', '<head>\n    <link rel="manifest" href="/manifest.json">\n    <meta name="theme-color" content="#2c6b2f">')

# Add service worker registration
if 'navigator.serviceWorker.register' not in content:
    sw_script = '''<script>
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('ServiceWorker registration successful with scope: ', registration.scope);
                    })
                    .catch(err => {
                        console.log('ServiceWorker registration failed: ', err);
                    });
            });
        }
    </script>
</body>'''
    content = content.replace('</body>', sw_script)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated base.html with PWA tags")
