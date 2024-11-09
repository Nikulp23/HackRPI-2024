import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import fs from 'fs';
import { fileURLToPath, pathToFileURL } from 'url';
import path from 'path';

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

const allowedOrigins = [
  'http://localhost:3000', 
  'http://localhost:8080', 
];

const corsOptions = {
  origin: (origin, callback) => {
    // Allow requests with no origin (like from Postman)
    if (!origin) return callback(null, true);

    if (allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  optionsSuccessStatus: 200,
};

app.use(cors(corsOptions));

// Function to recursively import routes
const importRoutesFromDirectory = (directory) => {
  fs.readdir(directory, { withFileTypes: true }, (err, files) => {
    if (err) {
      console.error('Could not list the directory.', err);
      process.exit(1);
    }

    files.forEach((dirent) => {
      const fullPath = path.join(directory, dirent.name);
      if (dirent.isDirectory()) {
        importRoutesFromDirectory(fullPath);
      } else if (dirent.name.endsWith('.js')) {
        const fileURL = pathToFileURL(fullPath).href;
        import(fileURL).then((router) => {
          app.use('/', router.default);
        });
      }
    });
  });
};

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const routesDirectory = path.join(__dirname, 'routes');

importRoutesFromDirectory(routesDirectory);

const port = 8080;
const server = app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
