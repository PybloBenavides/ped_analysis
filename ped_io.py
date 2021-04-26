import pandas as pd


def read_exp(path):
    df = pd.read_csv(path,sep='\t',skiprows=3)
    df.rename(columns={'# PersID' : 'PERS_ID', 'Frame':'TIME'},inplace=True)

    df.loc[:,'TIME'] = (df['TIME'] -df['TIME'].min()) *0.04
    if df.iloc[0]['X'] > 0:
        df.loc[:,'X'] = df['X'] * -1
    return df