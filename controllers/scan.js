const { spawn } = require('child_process')
const fs = require('fs')
const path = require('path')

const scanCnic = async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No image uploaded' })

  // Ensure 'uploads' folder exists
  const uploadsDir = path.join(__dirname, '../uploads')
  if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir)

  const imagePath = path.join(uploadsDir, `${Date.now()}_${req.file.originalname}`)
  fs.writeFileSync(imagePath, req.file.buffer)
//   console.log('Image saved at:', imagePath);

  const pythonProcess = spawn('python', ['controllers/cnic-ocr.py', imagePath])

  let result = ''
  pythonProcess.stdout.on('data', data => { result += data.toString() })

  pythonProcess.stderr.on('data', data => {
    console.error('Python error:', data.toString())
  })

  pythonProcess.on('close', code => {
    fs.unlinkSync(imagePath) // cleanup temp file

    if (code !== 0) return res.status(500).json({ error: 'Python script failed' })

    try {
      const parsed = JSON.parse(result)
      res.json(parsed)
    } catch (e) {
      res.status(500).json({ error: 'Invalid JSON from Python' })
    }
  })
}

module.exports = { scanCnic }
