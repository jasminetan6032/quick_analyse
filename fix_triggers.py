#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 13:24:41 2023

@author: jwt30
"""
import pandas
import mne
import numpy
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
            cfg.event_dict.pop('response/left')
            print("Warning: Missing left response")

        elif numpy.any(likely_response_triggers[0] == cfg.left_responses):
            cfg.event_dict.update({'response/left':likely_response_triggers[0]})
            cfg.event_dict.pop('response/right')
            print("Warning: Missing right response")
            
    elif len(likely_response_triggers) == 0:
        print("Warning: Missing all response triggers")

def fix_old_triggers(events):
    old_triggers = [131,132,133,134]
    old_triggers_to_fix = [i for i in range(0, len(events)) if numpy.any(events[i,2]== old_triggers)]
    if len(old_triggers_to_fix) > 0:
        events[events[:,2] == 131,2] = 35
        events[events[:,2] == 132,2] = 36
        events[events[:,2] == 133,2] = 37
        events[events[:,2] == 134,2] = 38 
    return events

def remove_spurious_triggers(events):
    spurious_triggers = [i for i in range(0, len(events)) if events[i,1]!=0 and events[i,1]==events[i-1,2] and events[i,0] - events[i-1,0]==1]
    trigger_to_remove = [i - 1 for i in spurious_triggers]
    events = numpy.delete(events, trigger_to_remove ,axis = 0)
    for i in trigger_to_remove:
        events[i,1] = 0
    return events                     

def check_triggers(events):
    #check for number of stimuli and response triggers. If it doesn't equal to 288 for AttenAud and 168 for AttenVis (per run), or if there are an unreasonable number of response triggers, flag to take a look.
    stimuli_list = events[:, 2].tolist()
    list_of_stimuli_triggers = [i for i in stimuli_list if i < 255]
    nStimuli = len(list_of_stimuli_triggers)
    if nStimuli != cfg.number_of_stimuli:
        warning = 'Unexpected number of stimuli triggers: '
        print(colored(warning + str(len(list_of_stimuli_triggers)),'magenta'))

    #check column two for any triggers that do not start from zero and extract events to eyeball
    non_zero_initial_states = [i for i in range(0, len(events)) if not events[i,1]==0]
    problematic_events = events[non_zero_initial_states,:]
    return problematic_events, nStimuli

        
def fix_superimposed_triggers(events):
    
    non_zero_initial_states = [i for i in range(0, len(events)) if events[i,1]!=0]
    
    for i in non_zero_initial_states:
        events[i,2] = events[i,2] - events[i,1] 
        
    stimuli_list = events[:, 2].tolist()
    uncorrected_events = set(stimuli_list) - set(list(cfg.event_dict.values()) + cfg.all_responses)
    if uncorrected_events:
        for event in uncorrected_events:
            index_of_uncorrected_events = [index for index in range(len(events)) if numpy.any(events[index,2] == event)]
            
            for i in index_of_uncorrected_events:
                events[i,2] = events[i,2] - events[i-1,2]
    return events

def find_sticky_triggers(events,trigger):
    #check for range of gaps between sticky triggers after deleting stimuli triggers
    events_del = numpy.delete(events, numpy.where(events[:,1]!=0),axis = 0)
    
    sticky_trigger = events_del[events_del[:,2] == trigger]
    event_sample_number = sticky_trigger[:,0]

    sample_differences = numpy.diff(event_sample_number).tolist()
    sample_differences.insert(0, 0)

    sample_differences = numpy.array(sample_differences)
    sample_differences = numpy.reshape(sample_differences,(sample_differences.size,1))
    sticky_trigger_with_difference = numpy.append(sticky_trigger,sample_differences, axis = 1)
    stuck_responses = sticky_trigger_with_difference[sticky_trigger_with_difference[:,3] < 10000]
    stuck_responses = stuck_responses[1:,]
    if len(stuck_responses)>1:
        sticky_trigger_dict = {'trigger': trigger, 
                               'max_sample_difference': numpy.max(stuck_responses[1:,3]),
                               'min_sample_difference': numpy.min(stuck_responses[1:,3]),
                               'mean_sample_difference': numpy.mean(stuck_responses[1:,3]),
                               'median_sample_difference': numpy.median(stuck_responses[1:,3])}
    else:
        sticky_trigger_dict = {'trigger': trigger, 
                               'max_sample_difference': 0,
                               'min_sample_difference': 0,
                               'mean_sample_difference': 0,
                               'median_sample_difference': 0}

    sticky_trigger_array = numpy.array(list(sticky_trigger_dict.items()))
    return sticky_trigger_array
#     #defined as any response triggers that follow a response trigger or a trigger corrected from an initial state of a response trigger
#     stuck_triggers = [i for i in range(0, len(events)) if numpy.any(events[i,2]== cfg.all_responses) and (numpy.any(events[i-1,2]== cfg.all_responses) or numpy.any(events[i-1,1]== cfg.all_responses))]
#     time_to_repeat = pandas.Series(original_events[stuck_triggers,3])
        

        
#load alignment csv file
df = pandas.read_csv ('/local_mount/space/hypatia/2/users/Jasmine/github/alignment/AttenAud_ERM_MRI_alignment_from_20190314_to_20230327.csv')
df['problematic_events'] = ''
df['new_problematic_events'] = ''
df['sticky_triggers_left'] = ''
df['sticky_triggers_right'] = ''

for i in range(0,len(df)):
    file = df.loc[i,'Paradigm_data_path']
    raw = mne.io.read_raw_fif(file)
    try:
        events = mne.find_events(raw, stim_channel='STI101',uint_cast=True)
        df.at[i,'errors'] = 'no input error'
    except:
        events = mne.find_events(raw, stim_channel='STI101',shortest_event=1, uint_cast=True)
        df.at[i,'errors'] = 'ValueError:shortest_event=1'
        
    find_response_triggers(events)
    
    events = fix_old_triggers(events)
    events = remove_spurious_triggers(events)
        
    problematic_events, nStimuli = check_triggers(events)
    
    df.at[i,'problematic_events'] = problematic_events.astype(object)
    
    df.at[i,'nStimuli'] = nStimuli
    
    fixed_events = fix_superimposed_triggers(events)
    
    new_problematic_events, new_nStimuli = check_triggers(fixed_events)
    
    df.at[i,'new_problematic_events'] = new_problematic_events.astype(object)
    
    df.at[i,'new_nStimuli'] = new_nStimuli
    
    if cfg.event_dict.get('response/left'):
        df.at[i,'sticky_triggers_left'] = find_sticky_triggers(events, cfg.event_dict['response/left']).astype(object)
    if cfg.event_dict.get('response/right'):    
        df.at[i,'sticky_triggers_right'] = find_sticky_triggers(events, cfg.event_dict['response/right']).astype(object)
        
    
df.to_csv('AttenAud_ERM_MRI_alignment_from_20190314_to_20230327_new_fix.csv')


