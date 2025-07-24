const express = require('express')
const multer = require('multer')
const { scanCnic ,scanAlumni} = require('../controllers/scan')

const router = express.Router()
const upload = multer({ storage: multer.memoryStorage() })

router.post('/cnic/scan/', upload.single('image'), scanCnic)
router.post('/alumni/scan',upload.single('image'),scanAlumni)
module.exports = router
