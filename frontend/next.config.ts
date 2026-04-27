import path from "path";
import type { NextConfig } from "next";

const isPages = process.env.GITHUB_PAGES === "true";

const nextConfig: NextConfig = {
  // ルートにも package-lock がある場合のファイルトレース警告を抑える
  outputFileTracingRoot: path.join(__dirname, ".."),
  // Playwright 等で 127.0.0.1 から開くケースの警告回避
  allowedDevOrigins: ["http://127.0.0.1", "http://localhost"],
  // GitHub Pages 用（静的書き出し + basePath）
  ...(isPages
    ? {
        output: "export",
        images: { unoptimized: true },
        trailingSlash: true,
        basePath: "/vlm-room-refiner",
        assetPrefix: "/vlm-room-refiner/",
      }
    : {}),
};

export default nextConfig;
