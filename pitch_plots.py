# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 18:57:29 2023

@author: adamm
"""

import numpy as np
import pandas as pd
import matplotlib
from mplsoccer import Pitch, VerticalPitch
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from highlight_text import ax_text, fig_text
from PIL import Image

def plot_origin_zones(): 
    pitch = Pitch(pitch_type = 'opta', half = True, pitch_color = 'white', line_color = 'black')
    fig, ax = pitch.draw(figsize=(10,20), constrained_layout = True, tight_layout = False)
    fig.set_facecolor('white')
    
    # Zone 1
    ax.add_patch(Rectangle((60, 0), 23, 29,
                           edgecolor = 'blue',
                           facecolor = 'blue',
                           alpha = 0.6))
    ax.text(72, 13, 'Zone 1', weight='bold', ha='center', family = 'monospace', fontsize = 24)
    
    
    # Zone 2
    ax.add_patch(Rectangle((83, 0), 8.5, 21.1,
                           edgecolor = 'blue',
                           facecolor = 'blue',
                           alpha = 0.45))
    ax.text(87.25, 10.55, 'Zone 2', weight='bold', ha='center', family = 'monospace', fontsize = 18)
    
    
    # Zone 3
    ax.add_patch(Rectangle((91.5, 0), 8.5, 21.1,
                           edgecolor = 'blue',
                           facecolor = 'blue',
                           alpha = 0.3))
    ax.text(95.75, 10.55, 'Zone 3', weight='bold', ha='center', family = 'monospace', fontsize = 18)
    
    
    # Zone 4
    ax.add_patch(Rectangle((83, 21.1), 17, 15.7,
                           edgecolor = 'blue',
                           facecolor = 'blue',
                           alpha = 0.15))
    ax.text(92, 28, 'Zone 4', weight='bold', ha='center', family = 'monospace', fontsize = 18)
    fig.savefig("Plots/origin_zones.png", dpi=None, bbox_inches="tight")  
    plt.show()
    

def plot_destination_zones(): 
    pitch = Pitch(pitch_type = 'opta', half = True, pitch_color = 'white', line_color = 'gray')
    fig, ax = pitch.draw(figsize=(10,20), constrained_layout = True, tight_layout = False)
    fig.set_facecolor('white')
    
    # Zone 1
    ax.add_patch(Rectangle((83, 30), 17, 14.2,
                           edgecolor = 'blue',
                           facecolor = 'blue',
                           alpha = 0.6))
    ax.text(92, 37.1, 'Short post', weight='bold', ha='center', family = 'monospace', fontsize = 24)
    
    
    # Zone 2
    ax.add_patch(Rectangle((83, 44.2), 17, 11.6,
                           edgecolor = 'blue',
                           facecolor = 'blue',
                           alpha = 0.45))
    ax.text(91.5, 49.5, 'Inside goal width', weight='bold', ha='center', family = 'monospace', fontsize = 20)
    
    
    # Zone 3
    ax.add_patch(Rectangle((83, 55.8), 17, 14.2,
                           edgecolor = 'blue',
                           facecolor = 'blue',
                           alpha = 0.3))
    ax.text(92, 61.9, 'Wide post', weight='bold', ha='center', family = 'monospace', fontsize = 24)
    fig.text(0.65, 0.19, '@AdPieta | Data @Opta', alpha = 0.4, fontfamily = 'monospace', fontsize = 16)
    fig.savefig("Plots/destination_zones.png", dpi=None, bbox_inches="tight")  
    plt.show()




# Plot crosses for teams - initial

def plot_crosses(cross_df, team_list, opponent = False):
    
    # Set every plot
    pitch = VerticalPitch(pitch_type = 'opta', half = True, pitch_color = 'white', line_color = 'black')
    
    fig, axs = pitch.grid(nrows=3, ncols=6, figheight=20, bottom=0.025, space=0.1, endnote_height=0, title_height = 0.05)
    # Do the plotting
    for n, ax in enumerate(axs['pitch'].flat):
        team = team_list[n]
        if opponent == False:
            crosses_team = cross_df[cross_df['opponentTeam'] == team].reset_index(drop = True)
        else:
            crosses_team = cross_df[cross_df['contestantId'] == team].reset_index(drop = True)
        pitch.arrows(crosses_team.x, crosses_team.y, crosses_team.end_x, crosses_team.end_y,
                     color='blue', ax=ax, zorder=1, headwidth  = 2, headlength  = 2, headaxislength = 2, alpha = 0.03)
       
        ax.scatter(crosses_team['y'], crosses_team['x'], marker='o', fc=ax.get_facecolor(), ec='black', zorder=2,
                   s = 40, alpha = 0.05)
        
        # Goals should be more clear and visible
        team_crosses_goal = crosses_team[crosses_team['assist'] == 1]
    
        pitch.arrows(team_crosses_goal.x, team_crosses_goal.y, team_crosses_goal.end_x, team_crosses_goal.end_y,
                     color='blue', ax=ax, width = 3, zorder=3, headwidth  = 5, headlength  = 5, headaxislength = 5, alpha = 0.9)
       
        ax.scatter(team_crosses_goal['y'], team_crosses_goal['x'], marker='o', fc=ax.get_facecolor(), ec='black', zorder=4,
                   s = 220)
        
        ax_text(50, 106, team, ha='center', va='center', fontsize = 25, color = 'black', family = 'monospace', ax = ax)
        axx = ax.inset_axes([.83, .97, .10, .20],)
        axx.axis('off')
        image = Image.open('Logos/'+ team + '.png')
        axx.imshow(image)
    axs['title'].remove()   
    
    if opponent == False:
        fig_text(
            x = 0.5, y = .85, 
            s = "Ekstraklasa Teams' crosses",
            va = "center", ha = "center",
            fontsize = 40, color = "black", family = 'monospace', weight = 'bold'
            )   
    else:
        fig_text(
            x = 0.5, y = .85, 
            s = "Ekstraklasa Teams' crosses against",
            va = "center", ha = "center",
            fontsize = 40, color = "black", family = 'monospace', weight = 'bold'
            )   
    fig_text(
    	x = 0.5, y = .79, 
        s = "Crosses in 2022/2023 season <bold ones - assists>",
        highlight_textprops=[{"weight": "bold", "color": "blue"}],
    	va = "bottom", ha = "center",
    	fontsize = 28, family = 'monospace'
    )
    
    fig.text(0.75, 0.001, '@AdPieta | Data @Opta | Inspiration: @sonofacorner', alpha = 0.4, fontfamily = 'monospace', fontsize = 20)
    if opponent == False:
        fig.savefig("Plots/Crosses_teams.png", dpi=None, bbox_inches="tight")
    else:
        fig.savefig("Plots/Crosses_against_teams.png", dpi=None, bbox_inches="tight")
    plt.show()
    

# Plot cutbacks

def plot_cutbacks(df, team_list, opponent = False):
    pitch = VerticalPitch(pitch_type = 'opta', half = True, pitch_color = 'white', line_color = 'black')
    
    fig, axs = pitch.grid(nrows=3, ncols=6, figheight=20, bottom=0.025, space=0.1, endnote_height=0, title_height = 0.05)
    # Do the plotting
    for n, ax in enumerate(axs['pitch'].flat):
        team = team_list[n]
        if opponent == False:
            cutbacks_team = cutbacks_df[cutbacks_df['contestantId'] == team].reset_index(drop = True)
        else:
            cutbacks_team = cutbacks_df[cutbacks_df['opponentTeam'] == team].reset_index(drop = True)
        #team_crosses_key = crosses_team[crosses_team['keyPass'] == 1]
    
        ax.scatter(cutbacks_team['y'], cutbacks_team['x'], marker='o', fc=ax.get_facecolor(), ec='black', zorder=4,
                   s = 80)
        
        cutbacks_keypass = cutbacks_team[cutbacks_team['keyPass'] == 1]
        pitch.arrows(cutbacks_keypass.x, cutbacks_keypass.y, cutbacks_keypass.end_x, cutbacks_keypass.end_y,
                     color='blue', ax=ax, width = 3, zorder=2, headwidth  = 5, headlength  = 5, headaxislength = 5, alpha = 0.3)
       
        cutbacks_goals = cutbacks_team[cutbacks_team['assist'] == 1]
        pitch.arrows(cutbacks_goals.x, cutbacks_goals.y, cutbacks_goals.end_x, cutbacks_goals.end_y,
                     color='red', ax=ax, width = 3, zorder=3, headwidth  = 5, headlength  = 5, headaxislength = 5, alpha = 0.9)
       
        
        key_pass = cutbacks_team.keyPass.sum()
        assist = cutbacks_team.assist.sum()
        
        ax_text(25, 65, 'Key passes: ' + str(int(key_pass)), ha='center', va='center', fontsize = 15, color = 'black', family = 'monospace', ax = ax, zorder = 3)
        ax_text(80, 65, 'Assists: ' + str(int(assist)), ha='center', va='center', fontsize = 15, color = 'black', family = 'monospace', ax = ax, zorder = 3)
        ax_text(50, 106, team, ha='center', va='center', fontsize = 25, color = 'black', family = 'monospace', ax = ax)
        axx = ax.inset_axes([.83, .97, .10, .20],)
        axx.axis('off')
        image = Image.open('Logos/'+ team + '.png')
        axx.imshow(image)
    axs['title'].remove()   
    if opponent == False:
        fig_text(
            x = 0.5, y = .85, 
            s = "Ekstraklasa Teams' cutbacks in season 2022/2033",
            va = "center", ha = "center",
            fontsize = 40, color = "black", family = 'monospace', weight = 'bold'
        )   
    else:
        fig_text(
            x = 0.5, y = .85, 
            s = "Ekstraklasa Teams' cutbacks against in season 2022/2033",
            va = "center", ha = "center",
            fontsize = 40, color = "black", family = 'monospace', weight = 'bold'
        )   
    fig_text(
    	x = 0.42, y = .79, 
        s = "<blue - key passes>",
        highlight_textprops=[{"weight": "bold", "color": "blue"}],
    	va = "bottom", ha = "center",
    	fontsize = 28, family = 'monospace'
    )
    fig_text(
    	x = 0.58, y = .79, 
        s = "<red - assists>",
        highlight_textprops=[{"weight": "bold", "color": "red"}],
    	va = "bottom", ha = "center",
    	fontsize = 28, family = 'monospace'
    )
    
    fig.text(0.75, 0.001, '@AdPieta | Data @Opta | Inspiration: @sonofacorner', alpha = 0.4, fontfamily = 'monospace', fontsize = 20)
    if opponent == False:
        fig.savefig("Plots/Cutbacks_teams.png", dpi=None, bbox_inches="tight")
    else:
        fig.savefig("Plots/Cutbacks_against_teams.png", dpi=None, bbox_inches="tight")
    plt.show()
    




