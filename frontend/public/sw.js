// sw.js — Service Worker for PWA offline support
// Story: REM-039 — PWA Offline Support
// Strategy: Cache-first for static assets, Network-first for API calls

const CACHE_NAME = 'consulta-processual-v1';

// Static assets to pre-cache on install
const PRECACHE_URLS = [
  '/',
  '/manifest.json',
];

// ── Install: pre-cache static shell ─────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    })
  );
  // Take control immediately (skip waiting)
  self.skipWaiting();
});

// ── Activate: clean up old caches ────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  // Take control of all clients immediately
  self.clients.claim();
});

// ── Fetch: hybrid strategy ────────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests and cross-origin requests
  if (request.method !== 'GET' || url.origin !== location.origin) {
    return;
  }

  // API calls: Network-first (fresh data preferred)
  if (url.pathname.startsWith('/processes') ||
      url.pathname.startsWith('/health') ||
      url.pathname.startsWith('/stats') ||
      url.pathname.startsWith('/history') ||
      url.pathname.startsWith('/settings') ||
      url.pathname.startsWith('/sql')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful API responses briefly
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => {
          // Offline: return cached API response if available
          return caches.match(request).then((cached) => {
            if (cached) return cached;
            // Return offline JSON response
            return new Response(
              JSON.stringify({ error: 'Sem conexao. Dados podem estar desatualizados.' }),
              { status: 503, headers: { 'Content-Type': 'application/json' } }
            );
          });
        })
    );
    return;
  }

  // Static assets: Cache-first
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;

      return fetch(request).then((response) => {
        if (!response.ok) return response;

        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        return response;
      }).catch(() => {
        // For navigation requests offline, return the cached root
        if (request.mode === 'navigate') {
          return caches.match('/');
        }
        return new Response('Offline', { status: 503 });
      });
    })
  );
});
