from dagster import ConfigurableResource
from bs4 import BeautifulSoup
from requests import request
import re, logging, time

from data_platform.assets import constants


# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class IMDBScraper(ConfigurableResource):
    site_url: str = constants.SITE_URL
    headers: dict = constants.HEADERS
    link: str = constants.LINK
    list_movies: list = []
    movies_data: list = []

    def scrape_score(self, movie_soup):
        # Get the score
        logger.debug("Getting score from movie page")
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
            logger.exception(f"Exception: {e}")
            score = None
        logger.debug(f"Added score successfully: {score}")
        return score

    def scrape_title(self, movie_soup):
        # Get the title
        logger.debug("Getting title from movie page")
        try:
            title = movie_soup.find("h1").text
        except Exception as e:
            logger.exception(f"Exception: {e}")
            title = None
        logger.debug(f"Adding title: {title}")
        return title

    def scrape_duration(self, movie_soup):
        # Get the duration
        logger.debug("Getting duration from movie page")
        try:
            metadata_inline = movie_soup.find_all("ul", class_="ipc-inline-list")[1]
            duration = metadata_inline.find_all("li")[-1].text
            time_pattern = re.compile(r"^(\d{1,2}h\s)?(\d{1,2}m)$")
            if time_pattern.match(duration):
                logger.debug(f"Duration is valid: {duration}")
            else:
                duration = None
                logger.warning(f"Duration is invalid: {duration}")
        except Exception as e:
            logger.exception(f"Exception: {e}")
            duration = None
        logger.debug(f"Adding duration: {duration}")
        return duration

    def scrape_contributors(self, movie_soup):
        # Get the director, actor 1, actor 2, actor 3 names
        logger.debug("Getting director and actor names from movie page")
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
            logger.exception(f"Exception: {e}")
        logger.debug(f"Adding director name: {director_name}")
        logger.debug(f"Adding actor 1 name: {actor_1_name}")
        logger.debug(f"Adding actor 2 name: {actor_2_name}")
        logger.debug(f"Adding actor 3 name: {actor_3_name}")
        return director_name, actor_1_name, actor_2_name, actor_3_name

    def scrape_reviews(self, movie_soup):
        # Get the number of reviewed users, number of reviewed critics, metascore
        logger.debug(
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
            logger.exception(f"Exception: {e}")
        logger.debug(f"Adding number of reviewed users: {num_reviews}")
        logger.debug(f"Adding number of reviewed critics: {num_critics}")
        logger.debug(f"Adding metascore: {metascore}")
        return num_reviews, num_critics, metascore

    def scrape_votes(self, movie_soup):
        # Get the number of votes
        logger.debug("Getting number of votes from movie page")
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
            logger.exception(f"Exception: {e}")
            num_votes = None
        logger.debug(f"Adding number of votes: {num_votes}")
        return num_votes

    def scrape_language(self, movie_soup):
        # Get the language
        logger.debug("Getting language from movie page")
        try:
            language_block = movie_soup.find(
                "li", attrs={"data-testid": "title-details-languages"}
            )
            language = language_block.find("a").text
        except Exception as e:
            logger.exception(f"Exception: {e}")
            language = None
        logger.debug(f"Adding language: {language}")
        return language

    def scrape_budget(self, movie_soup):
        # Get the budget
        logger.debug("Getting budget from movie page")
        try:
            budget_block = movie_soup.find(
                "li", attrs={"data-testid": "title-boxoffice-budget"}
            )
            budget_value_box = budget_block.find(
                "div", class_="ipc-metadata-list-item__content-container"
            )
            budget = budget_value_box.find("span").text
        except AttributeError:
            logger.warning(f"Budget not found")
            budget = None
        except Exception as e:
            logger.exception(f"Exception: {e}")
            budget = None
        logger.debug(f"Adding budget: {budget}")
        return budget

    def scrape_gross(self, movie_soup):
        # Get the global gross
        logger.debug("Getting global gross from movie page")
        try:
            global_gross_block = movie_soup.find(
                "li", {"data-testid": "title-boxoffice-cumulativeworldwidegross"}
            )
            gross = global_gross_block.find(
                "span", class_="ipc-metadata-list-item__list-content-item"
            ).text
        except AttributeError:
            logger.warning(f"Global gross not found")
            gross = None
        except Exception as e:
            logger.exception(f"Exception: {e}")
            gross = None
        logger.debug(f"Adding global gross: {gross}")
        return gross

    def scrape_year(self, movie_soup):
        # Get the year
        logger.debug("Getting year from movie page")
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
            logger.debug(f"Year before: {year}")
            while not year[-1].isdigit():
                year = year[:-1]
            year = int(year[-4:])
        except ValueError:
            logger.warning(f"Year not found")
            year = None
        except Exception as e:
            logger.exception(f"Exception: {e}")
            year = None
        logger.debug(f"Adding year: {year}")
        return year

    def scrape_comment(self, comment_soup, movie_id, is_positive):
        # Get the comment
        comments_list = []
        try:
            comments = comment_soup.find_all(
                "div", class_=re.compile(r"text show-more__control(\s| clickable)?")
            )
            for comment in comments:
                comments_list.append([movie_id, comment.text, is_positive])
        except Exception as e:
            logger.exception(f"Exception: {e}")
            comment = None
        logger.debug(
            f"Adding {len(comments_list)} {'positive' if is_positive else 'negative'} comments for movie: {movie_id}"
        )

        return comments_list

    def scrape_overview(self, movie_soup):
        # Get the overview
        logger.debug("Getting overview from movie page")
        try:
            overview_block = movie_soup.find("p", {"data-testid": "plot"})
            overview = overview_block.find("span", {"data-testid": "plot-xl"}).text
        except:
            logger.warning(f"Overview not found")
            overview = None
        logger.debug(f"Adding overview: {overview}")
        return overview

    def scrape_thumbnail(self, movie_soup: BeautifulSoup):
        try:
            thumbnail_block = movie_soup.find_all(
                "div", {"data-testid": "hero-media__slate"}
            )

            # If the thumbnail block is empty, try to find the poster block
            if len(thumbnail_block) == 0:
                thumbnail_block = movie_soup.find_all(
                    "div", {"data-testid": "hero-media__poster"}
                )

            thumbnail_img = thumbnail_block[0].find("img")
            thumbnail_link = thumbnail_img["src"]
            thumbnail_alt = thumbnail_img["alt"]
        except Exception as e:
            logger.exception(f"Exception: {e}")
            thumbnail_link = None
            thumbnail_alt = None
        logger.debug(f"Adding thumbnail link: {thumbnail_link}")
        logger.debug(f"Adding thumbnail alt: {thumbnail_alt}")

        return thumbnail_link, thumbnail_alt

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
            logger.info(
                f"<======== Scraping movie {count} of {len(self.list_movies)} movies ========>"
            )

            # Get the link and fetch the movie page
            link = self.site_url + movie
            movie_response = None
            try:
                movie_response = request(
                    method="GET", url=link, headers=self.headers, timeout=60
                )
            except Exception:
                logger.warning("Connection refused by the server")
                logger.info("Sleeping for 10 seconds...")
                time.sleep(10)

            if movie_response is None:
                continue
            if movie_response.status_code != 200:
                logger.warning(f"Status code is not 200, skipping movie: {link}")
                continue

            logger.debug(f"Status code: {movie_response.status_code}")
            logger.debug(f"Adding movie page: {link}")

            # Parse the movie page
            movie_soup = BeautifulSoup(movie_response.text, "html.parser")
            self.scrape_movie(link, movie_soup)

            logger.info("Finished scraping this movie!")

        return self.movies_data

    def scrape_comments_by_id(self, movie_id: str) -> list:
        # Get the link and fetch the movie page
        comments_list = []

        link = self.site_url + "/title/" + movie_id + "/reviews"
        links = [
            link + "?sort=helpfulnessScore&dir=asc&ratingFilter=1",  # Negative = 0
            link + "?sort=helpfulnessScore&dir=desc&ratingFilter=10",  # Positive = 1
        ]

        for index, link in enumerate(links):
            logger.debug(
                f"Fetching {'positive' if index == 1 else 'negative'} comments for movie: {link}"
            )
            movie_response = None
            try:
                movie_response = request(
                    method="GET", url=link, headers=self.headers, timeout=60
                )
            except Exception:
                logger.warning("Connection refused by the server")
                logger.info("Sleeping for 10 seconds...")
                time.sleep(10)

            if movie_response is None:
                continue

            if movie_response.status_code != 200:
                logger.warning(f"Status code is not 200, skipping movie: {link}")
                continue

            logger.debug(f"Status code: {movie_response.status_code}")
            logger.debug(f"Scraping positive comments for movie: {link}")

            # Parse the movie page
            comment_soup = BeautifulSoup(movie_response.text, "html.parser")
            comments = self.scrape_comment(comment_soup, movie_id, index % 2)

            comments_list.extend(comments)

        return comments_list

    def scrape_thumbnail_by_id(self, movie_id: str) -> list:
        link = self.site_url + "/title/" + movie_id

        logger.debug(f"Fetching thumbnail for movie: {link}")
        movie_response = None

        try:
            movie_response = request(
                method="GET", url=link, headers=self.headers, timeout=60
            )
        except Exception:
            logger.warning("Connection refused by the server")
            logger.info("Sleeping for 10 seconds...")
            time.sleep(10)

        if movie_response is None:
            return []

        if movie_response.status_code != 200:
            logger.warning(f"Status code is not 200, skipping movie: {link}")
            return []

        logger.debug(f"Status code: {movie_response.status_code}")
        logger.debug(f"Scraping thumbnail for movie: {link}")

        # Parse the movie page
        movie_soup = BeautifulSoup(movie_response.text, "html.parser")
        thumbnail_link, thumbnail_alt = self.scrape_thumbnail(movie_soup)

        return [movie_id, thumbnail_link, thumbnail_alt]
