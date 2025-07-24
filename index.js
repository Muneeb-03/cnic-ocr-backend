const express = require('express')
const mongoose = require('mongoose')
const config = require('./config/config')

const app = express()
const mainRoute = require('./routes/index')

app.use('/api/', mainRoute)
// Base route
app.get('/', (req, res) => {
  res.send('CNIC OCR Backend is running')
})

// Connect to MongoDB and start the server
// mongoose.connect(config.mongoose)
//   .then(() => {
//     console.log('✅ MongoDB connected')

    app.listen(config.port, () => {
      console.log(`🚀 Server is running on port ${config.port}`)
    })
//   })
//   .catch((err) => {
//     console.error('❌ Failed to connect to MongoDB:', err)
//   })
