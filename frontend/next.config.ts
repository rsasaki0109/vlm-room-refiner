import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // ルートにも package-lock がある場合のファイルトレース警告を抑える
  outputFileTracingRoot: path.join(__dirname, ".."),
  // Playwright 等で 127.0.0.1 から開くケースの警告回避
  allowedDevOrigins: ["http://127.0.0.1", "http://localhost"],
};

export default nextConfig;
