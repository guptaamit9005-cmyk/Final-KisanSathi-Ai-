import re

file_path = r'c:\Users\Amit kumar gupta\Downloads\AgriVisionAi-main\AgriVisionAi-main\templates\core\home.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Reviews and Stats Section
reviews_section = '''
<!-- STATS -->
<section class="section stats" style="background: var(--primary); color: white; padding: 60px 0;">
    <div class="container" style="display: flex; justify-content: space-around; flex-wrap: wrap; text-align: center; gap: 30px;">
        <div>
            <div style="font-size: 48px; font-weight: 800; font-family: 'Outfit', sans-serif;">10k+</div>
            <div style="font-size: 16px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">Farmers Assisted</div>
        </div>
        <div>
            <div style="font-size: 48px; font-weight: 800; font-family: 'Outfit', sans-serif;">98%</div>
            <div style="font-size: 16px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">Detection Accuracy</div>
        </div>
        <div>
            <div style="font-size: 48px; font-weight: 800; font-family: 'Outfit', sans-serif;">50+</div>
            <div style="font-size: 16px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">Crops Supported</div>
        </div>
        <div>
            <div style="font-size: 48px; font-weight: 800; font-family: 'Outfit', sans-serif;">24/7</div>
            <div style="font-size: 16px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px;">AI Availability</div>
        </div>
    </div>
</section>

<!-- REVIEWS -->
<section class="section reviews" id="reviews" style="background: var(--bg-color);">
    <div class="container">
        <div class="section-heading">
            <div class="section-kicker">Testimonials</div>
            <h2>What Farmers Are Saying</h2>
            <p>Join thousands of farmers who are transforming their yields with KisanSathi AI.</p>
        </div>

        <div class="feature-grid">
            <article class="feature-card" style="display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="color: var(--accent); font-size: 20px; margin-bottom: 15px;">★★★★★</div>
                    <p style="font-size: 16px; font-style: italic; line-height: 1.8;">"This app has completely changed how I manage my crops. The AI disease detection spotted blight early enough for me to save my entire tomato harvest!"</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px; margin-top: 25px;">
                    <div style="width: 45px; height: 45px; border-radius: 50%; background: var(--feature-icon-bg); display: grid; place-items: center; font-weight: bold; color: var(--primary);">R</div>
                    <div>
                        <h4 style="font-size: 16px; margin: 0; color: var(--text-main);">Ramesh Kumar</h4>
                        <span style="font-size: 14px; color: var(--text-muted);">Vegetable Farmer</span>
                    </div>
                </div>
            </article>

            <article class="feature-card" style="display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="color: var(--accent); font-size: 20px; margin-bottom: 15px;">★★★★★</div>
                    <p style="font-size: 16px; font-style: italic; line-height: 1.8;">"The weather intelligence feature is incredible. It gave me a hyper-local forecast that helped me plan my irrigation perfectly, saving water and money."</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px; margin-top: 25px;">
                    <div style="width: 45px; height: 45px; border-radius: 50%; background: var(--feature-icon-bg); display: grid; place-items: center; font-weight: bold; color: var(--primary);">A</div>
                    <div>
                        <h4 style="font-size: 16px; margin: 0; color: var(--text-main);">Amit Sharma</h4>
                        <span style="font-size: 14px; color: var(--text-muted);">Wheat Farmer</span>
                    </div>
                </div>
            </article>

            <article class="feature-card" style="display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <div style="color: var(--accent); font-size: 20px; margin-bottom: 15px;">★★★★★</div>
                    <p style="font-size: 16px; font-style: italic; line-height: 1.8;">"I use the voice assistant daily. Being able to just speak into my phone and get immediate farming advice in Hindi is a game-changer for our community."</p>
                </div>
                <div style="display: flex; align-items: center; gap: 15px; margin-top: 25px;">
                    <div style="width: 45px; height: 45px; border-radius: 50%; background: var(--feature-icon-bg); display: grid; place-items: center; font-weight: bold; color: var(--primary);">S</div>
                    <div>
                        <h4 style="font-size: 16px; margin: 0; color: var(--text-main);">Suresh Patel</h4>
                        <span style="font-size: 14px; color: var(--text-muted);">Cotton Farmer</span>
                    </div>
                </div>
            </article>
        </div>
    </div>
</section>

<!-- CTA -->
'''

content = content.replace('<!-- CTA -->', reviews_section)

# Also let's make the nav-links update to point to reviews
content = content.replace('<a href="#how-it-works" data-i18n="nav_how_it_works">How It Works</a>', '<a href="#how-it-works" data-i18n="nav_how_it_works">How It Works</a>\n            <a href="#reviews">Reviews</a>')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Added Reviews and Stats")
