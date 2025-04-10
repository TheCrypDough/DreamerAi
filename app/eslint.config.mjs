import { defineConfig } from "eslint/config";
import js from "@eslint/js";
import globals from "globals";
import pluginReact from "eslint-plugin-react";
import pluginJsxA11y from "eslint-plugin-jsx-a11y";
import pluginImport from "eslint-plugin-import";
import json from "@eslint/json";


export default defineConfig([
  { files: ["**/*.{js,mjs,cjs,jsx}"], plugins: { js }, extends: ["js/recommended"] },
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    plugins: {
        import: pluginImport
    },
    extends: ["airbnb-base"],
    settings: {
      "import/resolver": {
        node: {
          extensions: [".js", ".jsx", ".mjs", ".cjs"]
        }
      }
    },
    rules: {
        "import/extensions": [
            "error",
            "ignorePackages",
            {
              js: "never",
              jsx: "never",
              mjs: "never",
              cjs: "never",
            }
         ],
         "no-console": "warn",
    }
  },
  {
    files: ["**/*.{js,jsx,mjs,cjs}"],
    plugins: {
        react: pluginReact,
        "jsx-a11y": pluginJsxA11y,
    },
    languageOptions: {
        parserOptions: {
            ecmaFeatures: {
                jsx: true,
            },
        },
        globals: {
            ...globals.browser,
        },
    },
    extends: [
        "plugin:react/jsx-runtime",
        "plugin:jsx-a11y/recommended",
        "airbnb",
    ],
    settings: {
        react: {
          version: "detect",
        },
        "import/resolver": {
            node: {
              extensions: [".js", ".jsx", ".mjs", ".cjs"]
            }
        }
    },
    rules: {
        "react/jsx-filename-extension": ["warn", { "extensions": [".js", ".jsx"] }],
        "react/react-in-jsx-scope": "off",
        "react/prop-types": "warn",
        "import/extensions": [
            "error",
            "ignorePackages",
            {
              js: "never",
              jsx: "never",
              mjs: "never",
              cjs: "never",
            }
         ],
         "no-console": "warn",
    },
  },
  { files: ["**/*.json"], plugins: { json }, languageOptions: { parser: json.parse }, extends: ["json/recommended"] },
  { files: ["**/*.jsonc"], plugins: { json }, languageOptions: { parser: json.parse }, extends: ["json/recommended"] },
  { files: ["**/*.json5"], plugins: { json }, languageOptions: { parser: json.parse }, extends: ["json/recommended"] },
]);