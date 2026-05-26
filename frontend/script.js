document.addEventListener('DOMContentLoaded', () => {

    /* ── Elements ──────────────────────────────────── */
    const input     = document.getElementById('query-input');
    const chatBox   = document.getElementById('chat-box');
    const sendBtn   = document.getElementById('send-btn');
    const loading   = document.getElementById('loading-indicator');

    /* ── Geometric Background Canvas ──────────────── */
    (function initCanvas() {
        const canvas = document.getElementById('bg-canvas');
        const ctx    = canvas.getContext('2d');

        function resize() {
            canvas.width  = window.innerWidth;
            canvas.height = window.innerHeight;
            draw();
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const size = 80;
            const cols = Math.ceil(canvas.width  / size) + 2;
            const rows = Math.ceil(canvas.height / size) + 2;

            ctx.strokeStyle = 'rgba(201,168,76,0.18)';
            ctx.lineWidth   = 0.6;

            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    const x = c * size;
                    const y = r * size;
                    const half = size / 2;

                    // Star / cross pattern
                    ctx.beginPath();
                    ctx.moveTo(x, y + half);
                    ctx.lineTo(x + half, y);
                    ctx.lineTo(x + size, y + half);
                    ctx.lineTo(x + half, y + size);
                    ctx.closePath();
                    ctx.stroke();

                    // Inner diamond
                    const q = size / 4;
                    ctx.beginPath();
                    ctx.moveTo(x + half, y + q);
                    ctx.lineTo(x + size - q, y + half);
                    ctx.lineTo(x + half, y + size - q);
                    ctx.lineTo(x + q, y + half);
                    ctx.closePath();
                    ctx.stroke();
                }
            }
        }

        window.addEventListener('resize', resize);
        resize();
    })();

    /* ── Auto-resize textarea ──────────────────────── */
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 140) + 'px';
    });

    /* ── Send on Enter (Shift+Enter = newline) ─────── */
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    sendBtn.addEventListener('click', handleSend);

    /* ── Suggestion Chips ──────────────────────────── */
    window.fillQuery = function(btn) {
        input.value = btn.textContent.trim();
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 140) + 'px';
        input.focus();
        handleSend();
    };

    /* ── Core Send Logic ───────────────────────────── */
    async function handleSend() {
        const query = input.value.trim();
        if (!query) return;

        // Hide welcome block if still visible
        const welcome = document.querySelector('.welcome-block');
        if (welcome) welcome.remove();

        appendMessage(query, 'user');
        input.value = '';
        input.style.height = 'auto';

        setLoading(true);

        try {
            // Use a relative URL — works both locally and inside Docker
            const response = await fetch('/api/chat', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ query, top_k: 3 }),
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const reader  = response.body.getReader();
            const decoder = new TextDecoder('utf-8');

            // Create bot message element and mark it as streaming
            const wrapperObj = appendMessage('', 'bot', false, true);
            const botEl = wrapperObj.msg;
            const labelEl = wrapperObj.label;

            setLoading(false);

            let buffer = "";

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                
                // Keep the last incomplete line in the buffer
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        if (data.type === "meta" && data.rephrased_query) {
                            // Display the expert's rephrased search query in the label
                            labelEl.innerHTML = `ALLaM <span style="font-size: 0.75rem; color: #a0a0a0; font-weight: normal; margin-right: 8px;">(البحث عن: ${data.rephrased_query})</span>`;
                        } else if (data.type === "chunk") {
                            botEl.textContent += data.text;
                        }
                    } catch (e) {
                        // fallback if json parse fails
                        console.error('Failed to parse NDJSON line', e, line);
                    }
                }
                chatBox.scrollTop  = chatBox.scrollHeight;
            }

            // Remove streaming cursor once done
            botEl.classList.remove('streaming');

        } catch (err) {
            setLoading(false);
            console.error('API error:', err);
            appendMessage(`حدث خطأ في الاتصال: ${err.message}`, 'bot', true);
        }

        chatBox.scrollTop = chatBox.scrollHeight;
    }

    /* ── Helpers ───────────────────────────────────── */
    function appendMessage(text, sender, isError = false, streaming = false) {
        const wrapper = document.createElement('div');
        wrapper.classList.add('message-wrapper', `${sender}-wrapper`);

        const label = document.createElement('div');
        label.classList.add('message-label');
        if (sender === 'user') {
            label.textContent = 'أنت';
        } else {
            label.textContent = 'ALLaM';
            label.classList.add('gold');
        }

        const msg = document.createElement('div');
        msg.classList.add('chat-message', `${sender}-message`);
        if (isError) msg.classList.add('error-message');
        if (streaming) msg.classList.add('streaming');
        msg.textContent = text;

        wrapper.appendChild(label);
        wrapper.appendChild(msg);
        chatBox.appendChild(wrapper);
        chatBox.scrollTop = chatBox.scrollHeight;

        return { msg, label, wrapper }; // return elements to allow updating metadata
    }

    function setLoading(on) {
        loading.style.display = on ? 'flex' : 'none';
        sendBtn.disabled = on;
    }
});