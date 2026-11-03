import axios from "axios";
import { useEffect, useState } from "react";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

type Status = "checking" | "online" | "offline";

export default function App() {
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => {
    axios
      .get(`${baseURL}/health`)
      .then(() => setStatus("online"))
      .catch(() => setStatus("offline"));
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <h1 className="text-2xl font-extrabold tracking-tight">SupportAgent Desk</h1>
        <p className="mt-2 text-sm text-slate-500">Project scaffold is running.</p>
        <p className="mt-5 text-sm font-semibold">
          Backend:{" "}
          <span className={status === "online" ? "text-emerald-600" : status === "offline" ? "text-red-600" : "text-slate-400"}>
            {status}
          </span>
        </p>
      </div>
    </main>
  );
}
