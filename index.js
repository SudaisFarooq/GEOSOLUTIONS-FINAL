// index.js
import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/floodPrediction', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'floodPrediction.html'));
});

app.get('/test', (req, res) => {
  res.send('Server is running correctly.');
});

app.post('/predict', (req, res) => {
  const { startDate, endDate, latitude, longitude } = req.body;

  if (!startDate || !endDate || latitude == null || longitude == null) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  const pythonPath = path.join('venv', 'bin', 'python'); // adjust if using Windows
  const scriptPath = path.join('api', 'predict.py');

  const py = spawn(pythonPath, [scriptPath, startDate, endDate, latitude, longitude]);

  let data = '';
  let errorOutput = '';

  py.stdout.on('data', chunk => data += chunk.toString());
  py.stderr.on('data', chunk => errorOutput += chunk.toString());

  py.on('close', code => {
    if (code !== 0) {
      console.error(errorOutput);
      return res.status(500).json({ error: errorOutput });
    }
    try {
      res.json(JSON.parse(data));
    } catch (e) {
      console.error(e);
      res.status(500).json({ error: 'Invalid JSON from Python script' });
    }
  });
});

app.listen(PORT, () => console.log(`🚀 Flood prediction server running on http://localhost:${PORT}`));
