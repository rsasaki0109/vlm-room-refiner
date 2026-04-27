import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // ルートにも package-lock がある場合のファイルトレース警告を抑える
  outputFileTracingRoot: path.join(__dirname, ".."),
};

export default nextConfig;
