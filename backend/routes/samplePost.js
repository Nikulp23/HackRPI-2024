import express from 'express';
import { fileURLToPath } from 'url';
import path from 'path';
import dotenv from 'dotenv';
import axios from 'axios';
const router = express.Router();

// Get file route name (Same as file name)
const __filename = fileURLToPath(import.meta.url);
const parsed = path.parse(__filename);

dotenv.config();
// const apiKey = process.env.KEY;

router.post(`/${parsed.name}`, async (req, res) => {
  const value = req.body.value;
  if (value == undefined) {
    return res.status(400).json({ error: 'Value is required' });
  }

  res.send(value)
});

export default router;