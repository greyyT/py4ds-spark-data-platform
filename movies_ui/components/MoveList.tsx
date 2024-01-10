import React from 'react';

import { isEmpty } from 'lodash';
import MovieCard from './MovieCard';
import IMDBCard from './IMDBCard';

interface MovieListProps {
  data: Record<string, any>[];
  title: string;
  type?: 'normal' | 'imdb';
}

const MovieList: React.FC<MovieListProps> = ({ data, title, type = 'normal' }): JSX.Element | null | undefined => {
  return (
    <div className="px-4 md:px-14 mt-4 space-y-8">
      <div>
        <p className="text-white text-md md:text-xl lg:text-2xl font-semibold mb-4">{title}</p>
        {!isEmpty(data) && (
          <div className="grid grid-cols-4 gap-x-4 gap-y-16">
            {type !== 'imdb' && data.map((movie, idx) => <MovieCard key={idx} data={movie} />)}
            {type === 'imdb' && data.map((movie, idx) => <IMDBCard key={idx} movie={movie} />)}
          </div>
        )}
      </div>
    </div>
  );
};

export default MovieList;
