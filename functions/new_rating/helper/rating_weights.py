import pandas as pd
import math

# Sample data
data = {'RoundProgress': [0.143677],
        'Victim': ['b1t'],
        'Damage': [19],
        'KillNumber': [3],
        'IsTrade': [False],
        'RoundEndReason': ['TerroristsWin'],
        'PlayerTeamWon': [False],
        'KilledHelpedAliveFlag': ['Killed'],
        'PlayerWeapon': ['[AWP]'],
        'VictimWeapon': ['AK-47'],
        'PlayerTeamEconomy': ['Full Buy'],
        'VictimTeamEconomy': ['Full Buy'],
        'AliveTeammates': [0],
        'PlayerSide': ['CT'],
        'PlayerTeamScore': [2],
        'VictimTeamScore': [5]}

df = pd.DataFrame(data)

# Defining weights for each factor
weights_killed_flag_positive={
    "Killed": 5,
    "Significantly Assisted": 4,
    "Assisted": 3,
    "Significantly Helped": 2,
    "Helped": 1.5,
    "Survived": 0.5
}

weights_round_won_positive={
    True: 1.2,
    False: 0.6
}

weights_traded_positive={
    True:1.1,
    False:1,
    "N/A":1
}

weights_roundendreason={
    "TerroristsWin":{"ImportantKills": [1,2,3,4,5], "PunishedDeaths":[5]},
    "CounterTerroristsWin":{"ImportantKills": [1,2,3,4,5], "PunishedDeaths":[5]},
    "BombExploded":{"ImportantKills": [1,2,3], "PunishedDeaths":[1,2,5]},
    "BombDefused":{"ImportantKills": [3,4,5], "PunishedDeaths":[1,2,5]},
    "positive_weight": 1.25,
    "negative_weight": 0.75
}

weights_buytype_win={
    "Full Buy":{"Full Buy":1.1,"Semi Buy":0.9,"Semi Eco":0.7,"Full Eco":0.5,},
    "Semi Buy":{"Full Buy":3,"Semi Buy":1.5,"Semi Eco":1.2,"Full Eco":0.7},
    "Semi Eco":{"Full Buy":4,"Semi Buy":3,"Semi Eco":1.7,"Full Eco":0.9},
    "Full Eco":{"Full Buy":5,"Semi Buy":4,"Semi Eco":3,"Full Eco":1,}
}

weights_buytype_lose={
    "Full Buy":{"Full Buy":0.7,"Semi Buy":0.5,"Semi Eco":0.3,"Full Eco":0.2,},
    "Semi Buy":{"Full Buy":0.8,"Semi Buy":0.7,"Semi Eco":0.5,"Full Eco":0.3},
    "Semi Eco":{"Full Buy":0.85,"Semi Buy":0.9,"Semi Eco":0.7,"Full Eco":0.4},
    "Full Eco":{"Full Buy":0.9,"Semi Buy":0.9,"Semi Eco":0.9,"Full Eco":0.5,}
}

weights_playerside_positive={
    "CT":1,
    "T":1.2
}

weights_killnumber={
    0: 1,
    1: 1.2,
    2: 1,
    3: 1,
    4: 1,
    5: 1.2
}

def calculate_alive_teammate_impact(alive_teammates):
    return 2-alive_teammates/4

# Function to calculate score impact based on the sum of scores
def calculate_score_impact(player_score, victim_score):
    sum_scores = player_score + victim_score
    target_sum1 = 30  # Adjust as needed based on your preference
    target_sum2 = 15  # Adjust as needed based on your preference
    sum_scores = 30 if sum_scores>30 else sum_scores
    if sum_scores<15:
        impact = 2 - abs(sum_scores - target_sum2) / target_sum2
    else:
        impact = 2.5 - abs(sum_scores - target_sum1) / target_sum1
    if (sum_scores == 0) | (sum_scores==15):
        impact=2.0
    #print(impact)
    return impact*calculate_remaining_rounds_impact(player_score,victim_score)


# Function to calculate remaining rounds impact
def calculate_remaining_rounds_impact(player_score, opponent_score):
    if (player_score in range(10)) | (opponent_score in range(10)):
        return 1
    return max(math.log(player_score),math.log(opponent_score))/1.75


