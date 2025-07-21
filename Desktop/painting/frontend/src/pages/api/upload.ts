import { NextApiRequest, NextApiResponse } from 'next';
import formidable, { File } from 'formidable';

// Configure API route for larger file uploads
export const config = {
  api: {
    bodyParser: false,
    responseLimit: '50mb',
  },
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Configure formidable for larger files
    const form = formidable({
      maxFileSize: 50 * 1024 * 1024, // 50MB
      keepExtensions: true,
    });

    const [_fields, files] = await form.parse(req);
    
    // Get the uploaded file with proper typing
    const uploadedFile = files.file as File | File[] | undefined;
    let fileSize: number | undefined;
    
    if (Array.isArray(uploadedFile)) {
      fileSize = uploadedFile[0]?.size;
    } else if (uploadedFile) {
      fileSize = uploadedFile.size;
    }
    
    // Return success response
    res.status(200).json({
      message: 'File uploaded successfully',
      size: fileSize,
    });
  } catch (_error) {
    console.error('Upload error:', _error);
    res.status(500).json({ error: 'Upload failed' });
  }
} 