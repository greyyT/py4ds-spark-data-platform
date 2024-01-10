import useSWR from 'swr';
import fetcher from '@/lib/fetcher';

const useIMDBMovie = (id?: string) => {
  const { data, error, isLoading } = useSWR(id ? `/api/imdb-movies/${id}` : null, fetcher, {
    revalidateIfStale: false,
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
  });

  return {
    data,
    error,
    isLoading,
  };
};

export default useIMDBMovie;
