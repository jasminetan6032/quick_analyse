#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  9 12:05:43 2023

@author: jwt30
"""
import mne 
import pandas
import numpy
import glob
import quick_analyse_config as cfg
from termcolor import colored

def find_response_triggers(events):
    events_data = pandas.DataFrame(events)
    events_data.columns = ['sample', 'initialState','trigger']
    trigger_counts = events_data['trigger'].value_counts()
    #check for largest number of triggers (leave case for those that are missing one side - eg. participant 075801)
    likely_response_triggers = trigger_counts[trigger_counts.index > 255].nlargest(2).index
    
    if len(likely_response_triggers) == 2:
        if numpy.any(likely_response_triggers[0] == cfg.right_responses):
            cfg.event_dict.update({'response/right':likely_response_triggers[0]})
            cfg.event_dict.update({'response/left':likely_response_triggers[1]})
        elif numpy.any(likely_response_triggers[0] == cfg.left_responses):
            cfg.event_dict.update({'response/right':likely_response_triggers[1]})
            cfg.event_dict.update({'response/left':likely_response_triggers[0]})

    elif len(likely_response_triggers) == 1:
        if numpy.any(likely_response_triggers[0] == cfg.right_responses):
            cfg.event_dict.update({'response/right':likely_response_triggers[0]})
            print("Warning: Missing left response")

        elif numpy.any(likely_response_triggers[0] == cfg.left_responses):
            cfg.event_dict.update({'response/left':likely_response_triggers[0]})
            print("Warning: Missing right response")
            
    elif len(likely_response_triggers) == 0:
        print("Warning: Missing all response triggers")

def remove_spurious_triggers(events):
    #removes triggers in which sample was interrupted on the way to the intended trigger
    spurious_triggers = [i for i in range(0, len(events)) if events[i,1]!=0 and events[i,1]==events[i-1,2] and events[i,0]-events[i-1,0]==1]
    for i in spurious_triggers:
        events = numpy.delete(events, i-1,0)
        events[i-1,1] = 0 
    return events             

def check_triggers(events):
    #check for number of stimuli and response triggers. If it doesn't equal to 288 for AttenAud and 168 for AttenVis (per run), or if there are an unreasonable number of response triggers, flag to take a look.
    stimuli_list = events[:, 2].tolist()
    list_of_stimuli_triggers = [i for i in stimuli_list if i < 255]
    if len(list_of_stimuli_triggers) != cfg.number_of_stimuli:
        warning = 'Unexpected number of stimuli triggers: '
        print(colored(warning + str(len(list_of_stimuli_triggers)),'magenta'))
    
    #print number of responses triggers to check for sticky or missing responses
    list_of_response_triggers = [i for i in stimuli_list if i > 255]
    report_nResponses = 'Number of response triggers: '
    print(colored(report_nResponses + str(len(list_of_response_triggers)),'magenta'))
    
    #check column two for any triggers that do not start from zero and extract events to eyeball
    non_zero_initial_states = [i for i in range(0, len(events)) if not events[i,1]==0]
    problematic_events = events[non_zero_initial_states,:]
    return problematic_events


def get_metadata_and_behaviour(events):
    row_events = [event_name for event_name in list(cfg.event_dict.keys()) if not 'response' in event_name]
    keep_first = ["response"]
    metadata, events, event_id = mne.epochs.make_metadata(
        events=events, event_id=cfg.event_dict,
        tmin=cfg.metadata_tmin, tmax=cfg.metadata_tmax, sfreq=raw.info['sfreq'],
        row_events=row_events,
        keep_first=keep_first)
    
    if cfg.paradigm in ('AttenAud','Misophonia'):
        
        metadata[['attention_side','stimuli_type', 'pitch','stimulus_side']] = metadata.event_name.str.split('/',expand = True)
        metadata.loc[(metadata['first_response'] == metadata['stimulus_side']) & (metadata['stimuli_type'].str.contains('target')),
                     'response_correct'] = 'Hit'
        metadata.loc[(metadata['first_response'] != metadata['stimulus_side']) & (metadata['stimuli_type'].str.contains('target')),
                     'response_correct'] = 'Incorrect Response'
        metadata.loc[~(metadata['first_response'].isnull()) & ~(metadata['stimuli_type'].str.contains('target')),
                     'response_correct'] = 'False Alarm'
        metadata.loc[(metadata['first_response'].isnull()) & (metadata['stimuli_type'].str.contains('target')),
                     'response_correct'] = 'Missed Target'
        metadata.loc[(metadata['first_response'].isnull()) & ~(metadata['stimuli_type'].str.contains('target')),
                     'response_correct'] = 'Correct Rejection'
        
        stimuli_counts = metadata.value_counts(['stimuli_type','stimulus_side','attention_side'], sort = False)
        
        if not set(cfg.stimuli_count_reference).issubset(stimuli_counts.index):
            stimuli_counts= stimuli_counts.reindex(cfg.stimuli_count_reference,fill_value=0)
        
        stimuli_counts = stimuli_counts.sort_index()
        
        response_counts = metadata['response_correct'].value_counts()
        
        if not set(cfg.response_count_reference).issubset(response_counts.index):
            response_counts= response_counts.reindex(cfg.response_count_reference,fill_value=0)
    
        
        average_performance_in_run = pandas.DataFrame([{"%correct": round(response_counts['Hit']/stimuli_counts['target'].sum(),2), "reaction_time":metadata['response'].median()}])
        
        if cfg.paradigm == 'AttenAud':
            run_info = pandas.DataFrame([{"Stds_on_R_Attend_R":stimuli_counts['standard','right','attendRight'],"Stds_on_L_Attend_L":stimuli_counts['standard','left','attendLeft'],
                        "Beeps_on_R_Attend_L":stimuli_counts['beep','right','attendLeft'],"Beeps_on_L_Attend_R":stimuli_counts['beep','left','attendRight'],
                        "Targets_on_R_Attend_R":stimuli_counts['target','right'].sum(),"Targets_on_L_Attend_L":stimuli_counts['target','left'].sum(),
                        "Novels_on_R_Attend_L":stimuli_counts['novel','right'].sum(),"Novels_on_L_Attend_R":stimuli_counts['novel','left'].sum(),
                        "Distractors_on_R_Attend_L":stimuli_counts['dev','right'].sum(),"Distractors_on_L_Attend_R":stimuli_counts['dev','left'].sum(),
                        "Hits": response_counts['Hit'], "FalseAlarms": response_counts['False Alarm'], "IncorrectResponses":response_counts['Incorrect Response'],
                        "Misses":response_counts['Missed Target'],"CorrectRejections":response_counts['Correct Rejection'],
                        "nStimuli":len(metadata),"nResponses":metadata['response'].notna().sum()}])
        
        elif cfg.paradigm == 'Misophonia':
            run_info = pandas.DataFrame([{"Stds_on_R_Attend_R":stimuli_counts['standard','right','attendRight'],"Stds_on_L_Attend_L":stimuli_counts['standard','left','attendLeft'],
                        "Beeps_on_R_Attend_L":stimuli_counts['beep','right','attendLeft'],"Beeps_on_L_Attend_R":stimuli_counts['beep','left','attendRight'],
                        "Targets_on_R_Attend_R":stimuli_counts['target','right'].sum(),"Targets_on_L_Attend_L":stimuli_counts['target','left'].sum(),
                        "Novels_on_R_Attend_L":stimuli_counts['novel','right'].sum(),"Novels_on_L_Attend_R":stimuli_counts['novel','left'].sum(),
                        "Distractors_on_R_Attend_L":stimuli_counts['dev','right'].sum(),"Distractors_on_L_Attend_R":stimuli_counts['dev','left'].sum(),
                        "Misophones_on_R_Attend_L":stimuli_counts['misophone','right'].sum(),"Misophones_on_L_Attend_R":stimuli_counts['misophone','right'].sum(),
                        "Hits": response_counts['Hit'], "FalseAlarms": response_counts['False Alarm'], "IncorrectResponses":response_counts['Incorrect Response'],
                        "Misses":response_counts['Missed Target'],"CorrectRejections":response_counts['Correct Rejection'],
                        "nStimuli":len(metadata),"nResponses":metadata['response'].notna().sum()}])
        
    elif cfg.paradigm == 'AttenVis':
        metadata[['condition','difficulty']] = metadata.event_name.str.split('/',expand = True)
        metadata.loc[metadata['event_name'] == 'target',
                     'response'] = float("nan")
        metadata.loc[metadata['event_name'] == 'target',
                     'first_response'] = 'None'
        stimuli_counts = metadata.value_counts(['condition','difficulty'], sort = False)
        response_counts = metadata['first_response'].value_counts()
        run_info = pandas.DataFrame([{"pop_out4": stimuli_counts['pop-out','4'],"pop_out6": stimuli_counts['pop-out','6'], 
                    "pop_out8": stimuli_counts['pop-out','8'], "pop_out10": stimuli_counts['pop-out','10'],
                    "search4": stimuli_counts['search','4'],"search6": stimuli_counts['search','6'], 
                    "search8": stimuli_counts['search','8'], "search10": stimuli_counts['search','10'],
                    "total_pop-outs": stimuli_counts['pop-out'].sum(),"total_search": stimuli_counts['search'].sum(), 
                    "right_responses": response_counts['right'], "left_responses": response_counts['left'],
                    "nStimuli": stimuli_counts.sum(),"nResponses":metadata['response'].notna().sum()}])
        average_performance_in_run = pandas.DataFrame([{"reaction_time":metadata['response'].median()}])
   
    return run_info, average_performance_in_run


summary = pandas.DataFrame()
average_performance = pandas.DataFrame()

files = glob.glob(cfg.data_dir + str(cfg.participant) + '_' +cfg.paradigm + '_run0*_raw.fif')
files.sort()

for file in files:
    raw = mne.io.read_raw_fif(file)
    try:
        events = mne.find_events(raw, stim_channel='STI101', uint_cast= True)
    except:
        events = mne.find_events(raw, stim_channel='STI101',shortest_event=1,uint_cast= True)
        print(colored("Warning: ValueError:shortest event length = 1",'blue'))
    find_response_triggers(events)
    events = remove_spurious_triggers(events)
    problematic_events = check_triggers(events)
    if problematic_events.size >0:
        print(problematic_events)
  
    run_info,average_performance_in_run = get_metadata_and_behaviour(events)
    average_performance = pandas.concat([average_performance,average_performance_in_run])
    summary = pandas.concat([summary,run_info])

print(colored(summary.sum(),'cyan'))
print(average_performance.mean())
