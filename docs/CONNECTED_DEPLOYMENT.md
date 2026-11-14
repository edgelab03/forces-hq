# Connected foundation — local use and proposed deployment

**No deployment or merge is part of this change.** The existing Streamlit service stays operational and unchanged. Stage A is a private, protected foundation, not a public multi-user release.

For phone-only account setup, use the [Android Render/Vercel walkthrough](STAGE_A_PHONE_PREVIEW.md). The [deployment preparation record](STAGE_A_DEPLOYMENT_PREPARATION.md) distinguishes local container/access checks from manual hosted verification.

## Architecture

Android/browser → HTTPS Next.js on Vercel → same-origin authenticated `/api/backend` gateway → independent HTTPS FastAPI service. Backend profile operations are stateless and reuse root Python validation/encryption. Never point Vercel at a process in Codex or at your laptop's localhost.

For backend hosting, propose a separate container service on Render (or equivalent managed container hosting) using `backend/Dockerfile`, built with repository root as its context. It needs no persistent disk/database for Stage A. Use a provider with appropriate region, privacy controls and no request-body logging. Configure the service's internal port as 8000, health check `/healthz`, TLS ingress and platform limits/rate limiting. Verify these controls before allowing personal data. The Dockerfile whitelists source files rather than copying secrets or policy caches.

## Secrets and access controls

| Variable | Runtime | Purpose |
| --- | --- | --- |
| `FHQ_API_TOKEN` | Python and Next.js server | Same random ASCII secret, at least 32 characters; Python refuses startup without it |
| `FHQ_API_URL` | Next.js server | Backend origin, HTTPS in hosted environments; no path/query/userinfo |
| `FHQ_ACCESS_USERNAME` | Next.js server | Private foundation preview username |
| `FHQ_ACCESS_PASSWORD` | Next.js server | Private foundation preview password, at least 20 characters |
| `FHQ_FRONTEND_ORIGIN` | Next.js server | Exact frontend origin for mutation/CSRF checks; set to the branch/staging Vercel HTTPS URL |
| `FHQ_ALLOW_LOCAL_API=1` | Next.js, local testing only | Explicitly permit HTTP to loopback only; omit in hosted production |

All variables are server-only. **Never use `NEXT_PUBLIC_` for secrets, passphrases or profile data.** Use hosting secret stores, not tracked `.env` files. Rotate tokens by replacing both services' settings together; do not print them in command lines/logs. Examples contain placeholders only.

Next.js is fail-closed if private-preview credentials are missing. Browser Basic authentication protects pages and the API gateway; the gateway repeats the check rather than relying only on Next.js Proxy. This is an interim **shared private-preview gate**, not a claim of individual user accounts or full production authentication. Each visitor's confirmed profile remains only in their browser memory; no shared profile store exists.

Before public/multi-user release, implement and review individual identity (e.g. OIDC), per-user authorisation/session revocation, rate limits for crypto operations, a secure persistence model if desired, abuse protection and operational privacy controls. Do not remove the preview gate just to make a Vercel URL public. If the protected frontend cannot be configured securely, it returns 503 rather than silently reverting to sample data or exposing an anonymous proxy.

## Local development

Use Python 3.12 and Node.js 22+. Install API dependencies separately from Streamlit's unchanged requirements:

```sh
python3.12 -m venv .venv-api
.venv-api/bin/python -m pip install -r backend/requirements.txt
# Set a new private FHQ_API_TOKEN in this terminal's environment first.
.venv-api/bin/python -m uvicorn backend.api:create_app --factory --host 127.0.0.1 --port 8010 --no-access-log
```

In another terminal, copy `frontend/.env.example` to ignored `frontend/.env.local`. Replace the placeholders with your own credentials, use the same API token, `FHQ_API_URL=http://127.0.0.1:8010` and `FHQ_ALLOW_LOCAL_API=1`. Set the exact origin you will browse, e.g. `FHQ_FRONTEND_ORIGIN=http://localhost:3000`.

```sh
cd frontend
npm ci
npm run dev -- --hostname 127.0.0.1 --port 3000
# Or: npm run build && npm start -- --port 3000
```

Open the chosen origin and enter the private preview credentials when prompted. For Android USB preview, use `adb reverse tcp:3000 tcp:3000` and browse that same `http://localhost:3000` origin on the device. Keep Python loopback-only: Android communicates with Next.js, not directly with Python. LAN development is only for fictional test data on a trusted network; hosted personal-data testing must use HTTPS. No cloud account or automatic sync is required by the app.

## Verification

```sh
.venv-api/bin/python -m unittest discover -s backend/tests -v
# Existing regression environment:
.venv/bin/python -m unittest discover -s tests -v
cd frontend
npm run typecheck
npm run build
# With API and protected frontend running, set FHQ_TEST_USERNAME/PASSWORD to
# your preview credentials. Tests use synthetic profiles only.
APP_URL=http://localhost:3000 npm test
```

Browser tests make real profile/export/restore requests through Next.js to Python at 360/390/412px; only the explicit outage test aborts a request to verify state preservation. Test screenshot artifacts are synthetic. Existing frontend demo tests are updated for memory-only retention and accurately marked stage boundaries, rather than claiming their conversations use policy logic.

## Deployment and rollback sequence

1. Review the branch, audit inventory, contracts, test results and privacy settings. This stage is not ready for anonymous public access.
2. Independently provision the backend container with its runtime token, TLS, no body/credential capture, and abuse limits. Verify unauthorised calls fail, `/healthz` is minimal and arbitrary files/docs are not served. Keep backend service revisions available for rollback.
3. Set the server-only variables on a **separate protected Vercel preview/staging environment**. Keep the existing production frontend and Streamlit deployment unchanged until reviewed. Redeploy that preview only through the normal operator workflow.
4. Test the hosted Next.js→hosted Python path on a physical Android device, including profile changes, network failure, encrypted download/new-session restore, keyboard and Back behaviour. Check the backend log policy independently. A local browser pass does not verify a hosted environment.
5. If verification fails, restore the previous Vercel deployment/commit and backend container revision; remove the staging integration variables or disable the staging service. No server profile data needs migration. `.fhq` compatibility is retained because the original crypto module/format is unchanged. Keep Streamlit available throughout.

Stages B–D remain separate future changes. No backend endpoint or frontend preview sheet should imply those stages have been connected in this release.
