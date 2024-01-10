from pyspark.sql.types import StringType
import pyspark.sql.functions as F
import re


def tokenize(text):
    return re.findall("\\w+", text.lower())


def search(spark, tfidf, query, num_movies):
    # tokenize query into terms
    terms = tokenize(query)
    # create a dataframe with each term as a separate row
    query_tokens = spark.createDataFrame(terms, StringType()).withColumnRenamed(
        "value", "token"
    )
    # get aggregated score and count for each document for all the matched tokens
    result = (
        query_tokens.join(tfidf, "token")
        .groupBy("title")
        .agg(F.sum("tfidf").alias("score_sum"), F.count("tfidf").alias("matched_terms"))
    )
    # calculate document score
    result = result.withColumn(
        "score", F.col("score_sum") * F.col("matched_terms") / len(terms)
    )

    result_df = result.select("title").sort(F.col("score").desc())
    return [x.title for x in result_df.take(num_movies)]
