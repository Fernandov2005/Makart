import { NextApiRequest, NextApiResponse } from 'next';
import { serialize } from 'cookie';

const VALID_EMAIL = "olimpia@makincome.com";
const VALID_PASSWORD = "Chanel2808";

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
    const { email, password } = req.body;

    if (!email || !password) {
      res.status(400).json({ error: 'Email and password required' });
      return;
    }

    if (email === VALID_EMAIL && password === VALID_PASSWORD) {
      // Set session cookie
      const cookie = serialize('session', JSON.stringify({ 
        logged_in: true, 
        email: email,
        timestamp: Date.now()
      }), {
        httpOnly: true,
        secure: true,
        sameSite: 'none',
        maxAge: 60 * 60 * 24 * 7, // 1 week
        path: '/',
      });

      res.setHeader('Set-Cookie', cookie);
      res.status(200).json({ message: 'Login successful', email: email });
    } else {
      res.status(401).json({ error: 'Invalid credentials' });
    }
  } catch (_error) {
    res.status(500).json({ error: 'Login failed' });
  }
} 