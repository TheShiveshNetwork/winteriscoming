/** @type {import("eslint").Linter.Config} */
module.exports = {
  parser: "@typescript-eslint/parser",
  plugins: ["@typescript-eslint", "import"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/strict-type-checked",
    "plugin:@typescript-eslint/stylistic-type-checked",
    "plugin:import/recommended",
    "plugin:import/typescript"
  ],
  rules: {
    "@typescript-eslint/consistent-type-imports":        ["error", { prefer: "type-imports" }],
    "@typescript-eslint/no-unused-vars":                 ["error", { argsIgnorePattern: "^_" }],
    "@typescript-eslint/explicit-function-return-type":  "error",
    "import/order": ["error", {
      "groups": ["builtin","external","internal","parent","sibling","index"],
      "newlines-between": "always",
      "alphabetize": { "order": "asc" }
    }]
  }
}
