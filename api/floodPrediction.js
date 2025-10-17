import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default function handler(req, res) {
  const filePath = path.join(__dirname, '..', 'public', 'floodPrediction.html');
  const fileContent = fs.readFileSync(filePath, 'utf8');

  res.setHeader('Content-Type', 'text/html');
  res.status(200).send(fileContent);
}
