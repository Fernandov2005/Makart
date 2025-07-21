import { NextApiRequest, NextApiResponse } from 'next';
import { serialize } from 'cookie';

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
    // Clear session cookie
    const cookie = serialize('session', '', {
      httpOnly: true,
      secure: true,
      sameSite: 'none',
      maxAge: 0, // Expire immediately
      path: '/',
    });

    res.setHeader('Set-Cookie', cookie);
    res.status(200).json({ message: 'Logout successful' });
  } catch (_error) {
    res.status(500).json({ error: 'Logout failed' });
  }
} 