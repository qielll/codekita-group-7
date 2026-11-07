import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
export default defineConfig({
  plugins: [react(), VitePWA({ registerType: "autoUpdate",
    manifest: { name: "CodeKita", short_name: "CodeKita", start_url: ".", display: "standalone",
      background_color: "#ffffff", theme_color: "#2563eb",
      icons: [{ src: "icon.svg", sizes: "any", type: "image/svg+xml" }] } })],
});
