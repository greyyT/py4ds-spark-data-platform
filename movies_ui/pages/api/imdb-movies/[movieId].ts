import { NextApiRequest, NextApiResponse } from 'next';

import prismadb from '@/utils/prismadb';
import serverAuth from '@/utils/serverAuth';
import axios from 'axios';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    await serverAuth(req, res);

    const { movieId } = req.query;

    if (typeof movieId !== 'string') {
      throw new Error('Invalid movieId');
    }

    if (!movieId) {
      throw new Error('Invalid movieId');
    }

    const movie = await axios.get(`http://localhost:8000/movies/${movieId}`);

    return res.status(200).json(movie.data);
  } catch (error) {
    console.log(error);
    return res.status(400).end();
  }
}
