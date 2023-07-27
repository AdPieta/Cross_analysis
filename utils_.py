# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 21:47:54 2023

Okay, here are utils to cross project.

@author: adamm
"""
import numpy as np
import pandas as pd
import json
import os


def import_jsons(path_to_json, json_file_names):
    # List, where I can store games
    games_df_list = []
    # Loading a game
    for file_name in json_file_names:
        with open(os.path.join(path_to_json, file_name)) as json_file:
            json_text = json.load(json_file)
            data_dict = json.loads(json_text)
            single_game = pd.DataFrame(data_dict['liveData']['event'])
            # This one adds a column with opponent
            game_team_list = single_game['contestantId'].unique().tolist()
            opponent_list = []
            for i, row in single_game.iterrows():
                if row['contestantId'] == game_team_list[0]:
                    opponent_list.append(game_team_list[1])
                elif row['contestantId'] == game_team_list[1]:
                    opponent_list.append(game_team_list[0])        
            single_game['opponentTeam'] = opponent_list

            games_df_list.append(single_game)

    events_df = pd.concat(games_df_list)
    return events_df

def get_qualifier_values(subtype_id, qualifier_list):
    value_list = []
    for i in qualifier_list:
        my_item = next((item for item in i if item['qualifierId'] == subtype_id), None)
        value = my_item['value']
        value_list.append(value)
    return value_list


def select_subtype(subtype_id, df_to_search):
    list_to_df = []
    for i, row in df_to_search.iterrows():
        for j in row['qualifier']:
            lista = ([j['qualifierId'] for d in row])
            if any(el == subtype_id for el in lista):
                list_to_df.append(row)  
    list_to_df = pd.DataFrame(list_to_df).reset_index(drop = True)
    return list_to_df

def team_summary(df, side = 'offense'):
    if side == 'offense':
        team_crosses = df[['eventId', 'contestantId', 'keyPass', 'assist']].groupby('contestantId').count().sort_values('eventId').reset_index()
        team_crosses = team_crosses.rename(columns = {'contestantId':'team'})
    elif side == 'defense':
        team_crosses = df[['eventId', 'opponentTeam', 'keyPass', 'assist']].groupby('opponentTeam').count().sort_values('eventId').reset_index()
        team_crosses = team_crosses.rename(columns = {'opponentTeam':'team'})
        
    team_crosses = team_crosses.rename(columns = {'eventId':'crosses'})

    team_crosses['Conversion_to_shot'] = team_crosses['keyPass']/team_crosses['crosses']
    team_crosses['Conversion_to_goal'] = team_crosses['assist']/team_crosses['crosses']
    team_crosses['Crosses_per_game'] = team_crosses['crosses']/34

    # Table for shot conversion
    shot_conversion = team_crosses[['team', 'Crosses_per_game', 'Conversion_to_shot']].sort_values('Conversion_to_shot', ascending = True).reset_index(drop = True)

    # Table for goal conversion
    goal_conversion = team_crosses[['team', 'Crosses_per_game', 'Conversion_to_goal']].sort_values('Conversion_to_goal', ascending = True).reset_index(drop = True)

    # Joining tabbles
    total_conversion = shot_conversion.merge(goal_conversion[['team', 'Conversion_to_goal']], how = 'left', on = 'team').sort_values('Crosses_per_game', ascending = True).reset_index(drop = True)
    return total_conversion

def cross_origin_analysis(cross_df, zone):
    """

    Parameters
    ----------
    cross_df : Dataframe with all crosses
    zone : Describe the zone (Zone 1, Zone 2, Zone 3, Zone 4) depending on the origin of a cross
    Zone 1 - deep cross, Zone 2 - between start of penalty area and half of it
    Zone 3 - between the height of half of the penalty are and baseline
    Zone 4 - inside penalty area

    Returns
    -------
    File with analysis

    """
    if zone == 'Zone 1':
        origin_df = cross_df[cross_df['x'] < 83].reset_index(drop = True)
        origin_df['typeId'] = 'Zone 1 Cross'
    elif zone == 'Zone 2':
        origin_df = cross_df[(cross_df['x'].between(83, 91.5, inclusive = 'left')) & ((cross_df['y'].between(0, 21.1)) | (cross_df['y'].between(78.8, 100)))].reset_index(drop = True)
        origin_df['typeId'] = 'Zone 2 Cross'
    elif zone == 'Zone 3':
        origin_df = cross_df[(cross_df['x'] >= 91.5) & ((cross_df['y'].between(0, 21.1)) | (cross_df['y'].between(78.8, 100)))].reset_index(drop = True)
        origin_df['typeId'] = 'Zone 3 Cross'
    elif zone == 'Zone 4':
        origin_df = cross_df[(cross_df['x'] >= 83) & ((cross_df['y'].between(21.1, 36.8, inclusive = 'right')) | (cross_df['y'].between(63.2, 78.8, inclusive = 'left')))].reset_index(drop = True)
        origin_df['typeId'] = 'Zone 4 Cross'    
        
    # Origin blocked:
    origin_blocked_df = select_subtype(236, origin_df)
    # Inswingers and Outswingers
    origin_inswingers_df = select_subtype(223, origin_df)
    origin_outswingers_df = select_subtype(224, origin_df)


    # Overall summary for the origin of the cross
    origin_summary = conversion_summary(origin_df, origin_blocked_df, origin_inswingers_df, origin_outswingers_df)
    origin_summary['crosses_per_game'] = len(origin_df)/306

    return origin_summary

def destination_summary(cross_df, zone):
    destination_summary = cross_df[['keyPass', 'assist', 'typeId']].groupby(['typeId']).sum().reset_index()
    destination_summary = destination_summary.rename(columns = {'typeId':'crosses'})

    destination_summary['Conversion_to_shot'] = destination_summary['keyPass']/len(cross_df)
    destination_summary['Conversion_to_goal'] = destination_summary['assist']/len(cross_df)
    destination_summary['Crosses_per_game'] = len(cross_df)/306
    destination_summary['Destination'] = zone
    return destination_summary

def conversion_summary(cross_df, blocked_df, inswingers_df, outswingers_df):
    origin_summary = cross_df[['typeId', 'keyPass', 'assist']].groupby('typeId').sum().reset_index()    
    origin_summary['shot_conversion'] = origin_summary['keyPass']/len(cross_df)
    origin_summary['goal_conversion'] = origin_summary['assist']/len(cross_df)
    origin_summary['blocked_%'] = len(blocked_df)/len(cross_df)
    origin_summary['inswingers_%'] = len(inswingers_df)/len(cross_df)
    origin_summary['outswingers_%'] = len(outswingers_df)/len(cross_df)   
    return origin_summary



