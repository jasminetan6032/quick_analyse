#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  9 15:03:31 2023

@author: jwt30
"""
import os
import pandas

paradigm = 'Misophonia'
participant = '126401'
date = 231204

MEG_dir = '/autofs/space/megraid_research/MEG/tal'
#transcend_dir = '/autofs/cluster/transcend/MEG'

data_dir = os.path.join(MEG_dir,'subj_' + participant,str(date)+'/')
#data_dir = os.path.join(transcend_dir,paradigm,participant,'visit_' + str(date) + '/')

correct_stimuli_triggers = {'AttenVis': 168*2, #targets and stimuli grids
                            'AttenAud': 288,
                            'Misophonia': 288}

number_of_stimuli = correct_stimuli_triggers[paradigm]

tmin_tmax = {'AttenVis': {'tmin':0.0,
                          'tmax':2.0},
             'AttenAud': {'tmin':0.0,
                          'tmax':1.0},
             'Misophonia': {'tmin':0.0,
                            'tmax':1.0}}

metadata_tmin, metadata_tmax = tmin_tmax[paradigm]['tmin'], tmin_tmax[paradigm]['tmax']

right_responses = [256,512,1024,2048]
left_responses = [4096,8192,16384,32768]
all_responses = right_responses + left_responses

all_event_dicts = {

    'AttenVis' : {'search/4': 1,
                     'search/6': 2,
                     'search/8': 3,
                     'search/10': 4,
                     'pop-out/4': 5,
                     'pop-out/6': 6,
                     'pop-out/8': 7,
                     'pop-out/10': 8,
                     'target': 32,
                     'response/right': 2048,
                     'response/left': 32768
                     },

    'AttenAud' : {'attendRight/standard/high/right': 1,
                     'attendRight/standard/low/right': 3,
                     'attendRight/target/high/right': 11,
                     'attendRight/target/low/right': 13,
                     'attendRight/beep/low/left': 5,
                     'attendRight/beep/high/left': 7,
                     'attendRight/dev/low/left': 35,
                     'attendRight/dev/high/left': 37,
                     'attendRight/novel/low/left': 25,
                     'attendRight/novel/high/left': 27,
                     'attendLeft/standard/high/left': 2,
                     'attendLeft/standard/low/left': 4,
                     'attendLeft/target/high/left': 12,
                     'attendLeft/target/low/left': 14,
                     'attendLeft/beep/low/right': 6,
                     'attendLeft/beep/high/right': 8,
                     'attendLeft/dev/low/right': 36,
                     'attendLeft/dev/high/right': 38,
                     'attendLeft/novel/low/right': 26,
                     'attendLeft/novel/high/right': 28,
                     }, 

    'Misophonia': {'attendRight/standard/high/right': 1,
                     'attendRight/standard/low/right': 3,
                     'attendRight/target/high/right': 11,
                     'attendRight/target/low/right': 13,
                     'attendRight/beep/low/left': 5,
                     'attendRight/beep/high/left': 7,
                     'attendRight/dev/low/left': 35,
                     'attendRight/dev/high/left': 37,
                     'attendRight/novel/low/left': 25,
                     'attendRight/novel/high/left': 27,
                     'attendRight/misophone/low/left': 45,
                     'attendRight/misophone/high/left': 47,
                     'attendLeft/standard/high/left': 2,
                     'attendLeft/standard/low/left': 4,
                     'attendLeft/target/high/left': 12,
                     'attendLeft/target/low/left': 14,
                     'attendLeft/beep/low/right': 6,
                     'attendLeft/beep/high/right': 8,
                     'attendLeft/dev/low/right': 36,
                     'attendLeft/dev/high/right': 38,
                     'attendLeft/novel/low/right': 26,
                     'attendLeft/novel/high/right': 28,
                     'attendLeft/misophone/low/right': 46,
                     'attendLeft/misophone/high/right': 48
                     }  
    }

event_dict = all_event_dicts[paradigm]

stimuli_type = ['beep','beep','dev','dev','novel','novel','standard','standard','target','target']
stimuli_type_misophonia = stimuli_type + ['misophone','misophone']
 
stimulus_side = ['left','right','left','right','left','right','right','left','right','left']
stimulus_side_misophonia = stimulus_side + ['left','right']

attention_side=['attendRight','attendLeft','attendRight','attendLeft','attendRight','attendLeft','attendRight','attendLeft','attendRight','attendLeft']
attention_side_misophonia= attention_side + ['attendRight','attendLeft'] 

if paradigm == 'AttenAud':
    stimuli_count_reference = pandas.MultiIndex.from_arrays([stimuli_type,stimulus_side,attention_side], names=('stimuli_type', 'stimulus_side','attention_side'))
elif paradigm == 'Misophonia':
    stimuli_count_reference = pandas.MultiIndex.from_arrays([stimuli_type_misophonia,stimulus_side_misophonia,attention_side_misophonia], names=('stimuli_type', 'stimulus_side','attention_side'))
    
response_count_reference = ['Correct Rejection','Hit','False Alarm','Incorrect Response','Missed Target']
