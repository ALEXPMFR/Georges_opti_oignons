import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

df = pd.read_csv('Analyse_stats_mesure1.csv')

iteration, gaussien = [], []
for el in df['Description des séries']:
    iteration.append(el.split('_')[7])
    gaussien.append(el.split('_')[8])

contour = ['Fond 1', 'Fond 2', 'Fond 3', 'Fond foie', 'T foie', 'T1', 'T2', 'T3', 'T4']
contour = sorted(contour * int(len(df)/len(contour)))

df['Itérations'] = [int(f[0]) for f in iteration]
df['Gaussien (mm)'] = [int(f[1]) for f in gaussien]
df = df.drop(['Résultat', 'Description des séries'], axis=1)
df['Contour'] = contour
df = df.drop(['Min (BQML)', 'Max (BQML)'], axis=1)
df = df.set_index(['Itérations', 'Gaussien (mm)', 'Contour'])
pd.set_option('display.max_rows', None)

df_fond = df[df.index.get_level_values('Contour').isin(['Fond 1', 'Fond 2', 'Fond 3'])]
df_fond_mean = df_fond.groupby(level=['Itérations', 'Gaussien (mm)']).mean()
df_fond_mean['Contour'] = 'Moyenne Fond'
df_fond_mean['Volume (ml)'] = '14'
df_fond_mean = df_fond_mean.set_index('Contour', append=True)
df = pd.concat([df, df_fond_mean]).sort_index()

concentration_tumeur = 18000 # Bq/mL

concentration, CNR_T_foie, CNR_T, SNR_T_foie = [], [], [], []
for it in range(3, 7, 1):
    for gauss in range(0, 5, 2):
        for tum in ['T1', 'T2', 'T3', 'T4', 'T foie']:
            concentration.append(df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc[tum, 'Moyenne (BQML)'])
            CNR_T_foie.append((df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['T foie', 'Moyenne (BQML)'] - df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['Fond foie', 'Moyenne (BQML)']) / df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['Fond foie', 'Déviation standard (BQML)'])
            CNR_T.append((df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc[tum, 'Moyenne (BQML)'] - df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['Moyenne Fond', 'Moyenne (BQML)']) / df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['Moyenne Fond', 'Déviation standard (BQML)'])
            SNR_T_foie.append(df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['T foie', 'Moyenne (BQML)'] / df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['Fond foie', 'Déviation standard (BQML)'])

iteration = sorted([f for f in range(3, 7, 1)] * 5 * 3)
gaussien = sorted([f for f in range(0, 5, 2)] * 5) * 4
tumeur = ['T1', 'T2', 'T3', 'T4', 'T Foie'] * 12

df_CNR = pd.DataFrame.from_records([iteration, gaussien, tumeur, concentration]).T
df_CNR.columns = ['Itération', 'Gaussien (mm)', 'Tumeur', 'Concentration (Bq/mL)']
df_CNR = df_CNR.set_index(['Itération', 'Gaussien (mm)', 'Tumeur'])
df_CNR['Ecart concentration (Bq/mL)'] = concentration_tumeur - df_CNR['Concentration (Bq/mL)']
df_CNR['Ecart concentration carré (Bq/mL)^2'] = (concentration_tumeur - df_CNR['Concentration (Bq/mL)'])**2
df_CNR['CNR Tumeur'] = CNR_T
df_CNR['CNR Tumeur foie'] = CNR_T_foie
df_CNR['SNR Tumeur foie'] = SNR_T_foie
df_CNR['SNR^2 Tumeur foie'] = df_CNR['SNR Tumeur foie']**2


# df.to_csv('output/resultats_bruts_MiM_python_mesure1.csv')
# df_CNR.to_csv('output/resultats_CNR_MiM_python_mesure1.csv')
print(df_CNR)