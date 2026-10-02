import re

file_path = r'c:\Users\Amit kumar gupta\Downloads\AgriVisionAi-main\AgriVisionAi-main\templates\dashboard\dashboard.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We will replace the entire block from async function stopDashRecording() to the end of the aiDashMic listener

old_logic = '''    async function stopDashRecording() {
        if (!isDashRecording) return;
        isDashRecording = false;
        if (dashAutoStopTimer) { clearTimeout(dashAutoStopTimer); dashAutoStopTimer = null; }

        if (aiDashMic) {
            aiDashMic.textContent = '🎙️';
            aiDashMic.style.background = '#f0fdf4';
            aiDashMic.style.borderColor = '#86efac';
        }

        if (dashScriptNode) { try { dashScriptNode.disconnect(); } catch(e){} dashScriptNode = null; }
        if (dashSourceNode) { try { dashSourceNode.disconnect(); } catch(e){} dashSourceNode = null; }
        if (dashAudioStream) {
            dashAudioStream.getTracks().forEach(t => t.stop());
            dashAudioStream = null;
        }

        const sampleRate = (dashAudioCtx && dashAudioCtx.sampleRate) ? dashAudioCtx.sampleRate : 16000;
        if (dashAudioCtx && dashAudioCtx.state !== 'closed') {
            try { dashAudioCtx.close(); } catch(e){}
            dashAudioCtx = null;
        }

        let totalLength = 0;
        for (let i = 0; i < dashPcmChunks.length; i++) totalLength += dashPcmChunks[i].length;
        if (totalLength === 0) return;

        const merged = new Float32Array(totalLength);
        let offset = 0;
        for (let i = 0; i < dashPcmChunks.length; i++) {
            merged.set(dashPcmChunks[i], offset);
            offset += dashPcmChunks[i].length;
        }
        dashPcmChunks = [];

        const wavBlob = encodeDashWAV(merged, sampleRate);
        if (wavBlob.size < 1000) return;

        const formData = new FormData();
        formData.append('audio', wavBlob, 'recording.wav');
        const currentLang = window.KisanSathiI18n ? window.KisanSathiI18n.getCurrentLang() : 'hi';
        formData.append('lang', currentLang);

        try {
            aiInput.placeholder = "🔄 Samajh rahe hain / Processing...";
            const res = await fetch('/karran/speech/', { method: 'POST', body: formData });
            const data = await res.json();
            if (data.success && data.text) {
                aiInput.value = data.text;
                sendAIMessage(true);
            } else {
                aiInput.placeholder = "⚠️ Aawaz samajh nahi aayi. Type karein.";
            }
        } catch (err) {
            console.error('Speech error:', err);
            aiInput.placeholder = "Ask AI Sathi...";
        }
    }

    if (aiDashMic) {
        aiDashMic.addEventListener('click', async () => {
            if (isDashRecording) {
                stopDashRecording();
                return;
            }

            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert('Microphone support nahi karta aapka browser.');
                return;
            }

            try {
                dashAudioStream = await navigator.mediaDevices.getUserMedia({
                    audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true }
                });
            } catch (err) {
                alert('Mic access error: ' + err.message);
                return;
            }

            try {
                const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
                dashAudioCtx = new AudioCtxClass();
                if (dashAudioCtx.state === 'suspended') await dashAudioCtx.resume();

                dashSourceNode = dashAudioCtx.createMediaStreamSource(dashAudioStream);
                dashScriptNode = dashAudioCtx.createScriptProcessor(4096, 1, 1);
                dashPcmChunks = [];

                dashScriptNode.onaudioprocess = (e) => {
                    if (!isDashRecording) return;
                    const input = e.inputBuffer.getChannelData(0);
                    const chunk = new Float32Array(input.length);
                    chunk.set(input);
                    dashPcmChunks.push(chunk);
                };

                dashSourceNode.connect(dashScriptNode);
                dashScriptNode.connect(dashAudioCtx.destination);

                isDashRecording = true;
                aiDashMic.textContent = '⏹️';
                aiDashMic.style.background = '#fef2f2';
                aiDashMic.style.borderColor = '#ef4444';
                aiInput.placeholder = '🔴 Sun rahe hain... Boliye...';

                dashAutoStopTimer = setTimeout(() => {
                    if (isDashRecording) stopDashRecording();
                }, 15000);

            } catch (initErr) {
                console.error('Dash AudioContext error:', initErr);
                if (dashAudioStream) { dashAudioStream.getTracks().forEach(t => t.stop()); dashAudioStream = null; }
            }
        });
    }'''

