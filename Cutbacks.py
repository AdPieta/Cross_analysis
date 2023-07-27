# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 19:32:10 2023

@author: adamm
"""

import numpy as np
import pandas as pd
import os, json
from Opta_event_dict import optaEventTypes
from Opta_team_dict import opta_team_dict
from mplsoccer import VerticalPitch
import matplotlib as mpl
import matplotlib.pyplot as plt
from utils_ import *
from pitch_plots import *


# Path to data
path_to_json_autumn = 'Data/Jesien_2022/'
path_to_json_spring = 'Data/Wiosna_2023/'

#get all JSON file names as a list
json_file_autumn_names = [filename for filename in os.listdir(path_to_json_autumn) if filename.endswith('.json')]
json_file_spring_names = [filename for filename in os.listdir(path_to_json_spring) if filename.endswith('.json')]


# Load data 
events_autumn_df = import_jsons(path_to_json_autumn, json_file_autumn_names)
events_spring_df = import_jsons(path_to_json_spring, json_file_spring_names)

event_df = pd.concat([events_autumn_df, events_spring_df], axis = 0)


# Append event_types and team names
event_df = event_df.replace({'typeId':optaEventTypes})
event_df = event_df.replace({'contestantId':opta_team_dict})
event_df = event_df.replace({'opponentTeam':opta_team_dict})


### PRECLEAGNING
# Let's do some work with passes 
passes_df = event_df[event_df['typeId'] == 'Pass']

# Get list of qualifier
qualifier_list = passes_df['qualifier'].tolist()


# End X - qualifier 140
end_x_list = get_qualifier_values(140, qualifier_list)
    
# End Y - qualifier 141
end_y_list = get_qualifier_values(141, qualifier_list)
  
# Angle in radians - qualifier 213
angle_list = get_qualifier_values(213, qualifier_list)
  
   
    
# Change type to float
passes_df['end_x'], passes_df['end_y'], passes_df['angle'] = end_x_list, end_y_list, angle_list
passes_df['end_x'] = passes_df['end_x'].astype(float)
passes_df['end_y'] = passes_df['end_y'].astype(float)
passes_df['angle'] = passes_df['angle'].astype(float)



###### CROSSES #########
# Get crosses from passes dataframe
crosses_df = select_subtype(2, passes_df)
crosses_df = pd.DataFrame(crosses_df).reset_index(drop = True)

# Remove crosses from set pieces
for i, row in crosses_df.iterrows():
    for j in row['qualifier']:
        lista = ([j['qualifierId'] for d in row])
        if any((el == 5) | (el == 6) for el in lista):
            crosses_df.drop(i, inplace = True)

# Check, how many goals and shots occured after crosses
goals_after_crosses = crosses_df[crosses_df['assist'] == 1]
shots_after_crosses = crosses_df[crosses_df['keyPass'] == 1]

#######################
### TEAM COMPARISON ###
# Offensive
total_conversion_off = team_summary(crosses_df, side = 'offense')

# Defensive
total_conversion_def = team_summary(crosses_df, side = 'defense')

# ORIGIN OF A CROSS
# four zones: behind penalty area, start of penalty/middle, middle penalty/baseline, penalty area.

behind_zone_summary = cross_origin_analysis(crosses_df, zone = 'Zone 1')
further_zone_summary = cross_origin_analysis(crosses_df, zone = 'Zone 2')
baseline_zone_summary = cross_origin_analysis(crosses_df, zone = 'Zone 3')
inside_zone_summary = cross_origin_analysis(crosses_df, zone = 'Zone 4')

# Total summary by origin
origin_summary = pd.concat([behind_zone_summary, further_zone_summary, baseline_zone_summary, inside_zone_summary]).reset_index(drop = True)
origin_summary = origin_summary.sort_values('typeId', ascending = False).reset_index(drop = True)

# DESTINATION OF A CROSS
# It is easier to analyse end location having all crosses from the same side
# Therefor I reverse y and end_y coordinates though the middle of the pitch axis
end_zones_df = crosses_df.copy()

y_reversed = []
end_y_reversed = []
for i, row in end_zones_df.iterrows():
    if row['y'] > 50:
        y_rev = 100-row['y']
        end_y_rev = 100-row['end_y']
    else:
        y_rev = row['y']
        end_y_rev = row['end_y']
    y_reversed.append(y_rev)
    end_y_reversed.append(end_y_rev)

end_zones_df['y'] = y_reversed
end_zones_df['end_y'] = end_y_reversed



# I want to get rid of waay too long crosses
end_zones_df = end_zones_df[end_zones_df['end_y'].between(21.1, 78.9)]
    
# And of the blocked ones as well

for i, row in end_zones_df.iterrows():
    for j in row['qualifier']:
        lista = ([j['qualifierId'] for d in row])
        if any(el == 236 for el in lista):
            end_zones_df.drop(i, inplace = True)
end_zones_df = end_zones_df.reset_index(drop = True)



# Create dataframes based on cross origin
short_goal_cross = end_zones_df[end_zones_df['end_y'].between(30, 45.2, inclusive = 'left')]
short_goal_cross['Destination'] = 'Short'

inside_goal_cross = end_zones_df[end_zones_df['end_y'].between(45.2, 54.8, inclusive = 'both')]
inside_goal_cross['Destination'] = 'Goal Width'

wide_goal_cross = end_zones_df[end_zones_df['end_y'].between(54.8, 60, inclusive = 'right')] 
wide_goal_cross['Destination'] = 'Wide'


########## ANALIZA SKUTECZNOŚCI #########
# Shot goal
short_goal_summary = destination_summary(short_goal_cross, zone = 'Short')
inside_goal_summary = destination_summary(inside_goal_cross, zone = 'Goal width')
wide_goal_summary = destination_summary(wide_goal_cross, zone = 'Wide')


# OGÓLNIE
destination_summary = pd.concat([short_goal_summary, inside_goal_summary, wide_goal_summary]).reset_index(drop = True)


# START + END SUMMARY
# Without zone 4 - penalty area, too little crosses to be statistically significant
destination_cross = pd.concat([short_goal_cross, inside_goal_cross, wide_goal_cross]).reset_index(drop = True)

zone_1_cross = destination_cross[destination_cross['x'] < 83].reset_index(drop = True)
zone_1_cross['typeId'] = 'Zone 1 Cross'

zone_2_cross = destination_cross[(destination_cross['x'].between(83, 91.5, inclusive = 'left')) & ((destination_cross['y'].between(0, 21.1)) | (destination_cross['y'].between(78.8, 100)))].reset_index(drop = True)
zone_2_cross['typeId'] = 'Zone 2 Cross'

zone_3_cross = destination_cross[(destination_cross['x'] >= 91.5) & ((destination_cross['y'].between(0, 21.1)) | (destination_cross['y'].between(78.8, 100)))].reset_index(drop = True)
zone_3_cross['typeId'] = 'Zone 3 Cross'

origin_dest = pd.concat([zone_1_cross, zone_2_cross, zone_3_cross]).reset_index(drop = True)
# That is support to help me do stuff
origin_dest['crosses'] = 1

origin_dest_summary = origin_dest[['typeId', 'Destination', 'keyPass', 'assist', 'crosses']].groupby(['typeId', 'Destination']).sum().reset_index()


origin_dest_summary['Conversion_to_shot'] = origin_dest_summary['keyPass']/origin_dest_summary['crosses']
origin_dest_summary['Conversion_to_goal'] = origin_dest_summary['assist']/origin_dest_summary['crosses']
origin_dest_summary = origin_dest_summary.sort_values('crosses', ascending = True).reset_index(drop = True)

# Plotting
# Origin zones
origin_zones_plot = plot_origin_zones()

# Destination zones
destination_zones_plot = plot_destination_zones()

# Plot crosses for teams - initial
team_list = crosses_df.contestantId.unique().tolist()

team_crosses_plot = plot_crosses(crosses_df, team_list)
opponents_plot = plot_crosses(crosses_df, team_list, opponent = True)

######### CUTBACKS TO CLEAR ##########
# Cutback zone probably including areas outside the box - need to find the way to exclude high crosses
df_cutback_zone = passes_df[(passes_df['x'] > 83) & (passes_df['y'].between(0, 36.8) | passes_df['y'].between(63.2, 100))].reset_index(drop = True)

# The end of the pass should be behind the start of the pass
cutbacks_df = df_cutback_zone[df_cutback_zone['x'] > df_cutback_zone['end_x']]

# Filtering cutbacks step by step
# Angle criterion
cutbacks_df = cutbacks_df[~cutbacks_df.angle.between(2.5, 3.65)]
# End height criterion
cutbacks_df = cutbacks_df[cutbacks_df['end_x'] > 78]
# End width criterion
cutbacks_df = cutbacks_df[cutbacks_df['end_y'].between(36.8, 63.2)]


# Angle for the correct side
for i, row in cutbacks_df.iterrows():
    if (row['y'] < 50) & (row['angle'] > 3.14):
        cutbacks_df.drop(i, inplace = True)
    elif (row['y'] > 50) & (row['angle'] < 3.14):
        cutbacks_df.drop(i, inplace = True)

cutbacks_df = cutbacks_df.reset_index(drop = True)

# NO CROSSES
for i, row in cutbacks_df.iterrows():
    for j in row['qualifier']:
        lista = ([j['qualifierId'] for d in row])
        if any(el == 2 for el in lista):
            cutbacks_df.drop(i, inplace = True)
cutbacks_df = cutbacks_df.reset_index(drop = True)
            
# NO CHIPPED PASSES
for i, row in cutbacks_df.iterrows():
    for j in row['qualifier']:
        lista = ([j['qualifierId'] for d in row])
        if any(el == 155 for el in lista):
            cutbacks_df.drop(i, inplace = True)
cutbacks_df = cutbacks_df.reset_index(drop = True)

# No crosses, chipped passes or set pieces
for i, row in cutbacks_df.iterrows():
    for j in row['qualifier']:
        lista = ([j['qualifierId'] for d in row])
        if any((el == 5) | (el == 6) | (el == 107) for el in lista):
            cutbacks_df.drop(i, inplace = True)
cutbacks_df = cutbacks_df.reset_index(drop = True)

# Leave only assists and key passes
cutbacks_df = cutbacks_df[(cutbacks_df['keyPass'] == 1) | (cutbacks_df['assist'] == 1)]
cutbacks_df = cutbacks_df[cutbacks_df['outcome'] == 1]


test_to_plot = cutbacks_df[cutbacks_df['y'].between(21.1, 78.9)]
