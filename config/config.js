require('dotenv').config()

module.exports = {
  port: process.env.PORT || 3000,
//   mongoose: process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/your-db-name'
}
