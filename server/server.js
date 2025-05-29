const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const path = require('path');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
});

app.use(helmet({
  contentSecurityPolicy: false
}));
app.use(limiter);
app.use(cors());
app.use(express.json({ limit: '10mb' }));

app.use('/api/generate', require('./routes/generate'));
app.use('/api/rewrite', require('./routes/rewrite'));
app.use('/api/search', require('./routes/search'));
app.use('/api/images', require('./routes/images'));

if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../client/build')));
  
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../client/build/index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});