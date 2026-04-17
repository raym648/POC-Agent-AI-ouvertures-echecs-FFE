// POC-Agent-AI-ouvertures-echecs-FFE/frontend/server.js
// Serveur Node minimal pour valider le conteneur

const http = require("http");

const PORT = 4200;

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ status: "frontend running" }));
});

server.listen(PORT, () => {
  console.log(`Frontend running on http://localhost:${PORT}`);
});
