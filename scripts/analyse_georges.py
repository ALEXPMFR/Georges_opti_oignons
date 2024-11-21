import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

mesure = '5'
machine = 'vision'
if machine == 'vision':
    nombre_coupes = 351
    nombre_recon = int(len(list(Path('../recon_mesures/' + machine + '/mesure' + mesure).rglob('*.IMA')))/nombre_coupes)
else:
    nombre_coupes = 645
    nombre_recon = int(len(list(Path('../recon_mesures/' + machine + '/mesure' + mesure).rglob('*.ima')))/nombre_coupes)

df = pd.read_csv('../recon_mesures/' + machine + '/Analyse_stats_mesure' + mesure + '_' + machine + '_new_ROI.csv', decimal=',')
pd.set_option('display.max_rows', None)
iteration, gaussien = [], []
for el in df['Description des séries']:
    if machine == 'quadra':
        iteration.append(el.split('_')[7])
        gaussien.append(el.split('_')[8])
    else:
        iteration.append(el.split('_')[0])
        gaussien.append(el.split('_')[1])

contour = ['médiastin', 'Fond Foie', 'T1 - 5mm', 'T2 - 6mm', 'T3 - 8mm', 'T4 - 10mm', 'Rachis 8mm', 'Foie - 8mm', 'Reins', 'CQ Tumeurs']
contour = [[f] * int(len(df)/len(contour))  for f in contour]
new_contour = []
for con in contour:
    for concon in el:
        new_contour.append(concon)

df['Itérations'] = [int(f[0]) for f in iteration]
df['Gaussien (mm)'] = [int(f[1]) for f in gaussien]
df = df.drop('Description des séries', axis=1)
if mesure == '1':
    df = df.drop('Résultat', axis=1)
df['Contour'] = new_contour
df = df.drop(['Min (BQML)', 'Max (BQML)'], axis=1)
df = df.set_index(['Itérations', 'Gaussien (mm)', 'Contour'])
# pd.set_option('display.max_rows', None)
df['Moyenne (BQML)'] = df['Moyenne (BQML)'].astype(float)
df['Déviation standard (BQML)'] = df['Déviation standard (BQML)'].astype(float)

concentration_tumeur = 18000 # Bq/mL
concentration, CNR_T, SNR_fond, volume = [], [], [], []
for it in range(3, 7, 1):
    for gauss in range(0, 5, 2):
        for tum in ['T1 - 5mm', 'T2 - 6mm', 'T3 - 8mm', 'T4 - 10mm', 'Rachis 8mm', 'Foie - 8mm']:
            concentration.append(df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc[tum, 'Moyenne (BQML)'])
            volume.append(df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc[tum, 'Volume (ml)'])
            SNR_fond.append(df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['médiastin', 'Moyenne (BQML)'] / df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['médiastin', 'Déviation standard (BQML)'])
            if tum == 'Foie - 8mm':
                CNR_T.append((df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc[tum, 'Moyenne (BQML)'] - df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['Fond Foie', 'Moyenne (BQML)']) / df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['Fond Foie', 'Déviation standard (BQML)'])
            else:
                CNR_T.append((df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc[tum, 'Moyenne (BQML)'] - df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['médiastin', 'Moyenne (BQML)']) / df.xs(it, level='Itérations').xs(gauss, level='Gaussien (mm)').loc['médiastin', 'Déviation standard (BQML)'])

nombre_iterations = len(set(iteration))
nombre_gaussien = len(set(gaussien))
tumeur = ['T1 - 5mm', 'T2 - 6mm', 'T3 - 8mm', 'T4 - 10mm', 'Rachis 8mm', 'Foie - 8mm'] * nombre_recon
nombre_tumeurs = len(tumeur) / nombre_recon
# iteration = sorted(list(set(iteration)) * int(len(tumeur)/nombre_recon * nombre_gaussien))
iteration = sorted([int(f[0]) for f in list(set(iteration))] * int(nombre_tumeurs * nombre_gaussien))
gaussien = sorted([int(f[1]) for f in list(set(gaussien))] * int(nombre_tumeurs)) * nombre_iterations

df_metrique = pd.DataFrame.from_records([iteration, gaussien, tumeur, concentration, volume]).T
df_metrique.columns = ['Itération', 'Gaussien (mm)', 'Tumeur', 'Concentration (Bq/mL)', 'Volume (mL)']
# df_metrique = df_metrique.set_index(['Itération', 'Gaussien (mm)', 'Tumeur'])
df_metrique['Ecart concentration (Bq/mL)'] = concentration_tumeur - df_metrique['Concentration (Bq/mL)']
df_metrique['Ecart concentration carré (Bq/mL)^2'] = (concentration_tumeur - df_metrique['Concentration (Bq/mL)'])**2
df_metrique['CNR Tumeur'] = CNR_T
df_metrique['CNR Tumeur volumique'] = df_metrique['CNR Tumeur'] / df_metrique['Volume (mL)']
df_metrique['SNR Fond'] = SNR_fond

# df.to_csv('output/resultats_bruts_MiM_python_mesure' + mesure + '_' + machine + '.csv')
# df_metrique.to_csv('output/resultats_CNR_MiM_python_mesure' + mesure + '_' + machine + '.csv')

plt.figure(figsize=(12, 7))
for tum in tumeur[:6]:
    plt.scatter(df_metrique.loc[df_metrique['Tumeur'] == tum, 'SNR Fond'], df_metrique.loc[df_metrique['Tumeur'] == tum, 'CNR Tumeur'], label=tum)
plt.grid(ls='--')
plt.legend(loc='upper right')
plt.xlabel('SNR Fond')
plt.ylabel('CNR Tumeur')
plt.title('Mesure ' + mesure + ' ' + machine.upper())
# plt.savefig('output/figures/CNR_vol_' + machine + '_' + mesure + '.png', dpi=250)
plt.show()
plt.figure(figsize=(12, 7))
for tum in tumeur[:6]:
    plt.scatter(df_metrique.loc[df_metrique['Tumeur'] == tum, 'SNR Fond'], df_metrique.loc[df_metrique['Tumeur'] == tum, 'CNR Tumeur volumique'], label=tum)
plt.grid(ls='--')
plt.legend(loc='upper right')
plt.xlabel('SNR Fond')
plt.ylabel('CNR Tumeur volumique')
plt.title('Mesure ' + mesure + ' ' + machine.upper())
# plt.savefig('output/figures/CNR_vol_' + machine + '_' + mesure + '.png', dpi=250)
plt.show()

print(df)