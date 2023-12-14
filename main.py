# load history
# plan next actions
# save future plans.
from datetime import datetime
from typing import List
import numpy as np
import pandas as pd

from action import Patrol
from definitions import MISSING, MAXIMUM_SOLDIERS_IN_ACTION, SOLDIER
from soldier import Soldier
from tasks import GuardingStand
from definitions import SoldiersDF



def load():
    existing_shavzak = pd.read_csv("db/exp3.csv")
    existing_shavzak = existing_shavzak.reset_index()  # make sure indexes pair with number of rows
    soldiers = {}
    home = pd.read_csv("db/exp3.csv", encoding="utf-8-sig")
    for index, row in home.iterrows():
        soldier = Soldier(row[SoldiersDF.NAME])
        soldier.add_home_time(row["start_date"],row["start_hour"],row["end_date"],row["end_hour"])
        soldiers[row[SoldiersDF.NAME]] = soldier
    for index, row in existing_shavzak.iterrows():
        patrol = \
            Patrol(row["start_date"], row["start_time"], row["end_time"])
        for i in range(1, MAXIMUM_SOLDIERS_IN_ACTION + 1):
            if row[f"{SOLDIER}{i}"]:
                soldiers[row[f"{SOLDIER}{i}"]].add_action(patrol)

    soldiers_df = pd.DataFrame(columns=[SoldiersDF.NAME, SoldiersDF.LAST_PATROL, SoldiersDF.TASH_SCORE])
    # soldiers_df.set_index(SoldiersDF.NAME, inplace=True)
    i = 0
    for name, soldier in soldiers.items():
        row = [name, soldier.last_patrol, soldier.tash_score()]
        soldiers_df.loc[i] = row
        i += 1

    tasks = pd.read_csv("db/tasks.csv")
    tasks = tasks.reset_index()  # make sure indexes pair with number of rows
    all_tasks = []
    for index, row in tasks.iterrows():
        stand = GuardingStand(row[SoldiersDF.NAME], row["pattern"], row["start_date"], row["end_date"])
        all_tasks.append(stand.manning)
    all_tasks = pd.concat(all_tasks).sort_index().sort_values("start_time")
    all_tasks.to_csv(f"db/all.csv", encoding='utf-8-sig', index=False, mode="w+")
    for index, row in all_tasks.iterrows():
        for i in range(1, MAXIMUM_SOLDIERS_IN_ACTION + 1):
            if row[f"{SOLDIER}{i}"] == MISSING:
                patrol = Patrol(row["start_date"], row["start_time"], row["end_time"])
                soldier_name = find_next_soldier(soldiers_df, soldiers, patrol)
                all_tasks.at[index, f"{SOLDIER}{i}"] = soldier_name
                soldiers[soldier_name].add_action(patrol)
                soldiers_df = update_soldiers_df(soldiers_df, patrol.end_time, soldiers[soldier_name].tash_score())
    all_tasks.to_csv(f"db/final.csv", date_format='%d/%m/%Y', encoding='utf-8-sig', index=False, mode="w+")

def find_next_soldier(soldiers_df: pd.DataFrame, soldiers: dict, patrol: Patrol) -> str:
    soldier = soldiers_df.sort_values([SoldiersDF.LAST_PATROL, SoldiersDF.TASH_SCORE], ascending=[True, True]).head(1)
    while True:
        soldier_name = soldier[SoldiersDF.NAME].iloc[0]
        if soldiers[soldier_name].is_home(patrol.start_time) or soldiers[soldier_name].is_home(patrol.end_time):
            print(f"the soldier {soldier_name} is at home at {patrol.start_time}-{patrol.end_time}")
            soldiers_df = soldiers_df.apply(np.roll, shift=-1)
            soldier = soldiers_df.head(1)
        else:
            return soldier_name
def update_soldiers_df(soldiers_df: pd.DataFrame, last_patrol: datetime, tash_score: float) -> str:
    soldier = soldiers_df.sort_values([SoldiersDF.LAST_PATROL, SoldiersDF.TASH_SCORE], ascending=[True, True]).head(1)
    idx = soldiers_df.index[soldiers_df[SoldiersDF.NAME] == soldier[SoldiersDF.NAME].iloc[0]][0]
    soldiers_df.at[idx, SoldiersDF.LAST_PATROL] = last_patrol
    soldiers_df.at[idx, SoldiersDF.TASH_SCORE] = tash_score
    return soldiers_df



if __name__ == '__main__':
    load()
