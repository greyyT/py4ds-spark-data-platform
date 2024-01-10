import { useRouter } from 'next/router';
import { useRef, useState } from 'react';
import { BsSearch } from 'react-icons/bs';
import { IoMdClose } from 'react-icons/io';

const NavbarSearch: React.FC = (): JSX.Element => {
  const inputRef = useRef<HTMLInputElement>(null);

  const [showSearch, setShowSearch] = useState<boolean>(false);
  const [searchContent, setSearchContent] = useState<string>('');

  const router = useRouter();

  const onSearch = async (ev: any) => {
    ev.preventDefault();

    if (searchContent.trim() === '') return;

    router.push(`/search?q=${searchContent}`);
  };

  return (
    <form
      onSubmit={onSearch}
      className="text-gray-200 flex hover:text-gray-300 cursor-pointer transition relative items-center"
    >
      {showSearch && <div onClick={() => setShowSearch(false)} className="fixed inset-0 z-50 cursor-default"></div>}
      <input
        ref={inputRef}
        type="text"
        placeholder="Search for a movie, tv show, person..."
        value={searchContent}
        onChange={(ev) => setSearchContent(ev.target.value)}
        name="imdb-search"
        className={`bg-transparent border border-solid border-white rounded-[4px] py-1 pr-3 pl-10 outline-none z-50 ${
          showSearch ? 'opacity-100' : 'opacity-0 pointer-events-none'
        } transition w-96`}
      />
      <BsSearch
        onClick={(ev: any) => {
          ev.stopPropagation();
          setShowSearch(true);
          inputRef.current?.focus();
        }}
        className={`absolute ${
          showSearch ? 'left-3' : 'left-full -translate-x-full'
        }  transition-[left] duration-300 top-1/2 -translate-y-1/2 z-50`}
      />
      {showSearch && (
        <IoMdClose
          onClick={() => setSearchContent('')}
          className="absolute top-1/2 -translate-y-1/2 right-2 z-50 cursor-pointer"
        />
      )}
    </form>
  );
};

export default NavbarSearch;
