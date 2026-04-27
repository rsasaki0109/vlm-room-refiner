"use client";

import { useState } from "react";

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8010";

const MAX_IMAGE_BYTES = 8 * 1024 * 1024;

type Result = Record<string, unknown>;

type ApiError = { status: number; title: string; message: string };

function prettyJson(v: Result) {
  return JSON.stringify(v, null, 2);
}

function detailToString(d: unknown): string {
  if (d === undefined || d === null) {
    return "";
  }
  if (typeof d === "string") {
    return d;
  }
  if (Array.isArray(d)) {
    return d
      .map((x) => {
        if (x && typeof x === "object" && "msg" in x) {
          return String((x as { msg: string }).msg);
        }
        return JSON.stringify(x);
      })
      .join(" ");
  }
  return String(d);
}

function parseApiError(
  r: Response,
  body: unknown
): ApiError {
  const status = r.status;
  const message = detailToString(
    body && typeof body === "object" && body && "detail" in body
      ? (body as { detail: unknown }).detail
      : undefined
  );
  const title =
    status === 400
      ? "リクエストを確認してください"
      : status === 413
        ? "ファイルが大きすぎます"
        : status === 502
          ? "Ollama 側のエラー"
          : status === 503
            ? "Ollama に接続できません"
            : `通信エラー (${status})`;
  return {
    status,
    title,
    message: message || r.statusText,
  };
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [style, setStyle] = useState("");
  const [budget, setBudget] = useState("");
  const [beforeAfter, setBeforeAfter] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [data, setData] = useState<Result | null>(null);

  function onFileChange(f: File | null) {
    setFile(f);
    setData(null);
    setError(null);
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    setPreview(f ? URL.createObjectURL(f) : null);
  }

  async function submit() {
    if (!file) {
      setError({
        status: 0,
        title: "画像がありません",
        message: "分析する前に、部屋の画像を選んでください。",
      });
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      setError({
        status: 0,
        title: "ファイルが大きすぎます",
        message: `1 枚あたり約${MAX_IMAGE_BYTES / (1024 * 1024)}MB 以下の画像を選び、縮小・再エクスポートしてから試してください。`,
      });
      return;
    }
    setLoading(true);
    setError(null);
    setData(null);
    const form = new FormData();
    form.append("file", file);
    if (style.trim()) {
      form.append("style", style.trim());
    }
    if (budget.trim()) {
      form.append("budget", budget.trim());
    }
    form.append("before_after", beforeAfter ? "true" : "false");
    try {
      const r = await fetch(`${apiBase}/analyze`, {
        method: "POST",
        body: form,
      });
      const raw = (await r.json().catch(() => ({}))) as unknown;
      if (!r.ok) {
        setError(parseApiError(r, raw));
        return;
      }
      setData(raw as Result);
    } catch (e) {
      setError({
        status: 0,
        title: "接続に失敗しました",
        message: e instanceof Error ? e.message : "ネットワークまたはサーバー設定を確認してください。",
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-zinc-100 text-zinc-900 p-6 md:p-10">
      <div className="max-w-3xl mx-auto space-y-8">
        <header>
          <h1 className="text-2xl font-semibold tracking-tight">vlm-room-refiner</h1>
          <p className="text-sm text-zinc-600 mt-1">
            部屋の画像をアップロードすると、Ollama 上の Qwen2.5-VL
            による分析結果（JSON）を返します。短辺が極端に小さいと失敗しやすいため、
            ある程度の解像度（目安: 各辺 32 ピクセル以上）を推奨します。
          </p>
        </header>

        <section className="bg-white border border-zinc-200 rounded-xl p-5 shadow-sm space-y-4">
          <div>
            <label
              className="block text-sm font-medium text-zinc-800 mb-2"
              htmlFor="img"
            >
              部屋の画像
            </label>
            <p className="text-xs text-zinc-500 mb-2">
              形式: 一般的な画像（PNG / JPEG / WebP 等）。1 枚あたり目安
              約 {MAX_IMAGE_BYTES / (1024 * 1024)}MB 以下。
            </p>
            <input
              id="img"
              type="file"
              accept="image/*"
              onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
              className="block w-full text-sm"
            />
          </div>
          {preview && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={preview}
              alt="preview"
              className="max-h-56 w-full object-contain rounded-lg border border-zinc-200 bg-zinc-50"
            />
          )}

          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="block text-xs text-zinc-500 mb-1">目標スタイル（任意）</label>
              <input
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                placeholder="例: 韓国風 / ミニマル"
                className="w-full text-sm border border-zinc-200 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-xs text-zinc-500 mb-1">予算感（任意）</label>
              <input
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="例: 1万円前後"
                className="w-full text-sm border border-zinc-200 rounded-md px-3 py-2"
              />
            </div>
          </div>
          <label className="flex items-center gap-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={beforeAfter}
              onChange={(e) => setBeforeAfter(e.target.checked)}
            />
            Before/After 的な文言を積極的に入れる
          </label>

          <button
            type="button"
            onClick={() => void submit()}
            disabled={loading}
            className="w-full sm:w-auto rounded-md bg-zinc-900 text-white text-sm font-medium px-4 py-2.5 disabled:opacity-50"
          >
            {loading ? "分析中…" : "分析する"}
          </button>
        </section>

        {error && (
          <div
            className="text-sm bg-red-50 border border-red-200 rounded-md px-4 py-3 space-y-1"
            role="alert"
          >
            <p className="font-medium text-red-900">{error.title}</p>
            <p className="text-red-800 whitespace-pre-wrap break-words">
              {error.message}
            </p>
            {error.status > 0 && (
              <p className="text-xs text-red-600/90">HTTP {error.status}</p>
            )}
          </div>
        )}

        {data && (
          <section>
            <h2 className="text-sm font-medium text-zinc-700 mb-2">応答（JSON）</h2>
            <pre className="text-xs sm:text-sm bg-zinc-900 text-zinc-100 rounded-xl p-4 overflow-x-auto whitespace-pre-wrap break-words">
              {prettyJson(data)}
            </pre>
          </section>
        )}
      </div>
    </div>
  );
}
