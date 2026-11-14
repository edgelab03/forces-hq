# Forces HQ — connected Stage A

The approved Modern Forces interface now has a real Python-backed service profile. **Only Stage A is connected**: profile validation, confirmation/updates, promotion history, confirmed Home context and user-controlled encrypted `.fhq` export/restore. The existing Streamlit application remains operational and unchanged.

- [Functionality inventory](../docs/CONNECTED_FUNCTIONALITY_INVENTORY.md): actual reusable code, tests, source restrictions and missing capabilities.
- [API/data contract](../docs/CONNECTED_API_CONTRACT.md): typed documents, endpoints, provenance and privacy boundaries.
- [Local setup, security, hosting and rollback](../docs/CONNECTED_DEPLOYMENT.md).
- [Connected test/visual results](docs/CONNECTED_VALIDATION.md).

## Local preview

Start the separate Python API from repository root, after setting your own random `FHQ_API_TOKEN` in the terminal environment:

```sh
python3.12 -m venv .venv-api
.venv-api/bin/python -m pip install -r backend/requirements.txt
.venv-api/bin/python -m uvicorn backend.api:create_app --factory --host 127.0.0.1 --port 8010 --no-access-log
```

Copy `frontend/.env.example` to ignored `frontend/.env.local`. Replace all placeholders: use the matching API token, your private preview username/password, the loopback API URL and exact frontend origin. Never use `NEXT_PUBLIC_` for credentials. No account or hosted deployment is created by these commands.

```sh
cd frontend
npm ci
npm run build
npm start -- --port 3000
```

Open the configured frontend origin and authenticate with the preview credentials. For Android USB testing, forward port 3000 with `adb reverse tcp:3000 tcp:3000` and browse `http://localhost:3000` on the phone; set that exact origin in `FHQ_FRONTEND_ORIGIN`. Next.js proxies to loopback Python. A Vercel deployment needs a separately hosted HTTPS API; Codex/laptop processes are not accessible to Vercel.

Unconfigured private access or backend settings fail closed. The shared preview gate is not a production multi-user identity system; do not deploy this as an anonymous personal-data service. See the deployment guide before hosted testing.

## Storage and stage boundaries

Profile and drafts remain only in React memory for the mounted page. Navigating Home/Me preserves the confirmed profile; reload or closing clears it. No plaintext profile is written to browser storage, and there is no server profile database or automatic cloud sync. Use Backup to download the existing Python-encrypted `.fhq` file and explicitly restore it in another session. Compatible older files preserve structured career and FHTB progress. Passphrases are cleared after each operation and cannot be recovered.

Home contains no fictional person, monthly income or savings. Any displayed annual pensionable earnings are explicitly the user's attestation, not a computed or independently verified pay figure. Profile and birthday fields are not used to fabricate benefits or pensions.

**Still unconnected:** Money/pay/pension models and charts (B); real meal/mileage policy conversations (C); guided FHTB/career/learning (D). Ask remains a clearly labelled scripted demonstration. Non-connected tool panels accurately state which Python features exist and which are incomplete. Learning Credits eligibility, AFPS 05 reconstruction and EDP calculations are not implemented in the existing app.

## Testing

```sh
# Repository root, in your API test environment:
.venv-api/bin/python -m unittest discover -s backend/tests -v
# Existing Streamlit regression environment:
.venv/bin/python -m unittest discover -s tests -v
# Frontend:
npm run typecheck
npm run build
# With both protected services running, set FHQ_TEST_USERNAME and
# FHQ_TEST_PASSWORD to the chosen private preview credentials, then:
APP_URL=http://localhost:3000 npm test
```

Tests use only synthetic profiles and make real HTTP requests through Next.js to FastAPI. Playwright uses system Chromium if available, otherwise run `npx playwright install chromium`; `CHROMIUM_PATH` can override it. Do not run snapshot/trace tests with actual personal information.

The earlier prototype screenshots in `docs/VISUAL_REVIEW.md` are historical design artifacts, not evidence of current functional integration. Updated Stage A captures are under `docs/screenshots/connected/`. Physical Android keyboard, toolbar and hardware Back acceptance remains pending. No Android colour-mode behaviour is changed.
