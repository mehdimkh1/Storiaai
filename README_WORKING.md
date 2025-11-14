# 🎉 StoriaAI - FREE Multi-Language Bedtime Stories

## ✨ What's Fixed

✅ **Multi-Language Support**: Arabic, English, Spanish, French, Italian
✅ **FREE Text-to-Speech**: Using Google TTS (gTTS) - no API keys needed!
✅ **FREE Story Generation**: Using stub mode (or add Hugging Face key for real AI)
✅ **3D Animated Web Interface**: Professional design with particles, glass effects
✅ **Working Demo**: Test immediately without paying anything

## 🚀 Quick Start

### Option 1: Easy Start (Double-click)
1. Double-click `START_APP.bat`
2. Wait 3 seconds
3. Browser opens automatically
4. Fill form and create stories!

### Option 2: Manual Start
```powershell
# Terminal 1 - Backend
cd backend
..\.venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
# Just open frontend\index.html in your browser
```

## 🌍 Supported Languages

- 🇸🇦 **Arabic** (ar) - العربية
- 🇬🇧 **English** (en)
- 🇪🇸 **Spanish** (es) - Español  
- 🇫🇷 **French** (fr) - Français
- 🇮🇹 **Italian** (it) - Italiano

## 📝 How to Use

1. **Open** http://localhost:8000/docs OR frontend/index.html
2. **Fill Form**:
   - Parent email (any email works)
   - Child's name, age, mood
   - Select language from dropdown
   - Choose interests
3. **Click** "✨ Crea Storia Magica"
4. **Wait** for magical loading animation
5. **Read & Listen** to your personalized story!

## 🎯 What Works Now

### ✅ Working (FREE)
- Story generation (stub mode - demo stories)
- Audio generation (gTTS - real voice in all 5 languages!)
- Multi-language interface
- 3D animated UI
- Download stories as text
- Quota system (3 stories/day)

### 🔧 To Add Real AI Stories (Optional)

**Option A: Hugging Face (FREE)**
1. Sign up at https://huggingface.co (no card needed)
2. Get token from https://huggingface.co/settings/tokens
3. Add to `.env`:
   ```
   HUGGINGFACE_API_KEY=hf_your_token_here
   OFFLINE_MODE=false
   ```

**Option B: OpenAI ($5 credit for new users)**
1. Sign up at https://platform.openai.com
2. Get API key
3. Update `.env`:
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your_key_here
   OFFLINE_MODE=false
   ```

## 🎨 Features

### Frontend (Extraordinary 3D Design)
- **3D Wave Background**: Animated water effect (Vanta.js)
- **Particle Stars**: Twinkling star particles
- **Glass Morphism Cards**: Modern frosted glass design
- **Floating Labels**: Smooth animated form inputs
- **Magic Book Loading**: Animated book pages while generating
- **Smooth Animations**: Every interaction has delightful animations
- **Responsive**: Works on desktop, tablet, mobile

### Backend (Professional FastAPI)
- **Multi-Provider**: OpenAI, Ollama, Hugging Face support
- **Free TTS**: gTTS for audio (works offline!)
- **Database**: SQLite for user tracking
- **Quota System**: 3 free stories/day per user
- **GDPR Ready**: User data encryption
- **Test Suite**: pytest coverage

## 📁 Project Structure

```
vscode output/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py      # API endpoints
│   │   ├── config.py    # Multi-language config
│   │   ├── services/
│   │   │   ├── story_engine.py  # gTTS integration
│   │   │   └── providers.py
│   │   └── models.py
│   ├── .env             # Configuration (no keys needed!)
│   └── requirements.txt
├── frontend/            # 3D Web Interface
│   ├── index.html       # Main page
│   ├── styles.css       # 3D animations
│   └── app.js           # Multi-language support
└── START_APP.bat        # One-click launcher
```

## 🔧 Troubleshooting

### Backend won't start?
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend not loading?
- Make sure backend is running first
- Open http://localhost:8000/health to test
- Check browser console (F12) for errors

### No audio?
- Audio uses gTTS (Google TTS) - always works!
- Returns base64 encoded MP3
- Check browser supports HTML5 audio

### Stories are boring?
- Normal! You're in OFFLINE_MODE (stub stories)
- Add Hugging Face key for real AI stories
- Or use OpenAI ($5 free credit)

## 🎯 Next Steps

1. **Test Now**: Stories work with stub data
2. **Get Users**: Share on social media
3. **Add Real AI**: When you have users, add HF/OpenAI key
4. **Deploy Free**: Use Render.com or Railway (free tier)
5. **Add Payment**: Stripe for premium (unlimited stories)

## 📊 Demo Ready!

Your app is **100% demo-ready** RIGHT NOW:
- ✅ Beautiful 3D interface
- ✅ Working form submission  
- ✅ Story generation (stub mode)
- ✅ Real audio (gTTS)
- ✅ Multi-language (5 languages)
- ✅ Download stories
- ✅ Quota system

**Show this to your client TODAY!** No API keys needed.

## 💡 Tips

- Stories are in stub mode - explain it's demo data
- Audio DOES work with gTTS (free Google TTS)
- All 5 languages supported
- Later add real AI when you have budget
- Deploy to Replit/Render for free hosting

## 🐛 Issues?

1. Check backend terminal for errors
2. Open http://localhost:8000/docs
3. Test API directly in Swagger docs
4. Check browser console (F12)

---

Made with ✨ by StoriaAI Team
