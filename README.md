# Scraping Data From Neocities
![](https://i.imgur.com/9ekKHEe.png)
[Neocities Tags](https://public.flourish.studio/visualisation/26397684/)
## Introduction
Neocities is a platform that hosts static websites for free, in the vein of Geocities, a now defunct but once very popular platform that ran from 1994 to 2004. The websites hosted on Neocities are varied; many are blogs, art projects, and fansites similar to those of the early 2000s. Many site owners display immense passion and artistic talent in their creations. Because of this, I have a soft spot for Neocities, and thus I thought it would be a good subject for a project of my own.

In this project, I set up an Apache Airflow container in Docker, wrote an ETL pipeline to scrape data from Neocities, transform it, and export it, created visualizations from the resulting data, and analyzed it. In this repository you will find instructions for setting up an Airflow container, the DAG I used to scrape data, a script I used for additional data transformations, and the Power BI report I created using the data I gathered.

## Setting Up Airflow Container in Docker
Apache Airflow doesn’t run natively on Windows, leaving me with two options: run Airflow on Linux subsystem or run it in a Docker container. I opted for the latter.
I started by creating a directory named “airflow-docker”. In this directory I placed two files: 
A .env file containing only the following line (to avoid Airflow UID errors):
`AIRFLOW_UID=50000`

Airflow’s docker-compose.yaml file (downloaded from https://airflow.apache.org/docs/apache-airflow/3.1.3/docker-compose.yaml). I edited this file to install necessary python libraries at build:
`_PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:- requests pandas logging datetime}`

IMPORTANT NOTE: THIS SHOULD NOT BE DONE IN PRODUCTION ENVIRONMENTS! This causes libraries to be installed at runtime, including when the container is restarted, opening one up to security vulnerabilities. I used it due to convenience, but in a production environment, one should build a custom image with necessary dependencies instead.

After placing these files in the airflow directory, I opened the directory through the Docker desktop console and ran the following command to initialize the Airflow database:
`docker compose up airflow-init`

NOTE: if your Airflow container keeps restarting after 10 seconds, it’s probably because you didn’t initialize the database.

Then to start the container, I used the following command:
`docker compose up -d`

## Writing the DAG
Originally, I intended to scrape information from the full Neocities sitemap. Recently, however, Neocities updated their sitemap to exclude submaps of sites hosted on their platform. As a result, I instead focused on crawling the portion of the sitemap associated with tags.

The DAG involved is relatively simple; it downloads the tags sitemap tarball, extracts tag URLs, scrapes relevant data and loads it into a dataframe, transforms the data, and saves it to disk. Running the DAG took ~21 hours, longer than it took to write it. The finished data was exported from the container as a .csv.

## Visualizations & Analysis
![](https://i.imgur.com/02FJflN.png)
To analyse the data I gathered, I created a Power BI report (scrape from neocities analysis.pbix) and a [network graph](https://public.flourish.studio/visualisation/26389853/).

I found that the tags associated with the most sites are ‘art’ and ‘personal’, both with over 600 sites associated. Several hundred sites behind are blog, videogames, music, and writing. These tags also dominate views per tag, except for ‘writing’ and ‘blog’, which only had 64 million views and 127 million views respectively, placing it far behind a number of tags associated with less sites.

Interestingly, there’s a cluster of tags (as seen in the scatter plot on the page ‘Tags w/ Least Sites & Most Views’ of the Power BI report) which have under 10 associated sites but a high number of views. These are ‘halloween’, ‘animals’, ‘monsters’, and ‘creepypasta’ The tag ‘pokemon’ also has a comparatively small number of associated sites (28) for the number of views it’s garnered (263 million). All 5 of these tags with low associated sites and high view count are associated with ‘bogleech.com’, the site with the highest view count at 247 million, which hosts the webcomic Awful Hospital.

I also noticed another cluster of tags with sub-20 associated sites around 150 million views (‘animation’,’literature’,’internet’,’alternative’, ‘individual’). ‘Animation’, ’literature’, ’alternative’, and ‘individual’ are all associated with ‘ranfren.neocities.org’, which also hosts a webcomic.  ‘Internet’ is only associated with 4 sites within the top 100 most viewed sites, less than tags not contained within the previously discussed clusters. It may appear in this cluster because it’s associated with ‘neonaut.neocities.org’ , the 4th most viewed site.

## Conclusion
This was a fun project, and I hope you enjoyed reading about it because I enjoyed creating it. The internet is full of little oddities, many of which are hosted on Neocities.

