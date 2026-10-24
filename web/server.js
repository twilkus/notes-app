const express = require("express");
const { createProxyMiddleware } = require("http-proxy-middleware");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL || "http://127.0.0.1:8000";

// Forward /api/* requests to the Python service
app.use(
  "/api",
  createProxyMiddleware({
    target: API_URL,
    changeOrigin: true,
    pathRewrite: (p) => "/api" + p,
  })
);

// Serve the static page
app.use(express.static(path.join(__dirname, "public")));

app.listen(PORT, () => {
  console.log(`Web listening on port ${PORT}, proxying /api to ${API_URL}`);
});