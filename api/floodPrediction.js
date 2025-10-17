import path from 'path';
import { fileURLToPath } from 'url';

// Recreate __dirname and __filename in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default function handler(req, res) {
  const filePath = path.join(__dirname, '..', 'public', 'floodPrediction.html');
  res.sendFile(filePath);
}
