import { accessFailure } from '@/lib/server-access';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const routes: Record<string, string[]> = {
  'capabilities': ['GET'], 'profile/options': ['GET'], 'profile': ['PUT'],
  'profile/validate': ['POST'], 'profile/backup/export': ['POST'], 'profile/backup/restore': ['POST'],
};
const limit = 256 * 1024;
const headers = { 'Cache-Control': 'no-store, private', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer' };
const failure = (status: number, code: string) => Response.json({ error: { code } }, { status, headers });

async function forward(request: Request, context: { params: Promise<{ path: string[] }> }) {
  const rejected = accessFailure(request);
  if (rejected) return rejected;
  const path = (await context.params).path.join('/');
  if (!routes[path]?.includes(request.method)) return failure(404, 'unsupported_endpoint');
  if (new URL(request.url).search) return failure(400, 'query_parameters_not_supported');
  if (request.method !== 'GET') {
    const origin = new URL(process.env.FHQ_FRONTEND_ORIGIN || request.url).origin;
    if (request.headers.get('origin') !== origin) return failure(403, 'origin_rejected');
    if (request.headers.get('content-type')?.split(';')[0] !== 'application/json') return failure(415, 'json_required');
  }
  const base = process.env.FHQ_API_URL;
  const token = process.env.FHQ_API_TOKEN;
  if (!base || !token || token.length < 32) return failure(503, 'backend_not_configured');
  let target: URL;
  try {
    const url = new URL(base);
    const local = ['127.0.0.1', 'localhost'].includes(url.hostname) && process.env.FHQ_ALLOW_LOCAL_API === '1';
    if ((url.protocol !== 'https:' && !local) || url.username || url.password || url.search || url.hash || url.pathname !== '/') throw new Error();
    target = new URL(`/v1/${path}`, url);
  } catch { return failure(503, 'backend_configuration_invalid'); }

  let body: Uint8Array | undefined;
  if (request.body) {
    const reader = request.body.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.length;
      if (size > limit) { await reader.cancel(); return failure(413, 'request_too_large'); }
      chunks.push(value);
    }
    body = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.length; }
  }
  try {
    const upstream = await fetch(target, {
      method: request.method, headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: body as BodyInit | undefined, cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(20_000),
    });
    if (upstream.status >= 500 || upstream.status === 401) return failure(503, 'backend_unavailable');
    const content = await upstream.arrayBuffer();
    if (content.byteLength > limit) return failure(502, 'backend_response_rejected');
    return new Response(content, { status: upstream.status, headers: {
      ...headers, 'Content-Type': upstream.headers.get('content-type') || 'application/json',
      ...(path === 'profile/backup/export' && upstream.ok ? { 'Content-Disposition': 'attachment; filename="forces-hq-profile.fhq"' } : {}),
    } });
  } catch { return failure(503, 'backend_unavailable'); }
}

export const GET = forward;
export const POST = forward;
export const PUT = forward;
