import React from 'react';

import { BsPlayFill } from 'react-icons/bs';
import { useRouter } from 'next/router';

interface PlayButtonProps {
  movieId: string;
}

const PlayButton: React.FC<PlayButtonProps> = ({ movieId }): JSX.Element => {
  const router = useRouter();

  return (
    <div
      onClick={() => router.push(`/watch/${movieId}`)}
      className="bg-white cursor-pointer rounded-md py-1 md:py-2 px-2 md:px-4 w-auto text-xs lg:text-xl font-semibold flex flex-row items-center hover:bg-neutral-300 transition"
    >
      <BsPlayFill size={25} className="mr-1" />
      Play
    </div>
  );
};

export default PlayButton;
