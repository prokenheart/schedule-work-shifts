require("dotenv").config();
const express = require("express");
const { spawn } = require("child_process");
const path = require("path");

const app = express();
app.use(express.json());

// API sắp ca
app.post("/api/schedule", (req, res) => {
  const pyPath = path.join(__dirname, "scheduler.py");

  const py = spawn("python", [pyPath]);

  let output = "";
  let error = "";

  py.stdout.on("data", (data) => {
    output += data.toString();
  });

  py.stderr.on("data", (data) => {
    error += data.toString();
  });

  py.on("close", (code) => {
    if (code !== 0 || error) {
      return res.status(500).json({
        status: "error",
        message: error || "Python execution failed"
      });
    }

    try {
      const result = JSON.parse(output);
      res.json(result);
    } catch (e) {
      res.status(500).json({
        status: "error",
        message: "Invalid JSON from Python"
      });
    }
  });
});

app.listen(3000, () => {
  console.log("Server running at http://localhost:3000");
});

app.use(express.static("public"));
