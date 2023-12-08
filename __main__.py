from scraper import IMDBScraper
import sys
import os

if __name__ == "__main__":
    data_folder = "data"

    # Create the data folder if it doesn't exist
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    scraper = IMDBScraper()

    scraper.logger.info("Starting IMDB scraper")

    if len(sys.argv) != 2:
        print("Usage: python3 -m imdb_scraper <num_movies>")
        sys.exit(1)

    num_movies = int(sys.argv[1])

    num_batches = num_movies // 50 if num_movies % 50 == 0 else num_movies // 50 + 1

    print(f"Okay, we'll scrape {num_batches} batch(es) for {num_movies} movies.")

    scraper.scrape_movies(num_movies)