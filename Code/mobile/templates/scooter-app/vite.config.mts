import { defineConfig } from "vite";
import Vue from "@vitejs/plugin-vue";
import Vuetify, { transformAssetUrls } from "vite-plugin-vuetify";
import Components from "unplugin-vue-components/vite";
import ViteFonts from "unplugin-fonts/vite";
import { fileURLToPath, URL } from "node:url";

export default defineConfig({
  base: "/",
  plugins: [
    Vue({ template: { transformAssetUrls } }),
    Vuetify(),
    Components(),
    ViteFonts({
      google: {
        families: [{ name: "Roboto", styles: "wght@100;300;400;500;700;900" }],
      },
    }),
  ],
  define: { "process.env": {} },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
    extensions: [".js", ".json", ".jsx", ".mjs", ".ts", ".tsx", ".vue"],
  },
  css: {
    preprocessorOptions: {
      sass: { api: "modern-compiler" },
    },
  },
  build: {
    outDir: "../dist_vue",
    emptyOutDir: true,
  },
});
