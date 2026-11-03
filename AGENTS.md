# AGENTS.md

Read this file first in every session.

## Core Operating Principles

1. **Live Market Grounding with the Organic Fit Gate** requires loading `skills/market-intelligence` before ideating campaigns or positioning. Run live web searches to capture real Voice-of-Customer (VoC) phrases and competitor blind spots. Pass every market signal through the **Organic Fit Gate** so trends are woven in only when causally connected to the user's problem. Drop any trend that feels forced.
2. **Audience Cognitive Routing** uses `skills/audience-calibration` (Petty & Cacioppo's ELM + Construal Level Theory) to match hook velocity, tone, and proof type to the exact reader (Practitioner/Developer vs. Executive vs. Consumer vs. Peer Forum).
3. **Trust Before Any Hook** means pairing every curiosity or conversion hook with a **Trust Damper** from `skills/trust-architecture` (Pratfall admission, Inoculation, Operational Transparency, or Benevolent Anti-Pitch).
4. **4-Note Psychological Chords** come from `skills/hook-compounding`. Layer 3 to 4 complementary mechanisms at once (`Trust Damper + Cognitive Anchor + Active Generator + Forward Vector`), and pair text with spatial structure from `skills/visual-ux-hooks`.
5. **Anti-Scam High Conversion** follows `skills/marketing-hooks` to lift conversion via Self-Perception micro-commitments (Bem 1967), Mental Accounting reframes (Thaler 1985), and Regret Regulation (Zeelenberg 1999), never via fake urgency or inflated ROI.
6. **85-Rule Deep Anti-Slop Across Languages** requires every draft to obey `skills/anti-slop` and score `<= 15/100` on `python3 tools/slop_scan.py <file> --fix-hints`. Rewrite in 300-word blocks to prevent LLM voice drift.
7. **Self-Review in Any Language** runs `skills/self-review` after the scan: reread the draft as a native reader of its language and rewrite whatever still sounds machine-made, up to 3 rounds.
8. **Mandatory 13-Point Value Gate** runs `skills/value-check` before delivering output.

## Lite Lane vs. Full Lane Routing

- **Lite Lane (Fast Path for Short Edits & Single Pieces)** applies when the user asks to humanize existing text, write a short email or release note, or tighten a single headline. Load at most 3-4 skills (`writing-hooks` or `product-hooks` -> `anti-slop` -> `self-review` -> `value-check`) and run `tools/slop_scan.py`.
- **Full Lane (Deep Architecture for Campaigns, Funnels & New Products)** applies when building landing pages, cold outreach sequences, onboarding flows, or trend-grounded ideation. Follow the full routing table below.

## Skill Routing Table

| Task / Domain | Required Skills (Load in Order) |
|---|---|
| Market research, positioning, competitor teardown, or trend analysis | `market-intelligence` -> `audience-calibration` -> `trust-architecture` -> `value-check` |
| Brainstorming fresh hook ideas, content angles, or campaign concepts | `market-intelligence` -> `creative-ideation` -> `hook-compounding` -> `anti-slop` -> `self-review` -> `value-check` |
| Marketing campaigns, landing pages, pricing, cold outreach, ads, launches | `market-intelligence` -> `audience-calibration` -> `trust-architecture` -> `hook-compounding` -> `marketing-hooks` -> `visual-ux-hooks` -> `anti-slop` -> `self-review` -> `value-check` |
| Essays, articles, newsletters, scripts, documentation, copy | `audience-calibration` -> `trust-architecture` -> `hook-compounding` -> `writing-hooks` -> `anti-slop` -> `self-review` -> `value-check` |
| Product onboarding, SaaS flows, UI/UX layouts, retention, projects | `psychology-map` -> `trust-architecture` -> `visual-ux-hooks` -> `hook-compounding` -> `product-hooks` -> `value-check` |
| Rewriting or humanizing text in any language (Lite Lane) | `anti-slop` (plus `tools/slop_scan.py`) -> `self-review` -> `value-check` |
