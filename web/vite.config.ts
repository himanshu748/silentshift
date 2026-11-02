import { defineConfig } from "vite";

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
  build: { sourcemap: false },
});
