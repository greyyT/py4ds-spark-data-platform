from setuptools import find_packages, setup

setup(
    name="data_platform",
    packages=find_packages(exclude=["data_platform_tests"]),
    install_requires=[
        "dagster==1.4.*",
        "dagster-webserver",
        "dagster-docker",
        "dagster-cloud",
        "dagster-pyspark",
        "dagstermill",
        "pyspark==3.5",
        "beautifulsoup4",
        "pandas",
        "plotly",
        "shapely",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
