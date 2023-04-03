import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import math

url = 'https://www.sports-reference.com/cbb/seasons/men/2023-school-stats.html'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

schools = []
sids = []
for tr in soup.find_all('tr')[1:]:
    try:
        school = tr.find('td').text.replace('\xa0NCAA','')
        schools.append(str(school))
        sid = tr.find_all('td')[0].find('a')
        sids.append(sid['href'])
    except:
        pass

stripSchools = [s.lower().strip() for s in schools]


broken = {'UC-Riverside': 'UC Riverside', 'USC Upstate':'South Carolina Upstate', 'UNLV': 'Nevada-Las Vegas', 'LSU':'Louisiana State', 'UConn':'Connecticut', 'UNC':'North Carolina', 'Ole Miss':'Mississippi', 'UT-Southern':'Texas Southern', 'USC':'Southern California', 'Pitt':'Pittsburgh', "St. Joseph's":"Saint Joseph's", 'UMass':'Massachusetts', 'LIU':'Long Island University', 'UMBC':'Maryland-Baltimore County', 'UMass-Lowell':'Massachusetts-Lowell', 'ETSU':'East Tennessee State', 'UCSB':'UC Santa Barbara', 'Southern Miss':'Southern Mississippi', 'VCU':'Virginia Commonwealth', 'SMU':'Southern Methodist', 'UC-Davis':'UC Davis', 'UT-Martin':'Tennessee-Martin', 'UIC':'Illinois-Chicago', 'SIU-Edwardsville': 'SIU Edwardsville', "Saint Mary's":"Saint Mary's (CA)",'Penn':'Pennsylvania', "St. Peter's":"Saint Peter's", 'BYU':'Brigham Young', 'UC-San Diego': 'UC San Diego', 'UC-Irvine': 'UC Irvine', 'UCF':'Central Florida'}
def get_school_data(school,sid):
    school_url = f'https://www.sports-reference.com{sid}'
    school_url = school_url.replace('.html','-gamelogs.html')

    page = requests.get(school_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    conf = soup.find_all('p')[2].find('a').text.replace(' MBB','')

    gamelog = pd.read_html(page.content, header=1)[0]
    gamelog = gamelog.dropna(subset=['Opp'])
    gamelog = gamelog.loc[gamelog['Opp'] != 'Opp'].reset_index(drop=True)

    games = []
    effOs = []
    effDs = []
    effPs = []
    for game in gamelog.iterrows():
        try:
            opp = str(game[1][3])
            try:
                if opp in broken:
                    opp = broken[opp]
            except:
                pass
            if opp in schools:
                if game[1][2] == '@':
                    loc = 'A'
                else:
                    if game[1][2] == 'N':
                        loc = 'N'
                    else:
                        loc = 'H'
                if game[1][4][0] == 'W':
                    outcome = 1
                else:
                    outcome = 0
                poss = float(game[1][8]) - float(game[1][16]) + float(game[1][21]) + 0.475 * float(game[1][14])
                gEffO = float(game[1][5]) * 100 / poss
                gEffD = float(game[1][6]) * 100 / poss

                if math.isnan(gEffO) == False:
                    advO = 1.875
                    advD = 1.875
                    try:
                        if loc == 'H':
                            gEffO = gEffO + advO
                            gEffD = gEffD - advD
                    except:
                        try:
                            if loc == 'A':
                                gEffO = gEffO - advO
                                gEffD = gEffD + advD
                        except:
                            pass
                    g = [opp, loc, outcome]
                    games.append(g)
                    effOs.append(gEffO)
                    effDs.append(gEffD)
                    effPs.append(poss)
        except:
            pass

    schedule = pd.DataFrame(games, columns=['Opp','Loc','W/L'])
    
    if len(effOs) >= 4:
        qtr1 = len(effOs) // 4
        qtr2 = qtr1 * 2
        qtr3 = qtr1 * 3
        oPt1 = effOs[:qtr1]
        oPt2 = effOs[qtr1:qtr2]
        oPt3 = effOs[qtr2:qtr3]
        oPt4 = effOs[qtr3:]
        dPt1 = effDs[:qtr1]
        dPt2 = effDs[qtr1:qtr2]
        dPt3 = effDs[qtr2:qtr3]
        dPt4 = effDs[qtr3:]
        pPt1 = effPs[:qtr1]
        pPt2 = effPs[qtr1:qtr2]
        pPt3 = effPs[qtr2:qtr3]
        pPt4 = effPs[qtr3:]
        effO = 0.26 * (sum(oPt4) / len(oPt4)) + 0.253 * (sum(oPt3) / len(oPt3)) + 0.247 * (sum(oPt2) / len(oPt2)) + 0.24 * (sum(oPt1) / len(oPt1))
        effD = 0.26 * (sum(dPt4) / len(dPt4)) + 0.253 * (sum(dPt3) / len(dPt3)) + 0.247 * (sum(dPt2) / len(dPt2)) + 0.24 * (sum(dPt1) / len(dPt1))
        effP = 0.26 * (sum(pPt4) / len(pPt4)) + 0.253 * (sum(pPt3) / len(pPt3)) + 0.247 * (sum(pPt2) / len(pPt2)) + 0.24 * (sum(pPt1) / len(pPt1))
    else:
        effO = sum(effOs) / len(effOs)
        effD = sum(effDs) / len(effDs)
        effP = sum(effPs) / len(effPs)
    sdOs = [(x - effO)**2 for x in effOs]
    sdO = math.sqrt(sum(sdOs) / len(sdOs))
    sdDs = [(x - effD) ** 2 for x in effOs]
    sdD = math.sqrt(sum(sdDs) / len(sdDs))
    sdPs = [(x - effD) ** 2 for x in effOs]
    sdP = math.sqrt(sum(sdPs) / len(sdPs))
    stats = [school,conf,effO,sdO,effD,sdD,effP,sdP]
    return schedule,stats


def get_opp_rating(schedule):
    oppOs = []
    oppDs = []
    oppPs = []
    for game in schedule.iterrows():
        opp = game[1][0]
        row = master.loc[master['School'] == opp]
        gOppO = float(row.iloc[0,2])
        gOppD = float(row.iloc[0,3])
        gOppP = float(row.iloc[0,4])
        oppOs.append(gOppO)
        oppDs.append(gOppD)
        oppPs.append(gOppP)

    oppO = sum(oppOs) / len(oppOs)
    oppD = sum(oppDs) / len(oppDs)
    oppP = sum(oppPs) / len(oppPs)

    return [oppO,oppD,oppP]


def win_quality(schedule):
    Q1W = 0
    Q1L = 0
    Q2W = 0
    Q2L = 0
    Q3W = 0
    Q3L = 0
    Q4W = 0
    Q4L = 0
    for game in schedule.iterrows():
        opp = game[1][0]
        loc = game[1][1]
        outcome = game[1][2]
        row = master.loc[master['School'] == opp]
        rank = int(row.iloc[0,19])
        try:
            if loc == 'H':
                if rank <= 30:
                    if outcome == 1:
                        Q1W += 1
                    else:
                        Q1L += 1
                else:
                    if rank <= 75:
                        if outcome == 1:
                            Q2W += 1
                        else:
                            Q2L += 1
                    else:
                        if rank <= 160:
                            if outcome == 1:
                                Q3W += 1
                            else:
                                Q3L += 1
                        else:
                            if outcome == 1:
                                Q4W += 1
                            else:
                                Q4L += 1
            if loc == 'N':
                if rank <= 50:
                    if outcome == 1:
                        Q1W += 1
                    else:
                        Q1L += 1
                else:
                    if rank <= 100:
                        if outcome == 1:
                            Q2W += 1
                        else:
                            Q2L += 1
                    else:
                        if rank <= 200:
                            if outcome == 1:
                                Q3W += 1
                            else:
                                Q3L += 1
                        else:
                            if outcome == 1:
                                Q4W += 1
                            else:
                                Q4L += 1
            if loc == 'A':
                if rank <= 75:
                    if outcome == 1:
                        Q1W += 1
                    else:
                        Q1L += 1
                else:
                    if rank <= 135:
                        if outcome == 1:
                            Q2W += 1
                        else:
                            Q2L += 1
                    else:
                        if rank <= 240:
                            if outcome == 1:
                                Q3W += 1
                            else:
                                Q3L += 1
                        else:
                            if outcome == 1:
                                Q4W += 1
                            else:
                                Q4L += 1
        except:
            pass
    adjQ = 0.03125*Q1W + 0.01875*Q1L + 0.025*Q2W + 0.0125*Q2L + 0.01875*Q3W + 0.00625*Q3L + 0.0125*Q4W + 0.0*Q4L
    return adjQ


def quad_wins(schedule):
    W = 0
    L = 0
    HW = 0
    HL = 0
    NW = 0
    NL = 0
    AW = 0
    AL = 0
    Q1W = 0
    Q1L = 0
    Q2W = 0
    Q2L = 0
    Q3W = 0
    Q3L = 0
    Q4W = 0
    Q4L = 0
    for game in schedule.iterrows():
        opp = game[1][0]
        loc = game[1][1]
        outcome = game[1][2]
        row = master.loc[master['School'] == opp]
        rank = int(row.iloc[0, 19])
        try:
            if loc == 'H':
                if rank <= 30:
                    if outcome == 1:
                        Q1W += 1
                        W += 1
                        HW += 1
                    else:
                        Q1L += 1
                        L += 1
                        HL += 1
                else:
                    if rank <= 75:
                        if outcome == 1:
                            Q2W += 1
                            W += 1
                            HW += 1
                        else:
                            Q2L += 1
                            L += 1
                            HL += 1
                    else:
                        if rank <= 160:
                            if outcome == 1:
                                Q3W += 1
                                W += 1
                                HW += 1
                            else:
                                Q3L += 1
                                L += 1
                                HL += 1
                        else:
                            if outcome == 1:
                                Q4W += 1
                                W += 1
                                HW += 1
                            else:
                                Q4L += 1
                                L += 1
                                HL += 1
            if loc == 'N':
                if rank <= 50:
                    if outcome == 1:
                        Q1W += 1
                        W += 1
                        NW += 1
                    else:
                        Q1L += 1
                        L += 1
                        NL += 1
                else:
                    if rank <= 100:
                        if outcome == 1:
                            Q2W += 1
                            W += 1
                            NW += 1
                        else:
                            Q2L += 1
                            L += 1
                            NL += 1
                    else:
                        if rank <= 200:
                            if outcome == 1:
                                Q3W += 1
                                W += 1
                                NW += 1
                            else:
                                Q3L += 1
                                L += 1
                                NL += 1
                        else:
                            if outcome == 1:
                                Q4W += 1
                                W += 1
                                NW += 1
                            else:
                                Q4L += 1
                                L += 1
                                NL += 1
            if loc == 'A':
                if rank <= 75:
                    if outcome == 1:
                        Q1W += 1
                        W += 1
                        AW += 1
                    else:
                        Q1L += 1
                        L += 1
                        AL += 1
                else:
                    if rank <= 135:
                        if outcome == 1:
                            Q2W += 1
                            W += 1
                            AW += 1
                        else:
                            Q2L += 1
                            L += 1
                            AL += 1
                    else:
                        if rank <= 240:
                            if outcome == 1:
                                Q3W += 1
                                W += 1
                                AW += 1
                            else:
                                Q3L += 1
                                L += 1
                                AL += 1
                        else:
                            if outcome == 1:
                                Q4W += 1
                                W += 1
                                AW += 1
                            else:
                                Q4L += 1
                                L += 1
                                AL += 1
        except:
            pass
    Rec = '[' + str(W) + '-' + str(L) + ']'
    HRec = '[' + str(HW) + '-' + str(HL) + ']'
    NRec = '[' + str(NW) + '-' + str(NL) + ']'
    ARec = '[' + str(AW) + '-' + str(AL) + ']'
    Q1 = '[' + str(Q1W) + '-' + str(Q1L) + ']'
    Q2 = '[' + str(Q2W) + '-' + str(Q2L) + ']'
    Q3 = '[' + str(Q3W) + '-' + str(Q3L) + ']'
    Q4 = '[' + str(Q4W) + '-' + str(Q4L) + ']'
    quad = [Rec,HRec,NRec,ARec,Q1,Q2,Q3,Q4]
    return quad

schedules = []
ratings = []
for school,sid in zip(schools,sids):
    schedule,stats = get_school_data(school,sid)

    schedules.append(schedule)
    ratings.append(stats)

    print(stats)
    time.sleep(3)

master = pd.DataFrame(ratings, columns=['School','Conf','EffO','SDO','EffD','SDD','EffP','SDP'])

oppRatings = []
for school,schedule in zip(schools,schedules):
    oppStats = get_opp_rating(schedule)
    oppRatings.append(oppStats)
    print(school)
    print(oppStats)

oppEff = pd.DataFrame(oppRatings, columns=['OppO','OppD','OppP'])
master = pd.concat([master,oppEff], axis=1)

master['OppO'] = master['OppO'] - master['OppO'].mean()
master['OppD'] = master['OppD'] - master['OppD'].mean()
master['OppP'] = master['OppP'] - master['OppP'].mean()
master['AdjO'] = master['EffO'] - master['OppD']
master['AdjD'] = master['EffD'] - master['OppO']
master['AdjT'] = master['EffP'] - master['OppP']

confAvgs = master.groupby('Conf')[['AdjO', 'AdjD']].mean()
confAvgs['ConfStrO'] = confAvgs['AdjO'] - confAvgs['AdjO'].mean()
confAvgs['ConfStrD'] = confAvgs['AdjD'] - confAvgs['AdjD'].mean()

master = pd.merge(master,confAvgs[['ConfStrO', 'ConfStrD']], on='Conf', how='left')

master['AdjEM'] = master['AdjO'] - master['AdjD']
master['ConfStr'] = master['ConfStrO'] - master['ConfStrD']
master['SoS'] = master['OppO'] - master['OppD']
master['Rk'] = master['AdjEM'].rank(ascending=False)

qVals = []
for school,schedule in zip(schools,schedules):
    adjQ = win_quality(schedule)
    qVals.append(adjQ)
    print(school)
    print(adjQ)
'''
qVal = pd.DataFrame(qVals, columns=['AdjQ'])
master = pd.concat([master,qVal], axis=1)

print(master['AdjQ'].mean())
master['AdjQ'] = master['AdjQ'] - master['AdjQ'].mean()
master['AdjO'] = master['AdjO'] + 0.5*master['AdjQ']
master['AdjD'] = master['AdjD'] - 0.5*master['AdjQ']
master['AdjEM'] = master['AdjO'] - master['AdjD']
master['Rk'] = master['AdjEM'].rank(ascending=False)
'''
records = []
for school,schedule in zip(schools,schedules):
    record = quad_wins(schedule)
    records.append(record)
    print(school)
    print(record)

quadW = pd.DataFrame(records, columns=['Record','Home','Neutral','Away','Q1','Q2','Q3','Q4'])
master = pd.concat([master,quadW], axis=1)

#'AdjQ',
master = master.drop(['EffO','EffD','EffP','OppO','OppD','OppP','ConfStrO','ConfStrD'], axis=1)
master = master.reindex(columns=['Rk','School','Conf','ConfStr','AdjEM','AdjO','SDO','AdjD','SDD','AdjT','SDP','Record','Home','Neutral','Away','Q1','Q2','Q3','Q4'])
master = master.sort_values(by=['Rk'])

print(master.head(5))
master.to_csv('master.csv', index=False)