def calculate_positive_rating(row):
    #print(fr'Data. Initial Rating: {weights_killed_flag_positive[row["KilledHelpedAliveFlag"]]}, Player team won/lost impact: {weights_round_won_positive[row["PlayerTeamWon"]]}, Trade impact: {weights_traded_positive[row["IsTrade"]]}, Player Side Impact: {weights_playerside_positive[row["PlayerSide"]]}, Alive Teammate Impact: {calculate_alive_teammate_impact(row["AliveTeammates"])}, Score Impact: {calculate_score_impact(row["PlayerTeamScore"],row["VictimTeamScore"])}')
    player_team_won=row["PlayerTeamWon"]
    rating = weights_killed_flag_positive[row["KilledHelpedAliveFlag"]]
    rating=rating*weights_killnumber[row["KillNumber"]]*weights_round_won_positive[player_team_won]*weights_traded_positive[row["IsTrade"]]*weights_playerside_positive[row["PlayerSide"]]*calculate_alive_teammate_impact(row["AliveTeammates"])*calculate_score_impact(row["PlayerTeamScore"],row["VictimTeamScore"])
    if player_team_won:
        #rating=rating*weights_buytype_win[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]
        #print(fr'Impact of buytype at round win: {weights_buytype_win[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]}')
        impact_buytype=weights_buytype_win[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]
    else:
        #rating=rating*weights_buytype_win[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]
        #print(fr'Impact of buytype at round lose: {weights_buytype_lose[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]}')
        impact_buytype=weights_buytype_lose[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]
    rating=rating*impact_buytype
    #print(rating)
    return rating

death_initial_rating = -1.5

weights_round_won_negative={
    False: 0.6,
    True: 1.2
}

weights_playerside_negative={
    "CT":1.2,
    "T":1
}

weights_had_kit_negative={
    False: 1,
    True: 1.2,
    "N/A": 1
}

weights_had_awp_negative={
    False: 1,
    True: 1.4,
    "N/A": 1
}

weights_is_traded_negative={
    False: 1.1,
    True: 1,
    "N/A": 1
}

def calculate_negative_rating(row):
    #print(fr'Data. Initial Rating: {weights_killed_flag_positive[row["KilledHelpedAliveFlag"]]}, Player team won/lost impact: {weights_round_won_positive[row["PlayerTeamWon"]]}, Trade impact: {weights_traded_positive[row["IsTrade"]]}, Player Side Impact: {weights_playerside_positive[row["PlayerSide"]]}, Alive Teammate Impact: {calculate_alive_teammate_impact(row["AliveTeammates"])}, Score Impact: {calculate_score_impact(row["PlayerTeamScore"],row["VictimTeamScore"])}')
    player_team_won=row["RoundWon"]
    rating = death_initial_rating
    #rating=rating*weights_killnumber[row["KillNumber"]]*weights_round_won_positive[player_team_won]*weights_traded_positive[row["IsTrade"]]*weights_playerside_positive[row["PlayerSide"]]*calculate_alive_teammate_impact(row["AliveTeammates"])*calculate_score_impact(row["PlayerTeamScore"],row["VictimTeamScore"])
    rating=rating*weights_round_won_negative[player_team_won]*weights_playerside_negative[row["PlayerSide"]]*weights_had_kit_negative[row["HadKit"]]*weights_had_awp_negative[row["HadAWP"]]*weights_is_traded_negative[row["IsTraded"]]*calculate_score_impact(row["PlayerScore"],row["EnemyScore"])
    if player_team_won:
        #rating=rating*weights_buytype_win[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]
        #print(fr'Impact of buytype at round win: {weights_buytype_win[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]}')
        impact_buytype=1/weights_buytype_win[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]
    else:
        #rating=rating*weights_buytype_win[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]
        #print(fr'Impact of buytype at round lose: {weights_buytype_lose[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]}')
        impact_buytype=1/weights_buytype_lose[row["PlayerTeamEconomy"]][row["VictimTeamEconomy"]]
    rating=rating*impact_buytype
    #print(rating)
    return rating