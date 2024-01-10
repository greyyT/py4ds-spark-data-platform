import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

import serverAuth from '@/lib/serverAuth';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).end();
  }

  try {
    await serverAuth(req, res);

    const page = req.query.page || 1;
    const size = req.query.size || 20;

    const movies = await axios.get('http://localhost:8000/movies', {
      params: {
        page,
        size,
      },
    });

    return res.status(200).json(movies.data);
  } catch (error) {
    console.log(error);
    return res.status(400).end();
  }
}
