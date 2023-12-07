from scraper import IMDBScraper
import sys

if __name__ == "__main__":
    scraper = IMDBScraper()

    scraper.logger.info("Starting IMDB scraper")
    
    if len(sys.argv) != 2:
        print("Usage: python3 -m scraper <num_movies>")
        sys.exit(1)

    num_movies = int(sys.argv[1])
    
    num_batches = num_movies // 50 if num_movies % 50 == 0 else num_movies // 50 + 1

    print(f"Okay, we'll scrape {num_batches} batch(es) of movies.")

    scraper.get_movies_list(num_batches)
    scraper.scrape_movies()

    df = scraper.create_dataframe()