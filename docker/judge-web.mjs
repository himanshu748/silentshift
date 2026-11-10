// Keep the checkout read-only; npm and Vite write only to this project's volume.
import { cpSync, mkdirSync } from "node:fs";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";

const source = "/source/web";
const target = "/work";
const excluded = new Set([
  "node_modules", "dist", "playwright-report", "test-results", ".git",
]);

mkdirSync(target, { recursive: true });
cpSync(source, target, {
  recursive: true,
  filter(file) {
    const parts = path.relative(source, file).split(path.sep);
    return !parts.some((part) => excluded.has(part) || part.startsWith(".env"));
  },
});
const install = spawnSync("npm", ["ci", "--no-audit", "--no-fund"], {
  cwd: target,
  stdio: "inherit",
});
if (install.error || install.status !== 0) {
  console.error("Workbench dependency installation failed; no replay was run.");
  process.exit(1);
}
const server = spawn("npm", [
  "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173", "--strictPort",
], { cwd: target, stdio: "inherit" });
for (const signal of ["SIGTERM", "SIGINT"]) {
  process.on(signal, () => server.kill(signal));
}
server.on("error", () => {
  console.error("Workbench could not start.");
  process.exitCode = 1;
});
server.on("exit", (code, signal) => {
  process.exitCode = code ?? (signal ? 1 : 0);
});
