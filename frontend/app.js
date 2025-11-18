// Initialize 3D Background
VANTA.WAVES({
    el: "#vanta-bg",
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    scale: 1.00,
    scaleMobile: 1.00,
    color: 0x1a1a3e,
    shininess: 40.00,
    waveHeight: 15.00,
    waveSpeed: 0.75,
    zoom: 0.65
});

// API Configuration
// Backend base URL (production). If you need to test locally, change to 'http://127.0.0.1:8000'
const API_BASE = 'https://storiaai-backend.onrender.com';

const VOICE_OPTIONS = {
    it: [
        { value: 'it-IT-IsabellaNeural', label: '🇮🇹 Isabella (F)' },
        { value: 'it-IT-DiegoNeural', label: '🇮🇹 Diego (M)' },
        { value: 'gtts', label: '🆓 Voce classica (gTTS)' }
    ],
    en: [
        { value: 'en-GB-LibbyNeural', label: '🇬🇧 Libby (F)' },
        { value: 'en-GB-RyanNeural', label: '🇬🇧 Ryan (M)' },
        { value: 'gtts', label: '🆓 Classic voice (gTTS)' }
    ],
    es: [
        { value: 'es-ES-ElviraNeural', label: '🇪🇸 Elvira (F)' },
        { value: 'es-ES-AlvaroNeural', label: '🇪🇸 Álvaro (M)' },
        { value: 'gtts', label: '🆓 Voz clásica (gTTS)' }
    ],
    fr: [
        { value: 'fr-FR-DeniseNeural', label: '🇫🇷 Denise (F)' },
        { value: 'fr-FR-HenriNeural', label: '🇫🇷 Henri (M)' },
        { value: 'gtts', label: '🆓 Voix classique (gTTS)' }
    ],
    ar: [
        { value: 'ar-SA-ZariyahNeural', label: '🇸🇦 Zariyah (F)' },
        { value: 'ar-SA-HamedNeural', label: '🇸🇦 Hamed (M)' },
        { value: 'gtts', label: '🆓 صوت كلاسيكي (gTTS)' }
    ]
};

// DOM Elements
const storyForm = document.getElementById('story-form');
const generateBtn = document.getElementById('generate-btn');
const loadingContainer = document.getElementById('loading');
const storyCard = document.getElementById('story-card');
const creatorCard = document.querySelector('.creator-card');
const errorToast = document.getElementById('error-toast');
const quotaCount = document.getElementById('quota-count');
const languageSelect = document.getElementById('language');
const voiceSelect = document.getElementById('voice');
const audioPlayer = document.getElementById('audio-player');
const audioElement = document.getElementById('story-audio');
const voiceInfo = document.getElementById('voice-info');

// Story data
let currentStory = null;

function populateVoiceOptions(language) {
    if (!voiceSelect) return;
    const voices = VOICE_OPTIONS[language] || [];
    voiceSelect.innerHTML = '';

    voices.forEach((voice, index) => {
        const option = document.createElement('option');
        option.value = voice.value;
        option.textContent = voice.label;
        if (index === 0) {
            option.selected = true;
        }
        voiceSelect.appendChild(option);
    });

    if (voices.length === 0) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'Voce non disponibile';
        voiceSelect.appendChild(option);
    }
}

function getVoiceLabel(language, voiceValue) {
    if (!voiceValue) return null;
    const voices = VOICE_OPTIONS[language] || [];
    const match = voices.find((v) => v.value === voiceValue);
    if (match) return match.label;
    return voiceValue;
}

function hideAudioPlayer() {
    if (!audioPlayer) return;
    audioPlayer.style.display = 'none';
    if (audioElement) {
        audioElement.pause();
        audioElement.removeAttribute('src');
        audioElement.load();
    }
    if (voiceInfo) {
        voiceInfo.textContent = '';
    }
}

if (languageSelect) {
    populateVoiceOptions(languageSelect.value);
    languageSelect.addEventListener('change', () => {
        if (!voiceSelect) return;
        const previous = voiceSelect.value;
        populateVoiceOptions(languageSelect.value);
        const options = Array.from(voiceSelect.options).map((opt) => opt.value);
        if (previous && options.includes(previous)) {
            voiceSelect.value = previous;
        }
    });
}

// Form Submission
storyForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await generateStory();
});

