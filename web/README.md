# SilentShift evidence workbench

React, strict TypeScript, Vite, runtime-validated JSON boundaries, and self-hosted Manrope / IBM Plex Mono. The seven views use the native IRIS API. No seeded operational records, mock provider or synthetic benchmark results are served by the frontend.

```sh
npm ci
npm run dev
```

Open the loopback URL printed by Vite. Without a reachable native stack, the interface displays an unavailable state and keeps metrics unknown. This state does not demonstrate the native workflow. Follow the root README for the required build 154 setup and verification.

The development proxy defaults to `http://127.0.0.1:52773/silentshift`:

```sh
IRIS_API_ORIGIN=http://127.0.0.1:52773/silentshift npm run dev
```

`/api/health` therefore becomes `/silentshift/api/health` on the configured gateway. The variable includes the application base path. The browser uses same-origin requests; it cannot select an arbitrary remote API from the UI. A failed upstream connection produces JSON HTTP 503 with `IRIS_UNAVAILABLE`.

Connect with the username and password of a configured IRIS viewer account. Basic authorization is retained only in module memory, never browser storage or URLs. Reloading clears it. Reviews require the server's reviewer permission. Use HTTPS for any non-loopback deployment.

```sh
npm run check
npm run build
```

The production build is a browser client. Its hosting server must forward `/api` to the native API with the same path mapping; Vite's development proxy is not included in static assets. Do not publish a disconnected static build as a working online-native demo.

Case, health, scenario, policy, overview and evaluation responses are validated with Zod. Malformed responses show a contract error instead of substituting values. Scenario injections use a client-generated UUID and reuse it on retry after a failed response. Human reviews send an idempotency key and expected case version. Manual message JSON is forwarded as entered so native strict parsing can reject duplicate keys; the browser does not normalize it into a different payload first.

Fonts use the SIL Open Font License. Notices ship in `public/licenses/`. UI icons are from the ISC-licensed `lucide-react` package. `npm ci` installs the versions pinned by `package-lock.json`.
