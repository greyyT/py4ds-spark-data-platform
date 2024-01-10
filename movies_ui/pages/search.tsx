import React, { useEffect, useState } from 'react';

import useIMDBBMoie from '@/hooks/useIMDBMovie';
import { useRouter } from 'next/router';
import { AiOutlineArrowLeft } from 'react-icons/ai';
import Head from 'next/head';
import Navbar from '@/components/Navbar';
import MovieList from '@/components/MoveList';
import axios from 'axios';

export async function getServerSideProps(context: any) {
  try {
    const q = context.query?.q || '';

    const response = await axios.get('http://localhost:8000/search', {
      params: {
        q,
      },
    });

    const movies = response.data;

    return {
      props: {
        movies,
      },
    };
  } catch (error) {
    console.error('Error fetching data:', error);
    return {
      props: {
        movies: [],
      },
    };
  }
}

const Search = ({ movies }: { movies: any }) => {
  const router = useRouter();
  const { q } = router.query;

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

export default Search;
