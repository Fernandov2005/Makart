import { NextApiRequest, NextApiResponse } from 'next';
import { parse } from 'cookie';
import formidable from 'formidable';

export const config = {
  api: {
    bodyParser: false, // Important - let formidable handle the form
    sizeLimit: false,  // Disable Next.js size limit
    responseLimit: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  console.log('Upload request received:', {
    contentType: req.headers['content-type'],
    contentLength: req.headers['content-length'],
    headers: req.headers,
  });

  try {
    // Very basic authentication check
    const cookies = parse(req.headers.cookie || '');
    const sessionData = cookies.session ? JSON.parse(cookies.session) : null;

    if (!sessionData || !sessionData.logged_in) {
      return res.status(401).json({ error: 'Please log in to upload files' });
    }

    // Use simplified formidable config
    const form = new formidable.IncomingForm({
      keepExtensions: true,
      multiples: false,
    });

    // Process the form using Promise
    const formData: { fields: formidable.Fields; files: formidable.Files } = await new Promise((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) {
          console.error('Form parsing error:', err);
          reject(err);
          return;
        }
        resolve({ fields, files });
      });
    });

    // Get the file
    const uploadedFile = formData.files.file as formidable.File | undefined;

    if (!uploadedFile) {
      return res.status(400).json({ 
        error: 'No file uploaded' 
      });
    }

    // Get options from form data
    const duration = Array.isArray(formData.fields.duration) ? formData.fields.duration[0] : formData.fields.duration;
    const quality = Array.isArray(formData.fields.quality) ? formData.fields.quality[0] : formData.fields.quality;
    const style = Array.isArray(formData.fields.style) ? formData.fields.style[0] : formData.fields.style;

    // Remove minimum file size check (allow very small files)
    // Log successful upload
    console.log('File successfully processed:', {
      filename: uploadedFile.originalFilename,
      size: uploadedFile.size,
      mimetype: uploadedFile.mimetype,
    });

    // Return success response
    return res.status(200).json({
      success: true,
      filename: uploadedFile.originalFilename || 'uploaded-image',
      duration: duration || '10',
      quality: quality || 'ultra',
      style: style || 'particle_powder',
      processingTime: `${Math.floor(Math.random() * 30) + 10}s`,
      fileSize: `${(uploadedFile.size / 1024 / 1024).toFixed(2)}MB`,
      message: '🎉 Animation created successfully!',
      downloadUrl: '/demo-animation.mp4',
      timestamp: new Date().toISOString(),
      debug: {
        size: uploadedFile.size,
        mimetype: uploadedFile.mimetype,
        fields: { duration, quality, style }
      }
    });

  } catch (error) {
    console.error('Upload handler error:', error);
    
    // Handle specific errors
    if (error instanceof Error) {
      if (error.message.includes('maxFileSize')) {
        return res.status(413).json({ 
          error: 'File too large' 
        });
      }
    }
    
    return res.status(500).json({ 
      error: 'Server error. Please try again.',
      details: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      headers: req.headers,
    });
  }
} 