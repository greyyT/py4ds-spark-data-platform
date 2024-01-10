import { useCallback, useEffect, useState } from 'react';
import MobileMenu from './MobileMenu';
import NavbarItem from './NavbarItem';
import { BsChevronDown, BsSearch, BsBell } from 'react-icons/bs';
import AccountMenu from './AccountMenu';
import Link from 'next/link';
import NavbarSearch from './NavbarSearch';

const TOP_OFFSET = 66;

const Navbar: React.FC = (): JSX.Element => {
  const [showMobileMenu, setShowMobileMenu] = useState<boolean>(false);
  const [showAccountMenu, setShowAccountMenu] = useState<boolean>(false);
  const [showBackground, setShowBackground] = useState<boolean>(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY >= TOP_OFFSET) {
        setShowBackground(true);
      } else {
        setShowBackground(false);
      }
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const toggleMobileMenu = useCallback(() => {
    setShowMobileMenu((currentValue) => !currentValue);
  }, []);

  const toggleAccountMenu = useCallback(() => {
    setShowAccountMenu((currentValue) => !currentValue);
  }, []);

  return (
    <nav className="w-full fixed z-40">
      <div
        className={`
					px-4
					md:px-16
					py-6
					flex
					items-center
					transition
					duration-500
					${showBackground ? 'bg-zinc-900 bg-opacity-90' : ''}
				`}
      >
        <Link href="/">
          <img src="/images/logo.png" alt="Logo" className="h-4 lg:h-7" />
        </Link>
        <div className="ml-8 gap-7 hidden lg:flex">
          <NavbarItem href="/" label="Home" />
          <NavbarItem href="/" label="Series" />
          <NavbarItem href="/" label="Films" />
          <NavbarItem href="/" label="News & Popular" />
          <NavbarItem href="/" label="My List" />
          <NavbarItem href="/" label="Browse by Languages" />
        </div>
        <div onClick={toggleMobileMenu} className="lg:hidden flex items-center gap-2 ml-8 cursor-pointer relative">
          <p className="text-white text-sm">Browse</p>
          <BsChevronDown className={`text-white transition ${showMobileMenu ? 'rotate-180' : ''}`} />
          <MobileMenu visible={showMobileMenu} />
        </div>
        <div className="flex ml-auto gap-7 items-center">
          <NavbarSearch />
          <div className="text-gray-200 hover:text-gray-300 cursor-pointer transition">
            <BsBell />
          </div>
          <div onClick={toggleAccountMenu} className="flex items-center gap-2 cursor-pointer relative">
            <div className="w-6 h-6 lg:w-10 lg:h-10 rounded-md overflow-hidden">
              <img src="/images/default-blue.png" alt="Default Avatar" />
            </div>
            <BsChevronDown className={`text-white transition ${showAccountMenu ? 'rotate-180' : ''}`} />
            <AccountMenu visible={showAccountMenu} />
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
