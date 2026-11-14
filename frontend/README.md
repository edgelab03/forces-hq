# Modern Forces frontend prototype

A separate Next.js 16 / React 19 / TypeScript prototype of **Home** and **Ask**. All changes are contained in `frontend/`. The existing Python app, Streamlit configuration, policy rules, deployment and pension calculations remain unchanged.

## Preview on an Android phone

Use Node.js 22 LTS or later and npm. From your existing repository checkout:

```sh
git fetch origin
git switch feat/modern-forces-next-prototype
cd frontend
npm ci
npm run build
npm start -- --port 3000
```

1. Keep that terminal running on your computer. Connect the computer and phone to the same Wi-Fi.
2. Find the computer's LAN IPv4 address (`ipconfig` on Windows; Wi-Fi network settings on macOS; `hostname -I` on Linux).
3. Open **`http://<computer-LAN-IP>:3000`** in Android Chrome, for example `http://192.168.1.25:3000`. `localhost` on the phone refers to the phone, not the computer.
4. If a firewall prompt appears, allow this app on your private network. If Wi-Fi client isolation prevents access, use another trusted network or the USB option below.

This is a separate Node process and port. Do not change the Streamlit app's entry point, deployment settings or domain. No hosting account, API key, AI service or Python process is needed. Stop the preview with Ctrl+C.

Optional USB preview, if Android Platform Tools and USB debugging are already configured:

```sh
adb devices
adb reverse tcp:3000 tcp:3000
```

Then open `http://localhost:3000` in Chrome on the connected phone. After testing, remove the forwarding with `adb reverse --remove tcp:3000`.

For live development, use `npm run dev -- --hostname 0.0.0.0 --port 3000` instead of the build/start commands. The small dev launcher also translates a managed preview runner's `--host` / `--strictPort` flags into Next.js arguments. Production preview uses native `next start`.

## What works

- Home: compact original F mark, fictional personal greeting, forest Ask panel with real input, two-column Pay/Housing/Pension/Learning cards, sample financial overview and an explicitly labelled demo opportunity.
- Ask: type **“Can I claim my lunch from yesterday?”**, answer the suggested questions or type a response, and review the retained conversation. Three contextual questions lead to a summary of stated circumstances, **never an eligibility outcome or invented JSP reference**. Home-buying and mileage scripts are also available.
- Native `/` and `/ask` routes, links, browser Back/Forward, direct entry and reload. The five bottom destinations work; Money, Explore, Me and non-migrated tools open honest preview sheets on Home rather than additional migrated screens. Dialogs support Escape, focus containment and close controls.
- The conversation and current draft are stored in this browser tab's `sessionStorage`. There is no account, shared database or cloud sync. “Start a new demo conversation” clears the demo. Home question submission intentionally starts a fresh scenario; tapping the Ask tab resumes the current one. Browser storage restrictions fall back to in-memory use.
- The composer is in normal flex layout above navigation, rather than floating over messages. `100dvh`, the Visual Viewport API and safe-area insets follow the available space; keyboard detection covers both visual-only and whole-layout resizing, and hides bottom navigation while typing in the reduced viewport. Only the conversation scrolls. There is no global scroll lock that blocks the message list.

Use fictional details only. Alex, the financial figures and the opportunity are demonstration content. No runtime requests go to an AI API, service-record system, Python backend or external font service. The Manrope variable font is bundled locally; icons use Lucide.

## Visual system

Maintainable CSS in `app/globals.css` defines shared tokens for ivory `#F7F7F2`, forest `#25483E`, ink `#263D36`, white surfaces, spacing, radii and elevation. This is intentionally a new application shell and conversational experience, rather than React copies of the Streamlit forms. No Tailwind build dependency is required.

## Verification and screenshots

```sh
npm run typecheck
npm run build
# Keep `npm start -- --port 3000` running in another terminal.
APP_URL=http://127.0.0.1:3000 npm test
```

Tests use `@playwright/test` and Chromium. If system Chromium is not installed, run `npx playwright install chromium`; the configuration uses Playwright's browser when `/usr/bin/chromium` is absent. `CHROMIUM_PATH` can override the executable. Windows PowerShell users can set `$env:APP_URL` and `$env:CHROMIUM_PATH` before `npm test`.

The 15 browser checks cover 360×800, 390×844 and 412×915: colours and grid, tap targets, all navigation/sheets, native browser history, direct Ask entry, tab-reload retention, malformed storage, complete lunch flow, reset and reduced-height composer clearance. They also exercise the overlay-keyboard layout branch with a simulated Visual Viewport change. These simulations do **not** certify a real Android keyboard, toolbar or hardware Back button.

[Rendered mobile screenshots and visual review](docs/VISUAL_REVIEW.md) include Home, the financial/opportunity section, an active Ask conversation, a completed demonstration and a reduced-height view at every requested width. Screenshots are real Chromium renders, not generated mockups. Review the images and the physical phone; CSS assertions alone do not establish design approval.

### Physical Android acceptance pass

On your phone, check Home and the overview after one short scroll. Submit the lunch question, tap a suggested reply, type the next answer and open/close the keyboard. Confirm the composer stays visible and the conversation scrolls without overlapping controls. Try Chrome Back/Forward, reload, portrait/landscape and a larger system text size. Check Pay and the other preview sheets; press Android Back while a sheet is open, then revisit Ask. Keep Streamlit open separately to compare the interfaces. Physical-device acceptance remains pending.

The managed environment's optional preview relay and interactive browser binding were unavailable during development; final validation used the built Next.js app on a local port with Playwright Chromium. Starting the local server/browser and running the Next.js TypeScript build subprocess required the environment's normal execution approvals. No Streamlit hosting change or cloud-account creation was used.

## Source map

- `app/`: App Router pages, metadata, viewport policy and design tokens.
- `components/`: Home, Ask, shared application shell, demo-state provider and native preview dialog.
- `lib/conversation.ts`: bounded, deterministic demonstration state machine; no real policy logic.
- `tests/`: mobile browser acceptance tests.
- `docs/screenshots/`: committed rendered review artifacts.

This is a visual/interaction prototype, not a production migration. Authentication, real user profiles, verified policy-service integration, financial calculations and a full accessibility audit are outside this phase. Do not merge or replace the existing deployment before review.
