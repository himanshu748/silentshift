import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";

// Each public page is a real HTML document so it can be loaded and refreshed directly.
// The workbench stays on the root document and keeps its hash routes.
const pages = ["how-it-works", "product", "safeguards", "evidence-record", "run-locally"];
const entry = (path: string) => fileURLToPath(new URL(path, import.meta.url));

const irisApiOrigin = new URL(
  process.env.IRIS_API_ORIGIN ?? "http://127.0.0.1:52773/silentshift",
);

export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: irisApiOrigin.origin,
        changeOrigin: true,
        rewrite: (path) =>
          `${irisApiOrigin.pathname.replace(/\/$/, "")}${path}`,
        configure(proxy) {
          proxy.on("error", (_error, _request, response) => {
            if ("writeHead" in response && !response.headersSent) {
              response.writeHead(503, { "Content-Type": "application/json" });
              response.end(
                JSON.stringify({
                  error: {
                    code: "IRIS_UNAVAILABLE",
                    message:
                      "The native IRIS API could not be reached. Start the build 154 stack, then refresh.",
                  },
                }),
              );
            }
          });
        },
      },
    },
  },
  build: {
    sourcemap: false,
    rollupOptions: {
      input: Object.fromEntries([
        ["home", entry("./index.html")],
        ...pages.map((page) => [page, entry(`./${page}/index.html`)]),
      ]),
    },
  },
});
