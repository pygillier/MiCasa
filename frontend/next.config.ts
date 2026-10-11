import { readFileSync } from "node:fs";
import type { NextConfig } from "next";

const API_URL = process.env.API_URL ?? "http://localhost:5000";

const { version } = JSON.parse(readFileSync("./package.json", "utf8"));

const nextConfig: NextConfig = {
  env: { NEXT_PUBLIC_APP_VERSION: version },
  output: "standalone",
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_URL}/api/:path*` }];
  },
};

export default nextConfig;
