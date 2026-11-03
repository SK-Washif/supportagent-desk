import { backendDir, loadEnv, requireVenv, run, venvPython } from "./lib.mjs";

requireVenv();
const env = loadEnv();
const host = env.BACKEND_HOST || "127.0.0.1";
const port = env.BACKEND_PORT || "8000";
console.log(`Backend: http://${host}:${port}  (docs: /docs)`);
run(
  venvPython,
  ["-m", "uvicorn", "app.main:create_app", "--factory", "--reload", "--reload-dir", "app", "--host", host, "--port", port],
  { cwd: backendDir },
);
