import pandas as pd
import os

#loading tags_done.csv
script_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = script_directory + "\\" + "tags_done.csv"
tags_done_df = pd.read_csv(csv_path)

#prep for sites per tag
tags_done_df = tags_done_df[["tags","siteURL"]]
sites_df = tags_done_df.drop_duplicates()
sites_df = sites_df.groupby("tags")["siteURL"].nunique().reset_index()
sites_path = script_directory + "\\" + "tags_num_sites.csv"
sites_df.to_csv(sites_path,index=False)

#prep for outer join
tags_done_df2 = tags_done_df
tags_done_df = tags_done_df.rename(columns={"tags":"source"})
tags_done_df2 = tags_done_df2.rename(columns={"tags":"target"})

#outer join on url to get sources & targets
network_df = pd.merge(tags_done_df,tags_done_df2,on="siteURL",how="outer").reset_index()
network_df = network_df[["source","target"]]
network_df["weight"] = 1
network_path = script_directory + "\\" + "tags_source_target.csv"
network_df.to_csv(network_path,index=False)

