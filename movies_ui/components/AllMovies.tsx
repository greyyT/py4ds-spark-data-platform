import React, { useEffect, useRef, useState } from 'react';

import IMDBCard from './IMDBCard';
import axios from 'axios';

const AllMovies: React.FC = (): JSX.Element | null | undefined => {
  const [IMDBMovies, setIMDBMovies] = useState<any>([]);
  const [currentPage, setCurrentPage] = useState(2);
  const [totalPages, setTotalPages] = useState(1); // response.data.total_pages
  const [isLoading, setIsLoading] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchMovies = async () => {
      setIsLoading(true);

      try {
        const response = await axios.get('/api/imdb-movies', {
          params: {
            page: 1,
            size: 20,
          },
        });
        setIMDBMovies(response.data.data);
        setTotalPages(response.data.totalPages);
        setCurrentPage(2);
      } catch (error) {
        console.log(error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMovies();
  }, []);

  useEffect(() => {
    if (currentPage > totalPages) return;

    const node = bottomRef.current;

    const fetchMovies = async () => {
      setIsLoading(true);

      try {
        const response = await axios.get('/api/imdb-movies', {
          params: {
            page: currentPage,
            size: 20,
          },
        });
        setIMDBMovies((prevMovies: any) => [...prevMovies, ...response.data.data]);
        setTotalPages(response.data.totalPages);
        setCurrentPage((prevPage: number) => prevPage + 1);
      } catch (error) {
        console.log(error);
      } finally {
        setIsLoading(false);
      }
    };

    const handleIntersection = (entries: any) => {
      const [entry] = entries;

      if (entry.isIntersecting) {
        fetchMovies();
      }
    };

    const observer = new IntersectionObserver(handleIntersection, { root: null, rootMargin: '0px', threshold: 0.1 });

    if (node) observer.observe(node);

    return () => {
      if (node) observer.unobserve(node);
    };
  }, [currentPage, totalPages]);

  return (
    <div className="px-4 md:px-12 mt-4 space-y-8">
      <div>
        <p className="text-white text-md md:text-xl lg:text-2xl font-semibold mb-4">All Movies</p>
        <div className="grid grid-cols-5 gap-x-4 gap-y-16">
          {IMDBMovies?.map((movie: any, idx: number) => (
            <IMDBCard key={idx} movie={movie} />
          ))}
        </div>
        <div ref={bottomRef}></div>
      </div>
    </div>
  );
};

export default AllMovies;
