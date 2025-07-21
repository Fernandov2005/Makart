import { NextApiRequest, NextApiResponse } from 'next';
import { parse } from 'cookie';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  // Handle CORS
  res.setHeader('Access-Control-Allow-Origin', 'https://makart.vercel.app');
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

    // For demo purposes, return success (file processing will be added later)
    res.status(200).json({
      message: 'File upload endpoint ready! Animation processing will be available soon.',
      status: 'received'
    });
  } catch (error) {
    res.status(500).json({ error: 'Upload failed' });
  }
} 