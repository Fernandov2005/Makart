import { NextApiRequest, NextApiResponse } from 'next';
import { parse } from 'cookie';
import formidable from 'formidable';

export const config = {
  api: {
    bodyParser: false,
    sizeLimit: '50mb', // Set larger size limit
  },
};

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  // Handle CORS - allow multiple origins
  const origin = req.headers.origin;
  const allowedOrigins = [
    'https://makart.vercel.app',
    'http://localhost:3000',
    'https://localhost:3000'
  ];
  
  if (origin && (allowedOrigins.includes(origin) || origin.includes('.vercel.app'))) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Credentials', 'true');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    // Check authentication
    const cookies = parse(req.headers.cookie || '');
    const sessionData = cookies.session ? JSON.parse(cookies.session) : null;

    if (!sessionData || !sessionData.logged_in) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    // Parse form data with size limits
    const form = formidable({
      maxFileSize: 50 * 1024 * 1024, // 50MB limit
      maxFields: 10,
      allowEmptyFiles: false,
      filter: function ({ name, originalFilename, mimetype }) {
        // Only allow image files
        return name === 'file' && (mimetype?.includes('image/') || false);
      }
    });

    form.parse(req, (err, fields, files) => {
      if (err) {
        console.error('Upload parsing error:', err);
        
        if (err.code === 'LIMIT_FILE_SIZE') {
          res.status(413).json({ error: 'File too large. Maximum size is 50MB.' });
          return;
        }
        
        res.status(500).json({ error: 'Failed to parse upload' });
        return;
      }

      const file = Array.isArray(files.file) ? files.file[0] : files.file;
      const duration = Array.isArray(fields.duration) ? fields.duration[0] : fields.duration;
      const quality = Array.isArray(fields.quality) ? fields.quality[0] : fields.quality;
      const style = Array.isArray(fields.style) ? fields.style[0] : fields.style;

      if (!file) {
        res.status(400).json({ error: 'No file uploaded' });
        return;
      }

      // Check file size on our end too
      if (file.size > 50 * 1024 * 1024) {
        res.status(413).json({ error: 'File too large. Maximum size is 50MB.' });
        return;
      }

      // Simulate processing and return a demo animation result
      const animationResult = {
        success: true,
        filename: file.originalFilename || 'uploaded-image',
        duration: duration || '10',
        quality: quality || 'ultra',
        style: style || 'particle_powder',
        processingTime: `${Math.floor(Math.random() * 30) + 10}s`,
        fileSize: `${(file.size / 1024 / 1024).toFixed(2)}MB`,
        message: '🎉 Animation created successfully! (Demo mode)',
        downloadUrl: '/demo-animation.mp4'
      };

      // Return JSON response with success data
      res.status(200).json(animationResult);
    });

  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Upload failed' });
  }
} 