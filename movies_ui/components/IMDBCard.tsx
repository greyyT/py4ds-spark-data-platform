import useInfoModal from '@/hooks/useInfoModal';
import { useRouter } from 'next/router';
import React from 'react';
import { BsChevronDown, BsFillPlayFill } from 'react-icons/bs';
import FavoriteButton from './FavoriteButton';
import { formatTime } from '@/lib/formatTime';

interface IMDBCardProps {
  movie: Record<string, any>;
}

const IMDBCard: React.FC<IMDBCardProps> = ({ movie }): JSX.Element => {
  const router = useRouter();

  return (
    <div className="group bg-zinc-900 col-span relative h-[10vw] z-20">
      <img
        className="
          cursor-pointer
          object-cover
          transition
          duration
          shadow-xl
          rounded-sm
          group-hover:opacity-90
          sm:group-hover:opacity-0
          delay-300
          w-full
          h-[10vw]
        "
        src={movie?.src}
        alt=""
        onClick={() => router.push(`/title/${movie?.movie_id}`)}
      />
      <h1 className="text-white text-center mt-2">{movie?.title}</h1>
      <div
        className="
          opacity-0
          absolute
          top-0
          transition
          duration-200
          z-10
          invisible
          sm:visible
          delay-300
          w-full
          scale-0
          group-hover:scale-110
          group-hover:-translate-y-[6vw]
          group-hover:translat-x-[2vw]
          group-hover:opacity-100
        "
      >
        <div className="relative">
          <img
            className="cursor-pointer object-cover transition duration-0 shadow-xl rounded-t-sm w-full h-[10vw]"
            src={movie?.src}
            alt={movie?.alt}
            onClick={() => router.push(`/title/${movie?.movie_id}`)}
          />
          <h1 className="absolute bottom-4 left-4 line-clamp-1 text-white text-2xl font-bold">{movie?.title}</h1>
        </div>
        <div className="z-10 bg-zinc-800 p-2 lg:p-4 absolute w-full transition shadow-md rounded-b-sm">
          <p className="text-green-400 font-semibold mt-2">
            {movie?.year === 2024 && 'New'} <span className="text-white">{movie?.year}</span>
          </p>
          <div className="flex mt-4 gap-2 items-center">
            <p className="text-white text-[10px] lg:text-sm">{formatTime(movie?.duration)}</p>
          </div>
          <div className="flex mt-4 gap-2 items-center">
            <p className="text-white text-[10px] lg:text-sm">Meta Score: {movie?.metascore}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IMDBCard;