// Generate Story Function
async function generateStory() {
    // Get form values
    const formData = {
        parent_email: document.getElementById('parent-email').value,
        child: {
            name: document.getElementById('child-name').value,
            age: parseInt(document.getElementById('child-age').value),
            mood: document.getElementById('child-mood').value,
            interests: document.getElementById('child-interests').value
                .split(',')
                .map(i => i.trim())
                .filter(i => i)
        },
        controls: {
            no_scary: document.getElementById('no-scary').checked,
            kindness_lesson: document.getElementById('kindness').checked,
            italian_focus: document.getElementById('italian-focus').checked,
            educational: document.getElementById('educational').checked
        },
        language: languageSelect.value,
        target_duration_minutes: 7,
        sequel: false
    };

    const selectedVoice = voiceSelect?.value;
    if (selectedVoice) {
        formData.voice = selectedVoice;
    }

    // Optional new controls: style, tone, educational_topic, generate_panels
    const styleEl = document.getElementById('story-style');
    const toneEl = document.getElementById('story-tone');
    const topicEl = document.getElementById('educational-topic');
    const panelsEl = document.getElementById('generate-panels');
    if (styleEl && styleEl.value.trim()) formData.style = styleEl.value.trim();
    if (toneEl && toneEl.value.trim()) formData.tone = toneEl.value.trim();
    if (topicEl && topicEl.value.trim()) formData.educational_topic = topicEl.value.trim();
    // Default to true if the checkbox is not present
    formData.generate_panels = panelsEl ? !!panelsEl.checked : true;

    // Show loading
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="btn-text">⏳ Creando magia...</span>';
    loadingContainer.style.display = 'block';
    storyCard.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/generate_story`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Errore nella generazione della storia');
        }

        const data = await response.json();
        currentStory = data;
        
        // Update quota
        if (data.stories_remaining_today !== undefined) {
            quotaCount.textContent = data.stories_remaining_today;
        }

        // Display story
        displayStory(data);

    } catch (error) {
        showError(error.message);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<span class="btn-text">✨ Crea Storia Magica</span>';
        loadingContainer.style.display = 'none';
    }
}

// Display Story
function displayStory(data) {
    const storyContent = document.getElementById('story-content');
    const storyTitle = document.getElementById('story-title');

    const story = data.story || data.story_text;

    // Set title (use intro as title if available)
    if (story?.intro) {
        const preview = story.intro.length > 60 ? `${story.intro.substring(0, 57)}...` : story.intro;
        storyTitle.textContent = preview;
    } else {
        storyTitle.textContent = 'La Tua Storia Magica ✨';
    }

    // Build story HTML
    let html = '';

    if (story) {
        // Intro
        if (story.intro) {
            html += `<div class="story-section">
                <h3>📖 L'inizio dell'avventura</h3>
                <p>${story.intro}</p>
            </div>`;
        }

        // First choice
        if (story.choice_1_prompt) {
            html += `<div class="story-section">
                <h3>🔮 Prima scelta</h3>
                <p><strong>${story.choice_1_prompt}</strong></p>
                ${story.choice_1_options ? `
                    <ul>
                        ${story.choice_1_options.map(opt => `<li>${opt}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>`;
        }

        // Branch 1
        if (story.branch_1) {
            html += `<div class="story-section">
                <p>${story.branch_1}</p>
            </div>`;
        }

        // Second choice
        if (story.choice_2_prompt) {
            html += `<div class="story-section">
                <h3>🌟 Seconda scelta</h3>
                <p><strong>${story.choice_2_prompt}</strong></p>
                ${story.choice_2_options ? `
                    <ul>
                        ${story.choice_2_options.map(opt => `<li>${opt}</li>`).join('')}
                    </ul>
                ` : ''}
            </div>`;
        }

        // Branch 2
        if (story.branch_2) {
            html += `<div class="story-section">
                <p>${story.branch_2}</p>
            </div>`;
        }

        // Ending
        if (story.resolution) {
            html += `<div class="story-section">
                <h3>✨ Il finale magico</h3>
                <p>${story.resolution}</p>
            </div>`;
        }

        // Moral lesson
        if (story.moral_summary) {
            html += `<div class="story-section moral-lesson">
                <h3>💝 La lezione</h3>
                <p><em>${story.moral_summary}</em></p>
            </div>`;
        }

        // Panel prompts for illustrations
        if (Array.isArray(story.panel_prompts) && story.panel_prompts.length > 0) {
            html += `<div class="story-section">
                <h3>🎨 Idee per le illustrazioni</h3>
                <ul>${story.panel_prompts.map(p => `<li>${p}</li>`).join('')}</ul>
            </div>`;
        }

        if (story.suggested_sequel_hook) {
            html += `<div class="story-section">
                <h3>🔔 Prossima avventura</h3>
                <p>${story.suggested_sequel_hook}</p>
            </div>`;
        }
    } else {
        html = '<p>Storia generata con successo! 🎉</p>';
    }

    // Memory snapshot section
    const ms = data.memory_snapshot;
    if (ms) {
        const chars = Array.isArray(ms.characters) && ms.characters.length
            ? `<ul>${ms.characters.map(c => `<li>${c}</li>`).join('')}</ul>`
            : '<p><em>Nessun personaggio memorizzato</em></p>';
        const threads = Array.isArray(ms.unresolved_threads) && ms.unresolved_threads.length
            ? `<ul>${ms.unresolved_threads.map(t => `<li>${t}</li>`).join('')}</ul>`
            : '<p><em>Nessun filo narrativo aperto</em></p>';
        html += `<div class="story-section">
            <h3>🧠 Memoria della storia</h3>
            <p><strong>Morale recente:</strong> ${ms.moral || '<em>n/d</em>'}</p>
            <p><strong>Personaggi ricordati:</strong></p>
            ${chars}
            <p><strong>Trame da riprendere:</strong></p>
            ${threads}
            ${ms.sequel_hook ? `<p><strong>Aggancio futuro:</strong> ${ms.sequel_hook}</p>` : ''}
        </div>`;
    }

    storyContent.innerHTML = html;

    if (data.audio_url && audioElement) {
        audioElement.src = data.audio_url;
        audioElement.load();
        if (audioPlayer) {
            audioPlayer.style.display = 'block';
        }
        if (voiceInfo) {
            const label = getVoiceLabel(data.language || languageSelect.value, data.voice);
            const voiceText = label ? `Narratore: ${label}` : data.voice ? `Voce: ${data.voice}` : '';
            voiceInfo.textContent = voiceText;
        }
    } else {
        hideAudioPlayer();
    }
    
    // Show story card
    creatorCard.style.display = 'none';
    storyCard.style.display = 'block';
    
    // Scroll to story
    storyCard.scrollIntoView({ behavior: 'smooth' });
    
    // Add entrance animation
    storyCard.style.animation = 'fadeInUp 0.6s ease-out';
}

// Close Story
document.getElementById('close-story').addEventListener('click', () => {
    storyCard.style.display = 'none';
    creatorCard.style.display = 'block';
    creatorCard.scrollIntoView({ behavior: 'smooth' });
    hideAudioPlayer();
});

// Read Again
document.getElementById('read-again').addEventListener('click', () => {
    storyCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// Create New Story
document.getElementById('create-new').addEventListener('click', () => {
    storyCard.style.display = 'none';
    creatorCard.style.display = 'block';
    creatorCard.scrollIntoView({ behavior: 'smooth' });
    storyForm.reset();
    // Re-check default toggles
    document.getElementById('no-scary').checked = true;
    document.getElementById('kindness').checked = true;
    document.getElementById('italian-focus').checked = true;
    populateVoiceOptions(languageSelect.value);
    hideAudioPlayer();
});

// Download Story
document.getElementById('download-story').addEventListener('click', () => {
    if (!currentStory) return;

    const storyText = formatStoryForDownload(currentStory);
    const blob = new Blob([storyText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `storia-${currentStory.story_id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showSuccess('Storia salvata! 💾');
});

// Format story for download
function formatStoryForDownload(data) {
    let text = '✨ STORIA MAGICA DA STORIAAI ✨\n\n';
    text += `ID Storia: ${data.story_id}\n`;
    text += `Data: ${new Date().toLocaleDateString('it-IT')}\n\n`;
    if (data.language) {
        text += `Lingua: ${data.language}\n`;
    }
    if (data.voice) {
        const label = getVoiceLabel(data.language || languageSelect.value, data.voice);
        text += `Voce: ${label || data.voice}\n\n`;
    }
    text += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n';

    const story = data.story || data.story_text;

    if (story) {
        
        if (story.intro) text += `📖 L'INIZIO\n${story.intro}\n\n`;
        if (story.choice_1_prompt) {
            text += `🔮 PRIMA SCELTA\n${story.choice_1_prompt}\n`;
            if (story.choice_1_options) {
                story.choice_1_options.forEach(opt => text += `  • ${opt}\n`);
            }
            text += '\n';
        }
        if (story.branch_1) text += `${story.branch_1}\n\n`;
        if (story.choice_2_prompt) {
            text += `🌟 SECONDA SCELTA\n${story.choice_2_prompt}\n`;
            if (story.choice_2_options) {
                story.choice_2_options.forEach(opt => text += `  • ${opt}\n`);
            }
            text += '\n';
        }
        if (story.branch_2) text += `${story.branch_2}\n\n`;
        if (story.resolution) text += `✨ FINALE\n${story.resolution}\n\n`;
        if (story.moral_summary) text += `💝 LEZIONE\n${story.moral_summary}\n\n`;
        if (Array.isArray(story.panel_prompts) && story.panel_prompts.length) {
            text += `🎨 IDEE ILLUSTRAZIONI\n`;
            story.panel_prompts.forEach(p => text += `  • ${p}\n`);
            text += '\n';
        }
        if (story.suggested_sequel_hook) text += `🔔 PROSSIMA AVVENTURA\n${story.suggested_sequel_hook}\n\n`;
    }

    if (data.memory_snapshot) {
        const ms = data.memory_snapshot;
        text += '🧠 MEMORIA\n';
        if (ms.moral) text += `Morale recente: ${ms.moral}\n`;
        if (Array.isArray(ms.characters) && ms.characters.length) {
            text += `Personaggi:\n`;
            ms.characters.forEach(c => text += `  • ${c}\n`);
        }
        if (Array.isArray(ms.unresolved_threads) && ms.unresolved_threads.length) {
            text += `Trame da riprendere:\n`;
            ms.unresolved_threads.forEach(t => text += `  • ${t}\n`);
        }
        if (ms.sequel_hook) text += `Aggancio futuro: ${ms.sequel_hook}\n`;
        text += '\n';
    }

    text += '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n';
    text += 'Creato con StoriaAI - Storie magiche per bambini\n';

    return text;
}

// Show Error Toast
function showError(message) {
    const toastMessage = document.getElementById('toast-message');
    toastMessage.textContent = message;
    errorToast.classList.add('show');

    setTimeout(() => {
        errorToast.classList.remove('show');
    }, 5000);
}

// Show Success Toast
function showSuccess(message) {
    const toast = errorToast.cloneNode(true);
    toast.style.background = 'rgba(78, 222, 128, 0.1)';
    toast.style.borderColor = 'var(--success)';
    toast.querySelector('.toast-icon').textContent = '✅';
    toast.querySelector('.toast-message').textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add sparkle effect on button hover
generateBtn.addEventListener('mouseenter', () => {
    createSparkles(generateBtn);
});

function createSparkles(element) {
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            const sparkle = document.createElement('div');
            sparkle.textContent = '✨';
            sparkle.style.position = 'absolute';
            sparkle.style.left = Math.random() * element.offsetWidth + 'px';
            sparkle.style.top = Math.random() * element.offsetHeight + 'px';
            sparkle.style.fontSize = '1.5rem';
            sparkle.style.pointerEvents = 'none';
            sparkle.style.animation = 'sparkle 1s ease-out forwards';
            
            element.appendChild(sparkle);
            
            setTimeout(() => sparkle.remove(), 1000);
        }, i * 100);
    }
}

// Add sparkle animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes sparkle {
        0% {
            opacity: 1;
            transform: translateY(0) scale(0);
        }
        50% {
            opacity: 1;
            transform: translateY(-20px) scale(1);
        }
        100% {
            opacity: 0;
            transform: translateY(-40px) scale(0);
        }
    }
    
    .story-section {
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 15px;
        border-left: 4px solid var(--accent);
    }
    
    .moral-lesson {
        background: rgba(78, 222, 128, 0.05);
        border-left-color: var(--success);
    }

    .audio-player {
        margin-top: 2rem;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .audio-player audio {
        width: 100%;
        margin: 1rem 0 0.5rem;
    }

    .voice-info {
        font-size: 0.9rem;
        color: var(--text-muted);
    }
`;
document.head.appendChild(style);

// Check API health on load
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            console.log('✅ API is healthy');
        }
    } catch (error) {
        showError('⚠️ Backend non raggiungibile. Riprova tra pochi secondi. Se il problema persiste verifica che il servizio sia online su Render.');
    }
}

checkAPIHealth();
