# StoriaAI MVP Blueprint

## 1. Product Vision
- Build the most trusted bedtime storytelling companion for Italian families, combining hyper-personalization, cultural authenticity, and strict safety controls.
- Deliver delightful bedtime experiences across mobile and web with stories under 10 minutes, narrated audio, and soft interactivity that encourages positive values.
- Operate on a lean weekly cadence to reach a live, testable MVP within seven days while maintaining GDPR compliance and budget discipline.

## 2. Target Audience
- Primary: parents of children aged 3-10 seeking culturally relevant, safe bedtime content.
- Secondary: Bilingual households looking for Italian/English switches, educators needing morality-infused tales, grandparents wanting simple sharing.
- Market size: ~5M Italian households with children under 10; smartphone penetration >90%.

## 3. Problem and Differentiation
- Gaps in current offerings (BedtimeStory.ai, Oscar Stories, StoryBee, StorySpark):
  - Weak parent controls (no explicit moral filters, violence toggles, or scary-content suppression).
  - Poor localization (little Italian folklore, minimal dialect or cultural references).
  - Lack of continuity (stories feel one-off; no sequels referencing past adventures).
  - Thin interactivity (no branching choices for kids to influence the plot).
  - Privacy risks (cloud storage of identifiable child data, unclear consent flows).
  - Repetitive content causing churn and low retention.
- StoriaAI advantages:
  - Explicit parental control sliders and checkboxes (violence, moral focus, humor level, bedtime calming).
  - Knowledge base of Italian folklore, regional myths, and modern Italian pop culture references.
  - Continuity engine that stores a minimal story state locally or in an encrypted vault for sequels.
  - Branching points at least 2-3 times per story, letting the child text-tap choices.
  - Offline audio caching and on-device storage to avoid cloud data retention beyond 30 days.
  - GDPR-first design (transparent consent, minimal data capture, user-controlled deletion).

## 4. Core Experience and User Flows
1. **Signup/Onboarding**
   - Email + password or federated login (Firebase Auth).
   - Consent screen (GDPR, child data policy, parental verification).
2. **Parent Profile + Child Setup**
   - Inputs: child name, age, pronouns, bedtime mood, interests (tags), preferred language (default Italian, optional English in beta), bedtime duration target.
   - Control toggles: "No scary elements", "Add kindness lesson", "Limit to Italian folklore", "Include educational facts".
3. **Story Generation**
   - Parent selects Story Mode: Quick (5 min), Standard (7 min), Extended (10 min), Sequel.
   - Backend call to `/generate_story` with child profile, control flags, optional previous story ID for continuity.
   - Receive story text segmented into sections (Intro, Choice 1, Branch A/B, Choice 2, Resolution).
   - Generate 3 choice prompts; user taps to continue.
4. **Audio Playback**
   - ElevenLabs API returns audio url; Android uses ExoPlayer, web uses HTML5 audio player with offline download.
5. **Save & Share**
   - Save story metadata locally and in cloud vault (anonymized ID). Parents can share via link/email; shared version strips child name or replaces with nickname token.
6. **Library & Continuity**
   - Story library lists past stories, sequel suggestions.
   - Continuity mechanism references stored attributes (favorite characters, resolved arcs).
7. **Payments & Upsells**
   - Freemium limit 3 stories/day. Premium unlocks unlimited stories, premium voices, custom DALL-E illustration per story.
   - Stripe Checkout for web, Stripe Billing with Google Play integration for Android (placeholder in MVP with manual upgrade toggle if store integration delayed).

## 5. Feature Breakdown for MVP Week
- Story Generation API (text + structured JSON for branching metadata).
- Audio synthesis pipeline (ElevenLabs) with fallback text-to-speech.
- Parent control enforcement (pre- and post-generation filters, banned-word regex, safe storytelling prompt instructions).
- Continuity using SQLite (backend) storing story summaries, characters, morals.
- Offline cache of last 5 stories + audio.
- Shareable link generation (signed URLs expiring in 7 days).
- Analytics events (story_generated, story_completed, branch_choice_made, subscription_upgrade).
- GDPR consent log + data deletion endpoint.

