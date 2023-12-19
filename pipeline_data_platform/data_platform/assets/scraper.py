import pandas as pd
import csv

import re, logging, time

from bs4 import BeautifulSoup
from requests import request


class Scraper:
    def __init__(self, url, headers, link):
        self.site_url = url
        self.headers = headers
        self.link = link


class IMDBScraper(Scraper):
    HEADERS = {
        "Accept-Language": "en-US, en;q=0.5",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
    }
    SITE_URL = "https://www.imdb.com"
    LINK = (
        "https://www.imdb.com/search/title/?adult=include&moviemeter={},{}&languages=en"
    )

    def __init__(self):
        super().__init__(self.SITE_URL, self.HEADERS, self.LINK)

        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s - %(name)s - %(levelname)s] %(message)s"
        )
        stream_handler.setFormatter(formatter)
        LOGGER.addHandler(stream_handler)

        self.logger = LOGGER

        self.list_movies = []

        self.movies_data = []

    def register_scraper(self, scraper_type):
        # return super().register_scraper(scraper_type)
        pass

    def get_scraper(self, scraper_type):
        # return super().get_scraper(scraper_type)
        pass

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
        self.logger.debug(f"Added score successfully: {score}")

        return score

    def scrape_title(self, movie_soup):
        # Get the title
        self.logger.debug("Getting title from movie page")
        try:
            title = movie_soup.find("h1").text
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            title = None
        self.logger.debug(f"Adding title: {title}")

        return title

    def scrape_duration(self, movie_soup):
        # Get the duration
        self.logger.debug("Getting duration from movie page")
        try:
            metadata_inline = movie_soup.find_all("ul", class_="ipc-inline-list")[1]
            duration = metadata_inline.find_all("li")[-1].text
            time_pattern = re.compile(r"^(\d{1,2}h\s)?(\d{1,2}m)$")
            if time_pattern.match(duration):
                self.logger.debug(f"Duration is valid: {duration}")
            else:
                duration = None
                self.logger.warning(f"Duration is invalid: {duration}")
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            duration = None
        self.logger.debug(f"Adding duration: {duration}")

        return duration

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
        self.logger.debug(f"Adding director name: {director_name}")
        self.logger.debug(f"Adding actor 1 name: {actor_1_name}")
        self.logger.debug(f"Adding actor 2 name: {actor_2_name}")
        self.logger.debug(f"Adding actor 3 name: {actor_3_name}")

        return director_name, actor_1_name, actor_2_name, actor_3_name

    def scrape_reviews(self, movie_soup):
        # Get the number of reviewed users, number of reviewed critics, metascore
        self.logger.debug(
            "Getting number of reviewed users, number of reviewed critics, metascore from movie page"
        )
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
        self.logger.debug(f"Adding number of reviewed users: {num_reviews}")
        self.logger.debug(f"Adding number of reviewed critics: {num_critics}")
        self.logger.debug(f"Adding metascore: {metascore}")

        return num_reviews, num_critics, metascore

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
        self.logger.debug(f"Adding number of votes: {num_votes}")

        return num_votes

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
        self.logger.debug(f"Adding language: {language}")

        return language

    def scrape_budget(self, movie_soup):
        # Get the budget
        self.logger.debug("Getting budget from movie page")
        try:
            budget_block = movie_soup.find(
                "li", attrs={"data-testid": "title-boxoffice-budget"}
            )
            budget_value_box = budget_block.find(
                "div", class_="ipc-metadata-list-item__content-container"
            )
            budget = budget_value_box.find("span").text
        except AttributeError:
            self.logger.warning(f"Budget not found")
            budget = None
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            budget = None
        self.logger.debug(f"Adding budget: {budget}")

        return budget

    def scrape_gross(self, movie_soup):
        # Get the global gross
        self.logger.debug("Getting global gross from movie page")
        try:
            global_gross_block = movie_soup.find(
                "li", {"data-testid": "title-boxoffice-cumulativeworldwidegross"}
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
        self.logger.debug(f"Adding global gross: {gross}")

        return gross

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
        self.logger.debug(f"Adding year: {year}")

        return year

    def scrape_overview(self, movie_soup):
        # Get the overview
        self.logger.debug("Getting overview from movie page")
        try:
            overview_block = movie_soup.find("p", {"data-testid": "plot"})
            overview = overview_block.find("span", {"data-testid": "plot-xl"}).text
        except:
            self.logger.warning(f"Overview not found")
            overview = None
        self.logger.debug(f"Adding overview: {overview}")

        return overview

    def scrape_movie(self, link, movie_soup):
        score = self.scrape_score(movie_soup)
        title = self.scrape_title(movie_soup)
        duration = self.scrape_duration(movie_soup)
        (
            director_name,
            actor_1_name,
            actor_2_name,
            actor_3_name,
        ) = self.scrape_contributors(movie_soup)
        num_reviews, num_critics, metascore = self.scrape_reviews(movie_soup)
        num_votes = self.scrape_votes(movie_soup)
        language = self.scrape_language(movie_soup)
        budget = self.scrape_budget(movie_soup)
        global_gross = self.scrape_gross(movie_soup)
        year = self.scrape_year(movie_soup)
        overview = self.scrape_overview(movie_soup)

        new_row = {
            "score": score,
            "title": title,
            "duration": duration,
            "director_name": director_name,
            "actor_1_name": actor_1_name,
            "actor_2_name": actor_2_name,
            "actor_3_name": actor_3_name,
            "num_reviews": num_reviews,
            "num_critics": num_critics,
            "num_votes": num_votes,
            "metascore": metascore,
            "language": language,
            "budget": budget,
            "global_gross": global_gross,
            "year": year,
            "overview": overview,
            "link": link,
        }

        self.movies_data.append(new_row)

    def get_movies_list_by_batch(self, current_batch, num_batches):
        # Calculate the start and end numbers for the batch
        start_num = current_batch * 50 - 49
        end_num = current_batch * 50

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

        self.logger.info(f"Batch {current_batch}: {len(movie_ids)} movies")

    def scrape_movies_by_multi_batches(self, num_movies):
        num_batches = num_movies // 50 if num_movies % 50 == 0 else num_movies // 50 + 1

        for batch_number in range(num_batches + 1):
            self.logger.info(f"Scraping batch {batch_number + 1}")
            self.get_movies_list_by_batch(batch_number + 1, num_batches)

            # For each movie take the link and scrape the data
            count = 0
            for movie in self.list_movies:
                count += 1

                self.logger.info(
                    f"<======== Scraping movie {count} of {len(self.list_movies)} movies in batch {batch_number + 1} ========>"
                )
                # Get the link and fetch the movie page
                link = self.site_url + movie
                movie_response = request(
                    method="GET", url=link, headers=self.headers, timeout=10
                )
                if movie_response.status_code != 200:
                    self.logger.warning(
                        f"Status code is not 200, skipping movie: {link}"
                    )
                    continue
                self.logger.debug(f"Status code: {movie_response.status_code}")
                self.logger.debug(f"Adding movie page: {link}")

                # Parse the movie page
                movie_soup = BeautifulSoup(movie_response.text, "html.parser")
                self.scrape_movie(link, movie_soup)
                self.append_csv(batch_number + 1)

                if len(self.movies_data) == num_movies:
                    break

            self.logger.info(f"Finished scraping batch {batch_number + 1}")
            self.list_movies = []

        self.logger.info(f"Finished scraping {num_movies} movies")

    def scrape_movies_by_single_batch(self, start_num: int, end_num: int) -> list:
        # Get the response object
        link = self.link.format(start_num, end_num)
        response = request(method="GET", url=link, headers=self.headers, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract movie ids and append to list
        movie_ids = soup.find_all("li", class_="ipc-metadata-list-summary-item")
        for i, movie_id in enumerate(movie_ids):
            movie_ids[i] = movie_id.a["href"]
        movie_ids = list(set(movie_ids))
        self.list_movies.extend(movie_ids)

        count = 0
        for movie in self.list_movies:
            count += 1
            self.logger.info(
                f"<======== Scraping movie {count} of {len(self.list_movies)} movies ========>"
            )

            # Get the link and fetch the movie page
            link = self.site_url + movie
            try:
                movie_response = request(
                    method="GET", url=link, headers=self.headers, timeout=60
                )
            except Exception:
                self.logger.warning("Connection refused by the server")
                self.logger.info("Sleeping for 10 seconds...")
                time.sleep(10)
            if movie_response.status_code != 200:
                self.logger.warning(f"Status code is not 200, skipping movie: {link}")
                continue
            self.logger.debug(f"Status code: {movie_response.status_code}")
            self.logger.debug(f"Adding movie page: {link}")

            # Parse the movie page
            movie_soup = BeautifulSoup(movie_response.text, "html.parser")
            self.scrape_movie(link, movie_soup)

            self.logger.info("Finished scraping this movie!")

        return self.movies_data

    def scrape_comment(self, comment_soup, movie_id, is_positive):
        # Get the comment
        comments_list = []
        try:
            comments = comment_soup.find_all("div", class_=re.compile(r"text show-more__control(\s| clickable)?"))
            for comment in comments:
                comments_list.append([movie_id, comment.text, is_positive])
        except Exception as e:
            self.logger.exception(f"Exception: {e}")
            comment = None
        self.logger.debug(f"Adding {len(comments_list)} {'positive' if is_positive else 'negative'} comments for movie: {movie_id}")

        return comments_list

    def scrape_comments_by_id(self, movie_id):
        # Get the link and fetch the movie page
        comments_list = []

        link = self.site_url + '/title/' + movie_id + '/reviews'
        positive_link = link + '?sort=helpfulnessScore&dir=desc&ratingFilter=10'
        negative_link = link + '?sort=helpfulnessScore&dir=asc&ratingFilter=1'

        self.logger.debug(f"Fetching positive comments for movie: {link}")
        movie_response = request(
            method="GET", url=positive_link, headers=self.headers, timeout=10
        )
        if movie_response.status_code != 200:
            self.logger.warning(f"Status code is not 200, skipping movie: {link}")
            return None
        self.logger.debug(f"Status code: {movie_response.status_code}")
        self.logger.debug(f"Scraping positive comments for movie: {link}")

        # Parse the movie page
        comment_soup = BeautifulSoup(movie_response.text, "html.parser")
        comments = self.scrape_comment(comment_soup, movie_id, True)

        comments_list.extend(comments)

        self.logger.debug(f"Fetching negative comments for movie: {link}")
        movie_response = request(
            method="GET", url=negative_link, headers=self.headers, timeout=10
        )

        if movie_response.status_code != 200:
            self.logger.warning(f"Status code is not 200, skipping movie: {link}")
            return None
        self.logger.debug(f"Status code: {movie_response.status_code}")
        self.logger.debug(f"Scraping negative comments for movie: {link}")

        # Parse the movie page
        comment_soup = BeautifulSoup(movie_response.text, "html.parser")
        comments = self.scrape_comment(comment_soup, movie_id, False)

        comments_list.extend(comments)

        return comments_list

    def append_csv(self, batch_num):
        self.logger.info(
            f"Appending movie {self.movies_data[-1]['title']} to batch {batch_num} csv"
        )
        try:
            with open(f"data/batch_{batch_num}.csv", "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.movies_data[-1].keys())

                writer.writerow(self.movies_data[-1])
        except:
            with open(f"data/batch_{batch_num}.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.movies_data[-1].keys())

                writer.writeheader()
                writer.writerow(self.movies_data[-1])

    def create_df(self):
        self.logger.info(f"Creating dataframe")
        df = pd.DataFrame(self.movies_data)
        return df
