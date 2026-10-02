/**
 * KisanSathi AI — Multilingual i18n System
 * Supports: English (en), Hindi (hi), Bengali (bn), Marathi (mr), Telugu (te), Tamil (ta)
 */
(function () {
  "use strict";

  var LANG_META = {
    en: { name: "English",  nativeName: "English", voiceLang: "en-US", flag: "EN" },
    hi: { name: "Hindi",    nativeName: "Hindi",   voiceLang: "hi-IN", flag: "HI" },
    bn: { name: "Bengali",  nativeName: "Bangla",  voiceLang: "bn-IN", flag: "BN" },
    mr: { name: "Marathi",  nativeName: "Marathi", voiceLang: "mr-IN", flag: "MR" },
    te: { name: "Telugu",   nativeName: "Telugu",  voiceLang: "te-IN", flag: "TE" },
    ta: { name: "Tamil",    nativeName: "Tamil",   voiceLang: "ta-IN", flag: "TA" }
  };

  var LANG_NATIVE = {
    en: "English", hi: "Hindi", bn: "Bangla", mr: "Marathi", te: "Telugu", ta: "Tamil"
  };

  var TRANSLATIONS = {
    nav_dashboard:    {en:"Dashboard",        hi:"डैशबोर्ड",                  bn:"ড্যাশবোর্ড",                mr:"डॅशबोर्ड",                 te:"డ్యాష్‌బోర్డ్",             ta:"முகப்புப்பலகை"},
    nav_analyze_crop: {en:"Analyze Crop",     hi:"फसल जांचें",               bn:"ফসল বিশ্লেষণ",            mr:"पीक तपासा",               te:"పంట విశ్లేషణ",             ta:"பயிர் ஆய்வு"},
    nav_govt_schemes: {en:"Govt Schemes",     hi:"सरकारी योजनाएं",           bn:"সরকারি প্রকল্প",            mr:"शासकीय योजना",             te:"ప్రభుత్వ పథకాలు",          ta:"அரசு திட்டங்கள்"},
    nav_3d_learning:  {en:"3D Learning",      hi:"3D शिक्षण",                bn:"3D শিক্ষা",                mr:"3D शिक्षण",                te:"3D అభ్యాసం",              ta:"3D கல்வி"},
    nav_login:        {en:"Login",            hi:"लॉग इन",                   bn:"লগইন",                    mr:"लॉगिन",                   te:"లాగిన్",                  ta:"உள்நுழைக"},
    nav_register:     {en:"Register",         hi:"पंजीकरण",                  bn:"নিবন্ধন",                  mr:"नोंदणी",                   te:"నమోదు",                   ta:"பதிவு செய்க"},
    nav_logout:       {en:"Logout",           hi:"लॉग आउट",                  bn:"লগআউট",                   mr:"लॉगआउट",                  te:"లాగ్అవుట్",               ta:"வெளியேறு"},
    nav_expert_panel: {en:"Expert Panel",     hi:"विशेषज्ञ पैनल",             bn:"বিশেষজ্ঞ প্যানেল",          mr:"तज्ज्ञ पॅनेल",             te:"నిపుణుల ప్యానెల్",          ta:"நிபுணர் குழு"},
    nav_dark_mode:    {en:"Dark Mode",        hi:"डार्क मोड",                bn:"ডার্ক মোড",                mr:"डार्क मोड",                te:"డార్క్ మోడ్",              ta:"டார்க் மோட்"},
    select_language:  {en:"Language",         hi:"भाषा",                     bn:"ভাষা",                     mr:"भाषा",                    te:"భాష",                     ta:"மொழி"},
    voice_title:      {en:"Voice Assistant",  hi:"वॉइस असिस्टेंट",           bn:"ভয়েস সহায়ক",             mr:"व्हॉइस असिस्टंट",          te:"వాయిస్ అసిస్టెంట్",        ta:"குரல் உதவியாளர்"},
    voice_speak_all:  {en:"Listen Full Report",hi:"पूरी रिपोर्ट सुनें",         bn:"সম্পূর্ণ রিপোর্ট শুনুন",    mr:"संपूर्ण अहवाल ऐका",        te:"పూర్తి నివేదిక వినండి",    ta:"முழு அறிக்கை கேட்க"},
    voice_pause:      {en:"Pause",            hi:"रोकें",                     bn:"বিরতি",                    mr:"थांबवा",                  te:"తాత్కాలికంగా ఆపు",        ta:"இடைநிறுத்து"},
    voice_resume:     {en:"Resume",           hi:"फिर शुरू करें",            bn:"পুনরায় শুরু",             mr:"पुन्हा सुरू",              te:"మళ్లీ ప్రారంభించు",       ta:"மீண்டும் தொடங்கு"},
    voice_stop:       {en:"Stop",             hi:"बंद करें",                 bn:"বন্ধ করুন",                mr:"बंद करा",                 te:"ఆపివేయి",                 ta:"நிறுத்து"},
    voice_test:       {en:"Test Voice",       hi:"वॉइस टेस्ट",               bn:"ভয়েস টেস্ট",              mr:"आवाज चाचणी",              te:"వాయిస్ పరీక్ష",           ta:"குரல் சோதனை"},
    voice_ready:      {en:"Voice ready. Press button to listen.",hi:"वॉइस तैयार है। सुनने के लिए बटन दबाएं।",bn:"ভয়েস প্রস্তুত। শুনতে বোতাম টিপুন।",mr:"व्हॉइस तयार आहे. ऐकण्यासाठी बटण दाबा.",te:"వాయిస్ సిద్ధంగా ఉంది. వినడానికి బటన్ నొక్కండి.",ta:"குரல் தயார். கேட்க பொத்தானை அழுத்தவும்."},
    voice_speaking:   {en:"Speaking...",      hi:"सुनाया जा रहा है...",      bn:"বলা হচ্ছে...",             mr:"वाचत आहे...",             te:"మాట్లాడుతోంది...",          ta:"பேசுகிறது..."},
    voice_done:       {en:"Report complete.", hi:"रिपोर्ट पूरी हो गई।",       bn:"রিপোর্ট সম্পন্ন।",          mr:"अहवाल पूर्ण झाला.",        te:"నివేదిక పూర్తయింది.",     ta:"அறிக்கை முடிந்தது."},
    voice_paused:     {en:"Paused.",          hi:"रोक दिया गया।",            bn:"স্থগিত করা হয়েছে।",       mr:"थांबवले.",                te:"ఆపబడింది.",              ta:"இடைநிறுத்தப்பட்டது."},
    voice_stopped:    {en:"Stopped.",         hi:"बंद कर दिया गया।",         bn:"বন্ধ করা হয়েছে।",          mr:"बंद केले.",               te:"ఆపివేయబడింది.",           ta:"நிறுத்தப்பட்டது."},
    footer_text:      {en:"KisanSathi AI - Smart Agriculture Platform",hi:"किसान साथी AI - स्मार्ट कृषि मंच",bn:"কিষাণসাথী AI - স্মার্ট কৃষি প্ল্যাটফর্ম",mr:"किसानसाथी AI - स्मार्ट कृषी व्यासपीठ",te:"కిసాన్‌సాథీ AI - స్మార్ట్ వ్యవసాయ వేదిక",ta:"கிசான்சாதி AI - நவீன வேளாண் தளம்"},
    nav_features:     {en:"Features",         hi:"विशेषताएं",                 bn:"বৈশিষ্ট্যসমূহ",             mr:"वैशिष्ट्ये",               te:"ప్రత్యేకతలు",             ta:"அம்சங்கள்"},
    nav_how_it_works: {en:"How It Works",     hi:"यह कैसे काम करता है",       bn:"এটি কিভাবে কাজ করে",       mr:"हे कसे कार्य करते",        te:"ఇది ఎలా పనిచేస్తుంది",     ta:"எப்படி செயல்படுகிறது"},
    nav_weather:      {en:"Weather",          hi:"मौसम",                      bn:"আবহাওয়া",                  mr:"हवामान",                  te:"వాతావరణం",                 ta:"வானிலை"},
    nav_get_started:  {en:"Get Started ↗",    hi:"शुरू करें ↗",              bn:"শুরু করুন ↗",              mr:"सुरू करा ↗",              te:"ప్రారంభించండి ↗",          ta:"தொடங்குங்கள் ↗"},
    hero_eyebrow:     {en:"AI-POWERED SMART AGRICULTURE", hi:"एआई-संचालित स्मार्ट कृषि", bn:"এআই-চালিত স্মার্ট কৃষি", mr:"AI-आधारित स्मार्ट शेती", te:"AI-ఆధారిత స్మార్ట్ వ్యవసాయం", ta:"AI-ஆற்றல் வாய்ந்த நவீன விவசாயம்"},
    hero_title:       {en:"Your Farm. Your AI Partner.", hi:"आपका खेत। आपका एआई साथी।", bn:"আপনার খামার। আপনার এআই সঙ্গী।", mr:"आपली शेती. आपला AI साथीदार.", te:"మీ పొలం. మీ AI భాగస్వామి.", ta:"உங்கள் பண்ணை. உங்கள் AI கூட்டாளி."},
    hero_desc:        {en:"Detect crop issues, understand weather conditions, and access intelligent farming insights — all through one simple platform built for modern agriculture.", hi:"फसलों की बीमारियों की पहचान करें, मौसम को समझें और आधुनिक खेती के लिए स्मार्ट सुझाव प्राप्त करें — एक ही मंच पर।", bn:"ফসলের রোগ শনাক্ত করুন, আবহাওয়ার তথ্য জানুন এবং আধুনিক চাষাবাদের জন্য স্মার্ট পরামর্শ পান — এক সহজ প্ল্যাটফর্মে।", mr:"पिकांवरील रोग ओळखा, हवामानाची माहिती घ्या आणि एकाच प्लॅटफॉर्मवरून शेतीविषयक स्मार्ट सल्ले मिळवा.", te:"పంట తెగుళ్లను గుర్తించండి, వాతావరణ పరిస్థితులను తెలుసుకోండి మరియు ఆధునిక వ్యవసాయానికి అవసరమైన సమాచారాన్ని ఒకే వేదికపై పొందండి.", ta:"பயிர் நோய்களைக் கண்டறிந்து, வானிலை நிலவரங்களை அறிந்து, நவீன விவசாயத்திற்கான சிறந்த ஆலோசனைகளை ஒரே தளத்தில் பெறுங்கள்."},
    hero_btn_explore: {en:"Explore KisanSathi →", hi:"किसानसाथी देखें →",     bn:"কিষাণসাথী এক্সপ্লোর করুন →", mr:"किसानसाथी पहा →",         te:"కిసాన్‌సాథీని అన్వేషించండి →", ta:"கிசான்சாதியை அறிய →"},
    hero_btn_scan:    {en:"📷 Scan a Crop",   hi:"📷 फसल स्कैन करें",          bn:"📷 ফসল স্ক্যান করুন",      mr:"📷 पीक स्कॅन करा",         te:"📷 పంటను స్కాన్ చేయండి",   ta:"📷 பயிரை ஸ்கேன் செய்க"},
    nav_soil:         {en:"Soil",             hi:"मिट्टी",                    bn:"মাটি",                      mr:"माती",                    te:"నేల",                     ta:"மண்"},
    nav_market:       {en:"Market",           hi:"मंडी",                      bn:"বাজার",                    mr:"बाजार",                   te:"మార్కెట్",                 ta:"சந்தை"},
    nav_land:         {en:"Land",             hi:"भूमि",                      bn:"জমি",                      mr:"जमीन",                    te:"భూమి",                    ta:"நிலம்"},
    nav_equipment:    {en:"Equipment",        hi:"उपकरण",                     bn:"যন্ত্রপাতি",                mr:"यंत्रसामग्री",             te:"పరికరాలు",                ta:"உபகரணங்கள்"}
  };

  var STORAGE_KEY = "kisansathi-lang";
  var DEFAULT_LANG = "hi";

  function getCurrentLang() {
    try { var s = localStorage.getItem(STORAGE_KEY); if (s && LANG_META[s]) return s; } catch(e){}
    return DEFAULT_LANG;
  }

  function setLang(lang) {
    if (!LANG_META[lang]) return;
    try { localStorage.setItem(STORAGE_KEY, lang); } catch(e){}
    applyLang(lang);
    document.dispatchEvent(new CustomEvent("ks:langchange", { detail: { lang: lang } }));
  }

  function t(key, lang) {
    lang = lang || getCurrentLang();
    var group = TRANSLATIONS[key];
    if (!group) return key;
    return group[lang] || group["en"] || key;
  }

  function applyLang(lang) {
    lang = lang || getCurrentLang();
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach(function(el) {
      var key = el.getAttribute("data-i18n");
      var attr = el.getAttribute("data-i18n-attr");
      var translated = t(key, lang);
      if (attr) { el.setAttribute(attr, translated); } else { el.textContent = translated; }
    });
    document.querySelectorAll("[data-lang-btn]").forEach(function(btn) {
      btn.classList.toggle("lang-active", btn.getAttribute("data-lang-btn") === lang);
    });
    var disp = document.getElementById("currentLangDisplay");
    if (disp) { disp.textContent = LANG_NATIVE[lang] || lang; }
  }

  function getVoiceLang(lang) {
    lang = lang || getCurrentLang();
    return (LANG_META[lang] || LANG_META["hi"]).voiceLang;
  }

  function findVoice(lang) {
    var targetLang = getVoiceLang(lang);
    var voices = window.speechSynthesis ? window.speechSynthesis.getVoices() : [];
    return voices.find(function(v){ return v.lang.toLowerCase() === targetLang.toLowerCase(); }) ||
           voices.find(function(v){ return v.lang.toLowerCase().startsWith(targetLang.split("-")[0].toLowerCase()); }) || null;
  }

  function speak(text, lang, callbacks) {
    if (!window.speechSynthesis || !("SpeechSynthesisUtterance" in window)) return false;
    callbacks = callbacks || {};
    lang = lang || getCurrentLang();
    window.speechSynthesis.cancel();
    var utterance = new SpeechSynthesisUtterance(text);
    utterance.lang   = getVoiceLang(lang);
    utterance.rate   = 0.88;
    utterance.pitch  = 1.0;
    utterance.volume = 1.0;
    var voice = findVoice(lang);
    if (voice) utterance.voice = voice;
    if (callbacks.onstart) utterance.onstart = callbacks.onstart;
    if (callbacks.onend)   utterance.onend   = callbacks.onend;
    if (callbacks.onerror) utterance.onerror = callbacks.onerror;
    window.speechSynthesis.speak(utterance);
    return true;
  }

  function buildLangSelector() {
    var current = getCurrentLang();
    var opts = "";
    Object.keys(LANG_META).forEach(function(code) {
      var info = LANG_META[code];
      opts += '<button type="button" class="lang-opt-btn' + (code === current ? ' lang-active' : '') +
              '" data-lang-btn="' + code + '">' + info.flag + ' ' + LANG_NATIVE[code] + '</button>';
    });
    return '<div class="lang-selector" id="langSelector">' +
           '<button type="button" class="lang-trigger" id="langTrigger" aria-haspopup="true" aria-expanded="false">' +
           '<span id="currentLangDisplay">' + (LANG_NATIVE[current] || current) + '</span>' +
           '<span class="lang-arrow">&#9662;</span></button>' +
           '<div class="lang-dropdown" id="langDropdown">' +
           '<div class="lang-dropdown-header">Language</div>' + opts + '</div></div>';
  }

  function injectSelectorCSS() {
    if (document.getElementById("ks-lang-css")) return;
    var style = document.createElement("style");
    style.id = "ks-lang-css";
    style.textContent = [
      ".lang-selector{position:relative;display:inline-flex;align-items:center;}",
      ".lang-trigger{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;background:#f0fdf4;border:1.5px solid #16a34a;border-radius:10px;color:#15803d;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;transition:all .2s;box-shadow:0 1px 3px rgba(0,0,0,0.06);}",
      ".lang-trigger:hover{background:#dcfce7;border-color:#15803d;color:#14532d;transform:translateY(-1px);}",
      ".navbar .lang-trigger{background:rgba(22,163,74,0.12);color:#15803d;border-color:rgba(22,163,74,0.4);}",
      "nav.navbar .lang-trigger{background:rgba(255,255,255,0.18);color:#ffffff;border-color:rgba(255,255,255,0.4);}",
      ".lang-arrow{font-size:10px;transition:transform .2s;margin-left:2px;}",
      ".lang-selector.open .lang-arrow{transform:rotate(180deg);}",
      ".lang-dropdown{display:none;position:absolute;top:calc(100% + 8px);right:0;background:#fff;border:1px solid #d1e7d5;border-radius:14px;box-shadow:0 12px 32px rgba(22,101,52,.2);min-width:170px;z-index:9999;overflow:hidden;}",
      ".lang-selector.open .lang-dropdown{display:block;animation:langIn .15s ease;}",
      "@keyframes langIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}",
      ".lang-dropdown-header{padding:9px 14px 5px;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:#64748b;border-bottom:1px solid #f0f4f1;}",
      ".lang-opt-btn{display:block;width:100%;padding:9px 14px;text-align:left;background:none;border:none;cursor:pointer;font-size:13px;color:#172018;font-weight:600;transition:background .12s;}",
      ".lang-opt-btn:hover{background:#f0fdf4;color:#15803d;}",
      ".lang-opt-btn.lang-active{background:#dcfce7;color:#166534;font-weight:800;}",
      ".ks-voice-lang-select{padding:7px 12px;border:1px solid #d1e7d5;border-radius:9px;background:#fff;font-size:13px;font-weight:600;cursor:pointer;color:#166534;}"
    ].join("");
    document.head.appendChild(style);
  }

  function initNavSelector() {
    var ph = document.getElementById("ksLangSelectorPlaceholder");
    if (!ph) return;
    ph.innerHTML = buildLangSelector();
    var trigger  = document.getElementById("langTrigger");
    var selector = document.getElementById("langSelector");
    var dropdown = document.getElementById("langDropdown");
    if (!trigger || !selector || !dropdown) return;
    trigger.addEventListener("click", function(e) {
      e.stopPropagation();
      selector.classList.toggle("open");
      trigger.setAttribute("aria-expanded", selector.classList.contains("open"));
    });
    document.addEventListener("click", function() {
      selector.classList.remove("open");
      trigger.setAttribute("aria-expanded", "false");
    });
    dropdown.querySelectorAll("[data-lang-btn]").forEach(function(btn) {
      btn.addEventListener("click", function(e) {
        e.stopPropagation();
        setLang(btn.getAttribute("data-lang-btn"));
        selector.classList.remove("open");
        trigger.setAttribute("aria-expanded", "false");
      });
    });
  }

  function init() {
    injectSelectorCSS();
    initNavSelector();
    applyLang(getCurrentLang());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  var api = {
    t: t, setLang: setLang, getCurrentLang: getCurrentLang,
    getVoiceLang: getVoiceLang, findVoice: findVoice, speak: speak,
    applyLang: applyLang, LANG_META: LANG_META
  };
  window.KisanSathiI18n = api;
  window.KsI18n = api;
})();
