#IMPORTS
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import requests, sqlite3, os, shutil, gzip, logging, time

default_args = {
    "owner":"airflow",
    "depends_on_past":False,
    "start_date":datetime(2025,7,19),
    "email_on_failure":False,
    "email_on_retry":False,
    "retries":1,
    "retry_delay":timedelta(minutes=5)
}

dag = DAG(
    dag_id = 'neocities_scraper',
    default_args = default_args,
    description='Scrapes Neocities sites using Airflow',
    schedule_interval=None
)

#GLOBAL VARIABLES
#get dir script running in
dest_dir =  '/opt/airflow/' #Make this your airflow directory

dest_dir = dest_dir + "//" + "outs"
os.makedirs(dest_dir, exist_ok=True)

#FUNCTIONS
def create_dirs(dest_dir):
    folder_list = ['tarballs','xml','to_be_transformed','transformed']

    for f in folder_list:

        make_dir = dest_dir + "//" + f

        if not os.path.exists(make_dir):
            os.makedirs(make_dir)

create_dirs_task = PythonOperator(
    task_id = 'create_dirs',
    python_callable=create_dirs,
    provide_context = True,
    dag = dag,
    op_kwargs={"dest_dir":dest_dir}
)

def request_and_save(startingURL,dest_dir):
    #used in scrape_tags & scrape_maps
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }

    r = requests.get(startingURL, headers=headers, allow_redirects=True)

    if r.status_code == 200:
        print('Status Code: ' + str(r.status_code))
        print('Request successful at ' + startingURL)
    else:
        print('Status Code: ' + str(r.status_code))
        print('Error: Request Denied. Exiting script.')
        exit()

    split_url = startingURL.split('/')
    dest_path = dest_dir + '//tarballs' + '//' + split_url[-1]
    open(dest_path,'wb').write(r.content)

    unzip_path = dest_dir + '//xml' + '//' + split_url[-1]
    unzip_path = unzip_path.replace('.gz','')

    with gzip.open(dest_path,"rb") as f_in:
        with open(unzip_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
            print('Xml extracted.')

    return unzip_path



def scrape_tags(dest_dir):
    print('Starting tag scraping')

    startingURL = 'https://neocities.org/sitemap/tags.xml.gz'

    unzip_path = request_and_save(startingURL,dest_dir)

#unzip tag tarball 
    with open(unzip_path, "r") as f:
        openXml = f.read()

#find all urls for each tag
    soupXml = BeautifulSoup(openXml, "xml")
    tagURLs = soupXml.find_all("loc")

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }

    tagsDict_list = []
#go tag by tag
#put tag, site, and site views into df
    #get tag from url
    for tagURL in tagURLs:
        r = requests.get(tagURL.text, headers=headers, allow_redirects=True)
        if r.status_code == 200:
            print('Status Code: ' + str(r.status_code))
            print('Request successful at ' + tagURL.text)
        else:
            print('Status Code: ' + str(r.status_code))
            print('Error: Request Denied at ' + tag_URL.text)
            continue

        soup = BeautifulSoup(r.content,'html.parser')
#parse tag search results for site urls
        #find urls 
        siteURLs = soup.find_all('div',class_='title')
        siteInfo = soup.find_all('div',class_='site-stats hide-on-mobile')
        siteTags = soup.find_all('div',class_='site-tags')

        for i in range(0,len(siteURLs)):
            indiv_siteURL = siteURLs[i].find('a').get('href')
            indiv_siteInfo = siteInfo[i].find('a').text
            tagtext = siteTags[i].text
            tagtext = tagtext.replace(" ","")
            tagtext = tagtext.replace(",","")
            tagtext2 = tagtext.split()
            indiv_siteInfo = indiv_siteInfo.replace(" ","")
            indiv_siteInfo = indiv_siteInfo.replace("\n","")
            tagsDict = {
                'tags': tagtext2,
                'siteViews': indiv_siteInfo,
                'siteURL': indiv_siteURL
                }

            tagsDict_list.append(tagsDict)

        time.sleep(2)

#compile into df
#column
        
    df = pd.DataFrame(tagsDict_list)
    df = df.explode(['tags']).reset_index(drop=True)
    df = df.drop_duplicates()
    csv_dest = dest_dir + '//to_be_transformed' + '//' + 'tags_raw.csv'
    df.to_csv(csv_dest)


scrape_tags_task = PythonOperator(
    task_id = 'scrape_tags',
    python_callable=scrape_tags,
    provide_context = True,
    dag = dag,
    op_kwargs={"dest_dir":dest_dir}
)


def transform_data(dest_dir):
    #copy tag csv from 
    tags_source_path = dest_dir + '//' + r'to_be_transformed/tags_raw.csv'
    tags_dest_path = dest_dir + '//' + r'transformed/tags_done.csv'
    shutil.copy(tags_source_path,tags_dest_path)

transforming_task = PythonOperator(
    task_id = 'transform_data',
    python_callable=transform_data,
    provide_context = True,
    dag = dag,
    op_kwargs={"dest_dir":dest_dir}
)

##def load_data(dest_dir):
##    sql_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '//' + 'airflow.db'
##    
##    cnxn = sqlite3.connect(sql_path)
##
##    done_dir = dest_dir + '//' + 'transformed'
##
##    for file in os.listdir(done_dir):
##        if file.endswith('.csv'):
##            file_path = os.path.join(done_dir,file)
##            df = pandas.read_csv(file_path)
##            df.to_sql(file,cnxn,if_exists='replace')
##
##loading_task = PythonOperator(
##    task_id = 'load_to_sqlite',
##    python_callable=load_data,
##    provide_context = True,
##    dag = dag,
##    op_kwargs={"dest_dir":dest_dir}
##)

create_dirs_task >> scrape_tags_task >> transforming_task