new_logic = '''    async function stopDashRecordingFallback() {
        if (!isDashRecording) return;
        isDashRecording = false;
        if (dashAutoStopTimer) { clearTimeout(dashAutoStopTimer); dashAutoStopTimer = null; }

        if (aiDashMic) {
            aiDashMic.textContent = '🎙️';
            aiDashMic.style.background = '#f0fdf4';
            aiDashMic.style.borderColor = '#86efac';
        }

        if (dashScriptNode) { try { dashScriptNode.disconnect(); } catch(e){} dashScriptNode = null; }
        if (dashSourceNode) { try { dashSourceNode.disconnect(); } catch(e){} dashSourceNode = null; }
        if (dashAudioStream) {
            dashAudioStream.getTracks().forEach(t => t.stop());
            dashAudioStream = null;
        }

        const sampleRate = (dashAudioCtx && dashAudioCtx.sampleRate) ? dashAudioCtx.sampleRate : 16000;
        if (dashAudioCtx && dashAudioCtx.state !== 'closed') {
            try { dashAudioCtx.close(); } catch(e){}
            dashAudioCtx = null;
        }

        let totalLength = 0;
        for (let i = 0; i < dashPcmChunks.length; i++) totalLength += dashPcmChunks[i].length;
        if (totalLength === 0) return;

        const merged = new Float32Array(totalLength);
        let offset = 0;
        for (let i = 0; i < dashPcmChunks.length; i++) {
            merged.set(dashPcmChunks[i], offset);
            offset += dashPcmChunks[i].length;
        }
        dashPcmChunks = [];

        const wavBlob = encodeDashWAV(merged, sampleRate);
        if (wavBlob.size < 1000) return;

        const formData = new FormData();
        formData.append('audio', wavBlob, 'recording.wav');
        const currentLang = window.KisanSathiI18n ? window.KisanSathiI18n.getCurrentLang() : 'hi';
        formData.append('lang', currentLang);

        try {
            aiInput.placeholder = "🔄 Samajh rahe hain / Processing...";
            const res = await fetch('/karran/speech/', { method: 'POST', body: formData });
            const data = await res.json();
            if (data.success && data.text) {
                aiInput.value = data.text;
                sendAIMessage(true);
            } else {
                aiInput.placeholder = "⚠️ Aawaz samajh nahi aayi. Type karein.";
            }
        } catch (err) {
            console.error('Speech error:', err);
            aiInput.placeholder = "Ask AI Sathi...";
        }
    }

    if (aiDashMic) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            
            recognition.onstart = function() {
                isDashRecording = true;
                aiDashMic.textContent = '⏹️';
                aiDashMic.style.background = '#fef2f2';
                aiDashMic.style.borderColor = '#ef4444';
                aiInput.placeholder = '🔴 Sun rahe hain... Boliye...';
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                aiInput.value = transcript;
                sendAIMessage(true);
            };
            
            recognition.onerror = function(event) {
                console.error('Speech error:', event.error);
                if (event.error !== 'no-speech') {
                    aiInput.placeholder = "⚠️ Aawaz samajh nahi aayi. Type karein.";
                }
                resetDashMic();
            };
            
            recognition.onend = function() {
                resetDashMic();
            };
            
            function resetDashMic() {
                isDashRecording = false;
                aiDashMic.textContent = '🎙️';
                aiDashMic.style.background = '#f0fdf4';
                aiDashMic.style.borderColor = '#86efac';
                if (!aiInput.value) aiInput.placeholder = "Ask AI Sathi...";
            }

            aiDashMic.addEventListener('click', () => {
                if (isDashRecording) {
                    recognition.stop();
                } else {
                    const currentLang = window.KisanSathiI18n ? window.KisanSathiI18n.getCurrentLang() : 'hi';
                    const langMap = {'hi': 'hi-IN', 'en': 'en-IN', 'bn': 'bn-IN', 'mr': 'mr-IN', 'te': 'te-IN', 'ta': 'ta-IN', 'gu': 'gu-IN', 'pa': 'pa-IN'};
                    recognition.lang = langMap[currentLang] || 'hi-IN';
                    try {
                        recognition.start();
                    } catch(e) {
                        console.error(e);
                    }
                }
            });
        } else {
            // Fallback for non-Chrome/Safari browsers
            aiDashMic.addEventListener('click', async () => {
                if (isDashRecording) {
                    stopDashRecordingFallback();
                    return;
                }

                if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                    alert('Microphone support nahi karta aapka browser.');
                    return;
                }

                try {
                    dashAudioStream = await navigator.mediaDevices.getUserMedia({
                        audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true }
                    });
                } catch (err) {
                    alert('Mic access error: ' + err.message);
                    return;
                }

                try {
                    const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
                    dashAudioCtx = new AudioCtxClass();
                    if (dashAudioCtx.state === 'suspended') await dashAudioCtx.resume();

                    dashSourceNode = dashAudioCtx.createMediaStreamSource(dashAudioStream);
                    dashScriptNode = dashAudioCtx.createScriptProcessor(4096, 1, 1);
                    dashPcmChunks = [];

                    dashScriptNode.onaudioprocess = (e) => {
                        if (!isDashRecording) return;
                        const input = e.inputBuffer.getChannelData(0);
                        const chunk = new Float32Array(input.length);
                        chunk.set(input);
                        dashPcmChunks.push(chunk);
                    };

                    dashSourceNode.connect(dashScriptNode);
                    dashScriptNode.connect(dashAudioCtx.destination);

                    isDashRecording = true;
                    aiDashMic.textContent = '⏹️';
                    aiDashMic.style.background = '#fef2f2';
                    aiDashMic.style.borderColor = '#ef4444';
                    aiInput.placeholder = '🔴 Sun rahe hain... Boliye...';

                    dashAutoStopTimer = setTimeout(() => {
                        if (isDashRecording) stopDashRecordingFallback();
                    }, 15000);

                } catch (initErr) {
                    console.error('Dash AudioContext error:', initErr);
                    if (dashAudioStream) { dashAudioStream.getTracks().forEach(t => t.stop()); dashAudioStream = null; }
                }
            });
        }
    }'''

content = content.replace(old_logic, new_logic)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced logic!")
