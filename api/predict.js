export default function handler(req, res) {
 const { startDate, endDate, latitude, longitude } = req.body;
 
   if (!startDate || !endDate || latitude == null || longitude == null) {
     return res.status(400).json({ error: "Missing required fields" });
   }
 
   const pythonPath = path.join('venv', 'bin', 'python'); // adjust if using Windows
   const scriptPath = path.join('model', 'predict.py');
 
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
}