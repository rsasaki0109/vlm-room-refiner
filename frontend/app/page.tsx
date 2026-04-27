"use client";

import { useState } from "react";

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8010";

const MAX_IMAGE_BYTES = 8 * 1024 * 1024;
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "1";

type Result = Record<string, unknown>;

type ApiError = { status: number; title: string; message: string };

const demoResponse: Result = {
  room_type: "ワンルーム",
  style: "無印系ミニマル",
  problems: [
    "配線が床沿いに見えて生活感が出やすい",
    "収納が足りず、床に物が溜まりやすい",
    "照明が単一で陰影が弱い",
  ],
  recommendations: [
    "配線モールで壁沿いにまとめ、床の露出配線を減らす",
    "縦長ラック（幅60cm前後）を壁際に置き、床置き物を集約",
    "間接照明を1灯追加し、色温度を暖色寄りに統一",
  ],
  shopping_keywords: [
    "配線モール 白 粘着",
    "スチールラック 幅60 奥行30",
    "フロアライト 間接照明 調光 暖色",
  ],
};

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

function DemoForm() {
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
    if (DEMO_MODE) {
      await new Promise((r) => setTimeout(r, 450));
      setData(demoResponse);
      setLoading(false);
      return;
    }
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
    <section className="bg-white border border-zinc-200 rounded-2xl p-5 md:p-6 shadow-sm space-y-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold tracking-tight text-zinc-900">
            今すぐ試す
          </h2>
          <p className="text-xs sm:text-sm text-zinc-600 mt-1">
            画像をアップロードすると、部屋タイプ・スタイル推定、問題点、改善提案、購入候補キーワードを JSON で返します。
          </p>
        </div>
        {DEMO_MODE && (
          <span className="shrink-0 inline-flex items-center rounded-full border border-zinc-200 bg-white px-3 py-1 text-xs font-medium text-zinc-700">
            Demo（モック応答）
          </span>
        )}
      </div>

      <div>
        <label
          className="block text-sm font-medium text-zinc-800 mb-2"
          htmlFor="img"
        >
          部屋の画像
        </label>
        <p className="text-xs text-zinc-500 mb-2">
          形式: PNG / JPEG / WebP。1 枚あたり目安約 {MAX_IMAGE_BYTES / (1024 * 1024)}MB 以下、短辺 32px 以上。
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
          <label className="block text-xs text-zinc-500 mb-1">
            目標スタイル（任意）
          </label>
          <input
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            placeholder="例: 韓国風 / ミニマル"
            className="w-full text-sm border border-zinc-200 rounded-md px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-xs text-zinc-500 mb-1">
            予算感（任意）
          </label>
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

      <div className="flex flex-col sm:flex-row gap-2 sm:items-center sm:justify-between">
        <button
          type="button"
          onClick={() => void submit()}
          disabled={loading}
          className="w-full sm:w-auto rounded-md bg-zinc-900 text-white text-sm font-medium px-4 py-2.5 disabled:opacity-50"
        >
          {loading ? "分析中…" : "分析する"}
        </button>
        <p className="text-xs text-zinc-500">
          {DEMO_MODE ? "Pages では API なしでサンプル応答を返します。" : `API: ${apiBase}`}
        </p>
      </div>

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
          <h3 className="text-sm font-medium text-zinc-700 mb-2">応答（JSON）</h3>
          <pre className="text-xs sm:text-sm bg-zinc-900 text-zinc-100 rounded-xl p-4 overflow-x-auto whitespace-pre-wrap break-words">
            {prettyJson(data)}
          </pre>
        </section>
      )}
    </section>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(1000px_circle_at_20%_-10%,rgba(56,189,248,0.35),transparent_55%),radial-gradient(900px_circle_at_90%_20%,rgba(34,197,94,0.28),transparent_60%),linear-gradient(to_bottom,rgba(255,255,255,0.05),transparent_50%)]" />
        <div className="relative mx-auto max-w-5xl px-6 py-14 md:py-20">
          <div className="flex items-center justify-between gap-4">
            <p className="text-xs font-medium text-zinc-300/90">
              Local VLM • Ollama • Qwen2.5‑VL • FastAPI • Next.js
            </p>
            {DEMO_MODE && (
              <a
                className="text-xs text-zinc-200 hover:text-white underline underline-offset-4"
                href="https://github.com/rsasaki0109/vlm-room-refiner"
                target="_blank"
                rel="noreferrer"
              >
                GitHub
              </a>
            )}
          </div>

          <h1 className="mt-4 text-3xl md:text-5xl font-semibold tracking-tight">
            部屋写真から、改善の打ち手を
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 to-sky-300">
              {" "}
              JSON
            </span>
            で返す。
          </h1>
          <p className="mt-4 text-zinc-200/90 text-sm md:text-base max-w-2xl">
            画像を入れるだけで「部屋タイプ」「スタイル推定」「問題点」「改善提案」「購入候補キーワード」を最大5件ずつ。
            ローカルVLM（Ollama + Qwen2.5‑VL）で動く MVP です。
          </p>

          <div className="mt-8 flex flex-col sm:flex-row gap-3">
            <a
              href="#demo"
              className="inline-flex justify-center rounded-lg bg-white text-zinc-950 px-4 py-2.5 text-sm font-semibold hover:bg-zinc-200"
            >
              デモを試す
            </a>
            <a
              href="https://github.com/rsasaki0109/vlm-room-refiner#api"
              target="_blank"
              rel="noreferrer"
              className="inline-flex justify-center rounded-lg border border-white/20 bg-white/5 px-4 py-2.5 text-sm font-semibold hover:bg-white/10"
            >
              API / セットアップ
            </a>
          </div>

          <div className="mt-10 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm font-semibold">具体的な指摘</p>
              <p className="mt-1 text-xs text-zinc-200/80">
                抽象論ではなく、配線・収納・採光・配色・家具サイズ感などに触れる。
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm font-semibold">すぐ実行できる提案</p>
              <p className="mt-1 text-xs text-zinc-200/80">
                レイアウト・小物・照明・色の調整まで、優先度順に最大5件。
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-sm font-semibold">購入キーワード付き</p>
              <p className="mt-1 text-xs text-zinc-200/80">
                検索しやすい短いフレーズで、次の行動（買う/探す）に繋げる。
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-zinc-100 text-zinc-900">
        <div className="mx-auto max-w-5xl px-6 py-10 md:py-14 space-y-10">
          <section className="grid gap-6 md:grid-cols-3">
            <div className="md:col-span-1">
              <h2 className="text-lg font-semibold">How it works</h2>
              <p className="mt-2 text-sm text-zinc-600">
                画像+プロンプトを Ollama に送り、構造化 JSON を返します。Pages ではデモ用にモック応答で動かしています。
              </p>
            </div>
            <ol className="md:col-span-2 grid gap-3">
              {[
                ["Upload", "部屋画像をアップロード"],
                ["Analyze", "Qwen2.5‑VL に質問 → JSON 生成"],
                ["Act", "提案と検索キーワードで手を動かす"],
              ].map(([t, d]) => (
                <li
                  key={t}
                  className="rounded-xl border border-zinc-200 bg-white p-4"
                >
                  <p className="text-sm font-semibold">{t}</p>
                  <p className="mt-1 text-sm text-zinc-600">{d}</p>
                </li>
              ))}
            </ol>
          </section>

          <section id="demo" className="scroll-mt-16 space-y-4">
            <DemoForm />
          </section>

          <footer className="pt-2 flex flex-col sm:flex-row gap-2 sm:items-center sm:justify-between text-xs text-zinc-500">
            <p>© vlm-room-refiner • MVP</p>
            <p>
              Pages: モック応答 / Local: FastAPI + Ollama{" "}
              <span className="text-zinc-400">(Qwen2.5‑VL)</span>
            </p>
          </footer>
        </div>
      </div>
    </div>
  );
}
