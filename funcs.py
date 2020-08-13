import json
import re
import pandas
import os

df = pandas.DataFrame()


def append_nans(parametru, dictionar):
    if parametru not in dictionar.keys():
        dictionar.update({parametru: None})


def clean_up_data(sd):
    for i in sd.keys():
        for j in sd[i]['Detalii']:
            if re.search('^[0-9].* mp utili', j):
                sd[i].update({'mp': j.strip(' mp utili')})
            elif re.search('^Etaj [0-9]*/[0-9]*', j) or re.search('^Parter/[0-9]*', j) \
                    or re.search('^Demisol/[0-9]*', j) \
                    or re.search('^Etaj [0-9]*', j) \
                    or re.search('^Parter$', j) or re.search('^Demisol', j) or re.search('^Demisol/[0-9]*', j) \
                    or re.search('^Mansarda', j) or re.search('^Mansarda/[0-9]*', j):
                sd[i].update({'et': j}) #etaj
            elif re.search('^[0-9]*.[0-9]*$', j) and len(j) >= 3:
                sd[i].update({'pret': j.replace('.', '')})
            elif re.search('^[0-9]* m* ', j):
                sd[i].update({'distanta_metrou': j.split()[0]})
        append_nans('mp', sd[i])
        append_nans('et', sd[i])
        append_nans('pret', sd[i])
        append_nans('distanta_metrou', sd[i])
        del sd[i]['Detalii']


def clin(dataframe):
    dataframe.dropna(subset=['pret', 'mp'], inplace=True)
    dataframe['pret'] = dataframe['pret'].astype(float)
    dataframe['mp'] = dataframe['mp'].str.replace(',', '.')
    dataframe['pret'] = dataframe['pret'].astype(float)
    dataframe.sort_values(by=['index', 'zi'], inplace=True)
    dataframe['pret_var']= dataframe['pret'].diff()


for file in os.listdir():
    if file.endswith('.json'):
        with open(file, 'r') as f:
            raw_data = json.load(f)
            clean_up_data(raw_data)
            temp = pandas.DataFrame.from_dict(raw_data, orient='index')
            temp['zi'] = file.strip('.json')
            temp.reset_index(inplace=True)
            df = df.append(temp)
        f.close()


clin(df)


