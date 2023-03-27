import pandas as pd
import numpy as np
import random

ratings = pd.read_csv('master.csv')
while True:
    team1 = input("Team 1: ")
    if team1 in ratings['School'].values:
        break
    else:
        print("Invalid team. Please try again.")

t1_stats = ratings.loc[ratings['School'] == team1]
AdjO1 = t1_stats['AdjO'].values[0]
SDO1 = t1_stats['SDO'].values[0]
AdjD1 = t1_stats['AdjD'].values[0]
SDD1 = t1_stats['SDD'].values[0]
AdjT1 = t1_stats['AdjT'].values[0]
SDP1 = t1_stats['SDP'].values[0]
print(f"Offense: {'{:.2f}'.format(AdjO1)}, {'{:.2f}'.format(SDO1)}")
print(f"Defense: {'{:.2f}'.format(AdjD1)}, {'{:.2f}'.format(SDD1)}")
print(f"Tempo: {'{:.2f}'.format(AdjT1)}, {'{:.2f}'.format(SDP1)}")

while True:
    team2 = input("Team 2: ")
    if team2 in ratings['School'].values:
        break
    else:
        print("Invalid team. Please try again.")

t2_stats = ratings.loc[ratings['School'] == team2]
AdjO2 = t2_stats['AdjO'].values[0]
SDO2 = t2_stats['SDO'].values[0]
AdjD2 = t2_stats['AdjD'].values[0]
SDD2 = t2_stats['SDD'].values[0]
AdjT2 = t2_stats['AdjT'].values[0]
SDP2 = t2_stats['SDP'].values[0]
print(f"Offense: {'{:.2f}'.format(AdjO2)}, {'{:.2f}'.format(SDO2)}")
print(f"Defense: {'{:.2f}'.format(AdjD2)}, {'{:.2f}'.format(SDD2)}")
print(f"Tempo: {'{:.2f}'.format(AdjT2)}, {'{:.2f}'.format(SDP2)}")


games = 0
t1_wins = 0
t2_wins = 0
t1_scores = []
t2_scores = []
while games != 1000000:
    w = random.uniform(0,1)
    tempo1 = np.random.normal(AdjT1,SDP1)
    tempo2 = np.random.normal(AdjT2,SDP2)
    t1_off = np.random.normal(AdjO1, SDO1) * tempo1 / 100
    t2_def = np.random.normal(AdjD2, SDD2) * tempo2 / 100
    t1_score = w * t1_off + (1 - w) * t2_def
    t2_off = np.random.normal(AdjO2, SDO2) * tempo2 / 100
    t1_def = np.random.normal(AdjD1, SDD1) * tempo1 / 100
    t2_score = (1 - w) * t2_off + w * t1_def
    t1_scores.append(t1_score)
    t2_scores.append(t2_score)
    if t1_score > t2_score:
        t1_wins += 1
    else:
        t2_wins += 1
    games += 1

t1_final = '{:.2f}'.format(sum(t1_scores) / 1000000)
t2_final = '{:.2f}'.format(sum(t2_scores) / 1000000)
print(f"{team1} Win Probability: {'{:.2f}'.format(t1_wins/10000)}%")
print(f"{team2} Win Probability: {'{:.2f}'.format(t2_wins/10000)}%")
print(f'{team1} {t1_final} - {t2_final} {team2}')