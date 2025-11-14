# StoriaAI AI-Orchestrated Launch Plan

## Overview
- Objective: Ship StoriaAI MVP in 7 days using AI-first, low-code stack while spending <2 hours/day on human orchestration.
- Principle: "You are the conductor." Offload all build tasks to ChatGPT o1 / GPT-4o, Claude 3.5 Sonnet, Bubble.io, Adalo, Replit, and automation services.
- Outcome Targets: Live backend, web app, Android APK, 50-200 beta users, first premium conversions by Day 7.

## Tool Stack and Budget
| Tool | Purpose | Notes | Est. Cost |
| --- | --- | --- | --- |
| ChatGPT o1 / GPT-4o | Generate backend code, plans, prompts | Replit-friendly FastAPI, detailed instructions | $20/mo |
| Claude 3.5 Sonnet | Prompt refinement, safety, Italian cultural QA | Use for reviews, marketing copy | Free tier |
| GitHub Copilot | Assist in quick code adjustments if needed | Optional within VS Code | $10/mo |
| Replit | Host FastAPI backend with OpenAI + ElevenLabs | Free tier sufficient | Free |
| Bubble.io | No-code responsive web app | Starter plan | $29/mo |
| Adalo | No-code Android app builder | Pro plan for APK export | $45/mo |
| OpenAI API | GPT-4.1-mini or GPT-4o-mini for story gen | $5 promo credit covers MVP | $5 |
| ElevenLabs | Italian TTS voices (Bella, Matteo) | Free tier for MVP | Free |
| Stripe | Subscription billing | Test mode free | Free |
| Namecheap | Domain (storiaai.it) | Connect via Bubble CNAME | $10 |
| Zapier (optional) | Automate analytics/export | Free (if needed) | Free |
| Midjourney/Leonardo (optional) | Icons & artwork | Can use free trials | $10 |
| Total |  |  | ~ $100 |

## Core Deliverables per Day
- **Day 1:** Gather AI-generated blueprint, prompts, and system design. Accounts created, API keys stored securely.
- **Day 2:** FastAPI backend live on Replit with `/generate`, `/summaries`, rate limiting, safety filters.
- **Day 3:** Bubble.io web app launched on custom domain.
- **Day 4:** Adalo Android app published (web share + APK download link).
- **Day 5:** Security and compliance pass (sanitization, consent flows, analytics). Visual polish.
- **Day 6:** Marketing launch (Reddit, influencers, paid ads). Stripe premium offering live.
- **Day 7:** Analytics review, iterate on top feedback, prep report.

## Day-by-Day Playbook

### Day 1 – Setup & AI Plans (≤2h)
1. **Prompt ChatGPT o1** with the full requirement (copied verbatim from request). Expect output covering:
   - Story prompt template.
   - FastAPI backend (OpenAI + ElevenLabs integration).
   - Bubble component map and API connector config.
   - Adalo screen wiring.
   - Stripe product setup instructions.
   - Launch checklist.
2. **Prompt Claude 3.5 Sonnet** for:
   - Safety guardrails (banned words, tone guidelines).
   - Italian folklore references (regional myths, holidays).
   - Alternative pitch angles.
3. **Create accounts** (Replit, Bubble, Adalo, OpenAI, ElevenLabs, Stripe, Google for analytics) and add API keys to a secure `.env` or password manager.
4. **Document** all outputs in a Notion/Google Doc for rapid copy/paste.

### Day 2 – Backend Live (≤1.5h)
1. **Replit project setup**:
   - Create new Python FastAPI repl.
   - Paste AI-supplied `main.py`, `requirements.txt`, `.replit` commands.
   - Add environment variables (`OPENAI_API_KEY`, `ELEVENLABS_API_KEY`).
2. **Run & test** using Replit’s built-in HTTP client or Hoppscotch:
   - POST `/generate` with sample payloads (Italian & English).
   - Confirm JSON structure (intro/choices/resolution, audio URL).
3. **Ask AI** to add features as needed (SQLite continuity, rate limiting, sanitized logs). Paste updates directly.
4. **Create `/.well-known/ai-plugin.json`** if planning future GPT plugin integration (optional).

### Day 3 – Web App (≤1h)
1. **Bubble.io build**:
   - Use AI output to create pages: Home, Generator, Dashboard.
   - Install API Connector plugin; configure POST to Replit with JSON body.
   - Map responses to text blocks and audio component (HTML5 audio).
   - Add Stripe plugin; configure checkout flow for premium upgrades.
2. **Connect domain**:
   - Purchase `storiaai.it` via Namecheap; create CNAME pointing to Bubble.
   - Setup DNS (propagation may take hours).
3. **Test** end-to-end: generate story, play audio, upgrade button linking to Stripe Checkout.

### Day 4 – Android App via Adalo (≤1h)
1. **Adalo project**:
   - Build screens: Welcome (value prop, login optional), Story Form, Story Detail, Library.
   - Use Custom Action to POST to backend; bind response fields to text and audio player.
   - Implement offline storage by enabling local database + caching story results.
   - Add premium upsell screen linking to Bubble/Stripe.
2. **Publish** as PWA and request APK via Adalo store submission queue (Pro plan).
3. **Test on device** using shareable link (PWA) before APK available.

