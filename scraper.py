from abc import abstractmethod

import pandas as pd

import re, logging

from bs4 import BeautifulSoup
from requests import request


class Scraper:
    def __init__(self, url, headers, link):
        self.site_url = url
        self.headers = headers
        self.link = link
        
        self.SCRAPPERS = {}

    @classmethod
    def register_scraper(cls, scraper_type):
        def decorator(fn):
            cls.SCRAPPERS[scraper_type] = fn
            return fn
        return decorator

    def get_scraper(self, scraper_type):
        if (scraper_type not in self.SCRAPPERS):
            raise ValueError(f"Unsupported scraper type: {scraper_type}")
        return self.SCRAPPERS[scraper_type]

    @abstractmethod
    def verify_lengths(self):
        pass

class IMDBScraper(Scraper):
    HEADERS = {
        "Accept-Language": "en-US, en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    }
    SITE_URL = "https://www.imdb.com"
    LINK = "https://www.imdb.com/search/title/?adult=include&moviemeter={},{}&languages=en"

    def __init__(self):
        super().__init__(self.SITE_URL, self.HEADERS, self.LINK)

        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s - %(levelname)s] %(message)s")
        stream_handler.setFormatter(formatter)
        LOGGER.addHandler(stream_handler)

        self.logger = LOGGER

        self.list_movies = []

        self.all_scores = []
        self.all_titles = []
        self.all_durations = []
        self.all_director_names = []
        self.all_actor_1_names = []
        self.all_actor_2_names = []
        self.all_actor_3_names = []
        self.all_reviewed_users = []
        self.all_reviewed_critics = []
        self.all_num_votes = []
        self.all_metascores = []
        self.all_links = []
        self.all_languages = []
        self.all_budgets = []
        self.all_global_grosses = []
        self.all_years = []

    def register_scraper(scraper_type):
        return super().register_scraper(scraper_type)

    def get_scraper(self, scraper_type):
        return super().get_scraper(scraper_type)
    
    @register_scraper('score')
    def scrape_score(self, movie_soup):
        # Get the score
        self.logger.debug("Getting score from movie page")
        try:
            score = (
                movie_soup.find(
                    "div",
                    attrs={"data-testid": "hero-rating-bar__aggregate-rating__score"},
                )
                .find("span")
                .text
            )
            score = float(score)
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            score = None
        self.all_scores.append(score)
        self.logger.info(f"Added score successfully: {score}")

    @register_scraper('title')
    def scrape_title(self, movie_soup):
        # Get the title
        self.logger.debug("Getting title from movie page")
        try:
            title = movie_soup.find("h1").text
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            title = None
        self.all_titles.append(title)
        self.logger.info(f"Adding title: {title}")

    @register_scraper('duration')
    def scrape_duration(self, movie_soup):
        # Get the duration
        self.logger.debug("Getting duration from movie page")
        try:
            metadata_inline = movie_soup.find_all("ul", class_="ipc-inline-list")[1]
            duration = metadata_inline.find_all("li")[-1].text
            time_pattern = re.compile(r"^(\d{1,2}h\s)?(\d{1,2}m)$")
            if time_pattern.match(duration):
                self.logger.info(f"Duration is valid: {duration}")
            else:
                duration = None
                self.logger.warning(f"Duration is invalid: {duration}")
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            duration = None
        self.all_durations.append(duration)
        self.logger.info(f"Adding duration: {duration}")

    @register_scraper('contributors')
    def scrape_contributors(self, movie_soup):
        # Get the director, actor 1, actor 2, actor 3 names
        self.logger.debug("Getting director and actor names from movie page")
        director_name, actor_1_name, actor_2_name, actor_3_name = "", "", "", ""
        try:
            cast_blocks = movie_soup.find_all(
                "li", attrs={"data-testid": "title-pc-principal-credit"}
            )
            cast_blocks = cast_blocks[: len(cast_blocks) // 2]
            for block in cast_blocks:
                if (
                    block.find("span", class_="ipc-metadata-list-item__label")
                    and block.find("span", class_="ipc-metadata-list-item__label").text
                    == "Director"
                ):
                    director_name = block.find("a").text
                elif (
                    block.find("a", class_="ipc-metadata-list-item__label")
                    and block.find("a", class_="ipc-metadata-list-item__label").text
                    == "Stars"
                ):
                    actor_1_name = block.find_all("a")[1].text
                    actor_2_name = block.find_all("a")[2].text
                    actor_3_name = block.find_all("a")[3].text
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
        self.all_director_names.append(director_name)
        self.logger.info(f"Adding director name: {director_name}")
        self.all_actor_1_names.append(actor_1_name)
        self.logger.info(f"Adding actor 1 name: {actor_1_name}")
        self.all_actor_2_names.append(actor_2_name)
        self.logger.info(f"Adding actor 2 name: {actor_2_name}")
        self.all_actor_3_names.append(actor_3_name)
        self.logger.info(f"Adding actor 3 name: {actor_3_name}")

    @register_scraper('reviews')
    def scrape_reviews(self, movie_soup):
        # Get the number of reviewed users, number of reviewed critics, metascore
        self.logger.debug("Getting number of reviewed users, number of reviewed critics, metascore from movie page")
        num_reviews, num_critics, metascore = None, None, None
        try:
            user_reviews_block = movie_soup.find_all("span", class_="three-Elements")
            if len(user_reviews_block) == 0:
                user_reviews_block = movie_soup.find_all(
                    "span", class_="less-than-three-Elements"
                )
            for block in user_reviews_block:
                if block.find("span", class_="label").text == "User reviews":
                    num_reviews = block.find("span", class_="score").text
                elif block.find("span", class_="label").text == "Critic reviews":
                    num_critics = block.find("span", class_="score").text
                elif (
                    block.find("span", class_="label")
                    .find("span", class_="metacritic-score-label")
                    .text
                    == "Metascore"
                ):
                    metascore = block.find("span", class_="score").text
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
        self.all_reviewed_users.append(num_reviews)
        self.logger.info(f"Adding number of reviewed users: {num_reviews}")
        self.all_reviewed_critics.append(num_critics)
        self.logger.info(f"Adding number of reviewed critics: {num_critics}")
        self.all_metascores.append(metascore)
        self.logger.info(f"Adding metascore: {metascore}")

    @register_scraper('votes')
    def scrape_votes(self, movie_soup):
        # Get the number of votes
        self.logger.debug("Getting number of votes from movie page")
        try:
            num_votes = (
                movie_soup.find(
                    "div",
                    attrs={"data-testid": "hero-rating-bar__aggregate-rating__score"},
                )
                .find_next_sibling("div")
                .find_next_sibling("div")
                .text
            )
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            num_votes = None
        self.all_num_votes.append(num_votes)
        self.logger.info(f"Adding number of votes: {num_votes}")

    @register_scraper('language')
    def scrape_language(self, movie_soup):
        # Get the language
        self.logger.debug("Getting language from movie page")
        try:
            language_block = movie_soup.find(
                "li", attrs={"data-testid": "title-details-languages"}
            )
            language = language_block.find("a").text
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            language = None
        self.all_languages.append(language)
        self.logger.info(f"Adding language: {language}")

    @register_scraper('budget')
    def scrape_budget(self, movie_soup):
        # Get the budget
        self.logger.debug("Getting budget from movie page")
        try:
            budget_block = movie_soup.find(
                "li", attrs={"data-testid": "title-boxoffice-budget"}
            )
            budget = budget_block.find(
                "span", class_="ipc-metadata-list-item__content-container"
            ).text
        except AttributeError:
            self.logger.warning(f"Budget not found")
            budget = None
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            budget = None
        self.all_budgets.append(budget)
        self.logger.info(f"Adding budget: {budget}")

    @register_scraper('gross')
    def scrape_gross(self, movie_soup):
        # Get the global gross
        self.logger.debug("Getting global gross from movie page")
        try:
            global_gross_block = movie_soup.find(
                "li", attrs={"data-testid": "title-boxoffice-cumulativeworldwidegross"}
            )
            gross = global_gross_block.find(
                "span", class_="ipc-metadata-list-item__list-content-item"
            ).text
        except AttributeError:
            self.logger.warning(f"Global gross not found")
            gross = None
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            gross = None
        self.logger.info(f"Adding global gross: {gross}")
        self.all_global_grosses.append(gross)

    @register_scraper('year')
    def scrape_year(self, movie_soup):
        # Get the year
        self.logger.debug("Getting year from movie page")
        try:
            metadata_inline = movie_soup.find_all("ul", class_="ipc-inline-list")[1]
            year = metadata_inline.find_all("li")[0].text
            TV_tags = [
                "TV Series",
                "TV Mini Series",
                "TV Movie",
                "TV Special",
                "TV Short",
                "TV Episode",
            ]
            if metadata_inline.find_all("li")[0].text in TV_tags:
                year = metadata_inline.find_all("li")[1].text
            # If the last character is not a digit, remove it
            self.logger.debug(f"Year before: {year}")
            while not year[-1].isdigit():
                year = year[:-1]
            year = int(year[-4:])
        except ValueError:
            self.logger.warning(f"Year not found")
            year = None
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            year = None
        self.all_years.append(year)
        self.logger.info(f"Adding year: {year}")

    def verify_lengths(self):
        num_movies = len(self.all_links)

        def validate_data_length(*args):
            for data_list, data_name in args:
                if num_movies != len(data_list):
                    self.logger.exception(f"Length of {data_name}: {len(data_list)}")
                    return False
            return True

        return validate_data_length(
            (self.all_scores, "scores"),
            (self.all_titles, "titles"),
            (self.all_durations, "durations"),
            (self.all_director_names, "director names"),
            (self.all_actor_1_names, "actor 1 names"),
            (self.all_actor_2_names, "actor 2 names"),
            (self.all_actor_3_names, "actor 3 names"),
            (self.all_reviewed_users, "number of reviewed users"),
            (self.all_reviewed_critics, "number of reviewed critics"),
            (self.all_num_votes, "number of votes"),
            (self.all_metascores, "metascores"),
            (self.all_languages, "languages"),
            (self.all_budgets, "budgets"),
            (self.all_global_grosses, "global grosses"),
            (self.all_years, "years"),
        )

    def get_movies_list(self, num_batches):
        for batch_number in range(1, num_batches + 1):
            # Calculate the start and end numbers for the batch
            start_num = batch_number * 50 - 49
            end_num = batch_number * 50

            # Get the response object
            link = self.link.format(start_num, end_num)
            response = request(method="GET", url=link, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract movie ids and append to list
            movie_ids = soup.find_all("li", class_="ipc-metadata-list-summary-item")
            for i, movie_id in enumerate(movie_ids):
                movie_ids[i] = movie_id.a["href"]
            movie_ids = list(set(movie_ids))
            self.list_movies.extend(movie_ids)

            self.logger.info(f"Batch {batch_number}/{num_batches}: {len(movie_ids)} movies")

        self.logger.info(f"Total number of movies scraped: {len(self.list_movies)}")

    def scrape_movies(self):
        # For each movie take the link and scrape the data
        count = 0
        for movie in self.list_movies:
            count += 1
            self.logger.info(
                f"<======== Scraping movie {count} of {len(self.list_movies)} movies ========>"
            )
            # Get the link and fetch the movie page
            link = self.site_url + movie
            movie_response = request(method="GET", url=link, headers=self.headers, timeout=10)
            if movie_response.status_code != 200:
                self.logger.warning(f"Status code is not 200, skipping movie: {link}")
                continue
            self.logger.info(f"Status code: {movie_response.status_code}")
            self.all_links.append(link)
            self.logger.info(f"Adding movie page: {link}")

            # Parse the movie page
            movie_soup = BeautifulSoup(movie_response.text, "html.parser")
            self.scrape_movie_data(movie_soup)

    def create_dataframe(self):
        if self.verify_lengths():
            self.logger.info(f"Creating dataframe")
            df = pd.DataFrame(
                {
                    "score": self.all_scores,
                    "title": self.all_titles,
                    "duration": self.all_durations,
                    "director_name": self.all_director_names,
                    "actor_1_name": self.all_actor_1_names,
                    "actor_2_name": self.all_actor_2_names,
                    "actor_3_name": self.all_actor_3_names,
                    "num_reviews": self.all_reviewed_users,
                    "num_critics": self.all_reviewed_critics,
                    "num_votes": self.all_num_votes,
                    "metascore": self.all_metascores,
                    "language": self.all_languages,
                    "budget": self.all_budgets,
                    "global_gross": self.all_global_grosses,
                    "year": self.all_years,
                    "link": self.all_links,
                }
            )
            self.logger.info("Data scraping and dataframe creation completed.")
            return df
        else:
            self.logger.error("Data scraping failed due to length mismatch.")

    def save_csv(self):
        df = self.create_dataframe()
        df.to_csv("data.csv", index=False)
        self.logger.info("Dataframe saved to csv file successfully.")


