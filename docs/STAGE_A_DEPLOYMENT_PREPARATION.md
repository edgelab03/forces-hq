# Stage A hosted-preview preparation record

Scope: deployment preparation on `feat/forces-hq-connected-foundation`, after Stage A commit `d772408`. No Stage B implementation, merge, Render provisioning, Vercel account changes or hosted deployment command was performed. Existing Streamlit code/configuration and all financial/policy logic are unchanged.

Use [the Android dashboard walkthrough](STAGE_A_PHONE_PREVIEW.md) for the actual manual setup. It contains the exact repository, branch, Docker context/path/port, Vercel variable scopes, protection and rollback instructions. No command-line access is required to follow that walkthrough.

## Completed locally

- Reviewed the Dockerfile, API factory/security middleware, profile models/backup integration, Next.js server gateway/authentication Proxy, environment template and Next.js configuration.
- Confirmed the Docker context must be repository root: `COPY` needs `profile_backup.py`, `benefit_journeys.py`, `app_context.py` and root requirements. No `app.py` or Streamlit server runs in the API container.
- Added `backend/Dockerfile.dockerignore`, scoped to this Dockerfile, to send only required build/runtime files. `.env`, secrets, Git metadata, browser files, local environments and policy caches are excluded from context. No repository-wide Docker/Vercel ignore behaviour changes.
- Corrected runtime Python `COPY` permissions to `0644`. This workspace's files were `0600`, so the original image's user `10001:10001` could not import them. The corrected image keeps the non-root user and works independently of checkout umask. No application behaviour was changed.
- Built a local validation image and verified its runtime with synthetic data only. The image was not pushed to a registry.
- Re-ran all **16 API integration tests** successfully.
- Passed `backend/tests/container_smoke.py`: non-root runtime, minimal public health, anonymous API denial, authenticated profile validation and encrypted round trip, wrong-passphrase rejection, redacted validation responses/logs, no secret/cache/frontend/Streamlit app files in image, no retained temporary CA, and startup refusal specifically for missing token.
- Passed `backend/tests/preview_guard_smoke.py` against the existing production-built Next.js app: unconfigured pages/API return 503; anonymous and wrong-password requests return 401; authenticated profile page opens; missing API configuration remains 503; arbitrary upstream paths and foreign mutation origins are rejected. The checker never connects to a hosted API and removes its temporary servers.
- Rechecked public built client assets: private API/access variable names and the previous synthetic service token were absent. No actual account secrets were available to this task.

### Important build-environment qualification

The stock Docker build reached dependency installation but failed because this managed environment intercepts HTTPS using a CA absent from the stock Python image. TLS verification was **not** disabled.

For local runtime validation only, a temporary Dockerfile in `/tmp` mounted the environment's trusted CA as a BuildKit secret for the `pip install` step (`pip --cert ...`). All application files, dependency requirements, runtime user and command matched the committed Dockerfile. The CA was neither copied into the image nor added to deployment source. Container checks confirm the temporary CA path is absent at runtime.

Thus the corrected container runtime/imports/security are locally verified, but a **pristine stock-image dependency build on Render has not been executed here**. Render's first build, actual HTTPS routing, account protection and log settings remain operator checks. Do not add `--trusted-host`, disable certificate verification, or upload this environment's CA to Render to disguise a build problem there.

## Deployment configuration conclusions

- Use a separate Render **Web Service**, Docker runtime, branch `feat/forces-hq-connected-foundation`, empty Root Directory, context `.`, Dockerfile `./backend/Dockerfile`, no Docker Command override, `PORT=8000` and `/healthz`. This allows Vercel to use its public HTTPS origin while application endpoints require the private server token. A Render-only private-network address is not reachable from Vercel by default.
- Leave the existing Vercel project's production branch/domain intact. Use a branch-scoped **Preview** deployment with root `frontend`, Next.js and Node 22.x. No tracked `vercel.json` override is needed for the existing source layout, but actual account/project settings were not accessed or verified.
- Keep server-only API URL/token and app preview credentials out of `NEXT_PUBLIC_*`. Use native Vercel Authentication for preview URLs as an additional layer; do not expose bypass links. `FHQ_FRONTEND_ORIGIN` must match the actual stable branch URL used on the phone, not an invented or changing deployment URL.
- Changing environment values requires a new Vercel deployment. Until its stable URL exists, a deliberate `.invalid` origin can safely reject all mutations; replace it and redeploy before testing writes.

## Security boundaries and what remains unverified

`/healthz` is deliberately anonymous and contains no profile information. Profile/options/capabilities/validation/backup endpoints require Bearer authentication in Python. Next.js pages and its allowlisted gateway require the private preview credentials, with a second check inside the handler. Public static assets are not personal-data endpoints. There is no server-side profile database to enumerate; each response concerns the request's supplied document/file.

These are **local verified properties**, not evidence that a live Render/Vercel account is already configured correctly. The operator must check unauthenticated live requests, HTTPS certificates, actual deployment IDs, platform logs/monitoring, access permissions and abuse limits. Keep the first physical-device test synthetic. Shared preview credentials are not individual production authentication; public multi-user release remains out of scope.

Rollbacks must retain authentication and align both services' token/environment snapshots. If a previous protected preview cannot be restored safely, suspend/delete only the new staging resources and keep production/Streamlit running. See the walkthrough's rollback section and the existing [deployment guide](CONNECTED_DEPLOYMENT.md).

## Reproduce the checks

In a normal trusted Docker/network environment, from repository root:

```sh
docker build -f backend/Dockerfile -t forces-hq-stage-a-validation:local .
python backend/tests/container_smoke.py
# After frontend/npm dependencies and a production build exist:
python backend/tests/preview_guard_smoke.py
.venv/bin/python -m unittest discover -s backend/tests -q
```

The container checker needs Docker access and standard Python; the frontend checker also needs Node.js and `frontend/.next` built. Both use generated in-memory credentials and loopback interfaces, not account secrets. Neither publishes or provisions anything.

Official platform references checked for the walkthrough: [Render Docker](https://render.com/docs/docker), [monorepo contexts](https://render.com/docs/monorepo-support), [ports](https://render.com/docs/web-services#port-binding), [health checks](https://render.com/docs/health-checks), [rollbacks](https://render.com/docs/rollbacks), [Vercel deployment protection](https://vercel.com/docs/deployment-protection), [environment scopes](https://vercel.com/docs/environment-variables), [generated branch URLs](https://vercel.com/docs/deployments/generated-urls) and [dashboard Git deployments](https://vercel.com/docs/git). Dashboard labels and plan offerings can change; inspect the displayed target environment/cost before confirming an account action.
