// Runs the backend virtualenv's Python with the given args, e.g. `node scripts/py.mjs -m pytest`.
import { backendDir, requireVenv, run, venvPython } from "./lib.mjs";

requireVenv();
run(venvPython, process.argv.slice(2), { cwd: backendDir });
