import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('output/resultats_CNR_MiM_python_mesure1.csv')

sum_CNR_tum, sum_error = [], []
for it in range(3, 7, 1):
    for gauss in range(0, 5, 2):
        sum_CNR_tum.append(df.loc[df['Itération'] == it, :].loc[df['Gaussien (mm)'] == gauss, 'CNR Tumeur'].sum())
        sum_error.append(df.loc[df['Itération'] == it, :].loc[df['Gaussien (mm)'] == gauss, 'Ecart concentration carré (Bq/mL)^2'].sum())

iteration = sorted([f for f in range(3, 7, 1)]*3)
gaussien = [f for f in range(0, 5, 2)]*4

df_sum = pd.DataFrame.from_records([iteration, gaussien, sum_CNR_tum, sum_error]).T
df_sum.columns = ['Itération', 'Gaussien (mm)', 'Somme CNR Tumeur', 'Somme erreurs carré (Bq/mL)^2']
df_sum['RMSE'] = np.sqrt(df_sum['Somme erreurs carré (Bq/mL)^2'] / 5)
df_sum['SNR Foie'] = df['SNR Tumeur'][4::5].to_list()
df_sum['SNR^2 Foie'] = df_sum['SNR Foie']**2

plt.figure(figsize=(12, 7))
plt.scatter(df_sum['SNR^2 Foie'], df_sum['RMSE'], label='RMSE')
# plt.scatter(df_sum['SNR^2 Foie'], df_sum['Somme CNR Tumeur'], label='CNR')
plt.grid(ls='--')
plt.xlabel('SNR^2')
plt.ylabel('RMSE')
plt.title('Mesure 1 Quadra')
plt.legend()
plt.show()

print(df_sum.max())