## 6. Technical Architecture Overview
- **Backend**: FastAPI (Python 3.12), hosted on Replit or Vercel serverless functions. SQLite for quick persistence; plan upgrade to PostgreSQL when scaling.
- **AI Generation**: OpenAI GPT-4.1 or GPT-4.1-mini for cost control; fallback to Claude via API when available. Prompt engineering documented below.
- **Audio**: ElevenLabs API (Italian voices: e.g., Bella, Matteo). Output stored temporarily in object storage (Replit bucket or Supabase storage) with auto deletion.
- **Android App**: Kotlin, Jetpack Compose, Retrofit for API, DataStore for cached preferences, ExoPlayer for audio, WorkManager for offline downloads.
- **Web App**: React + Vite or Next.js deployed on Vercel. Uses SWR/React Query for data fetching, Stripe Checkout, Firebase Analytics.
- **Data Privacy**: Minimal PII stored. Replace child name with hashed token for backend. Provide delete endpoint to wipe data instantly.

## 7. Prompt Engineering (Initial Drafts)
- **Story Generation Prompt (Italian default)**
  ```
  You are StoriaAI, a bedtime storyteller for Italian children aged {age}. Always follow safety controls:
  - Language: {language}.
  - Never include scary or violent elements if no_scary=true.
  - Integrate kindness or empathy moral if kindness_lesson=true.
  - Highlight Italian cultural touchstones (e.g., Pinocchio, regional festivals) when italian_focus=true.
  - Keep it positive, calming, and age-appropriate.
  - Duration target: {duration_minutes} minutes (~{word_target} words).
  - Provide 2-3 short choice points for the child with clear options.
  Structure output as JSON with keys: intro, choice_1_prompt, choice_1_options[], branch_1, choice_2_prompt, choice_2_options[], branch_2, resolution, moral_summary, suggested_sequel_hook.
  - Wrap each text value in plain strings without markdown.
  - Never mention policy or safety instructions.
  Context about child:
  Name: {child_name_or_alias}
  Interests: {interests}
  Mood: {mood}
  Previous story recap: {previous_story_summary}
  Now generate the story.
  ```
- **Continuity Summarizer Prompt**
  ```
  Summarize the following story in <=120 words capturing main characters, setting, moral, unresolved hooks, tone. Output JSON with keys: summary, characters[], moral, unresolved_threads[].
  ```
- **Safety Validation Prompt** (backup classifier request if heuristics flag content)
  ```
  Assess whether the following story text is safe for a child aged {age}. Output JSON {"safe": true/false, "issues": []}. Flag if violence, fear, bullying, negative moral.
  ```

## 8. Data Model Snapshot (Backend SQLite)
- `children` table: id (uuid), parent_id, alias, age, interests (json), controls (json), language, created_at.
- `stories` table: id (uuid), child_id, generated_text (json), audio_url, duration_minutes, created_at.
- `story_state` table: story_id, summary, characters (json), moral, unresolved_threads (json), sequel_hook.
- `consent_log`: parent_id, timestamp, version, accept_ip.
- `usage_metrics`: id, parent_id, story_id, event_type, payload (json), timestamp.

## 9. Privacy and Compliance
- GDPR checklist: parental consent gate, clear privacy policy, ability to export/delete data, minimal retention (auto-delete stories after 30 days or on request).
- Store personally identifiable data only with encryption at rest; child name replaced with alias token on server.
- Avoid storing raw audio once download completed; expire after 7 days.
- Stripe: store only customer ID; no credit card data on our servers.
- Firebase Analytics configured to respect EU data residency and disable ad personalization.

## 10. Monetization and Pricing
- Freemium: up to 3 stories/day, standard voice, text-only download.
- Premium (EUR 4.99/month): unlimited stories, premium voices, custom illustration per story (DALL-E mini prompt), unlock continuity history beyond 30 days.
- Upsell funnels: highlight premium benefits after 3rd story, email campaigns, referral bonus (1 free week per referral).

## 11. Marketing Website Information Architecture (10 Pages)
1. Home (hero value prop, CTA to try web app & download APK).
2. Features (detailed breakdown of controls, continuity, interactivity).
3. Stories Library (sample stories with Italian themes).
4. Safety & Privacy (GDPR compliance, parental controls).
5. Pricing (freemium vs premium comparisons, FAQs).
6. About Us (mission, founders, cultural advisors).
7. Blog (updates, parenting tips, Italian folklore articles).
8. Support (contact form, troubleshooting, data deletion request).
9. Beta Community (feedback form, roadmap voting, release notes).
10. Legal (terms of service, privacy policy, cookie notice).

