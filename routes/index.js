const express = require('express')
const multer = require('multer')
const { scanCnic } = require('../controllers/scan')

const router = express.Router()
const upload = multer({ storage: multer.memoryStorage() })

router.post('/cnic/scan/', upload.single('image'), scanCnic)

module.exports = router
