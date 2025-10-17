import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default function handler(req, res) {
    res.sendFile("floodPrediction.html", { root: path.join(__dirname, '..', 'public') });
}