import { frontendDir, isWindows, loadEnv, run } from "./lib.mjs";

const env = loadEnv();
const host = env.BACKEND_HOST && env.BACKEND_HOST !== "0.0.0.0" ? env.BACKEND_HOST : "127.0.0.1";
const apiBase = env.VITE_API_BASE_URL || `http://${host}:${env.BACKEND_PORT || "8000"}/api`;
run(isWindows ? "npm.cmd" : "npm", ["run", "dev"], {
  cwd: frontendDir,
  env: { ...process.env, VITE_API_BASE_URL: apiBase },
  shell: isWindows,
});