## 12. 7-Day Execution Roadmap
- **Day 1 (Nov 11)**
  - Deliver this blueprint, competitor research notes, initial prompts.
  - Sign up for tool accounts (OpenAI, ElevenLabs, Stripe test, Firebase/Analytics).
  - Validate sample stories manually and refine prompts.
  - Milestone: Spec + prompts + tool access ready.
- **Day 2 (Nov 12)**
  - Configure FastAPI project (Replit/Vercel) with `/generate_story`, `/summarize_story`, `/validate_story` endpoints.
  - Integrate OpenAI + ElevenLabs; implement SQLite persistence.
  - Add continuity logic and banned-word filtering.
  - Deploy to staging; manual API tests with Postman.
  - Milestone: Stable backend accessible publicly.
- **Day 3 (Nov 13)**
  - Set up Android project with Compose screens: login, child profile, story view.
  - Connect to backend via Retrofit; implement branching UI and audio playback.
  - Implement offline caching and DataStore persistence.
  - Milestone: APK installable on test device.
- **Day 4 (Nov 14)**
  - Build React web client (Vite + Tailwind) or Bubble alternative.
  - Implement same flows as Android, integrate Stripe Checkout test mode.
  - Deploy to Vercel, connect custom domain (purchase story domain).
  - Milestone: Live web client with basic auth and story generation.
- **Day 5 (Nov 15)**
  - Full integration testing (API load, story variety, offline playback).
  - QA on safety filters, GDPR consent, data deletion.
  - Polish UI, add basic illustrations, refine prompts, add analytics events.
  - Milestone: MVP feature-complete and stable.
- **Day 6 (Nov 16)**
  - Launch beta outreach (social posts, parenting forums, influencer DMs).
  - Run $20 FB/Instagram ads targeting Italian parents.
  - Monitor analytics, gather qualitative feedback (forms, DMs).
  - Milestone: 50+ beta users signed up.
- **Day 7 (Nov 17)**
  - Analyze usage data, iterate on top issues (e.g., repetitive plots, audio glitches).
  - Deploy prompt tweaks, bug fixes, onboarding improvements.
  - Prepare retention email, plan App Store submission prerequisites.
  - Milestone: MVP iteration report with metrics and next steps.

## 13. Risk Register and Mitigations
- **API Cost Overrun**: Cap daily OpenAI tokens, switch to smaller model for drafts, pre-generate templates offline.
- **Story Safety Failure**: Layered controls (prompt restrictions, regex filter, optional classifier). Manual review of flagged stories.
- **Audio Latency**: Cache voices, prefetch audio, allow text playback fallback.
- **GDPR Non-compliance**: Legal review of privacy policy, implement data deletion automation early.
- **Time Crunch**: Prioritize backend + Android (core use case), allow web version to use Bubble if coding lags.
- **User Acquisition Shortfall**: Prepare multiple messaging angles (cultural pride, bedtime peace, moral lessons), use personal network.

## 14. Testing Strategy
- Unit tests for prompt formatting, filter enforcement, API endpoints.
- Integration tests simulating story generation with different control flags.
- Android instrumentation tests for offline caching and branch navigation.
- Web e2e smoke via Playwright or Bubble workflows.
- Manual QA checklist (story safety, audio playback, subscription flow, consent logging).
- Beta feedback capture through Google Form + analytics dashboards.

## 15. Budget Overview (EUR)
- Domain storyai.it or storiaai.it: 10-15.
- OpenAI credits: 20 (target 400 stories @ 0.05 each with GPT-4.1-mini).
- ElevenLabs: free tier or 10 for extra characters.
- Stripe, Firebase: free tiers.
- Ads: 20 initial budget.
- Total week spend target: 60 max, with opportunity to trim audio/ad costs.

## 16. Sample Generated Story (Prototype Prompt Result)
- Prompted OpenAI manually: "Safe bedtime story for 7-year-old Mario who loves dinosaurs and soccer, Italian tone, kindness moral, no scary parts."
- Result summary: "Mario and Dino the gentle triceratops help friends share toys during a village festival in Tuscany; moral on teamwork and kindness." (Full story to be generated during backend implementation.)

## 17. Immediate Next Actions
1. Register tool accounts and capture API keys in secure vault (.env, never commit).
2. Stand up FastAPI skeleton with health endpoint.
3. Implement prompt templates in code and run first automated story generation.
4. Draft privacy policy and consent copy for onboarding.
