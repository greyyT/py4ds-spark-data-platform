import React from 'react';

import useIMDBBMoie from '@/hooks/useIMDBMovie';
import { useRouter } from 'next/router';
import { AiOutlineArrowLeft } from 'react-icons/ai';
import Head from 'next/head';
import Navbar from '@/components/Navbar';
import MovieList from '@/components/MoveList';

const Watch = () => {
  const router = useRouter();
  const { movieId } = router.query;

  const { data: movie } = useIMDBBMoie(movieId as string);

  return (
    <>
      <Head>
        <title>{movie?.title}</title>
      </Head>
      <Navbar />
      <div className="pt-24 ">
        <div className="flex relative">
          <div className="hero-info flex flex-col justify-center max-w-[800px] min-w-[500px] pt-4 pr-8 pb-16 relative w-[35%] z-20">
            <div className="ml-16 flex flex-col gap-4">
              <h1 className="text-white text-6xl font-bold">{movie?.title}</h1>
              <p className="text-[#a3a3a3] text-sm leading-5">
                {movie?.year} | {movie?.duration}
              </p>
              <p className="text-white">{movie?.overview}</p>
              <p className="text-white">
                <span className="text-[#a3a3a3]">Starring:</span> {movie?.actor_1_name}, {movie?.actor_2_name},{' '}
                {movie?.actor_3_name}
              </p>
            </div>
          </div>
          <div className="hero flex flex-auto h-0 pb-[45%]">
            <div
              style={{ backgroundImage: `url('${movie?.src}')` }}
              className="bg-[50%] bg-no-repeat bg-cover h-full absolute right-16 w-[103%]"
            ></div>
          </div>
        </div>
      </div>
      <div className="pt-10 pb-40">
        <MovieList data={[movie, movie, movie, movie, movie]} title="More Like This" type="imdb" />
      </div>
    </>
  );
};

export default Watch;
