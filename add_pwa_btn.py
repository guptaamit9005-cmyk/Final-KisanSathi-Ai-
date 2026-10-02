import re

file_path = r'c:\Users\Amit kumar gupta\Downloads\AgriVisionAi-main\AgriVisionAi-main\templates\core\home.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Download App Button to nav-actions
download_btn = '''<button id="pwa-install-btn" class="btn btn-outline" style="display: none; border-color: var(--primary); color: var(--primary); gap: 6px;"><svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Download App</button>
            <a href="/accounts/login/" class="btn btn-outline" data-i18n="nav_login">Login</a>'''

content = content.replace('<a href="/accounts/login/" class="btn btn-outline" data-i18n="nav_login">Login</a>', download_btn)

# Add Download App Button to Hero actions
hero_actions = '''<a href="/accounts/register/" class="btn btn-primary">
                    Explore KisanSathi <span>→</span>
                </a>

                <button id="pwa-install-btn-hero" class="btn btn-outline" style="display: none;">
                    <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Install Web App
                </button>

                <a href="/prediction/" class="btn btn-outline" id="scan-crop-btn">
                    <span>📷</span> Scan a Crop
                </a>'''
content = re.sub(r'<a href="/accounts/register/" class="btn btn-primary">.*?</a>\s*<a href="/prediction/" class="btn btn-outline">.*?</a>', hero_actions, content, flags=re.DOTALL)

# Add PWA installation Script at the end of body
pwa_script = '''
<!-- PWA INSTALL LOGIC -->
<script>
  let deferredPrompt;
  const installBtns = [document.getElementById('pwa-install-btn'), document.getElementById('pwa-install-btn-hero')];

  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;
    // Update UI to notify the user they can add to home screen
    installBtns.forEach(btn => {
        if(btn) btn.style.display = 'inline-flex';
    });
  });

  installBtns.forEach(btn => {
      if(!btn) return;
      btn.addEventListener('click', (e) => {
        // hide our user interface that shows our A2HS button
        installBtns.forEach(b => { if(b) b.style.display = 'none'; });
        if(deferredPrompt) {
            // Show the prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                  console.log('User accepted the A2HS prompt');
                } else {
                  console.log('User dismissed the A2HS prompt');
                }
                deferredPrompt = null;
            });
        }
      });
  });

  window.addEventListener('appinstalled', (evt) => {
    console.log('a2hs installed');
    installBtns.forEach(b => { if(b) b.style.display = 'none'; });
  });
</script>
'''

content = content.replace('</body>', pwa_script + '\n</body>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Added PWA install buttons and logic")
