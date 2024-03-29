#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 13:22:44 2023

@author: jwt30
"""
import pandas as pd
import os
import shutil
from termcolor import colored

downloads_dir = "/homes/7/jwt30/Downloads/"

download_file = []

for path, directory_names, filenames in os.walk(downloads_dir):
    for filename in filenames:
        if 'MisophoniaAudioQuest' in filename:
            download_file = os.path.join(path,filename)

if download_file:
    shutil.move(download_file, '/local_mount/space/hypatia/2/users/Jasmine/github/quick_analyse/MisophoniaAudioRatings.csv')
else: 
    print(colored("No RedCap file in Downloads. Do you need an updated file? If so, download from RedCap (with labels).",'yellow'))


#make sure you always have an updated file from RedCap called MisophoniaAudioRatings in quick_analyse
filepathname = '/local_mount/space/hypatia/2/users/Jasmine/github/quick_analyse/MisophoniaAudioRatings.csv'
df = pd.read_csv(filepathname, dtype=str)

participant_number = input("Enter participant number: ")

df = df[df['Event Name']=='Testing 1']
df = df.drop(columns = "Event Name")
df = df.rename(columns = {"Please identify this sound (guess if you are unsure)": "Please identify this sound (guess if you are unsure).0",
                          "Please rate the intensity of your reaction to this sound when made by another person or object":"Please rate the intensity of your reaction to this sound when made by another person or object.0"})
participant_df = df[df["Subject ID:"] == participant_number]
data_long = pd.wide_to_long(participant_df,["Please identify this sound (guess if you are unsure)","Please rate the intensity of your reaction to this sound when made by another person or object"],
                            "Subject ID:","Sound to identify",sep = ".")
data_long = data_long.rename(columns = {"Please identify this sound (guess if you are unsure)": "Identified sound",
                            "Please rate the intensity of your reaction to this sound when made by another person or object": "Rating"})
answers = ["lipsmack2","sniffing","throat clear","bang","nailclip2","bark","chain","chewing", 
           "cling","clong","dial tone","honk","raygun","snoring","breathing1","jointcrack5","slurp1","swallow1"]
miso_or_novel = [1,1,1,0,1,0,0,1,
                 0,0,0,0,0,1,1,1,1,1]
data_long["Correct answer"] = answers
data_long["Misophonic trigger"] = miso_or_novel
data_long["Rating"] = pd.to_numeric(data_long["Rating"])

miso_sounds = data_long[data_long["Misophonic trigger"] == 1]
miso_sounds = miso_sounds.sort_values(by="Rating",ascending = False)
top5_miso_avg = miso_sounds["Rating"][0:4].mean()

novels = data_long[data_long["Misophonic trigger"] == 0]
novels = novels.sort_values(by="Rating",ascending = False)
bottom3_novels_avg = novels["Rating"][-3:].mean()

if top5_miso_avg/bottom3_novels_avg > 0.5:
    print("Participant has valid sounds for experiment")
else: print(colored("Participant does NOT have valid sounds for experiment",'red'))
    
top5miso = miso_sounds[['Identified sound','Rating', 'Correct answer']].head(5)
print(colored(top5miso,'cyan'))

top_novels = novels[novels["Rating"] > 4]
novels_to_remove= top_novels[['Identified sound','Rating', 'Correct answer']]
print(colored(novels_to_remove,'magenta'))    

safe_novels = novels[novels["Rating"] < 4]
novels_to_keep = safe_novels[['Identified sound','Rating', 'Correct answer']]
print(colored(novels_to_keep,'green'))    
    
