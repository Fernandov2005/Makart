import { NextApiRequest, NextApiResponse } from 'next';
import { parse } from 'cookie';
import formidable from 'formidable';

export const config = {
  api: {
    bodyParser: false,
    sizeLimit: '25mb', // More conservative limit
    responseLimit: false,
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

  console.log('Upload request received - Content-Length:', req.headers['content-length']);

  try {
    // Check authentication
    const cookies = parse(req.headers.cookie || '');
    const sessionData = cookies.session ? JSON.parse(cookies.session) : null;

    if (!sessionData || !sessionData.logged_in) {
      res.status(401).json({ error: 'Authentication required. Please log in again.' });
      return;
    }

    console.log('Processing upload request...');

    // Parse form data with conservative settings
    const form = formidable({
      maxFileSize: 20 * 1024 * 1024, // 20MB limit (conservative)
      maxFields: 10,
      maxFieldsSize: 10 * 1024 * 1024, // 10MB for form fields
      allowEmptyFiles: false,
      keepExtensions: true,
      multiples: false,
      filter: function ({ name, originalFilename, mimetype }) {
        console.log(`Upload filter: name=${name}, filename=${originalFilename}, mimetype=${mimetype}`);
        // Only allow image files
        const isValidField = name === 'file' || name === 'duration' || name === 'quality' || name === 'style';
        const isValidMimeType = !mimetype || mimetype.includes('image/');
        return isValidField && (name !== 'file' || isValidMimeType);
      }
    });

    form.parse(req, (err, fields, files) => {
      if (err) {
        console.error('Upload parsing error:', err);
        console.error('Error details:', { 
          code: err.code, 
          message: err.message,
          httpCode: err.httpCode,
          receivedSize: err.receivedSize 
        });
        
        // Enhanced error handling
        if (err.code === 'LIMIT_FILE_SIZE' || err.code === 1009 || err.message.includes('maxFileSize')) {
          const fileSize = err.receivedSize ? Math.round(err.receivedSize / 1024 / 1024) : 'unknown';
          res.status(413).json({ 
            error: 'File too large. Please use images under 15MB for better compatibility.',
            details: `Your file size: ${fileSize}MB. Try compressing your image or using a smaller resolution.`,
            maxSize: '15MB'
          });
          return;
        }
        
        if (err.code === 'LIMIT_FIELD_VALUE' || err.message.includes('maxFieldsSize')) {
          res.status(413).json({ error: 'Form data too large. Please try again.' });
          return;
        }

        if (err.code === 'LIMIT_UNEXPECTED_FILE' || err.message.includes('Unexpected field')) {
          res.status(400).json({ error: 'Invalid file upload format.' });
          return;
        }

        // Generic error with more helpful message
        res.status(400).json({ 
          error: 'Upload failed. Please try a smaller image (under 10MB).',
          details: `Error: ${err.message}`,
          suggestion: 'Try compressing your image or reducing its resolution.'
        });
        return;
      }

      const file = Array.isArray(files.file) ? files.file[0] : files.file;
      const duration = Array.isArray(fields.duration) ? fields.duration[0] : fields.duration;
      const quality = Array.isArray(fields.quality) ? fields.quality[0] : fields.quality;
      const style = Array.isArray(fields.style) ? fields.style[0] : fields.style;

      console.log(`File received: ${file?.originalFilename}, size: ${file?.size} bytes (${Math.round((file?.size || 0) / 1024 / 1024 * 100) / 100}MB)`);

      if (!file) {
        res.status(400).json({ error: 'No file uploaded. Please select an image file.' });
        return;
      }

      // Validate file type
      if (!file.mimetype || !file.mimetype.startsWith('image/')) {
        res.status(415).json({ error: 'Invalid file type. Please upload a PNG, JPG, or JPEG image.' });
        return;
      }

      // Conservative file size check
      if (file.size > 15 * 1024 * 1024) { // 15MB conservative limit
        res.status(413).json({ 
          error: 'File too large for processing. Please use images under 15MB.',
          fileSize: `${Math.round(file.size / 1024 / 1024)}MB`,
          maxSize: '15MB',
          suggestion: 'Try compressing your image or reducing its resolution.'
        });
        return;
      }

      // Validate file has actual content
      if (file.size < 1024) { // Less than 1KB
        res.status(400).json({ error: 'File appears to be empty or corrupted.' });
        return;
      }

      console.log('File validation passed, creating demo response...');

      // Simulate processing time and return a demo animation result
      const animationResult = {
        success: true,
        filename: file.originalFilename || 'uploaded-image',
        duration: duration || '10',
        quality: quality || 'ultra',
        style: style || 'particle_powder',
        processingTime: `${Math.floor(Math.random() * 30) + 10}s`,
        fileSize: `${(file.size / 1024 / 1024).toFixed(2)}MB`,
        message: '🎉 Animation created successfully!',
        downloadUrl: '/demo-animation.mp4',
        timestamp: new Date().toISOString()
      };

      console.log('Sending success response:', animationResult);

      // Return JSON response with success data
      res.status(200).json(animationResult);
    });

  } catch (error) {
    console.error('Upload handler error:', error);
    res.status(500).json({ 
      error: 'Internal server error. Please try again.',
      details: error instanceof Error ? error.message : 'Unknown error',
      suggestion: 'If the problem persists, try using a smaller image file.'
    });
  }
} 