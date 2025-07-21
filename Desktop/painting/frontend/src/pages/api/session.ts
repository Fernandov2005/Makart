import { NextApiRequest, NextApiResponse } from 'next';
import { parse } from 'cookie';

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
  
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Credentials', 'true');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    const cookies = parse(req.headers.cookie || '');
    const sessionData = cookies.session ? JSON.parse(cookies.session) : null;

    if (sessionData && sessionData.logged_in) {
      res.status(200).json({ 
        logged_in: true, 
        email: sessionData.email 
      });
    } else {
      res.status(200).json({ logged_in: false });
    }
  } catch (_error) {
    res.status(200).json({ logged_in: false });
  }
} 