// Shared helpers for cross-platform dev scripts (Windows PowerShell, macOS, Linux).
import { spawn, spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
export const backendDir = join(root, "backend");
export const frontendDir = join(root, "frontend");
export const isWindows = process.platform === "win32";
export const venvDir = join(backendDir, "venv");
export const venvPython = join(venvDir, isWindows ? "Scripts" : "bin", isWindows ? "python.exe" : "python");

/** Minimal .env parser; backend/.env overrides the root .env. Process env wins over both. */
export function loadEnv() {
  const values = {};
  for (const file of [join(root, ".env"), join(backendDir, ".env")]) {
    if (!existsSync(file)) continue;
    for (const line of readFileSync(file, "utf8").split(/\r?\n/)) {
      const match = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/);
      if (match) values[match[1]] = match[2].replace(/^["']|["']$/g, "");
    }
  }
  return { ...values, ...process.env };
}

/** Find a usable Python >= 3.12 on PATH (python3, python, or the Windows `py` launcher). */
export function findPython() {
  const candidates = isWindows
    ? [["py", ["-3"]], ["python", []], ["python3", []]]
    : [["python3", []], ["python", []]];
  for (const [cmd, pre] of candidates) {
    const res = spawnSync(cmd, [...pre, "-c", "import sys;print(sys.version_info[0]*100+sys.version_info[1])"], {
      encoding: "utf8",
    });
    if (res.status === 0 && Number(res.stdout.trim()) >= 312) return { cmd, pre };
  }
  return null;
}

export function requireVenv() {
  if (!existsSync(venvPython)) {
    console.error("Backend virtual environment not found. Run `npm run install:all` first.");
    process.exit(1);
  }
}

export function run(cmd, args, options = {}) {
  const child = spawn(cmd, args, { stdio: "inherit", ...options });
  child.on("exit", (code, signal) => process.exit(code ?? (signal ? 1 : 0)));
  for (const sig of ["SIGINT", "SIGTERM"]) process.on(sig, () => child.kill(sig));
  return child;
}
