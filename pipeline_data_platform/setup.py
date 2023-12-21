from setuptools import find_packages, setup

setup(
    name="data_platform",
    packages=find_packages(exclude=["data_platform_tests"]),
    install_requires=[
        "dagster==1.4.17",
        "dagster-docker",
        "dagster-pyspark",
        "dagstermill",
        "pyspark==3.5",
        "beautifulsoup4",
        "pandas",
        "gdown",
        "pendulum==2.1.2",
        "fastapi==0.105.0",
        "uvicorn==0.24.0.post1",
        "jupyter",
        "matplotlib",
        "seaborn",
        "nltk",
        "wordcloud",
    ],
    extras_require={
        "dev": [
            "dagster-webserver",
            "pytest",
            "dagster-cloud",
            "plotly",
            "shapely",
        ]
    },
)
