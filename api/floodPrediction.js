import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default async function handler(req, res) {
  try {
    const filePath = path.join(__dirname, '..', 'public', 'floodPrediction.html');
    const fileContent = fs.readFileSync(filePath, 'utf8');

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.status(200).send(fileContent);
  } catch (error) {
    console.error('Error reading HTML file:', error);
    res.status(500).send('Error loading page.');
  }
}
