const express = require('express');
const path = require('path');
const app = express();
const port = process.env.PORT || 8080;

// Serve all static files from current directory
app.use(express.static(path.join(__dirname)));

// For any route, send index.html (for single page app)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(port, () => {
  console.log(`✅ Mini App server running on port ${port}`);
});