/**
 * KisanSathi AI — Karran AI Voice & RAG System
 * Features:
 * 1. Dual-Engine Voice Recorder (Native Web Speech API + High-Fidelity AudioContext WAV STT)
 * 2. Real-Time Speech Visualizer, Timer & Live Transcription Preview
 * 3. Text & Voice Response Output (Text-to-Speech with Indian Regional Voices & Auto-Speak)
 * 4. Markdown-to-Speech Sanitizer (Strips raw asterisks, symbols, code blocks for clear voice playback)
 * 5. Universal Integration across Floating Chatbot, Full-Page Assistant & Dashboard
 */

(function (window, document) {
  "use strict";

  // Configuration & Language Voice Metadata
  const VOICE_LANG_MAP = {
    hi: { code: "hi-IN", name: "Hindi", label: "हिंदी", speechHint: "बोलिए, हम सुन रहे हैं..." },
    en: { code: "en-IN", name: "English", label: "English", speechHint: "Speak now, listening..." },
    bn: { code: "bn-IN", name: "Bengali", label: "বাংলা", speechHint: "বলুন, আমরা শুনছি..." },
    mr: { code: "mr-IN", name: "Marathi", label: "मराठी", speechHint: "बोला, आम्ही ऐकत आहोत..." },
    te: { code: "te-IN", name: "Telugu", label: "తెలుగు", speechHint: "మాట్లాడండి, వింటున్నాము..." },
    ta: { code: "ta-IN", name: "Tamil", label: "தமிழ்", speechHint: "பேசுங்கள், கேட்கிறோம்..." }
  };

  // State
  let currentUtterance = null;
  let activeSpeakerBtn = null;
  let speechRate = 0.90; // Natural, clear pace for farmers
  let autoSpeakEnabled = true;

  // Recording State
  let activeRecorderMode = null; // 'webspeech' or 'audiocontext'
  let webSpeechRecognition = null;
  let audioCtx = null;
  let scriptNode = null;
  let sourceNode = null;
  let mediaStream = null;
  let pcmChunks = [];
  let recordingTimerInterval = null;
  let recordingSeconds = 0;
  let isCurrentlyRecording = false;

  /**
   * Cleans AI markdown text for smooth, natural Text-To-Speech pronunciation.
   * Removes asterisks, hashes, backticks, emojis, bullet symbols.
   */
  function cleanTextForSpeech(raw) {
    if (!raw) return "";
    let clean = raw
      // Remove headers like --- LIVE MANDI --- or ###
      .replace(/---.*?---/g, " ")
      .replace(/🌾\s*\*+.*?RAG.*?\*+/gi, " ")
      .replace(/💡[^\n]*/g, " ")
      .replace(/^#+\s+/gm, "")
      // Remove bold/italic markers
      .replace(/\*\*(.*?)\*\*/g, "$1")
      .replace(/\*(.*?)\*/g, "$1")
      .replace(/__(.*?)__/g, "$1")
      .replace(/_(.*?)_/g, "$1")
      // Conversational conversions for natural audio
      .replace(/Crop\/Fasal:\s*/gi, "फसल ")
      .replace(/Official MSP:\s*/gi, "सरकारी एमएसपी ")
      .replace(/Avg Market Price:\s*/gi, "औसत मंडी भाव ")
      .replace(/₹\s*(\d+)/g, "$1 रुपये")
      .replace(/\/(Quintal|Qtl)/gi, " प्रति क्विंटल")
      .replace(/\/\s*acre/gi, " प्रति एकड़")
      .replace(/(\d+)\s*%/g, "$1 प्रतिशत")
      .replace(/(\d+)\s*ml/gi, "$1 मिली")
      .replace(/(\d+)\s*gm/gi, "$1 ग्राम")
      .replace(/(\d+)\s*kg/gi, "$1 किलो")
      // Remove bullet symbols and numbers with dots
      .replace(/^[•\-\*]\s+/gm, "")
      // Remove markdown links [title](url) -> title
      .replace(/\[(.*?)\]\(.*?\)/g, "$1")
      // Remove backticks and code snippets
      .replace(/`{1,3}.*?`{1,3}/gs, "")
      // Remove emojis to avoid TTS pronouncing emoji names
      .replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, "")
      .replace(/[\|~`\^#<>]/g, " ")
      // Remove excessive newlines
      .replace(/\n+/g, ". ")
      // Clean duplicate spaces
      .replace(/\s+/g, " ")
      .trim();

    return clean;
  }

  /**
   * Find the best matching TTS voice for a given BCP-47 language tag.
   */
  function getBestVoice(voiceCode) {
    if (!window.speechSynthesis) return null;
    const voices = window.speechSynthesis.getVoices() || [];
    if (!voices.length) return null;

    const baseLang = voiceCode.split("-")[0].toLowerCase();

    // 1. Exact match (e.g. hi-IN)
    let found = voices.find(v => v.lang && v.lang.toLowerCase() === voiceCode.toLowerCase());
    if (found) return found;

    // 2. Base language match (e.g. hi)
    found = voices.find(v => v.lang && v.lang.toLowerCase().startsWith(baseLang));
    if (found) return found;

    // 3. Indian English match for en
    if (baseLang === "en") {
      found = voices.find(v => v.lang && (v.lang === "en-IN" || v.name.includes("India")));
      if (found) return found;
    }

    return null;
  }

  let currentAudio = null;

  /**
   * Play TTS Voice with dual-layer architecture:
   * 1. High-fidelity Server-side MP3 Audio Stream (/karran/tts/) -> 100% natural Indian pronunciation across all devices.
   * 2. Fallback to Browser SpeechSynthesis with sentence chunking if offline.
   */
  function speakText(text, voiceCode, onStartOrOptions, onEnd, onError) {
    let cbStart = onStartOrOptions;
    let cbEnd = onEnd;
    let cbError = onError;
    let explicitTtsUrl = null;

    if (onStartOrOptions && typeof onStartOrOptions === "object") {
      cbStart = onStartOrOptions.onStart;
      cbEnd = onStartOrOptions.onEnd;
      cbError = onStartOrOptions.onError;
      explicitTtsUrl = onStartOrOptions.ttsUrl || null;
    }

    // Cancel any ongoing speech or audio
    stopSpeaking();

    const spokenText = cleanTextForSpeech(text);
    if (!spokenText) {
      if (cbEnd) cbEnd();
      return;
    }

    // Take concise advisory content for voice (up to ~240 chars)
    let speechSnippet = spokenText;
    if (speechSnippet.length > 240) {
      const parts = speechSnippet.substring(0, 240).split(/[।\.!\?]/);
      if (parts.length > 1) {
        parts.pop();
        speechSnippet = parts.join("। ") + "।";
      } else {
        speechSnippet = speechSnippet.substring(0, 230) + "।";
      }
    }

    const lang = (voiceCode || "hi").split("-")[0].toLowerCase();
    const audioUrl = explicitTtsUrl || `/karran/tts/?lang=${encodeURIComponent(lang)}&text=${encodeURIComponent(speechSnippet)}`;

    // 1. Primary: Server-side Google TTS MP3 stream (guaranteed to work on Windows & Mobile)
    try {
      const audio = new Audio();
      audio.preload = "auto";
      currentAudio = audio;

      let started = false;
      let ended = false;

      const triggerStart = () => {
        if (!started) {
          started = true;
          if (cbStart) cbStart();
        }
      };

      const triggerEnd = () => {
        if (!ended) {
          ended = true;
          currentAudio = null;
          if (cbEnd) cbEnd();
        }
      };

      audio.onplay = triggerStart;
      audio.onplaying = triggerStart;
      audio.onended = triggerEnd;
      audio.onerror = (e) => {
        console.warn("Server TTS audio stream failed, falling back to browser speechSynthesis:", e);
        if (!started) {
          currentAudio = null;
          fallbackBrowserTTS(speechSnippet, voiceCode, cbStart, cbEnd, cbError);
        } else {
          triggerEnd();
        }
      };

      audio.src = audioUrl;
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.then(() => {
          triggerStart();
        }).catch((err) => {
          console.warn("Audio play prevented or failed, trying browser speechSynthesis:", err);
          if (!started) {
            currentAudio = null;
            fallbackBrowserTTS(speechSnippet, voiceCode, cbStart, cbEnd, cbError);
          }
        });
      }
      return;
    } catch (e) {
      console.warn("Failed creating Audio element, falling back:", e);
      fallbackBrowserTTS(speechSnippet, voiceCode, cbStart, cbEnd, cbError);
    }
  }

  /**
   * Browser SpeechSynthesis Fallback with sentence chunking & keepalive
   */
  function fallbackBrowserTTS(spokenText, voiceCode, cbStart, cbEnd, cbError) {
    if (!window.speechSynthesis) {
      if (cbError) cbError("Speech synthesis not supported.");
      return;
    }

    try {
      window.speechSynthesis.cancel();
    } catch (e) {}

    // Chunk text to prevent Chrome cutoff bug
    const chunks = spokenText.match(/[^.!?।\n]+[.!?।\n]+/g) || [spokenText];
    let currentChunkIndex = 0;
    
    let voice = getBestVoice(voiceCode || "hi-IN");
    if (!voice) {
      const allVoices = window.speechSynthesis.getVoices() || [];
      if (allVoices.length > 0) {
        voice = allVoices.find(v => v.lang && (v.lang.includes("IN") || v.lang.startsWith("hi"))) 
             || allVoices.find(v => v.lang && v.lang.startsWith("en")) 
             || allVoices[0];
      }
    }

    function speakNextChunk() {
        if (currentChunkIndex >= chunks.length) {
            currentUtterance = null;
            if (cbEnd) cbEnd();
            return;
        }

        const utter = new SpeechSynthesisUtterance(chunks[currentChunkIndex].trim());
        utter.lang = voiceCode || "hi-IN";
        utter.rate = speechRate || 0.95;
        utter.pitch = 1.0;
        if (voice) utter.voice = voice;

        utter.onstart = () => {
            currentUtterance = utter;
            if (currentChunkIndex === 0 && cbStart) cbStart();
        };

        utter.onend = () => {
            currentChunkIndex++;
            speakNextChunk();
        };

        utter.onerror = (e) => {
            currentUtterance = null;
            if (cbError) cbError(e);
        };

        window.speechSynthesis.speak(utter);
    }

    speakNextChunk();
  }

  function stopSpeaking() {
    if (currentAudio) {
      try {
        currentAudio.pause();
        currentAudio.currentTime = 0;
      } catch (e) {}
      currentAudio = null;
    }
    if (window.speechSynthesis) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
      currentUtterance = null;
    }
  }

  function pauseSpeaking() {
    if (currentAudio && !currentAudio.paused) {
      currentAudio.pause();
    } else if (window.speechSynthesis && window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
    }
  }

  function resumeSpeaking() {
    if (currentAudio && currentAudio.paused) {
      currentAudio.play();
    } else if (window.speechSynthesis && window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
  }

  function isSpeaking() {
    const audioPlaying = currentAudio && !currentAudio.paused && !currentAudio.ended && currentAudio.currentTime > 0;
    const synthSpeaking = window.speechSynthesis && (window.speechSynthesis.speaking || window.speechSynthesis.pending);
    return Boolean(audioPlaying || synthSpeaking);
  }

  /**
   * Encode Float32Array PCM samples into standard 16-bit PCM WAV Blob.
   */
  function encodeWAV(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    function writeString(offset, string) {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    }

    writeString(0, "RIFF");
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(8, "WAVE");
    writeString(12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // PCM format
    view.setUint16(22, 1, true); // Mono channel
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true);
    view.setUint16(32, 2, true); // Block align
    view.setUint16(34, 16, true); // 16-bit
    writeString(36, "data");
    view.setUint32(40, samples.length * 2, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    return new Blob([view], { type: "audio/wav" });
  }

  let currentRecordingOptions = null;
  let latestLiveTranscript = "";

  /**
   * Start Voice Recording:
   * 1. Direct hardware microphone capture via getUserMedia.
   * 2. Live PCM AudioContext recording (guaranteed to capture WAV audio).
   * 3. Parallel Web Speech API for instant live text streaming.
   * 4. Zero-fail fallback: if Web Speech doesn't produce text, server STT transcribes the WAV audio.
   */
  async function startRecording(options = {}) {
    if (isCurrentlyRecording) {
      await stopRecording();
    }

    // Stop any ongoing TTS playback
    stopSpeaking();

    currentRecordingOptions = options;
    latestLiveTranscript = "";
    pcmChunks = [];
    recordingSeconds = 0;
    isCurrentlyRecording = true;

    const lang = options.lang || "hi";
    const langCode = (VOICE_LANG_MAP[lang] && VOICE_LANG_MAP[lang].code) ? VOICE_LANG_MAP[lang].code : "hi-IN";

    // 1. Verify getUserMedia support
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      isCurrentlyRecording = false;
      if (options.onError) {
        options.onError("इस ब्राउज़र में माइक्रोफोन सपोर्ट उपलब्ध नहीं है।");
      }
      return;
    }

    // 2. Request microphone stream
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
    } catch (permErr) {
      isCurrentlyRecording = false;
      if (options.onError) {
        if (permErr.name === "NotAllowedError" || permErr.name === "PermissionDeniedError") {
          options.onError("माइक्रोफोन की अनुमति नहीं मिली। कृपया ब्राउज़र में Mic 'Allow' करें।");
        } else {
          options.onError("माइक एक्सेस नहीं हो सका: " + (permErr.message || permErr.name));
        }
      }
      return;
    }

    // 3. Setup AudioContext PCM recording
    try {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContextClass();
      if (audioCtx.state === "suspended") {
        await audioCtx.resume();
      }

      sourceNode = audioCtx.createMediaStreamSource(mediaStream);
      scriptNode = audioCtx.createScriptProcessor(4096, 1, 1);

      scriptNode.onaudioprocess = (e) => {
        if (!isCurrentlyRecording) return;
        const input = e.inputBuffer.getChannelData(0);
        const chunk = new Float32Array(input.length);
        chunk.set(input);
        pcmChunks.push(chunk);

        // Compute volume for visualizer
        if (options.onVolume) {
          let sum = 0;
          for (let i = 0; i < input.length; i++) sum += input[i] * input[i];
          const rms = Math.sqrt(sum / input.length);
          options.onVolume(Math.min(1, rms * 4));
        }
      };

      sourceNode.connect(scriptNode);
      scriptNode.connect(audioCtx.destination);
    } catch (audioErr) {
      console.warn("AudioContext setup warning:", audioErr);
    }

    // 4. In parallel, run Web Speech API if supported
    const SpeechRecClass = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecClass) {
      try {
        const recognition = new SpeechRecClass();
        recognition.lang = langCode;
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;

        recognition.onresult = (event) => {
          let interim = "";
          let final = "";
          for (let i = 0; i < event.results.length; ++i) {
            const piece = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              final += (final ? " " : "") + piece;
            } else {
              interim += piece;
            }
          }
          const full = (final + " " + interim).trim();
          if (full) {
            latestLiveTranscript = full;
            if (options.onInterimText) {
              options.onInterimText(full);
            }
          }
        };

        recognition.onerror = (e) => {
          // Log notice but do NOT kill recording - AudioContext is actively buffering WAV!
          console.warn("Interim speech recognition notice:", e.error);
        };

        recognition.onend = () => {
          // If still recording and recognition stopped prematurely, do not abort AudioContext
        };

        webSpeechRecognition = recognition;
        recognition.start();
      } catch (wsErr) {
        console.warn("WebSpeech recognition unavailable:", wsErr);
      }
    }

    // 5. Notify UI of successful start
    if (options.onStart) {
      options.onStart({ mode: "active" });
    }

    // 6. Start timer (auto-stop after 16s)
    recordingTimerInterval = setInterval(() => {
      recordingSeconds++;
      if (options.onProgress) {
        options.onProgress(recordingSeconds);
      }
      if (recordingSeconds >= 16) {
        stopRecording();
      }
    }, 1000);
  }

  function cleanupRecordingState() {
    isCurrentlyRecording = false;
    if (recordingTimerInterval) {
      clearInterval(recordingTimerInterval);
      recordingTimerInterval = null;
    }
    if (webSpeechRecognition) {
      try { webSpeechRecognition.stop(); } catch (e) {}
      webSpeechRecognition = null;
    }
    if (scriptNode) {
      try { scriptNode.disconnect(); } catch (e) {}
      scriptNode = null;
    }
    if (sourceNode) {
      try { sourceNode.disconnect(); } catch (e) {}
      sourceNode = null;
    }
    if (mediaStream) {
      try { mediaStream.getTracks().forEach((t) => t.stop()); } catch (e) {}
      mediaStream = null;
    }
    if (audioCtx && audioCtx.state !== "closed") {
      try { audioCtx.close(); } catch (e) {}
      audioCtx = null;
    }
  }

  /**
   * Stop Recording and Return Transcribed Speech.
   * Priority 1: Instant Web Speech text if recognized.
   * Priority 2: AudioContext WAV encoded & processed via /karran/speech/ endpoint.
   */
  async function stopRecording(additionalCallbacks = {}) {
    if (!isCurrentlyRecording && pcmChunks.length === 0) return;

    const opts = Object.assign({}, currentRecordingOptions, additionalCallbacks);
    const textFromLive = latestLiveTranscript ? latestLiveTranscript.trim() : "";
    const chunks = pcmChunks.slice();
    const sampleRate = (audioCtx && audioCtx.sampleRate) ? audioCtx.sampleRate : 16000;

    cleanupRecordingState();

    // 1. If WebSpeech captured text cleanly, use it immediately
    if (textFromLive && textFromLive.length >= 2) {
      if (opts.onComplete) {
        opts.onComplete({
          success: true,
          text: textFromLive,
          lang: opts.lang || "hi",
          engine: "live_speech"
        });
      }
      currentRecordingOptions = null;
      return;
    }

    // 2. Fallback to Server STT with captured WAV audio
    let totalLength = 0;
    for (let i = 0; i < chunks.length; i++) totalLength += chunks[i].length;

    if (totalLength < 1600) {
      if (opts.onError) {
        opts.onError("ऑडियो बहुत छोटा था। कृपया कम से कम 1-2 सेकंड बोलें।");
      }
      currentRecordingOptions = null;
      return;
    }

    const merged = new Float32Array(totalLength);
    let offset = 0;
    for (let i = 0; i < chunks.length; i++) {
      merged.set(chunks[i], offset);
      offset += chunks[i].length;
    }

    const wavBlob = encodeWAV(merged, sampleRate);
    if (wavBlob.size < 800) {
      if (opts.onError) {
        opts.onError("ऑडियो बहुत छोटा था।");
      }
      currentRecordingOptions = null;
      return;
    }

    if (opts.onProcessing) {
      opts.onProcessing("🔄 आवाज पहचानी जा रही है...");
    }

    const formData = new FormData();
    formData.append("audio", wavBlob, "recording.wav");
    formData.append("lang", opts.lang || "hi");

    try {
      const res = await fetch("/karran/speech/", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (data.success && data.text && data.text.trim()) {
        if (opts.onComplete) {
          opts.onComplete({
            success: true,
            text: data.text.trim(),
            lang: data.lang || opts.lang || "hi",
            engine: "server_stt"
          });
        }
      } else {
        if (opts.onError) {
          opts.onError(data.error || "आवाज साफ सुनाई नहीं दी। कृपया दोबारा बोलें या नीचे लिखें।");
        }
      }
    } catch (netErr) {
      if (opts.onError) {
        opts.onError("सर्वर से संपर्क नहीं हो सका। कृपया इंटरनेट जांचें।");
      }
    } finally {
      currentRecordingOptions = null;
    }
  }

  function cancelRecording() {
    latestLiveTranscript = "";
    pcmChunks = [];
    cleanupRecordingState();
    currentRecordingOptions = null;
  }

  /**
   * Helper to format seconds as M:SS
   */
  function formatSeconds(secs) {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  }

  // Expose API
  window.KarranVoiceSystem = {
    VOICE_LANG_MAP,
    cleanTextForSpeech,
    speakText,
    speak: speakText,
    stopSpeaking,
    pauseSpeaking,
    resumeSpeaking,
    isSpeaking,
    startRecording,
    stopRecording,
    cancelRecording,
    formatSeconds,
    getAutoSpeak: () => autoSpeakEnabled,
    setAutoSpeak: (val) => { autoSpeakEnabled = !!val; },
    getSpeechRate: () => speechRate,
    setSpeechRate: (r) => { speechRate = r; }
  };

  // Pre-load synthesis voices
  if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.getVoices();
    };
  }

})(window, document);
