#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 22 18:50:37 2023

@author: jwt30
"""

import scipy.io
import pandas
import shutil 
import glob

#save matlab results on Github in the right folders on transcend, adjust paradigm 
paradigm = 'AttenVis'
data_dir = '/local_mount/space/hypatia/2/users/Jasmine/github/VisAudAtten/results/'
files = glob.glob(data_dir + paradigm + '/**_Results.mat')
files.sort()

subjects = []
dates = []

for file in files:
    #extract participant number
    file_info = file.split('/')
    subject_info = file_info[-1].split('_')
    subject_id = subject_info[0]
    subjects.append(subject_id)
    #extract date and time of acquisition
    date_and_time = subject_info[1] + ' ' + subject_info[2]
    dates.append(date_and_time)

behav_df = pandas.DataFrame(data={'original_results_file': files, 'Subject': subjects, 'Date_collected': dates})

#correct date format
behav_df['Date_collected'] = pandas.to_datetime(behav_df['Date_collected'], format = '%d-%b-%Y %H:%M:%S')
    
behav_df['previous_row_subject'] = behav_df.Subject.shift(1)
behav_df.loc[behav_df['Subject'] != behav_df['previous_row_subject'],
                     'run'] = 1

for i in range(1,len(behav_df)):
    if behav_df.loc[i,'Subject'] == behav_df.loc[i-1,'Subject'] and behav_df.loc[i,'Date_collected'].date() != behav_df.loc[i-1,'Date_collected'].date():
        behav_df.loc[i,'run'] = 1
    elif behav_df.loc[i,'Subject'] == behav_df.loc[i-1,'Subject'] and behav_df.loc[i,'Date_collected'].date() == behav_df.loc[i-1,'Date_collected'].date():
        behav_df.loc[i,'run'] = behav_df.loc[i-1,'run'] + 1

behav_df['Date_formatted'] = behav_df.Date_collected.dt.strftime('%Y%m%d')
behav_df['run'] = behav_df['run'].astype('Int64').astype('str')
#construct save name
paradigm_dir = '/autofs/cluster/transcend/MEG/' + paradigm
behav_df['destination_folder']  = paradigm_dir + '/' + behav_df['Subject'] + '/visit_' + behav_df['Date_formatted'] +'/' 
behav_df['destination_file'] = behav_df['destination_folder'] + behav_df['Subject'] + '_' + paradigm + '_run' + behav_df['run'] + '_behaviour.mat'

for i in range(0,len(behav_df)):
    source_file = behav_df.loc[i,'original_results_file']
    dest_file = behav_df.loc[i,'destination_file']
    try:
        shutil.copyfile(source_file, dest_file)
    except:
        error_message = 'Investigate Participant ' + behav_df.loc[i,'Subject']
        print(error_message)
        
        
mat = scipy.io.loadmat('/autofs/cluster/transcend/MEG/AttenAud/009901/visit_20190515/009901_AttenAud_run2_behaviour.mat')
triggers = mat['Triggers_trace']
triggers = list(triggers)

res = [x for x in range(0,len(list_of_stimuli_triggers)) if list_of_stimuli_triggers[x] != triggers[x]]

triggers = [item for sublist in triggers for item in sublist]

responses_mat = mat['Response_trace']
responses = pandas.DataFrame(responses_mat[:,0])
responses_counts = responses.value_counts()

behavioural_summary = { "Hits":responses_counts[1.0], "Misses":responses_counts[1000.0],
                    "%correct":round(responses_counts[1.0]/(responses_counts[1.0]+responses_counts[1000.0]),2)}

stimuli_list = fixed_events[:,2].tolist()
list_of_stimuli_triggers = [i for i in stimuli_list if i < 255] 
list_of_response_triggers = [i for i in stimuli_list if i > 255] 
responses['triggers'] = list_of_stimuli_triggers

metadata['matlab_responses'] = responses_mat[:,0]