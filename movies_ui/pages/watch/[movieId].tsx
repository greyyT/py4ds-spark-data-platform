import React from 'react';

import useMovie from '@/hooks/useMovie';
import { useRouter } from 'next/router';
import { AiOutlineArrowLeft } from 'react-icons/ai';
import Head from 'next/head';

const Watch = () => {
  const router = useRouter();
  const { movieId } = router.query;

  const { data: movie } = useMovie(movieId as string);

  return (
    <>
      <Head>
        <title>{movie?.title}</title>
      </Head>
      <div className="h-screen w-screen bg-black">
        <nav className="fixed w-full p-4 z-10 flex items-center gap-8 bg-black bg-opacity-70">
          <AiOutlineArrowLeft className="text-white cursor-pointer" size={40} onClick={() => router.push('/')} />
          <p className="text-white text-1xl md:text-3xl font-bold">
            <span className="font-light">Watching:</span> {movie?.title}
          </p>
        </nav>
        <video src={movie?.videoUrl} className="h-full w-full" autoPlay controls></video>
      </div>
    </>
  );
};

export default Watch;