### Day 5 – Safety, GDPR, Polish (≤1h)
1. **Prompt Claude** to review backend & web flows for safety upgrades:
   - Input sanitization (strip harmful terms, length limits).
   - Banned word list (e.g., "morte", "sangue").
   - Rate limiting logic (3 stories/day free users).
   - Cookie/consent banner text in Italian & English.
   - Privacy policy template referencing GDPR rights.
2. **Implement fixes** by pasting code/snippets provided by AI into Replit, Bubble (conditional workflows), and Adalo (logic rules).
3. **Visual polish**:
   - Generate hero art via Midjourney prompt: `"Cute Italian child sleeping under stars, warm colors, bedtime story theme"`.
   - Add favicon, loader animation, testimonials placeholder.
4. **QA**: run through flows pretending to be three different parent personas.

### Day 6 – Launch & Acquisition (≤2h)
1. **Content creation** via AI prompts:
   - Reddit & Facebook posts (Italian cultural references, safety focus).
   - DM templates for influencers (offer free premium).
   - Email & WhatsApp scripts for friends/family.
   - FB/IG ad copy + creative prompt (e.g., for Canva/Midjourney).
2. **Publish & promote**:
   - Share on `r/italia`, `r/genitori`, relevant FB groups (vary copy to avoid spam).
   - Send DMs to 20 Italian parenting influencers.
   - Launch $20 FB/IG ad campaign (parents 25-45, interests: "fiabe", "genitorialità").
3. **Enable analytics**:
   - Bubble: integrate Google Analytics or Plausible.
   - Adalo: configure event tracking (story generated, audio played).
   - Stripe: confirm test mode checkout.

### Day 7 – Monitor & Iterate (≤2h)
1. **Set up dashboard**:
   - Use Google Sheets IMPORTJSON or Replit logs export to track daily stories, premium conversions, errors.
   - Optionally connect Zapier → Sheets for automated updates.
2. **Collect feedback**:
   - Create Google Form (Net Promoter-style + open responses).
   - Prompt Claude to summarize top feedback themes and highlight urgent fixes.
3. **Iterate**:
   - Request AI improvements (e.g., Pinocchio or Italian folklore mode, branch depth adjustments).
   - Update prompts for more variety if stories feel repetitive.
   - Implement voice selection toggles (male/female Italian voices).
4. **Prepare report**:
   - Document metrics: total signups, active users, conversions, top issues.
   - Capture learnings for app store submission or investor pitch.

## Key Prompts
- **Backend build (ChatGPT o1 / GPT-4o)**: Use master prompt from Day 1 instructions. Append clarifying follow-ups for rate limiting, GDPR endpoints, caching.
- **Safety pass (Claude)**: "Audit this FastAPI code for child safety and GDPR compliance; provide patched version with comments."
- **Bubble API Connector**: "Provide Bubble API Connector configuration JSON for POST request with headers, body fields, and response mapping for audio URL."
- **Adalo custom action**: "Generate step-by-step Adalo custom action to POST to backend and bind story fields to screen components."
- **Marketing copy (Claude)**: "Write 150-word Italian Facebook ad showcasing StoriaAI's Italian folklore focus and safety controls; include CTA."

## Monetization & Limits
- Freemium: 3 stories per child per day; auto-enforced by backend counter in SQLite.
- Premium: Stripe Checkout session created via Bubble workflow, passes customer email to backend for status update.
- Upsells: Offer custom illustration (DALL·E mini) and premium voices after story playback within both apps.

## Compliance Checklist
- Display GDPR consent on first visit; log timestamp (store hashed email + consent version).
- Provide link/button to request data deletion (Bubble workflow hitting backend `/delete_user_data`).
- Avoid storing child names in plain text; replace with alias token before persisting.
- Keep logs minimal; mask PII.
- Update privacy policy & terms on legal page (Bubble) referencing data practices.

## Testing Plan
- Daily smoke tests: form submission in Bubble, story playback, premium checkout (test mode).
- Edge cases: long interests list, invalid ages, language toggles, sequel with no prior story.
- Audio fallback: ensure text displayed even if ElevenLabs request fails.
- Mobile testing: Android PWA, iOS Safari (web app), Android APK when ready.
- Safety QA: run stories for 10 varied profiles; confirm banned words filter.

## Launch Checklist Snapshot
- [ ] Backend deployed, health endpoint verified.
- [ ] Bubble app connected to custom domain and SSL active.
- [ ] Adalo app tested and share link distributed.
- [ ] Stripe product and pricing live (test mode validated).
- [ ] Analytics dashboards recording events.
- [ ] Reddit/Facebook posts scheduled.
- [ ] Influencer outreach list contacted (track responses).
- [ ] Feedback form linked in app and follow-up emails.
- [ ] Day 7 metrics report template prepared.

## Success Metrics (Week 1)
- 50-200 signups (Bubble + Adalo combined).
- ≥10 premium trials initiated (test mode OK initially).
- ≥70% story completion rate.
- Qualitative feedback highlighting Italian cultural delight & safety trust.

## Post-Week Extensions
- Prepare App Store & Google Play submission (privacy labels, assets, test accounts).
- Expand content packs (regional folklore, holiday specials).
- Add multilingual support (German/French) if analytics show demand.
- Explore partnerships with Italian parenting blogs/podcasts.
- Hardening: migrate to Supabase/PostgreSQL, implement monitoring (Sentry), schedule backups.
