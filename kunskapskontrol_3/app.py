# den python filen innehåller all kod som behövs för att köra streamlit appen app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3 as sql
import seaborn as sns
from scipy import stats
# skapa connection till min Sqlite databas. För att se hur jag har laddad ner datan och lagrad den i databasen se Kunskapskontrol_3_into_sql.ipynb
connection = sql.connect(r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\kunskapskontrol_3\football_stats.db')
# skapar 2 dataframes som har med de 2 olika områden som jag vill kolla på att göra, skot och passningar

shots = pd.read_sql("""SELECT id, period, timestamp, minute, second, location_x, location_y, player, possession_team, shot_outcome, shot_statsbomb_xg
                      FROM WomensWorldCup2023 WHERE type IS 'Shot'
                      ORDER BY period, timestamp;""", connection)
shots['distance_from_goal'] = np.sqrt(((shots.location_y-40)**2) + ((shots.location_x-120)**2)) # räknar distans från mitten av målet (ligger i koordinat x124, y40), c^2 = a^2+b^2

passes = pd.read_sql("""SELECT id, period, timestamp, minute, second, location_x, location_y, player, possession_team, 
                    pass_type, pass_length, pass_angle, pass_outcome
                    FROM WomensWorldCup2023 WHERE type IS 'Pass'
                    ORDER BY period, timestamp;""", connection)
passes['distance_from_goal'] = np.sqrt(((passes.location_y-40)**2) + ((passes.location_x-120)**2))

passes.pass_outcome.fillna('Complete', inplace=True)
passes.pass_type.fillna('Pass', inplace=True)
passes['pass_length'] = passes.pass_length.apply(lambda x: x*0.9144) # omvändlar från yard til meter 

st.title('FIFA Womens World Cup 2023 statistics')
tab1, tab2 = st.tabs(['Shots', 'Passes'])
# Skapar 2 tabs på streamlit sidan där vi ser skot på tab1 och passningar på tab2
with tab1:
    st.header('Shots')
    col1, col2, col3 = st.columns(3)
    fig, ax = plt.subplots(figsize=(8,4))
    ax = plt.scatter(shots['location_x'], shots['location_y'], c=shots['shot_statsbomb_xg'], alpha=0.6, cmap='Blues')
    fig.colorbar(ax, shrink=0.75)
    ax = plt.gca()
    ax.set_ylim([80, 0])
    ax.set_xlim([0, 120])
    ax.set_title('xG location')
    #följande kod ritar inn linjer på graffen så den kommer se ut som fotbollsplan
    ax.axhline(y=18, xmax=0.15, linestyle='--', linewidth=0.5, c='black')
    ax.axhline(y=62, xmax=0.15, linestyle='--', linewidth=0.5, c='black')
    ax.axhline(y=36, xmax=0.007, linewidth=0.5, c='red')
    ax.axhline(y=44, xmax=0.007, linewidth=0.5, c='red')
    ax.axvline(x=0.1, ymax=(36/80), ymin=(44/80), linewidth=2, c='red')
    ax.axvline(x=119.7, ymax=(36/80), ymin=(44/80), linewidth=2, c='red')
    ax.axhline(y=36, xmin=0.993, xmax=1, linewidth=0.5, c='red')
    ax.axhline(y=44, xmin=0.993, xmax=1, linewidth=0.5, c='red')
    ax.axhline(y=18, xmin=0.85, xmax=1, linestyle='--', linewidth=0.5, c='black')
    ax.axhline(y=62, xmin=0.85, xmax=1, linestyle='--', linewidth=0.5, c='black')
    ax.axvline(x=60, linestyle='--', linewidth=0.5, c='black')
    ax.axvline(x=18, ymax=0.225, ymin=0.775, linestyle='--', linewidth=0.5, c='black')
    ax.axvline(x=102, ymax=0.225, ymin=0.775, linestyle='--', linewidth=0.5, c='black')
    col1.write(fig)
    
    fig, ax = plt.subplots()
    ax = sns.scatterplot(x=shots['distance_from_goal'], y=shots['shot_statsbomb_xg'], hue=shots['shot_outcome'],alpha=0.7)
    ax.set_ylabel('xG')
    ax.set_xlabel('Distance from goal')
    ax.set_title('xG, closeness to goal and shot outcomes')
    ax.invert_xaxis()
    corr = stats.pearsonr(shots['distance_from_goal'], shots['shot_statsbomb_xg'])
    col2.write(fig)
    
    fig, ax = plt.subplots()
    ax = sns.scatterplot(shots, x='minute', y='shot_statsbomb_xg', c='Pink', alpha=0.85)
    ax = plt.gca()
    ax.set_ylim([0,1])
    ax.set_xlim([0, 140])
    ax.set_ylabel('xG')
    ax.set_xlabel('Minute')
    ax.set_title('xG and minute of play')
    col3.write(fig)
    
    st.write('Corrolation between distance from goal and xG', stats.pearsonr(shots['distance_from_goal'], shots['shot_statsbomb_xg']))
    st.write('Corrolation between minute of play and xG', stats.pearsonr(shots.minute, shots.shot_statsbomb_xg))
    #Här försöker jag räkna om det kan finnas samband mellan två grupper av statistik, vi får ut pearson talan för båda grupporna 
    nations = st.selectbox('Nations', shots['possession_team'].unique(), None, key=1) 
    # skapa en selectbox i streamlit där man kan välja vilken land man vill kolla på
    # dessa graffer är i stort sätt samma och de övergripliga graffen överst på sidan fast bara filtrerad med det land som man väljer
    st.subheader('xG and shot location')
    data = shots[(shots.possession_team == nations)]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax = plt.scatter(data['location_x'], data['location_y'], c=data['shot_statsbomb_xg'], vmin=0, vmax=1, alpha=0.7, cmap='Reds')
    fig.colorbar(ax, shrink=0.75)
    ax = plt.gca()
    ax.set_ylim([80, 0]) 
    ax.set_xlim([0, 120])
    ax.axhline(y=18, xmax=0.15, linestyle='--', linewidth=0.5, c='black')
    ax.axhline(y=62, xmax=0.15, linestyle='--', linewidth=0.5, c='black')
    ax.axhline(y=36, xmax=0.007, linewidth=0.5, c='red')
    ax.axhline(y=44, xmax=0.007, linewidth=0.5, c='red')
    ax.axvline(x=0.1, ymax=(36/80), ymin=(44/80), linewidth=2, c='red')
    ax.axvline(x=119.7, ymax=(36/80), ymin=(44/80), linewidth=2, c='red')
    ax.axhline(y=36, xmin=0.993, xmax=1, linewidth=0.5, c='red')
    ax.axhline(y=44, xmin=0.993, xmax=1, linewidth=0.5, c='red')
    ax.axhline(y=18, xmin=0.85, xmax=1, linestyle='--', linewidth=0.5, c='black')
    ax.axhline(y=62, xmin=0.85, xmax=1, linestyle='--', linewidth=0.5, c='black')
    ax.axvline(x=60, linestyle='--', linewidth=0.5, c='black')
    ax.axvline(x=18, ymax=0.225, ymin=0.775, linestyle='--', linewidth=0.5, c='black')
    ax.axvline(x=102, ymax=0.225, ymin=0.775, linestyle='--', linewidth=0.5, c='black')
    fig

    fig, ax = plt.subplots(1)
    ax = sns.scatterplot(x=data['distance_from_goal'], y=data['shot_statsbomb_xg'], hue=data['shot_outcome'],alpha=0.7)
    ax.set_ylabel('xG')
    ax.set_xlabel('Distance from goal')
    ax.invert_xaxis()
    fig
    st.subheader('xG and minute of play')
    fig, ax = plt.subplots()
    ax = sns.scatterplot(data, x='minute', y='shot_statsbomb_xg', c='Pink', alpha=0.85)
    ax = plt.gca()
    ax.set_ylim([0,1])
    ax.set_xlim([0, 140])
    ax.set_ylabel('xG')
    ax.set_xlabel('Minute')
    fig
# här börjar tab2 där vi kollar passningar
with tab2:
    st.header('Passes')
    col1, col2, col3, col4 = st.columns(4)
    # 4 övergripliga graffer som visar statistiken för hela turneringen
    fig, ax = plt.subplots()
    ax = sns.histplot(data=passes, y='pass_length', x='distance_from_goal')
    ax.set_xlabel('Distance from goal')
    ax.set_ylabel('Pass Length')
    ax.invert_xaxis()
    col1.write(fig)
    
    fig, ax = plt.subplots(figsize=(8,5))
    ax = sns.histplot(data=passes, x='distance_from_goal', hue='pass_type', multiple='stack')
    ax.set_xlabel('Distance from goal')
    ax.invert_xaxis()
    col2.write(fig)
    
    fig, ax = plt.subplots()
    ax = sns.histplot(data=passes, x='pass_length', hue='pass_type', stat='count', palette='Set2', multiple='stack')
    ax.set_xlabel('Pass Length (m)')
    col3.write(fig)
    
    fig, (ax1, ax2) = plt.subplots(2, figsize=(7, 9))
    ax1 = sns.boxplot(passes, y='pass_length', x='pass_type', hue='pass_type', legend=False, palette='pastel', ax=ax1)
    ax2 = sns.boxplot(passes, y='pass_length', x='pass_outcome', hue='pass_outcome', legend=False, ax=ax2)
    ax1.set_title('Pass Type')
    ax2.set_title('Pass Outcome')
    ax1.tick_params(direction='inout', axis='x', labelsize='small')
    ax1.set_xlabel('')
    ax2.set_xlabel('')
    ax1.set_ylabel('')
    ax2.set_ylabel('')
    ax2.tick_params(axis='x', direction='inout', labelsize='small')
    fig.supylabel('Pass Length (m)')
    col4.write(fig)

    st.write('Corrolation between pass length and distance from goal', stats.pearsonr(passes['distance_from_goal'], passes['pass_length']))
    
    nations1 = st.selectbox('Nations', passes['possession_team'].unique(), None, key=2)
    data = passes[(passes.possession_team == nations1)]
    st.subheader('Pass length and distance from goal')
    fig, ax = plt.subplots()
    ax = sns.histplot(data=data, y='pass_length', x='distance_from_goal')
    ax.set_xlabel('Distance from goal')
    ax.set_ylabel('Pass Length')
    ax.invert_xaxis()
    fig
    st.subheader('Pass types and distance from goal')
    fig, ax = plt.subplots(figsize=(8,5))
    ax = sns.histplot(data=data, x='distance_from_goal', hue='pass_type', multiple='stack')
    ax.set_xlabel('Distance from goal')
    ax.invert_xaxis()
    fig
    st.subheader('Pass length and pass types')
    fig, ax = plt.subplots()
    ax = sns.histplot(data=data, x='pass_length', hue='pass_type', stat='count', palette='Set2', multiple='stack')
    ax.set_xlabel('Pass Length (m)')
    fig
    st.subheader('Pass length, pass types and pass outcomes')
    fig, (ax1, ax2) = plt.subplots(2, figsize=(7, 9))
    ax1 = sns.boxplot(data, y='pass_length', x='pass_type', hue='pass_type', legend=False, palette='pastel', ax=ax1)
    ax2 = sns.boxplot(data, y='pass_length', x='pass_outcome', hue='pass_outcome', legend=False, ax=ax2)
    ax1.set_title('Pass Type')
    ax2.set_title('Pass Outcome')
    ax1.tick_params(direction='inout', axis='x', labelsize='small')
    ax1.set_xlabel('')
    ax2.set_xlabel('')
    ax1.set_ylabel('')
    ax2.set_ylabel('')
    ax2.tick_params(axis='x', direction='inout', labelsize='small')
    fig.supylabel('Pass Length (m)')
    fig
    

