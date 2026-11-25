// Cloudflare Worker Edge Reverse Proxy Template
export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': '*'
        }
      });
    }

    const origin = env.ORIGIN_URL || 'http://127.0.0.1:5000';
    const url = new URL(request.url);
    const target = new URL(url.pathname + url.search, origin);

    return fetch(target, {
      method: request.method,
      headers: request.headers,
      body: request.method !== 'GET' ? request.body : undefined
    });
  }
};
