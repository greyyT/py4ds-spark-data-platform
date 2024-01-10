import React, { useEffect, useState } from 'react';

import useIMDBBMoie from '@/hooks/useIMDBMovie';
import { useRouter } from 'next/router';
import { AiOutlineArrowLeft } from 'react-icons/ai';
import Head from 'next/head';
import Navbar from '@/components/Navbar';
import MovieList from '@/components/MoveList';
import axios from 'axios';

const Watch = () => {
  const router = useRouter();
  const { q } = router.query;

  const [movies, setMovies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!q) return;

    const fetchMovies = async () => {
      setIsLoading(true);

      try {
        const response = await axios.get('http://localhost:8000/search', {
          params: {
            q,
          },
        });

        setMovies(response.data);
      } catch (error) {
        console.log(error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMovies();
  }, [q]);

  return (
    <>
      <Head>
        <title>Search Results for {`"${q}"`}</title>
      </Head>
      <Navbar />
      <div className="pt-40 pb-40">
        <MovieList title={`Search Results for "${q}"`} data={movies} type="imdb" />
      </div>
    </>
  );
};

export default Watch;
