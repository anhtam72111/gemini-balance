const CACHE_NAME = 'gbalance-cache-v1';
const urlsToCache = [
  '/',
  '/static/manifest.json',
  '/static/icons/icon-192x192.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.open(CACHE_NAME).then(cache => {
      // 1. Try to get from cache
      return cache.match(event.request).then(responseFromCache => {
        // 2. Simultaneously fetch from network (background process)
        const fetchPromise = fetch(event.request).then(responseFromNetwork => {
          // 3. Network request success, update cache
          cache.put(event.request, responseFromNetwork.clone());
          return responseFromNetwork;
        }).catch(err => {
          // Network request failed, can choose to log error or do nothing
          console.error('Network fetch failed:', err);
          // Ensure even if network fails, if cache exists, we still return cache
          // If cache also doesn't exist, this Promise will reject
          throw err;
        });

        // 4. If cache exists, return cache immediately; otherwise wait for network response
        //    Background network request still ongoing to update cache
        return responseFromCache || fetchPromise;
      });
    })
  );
});

self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
