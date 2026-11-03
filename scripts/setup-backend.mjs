// Creates backend/venv and installs requirements. No manual venv activation needed.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";
import { backendDir, findPython, venvDir, venvPython } from "./lib.mjs";

const py = findPython();
if (!py && !existsSync(venvPython)) {
  console.error("Python 3.12+ was not found on PATH. Install it from https://www.python.org/downloads/ and retry.");
  process.exit(1);
}

function exec(cmd, args) {
  const res = spawnSync(cmd, args, { stdio: "inherit", cwd: backendDir });
  if (res.status !== 0) process.exit(res.status ?? 1);
}

if (!existsSync(venvPython)) {
  console.log(`Creating virtual environment in ${venvDir}`);
  exec(py.cmd, [...py.pre, "-m", "venv", venvDir]);
}
console.log("Installing backend requirements");
exec(venvPython, ["-m", "pip", "install", "--disable-pip-version-check", "-r", join(backendDir, "requirements.txt")]);
console.log("Backend ready.");
