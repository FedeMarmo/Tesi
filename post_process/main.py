import pandas as pd

from post_process_functions import correzione_struttura, correzione_outliers
from plots_function import plot_lineare_multigiorno
from calcoli_energetici import rebound_energy


#PERCORSO FILE
percorso_file = r"C:\Users\Federico\Desktop\Uni\Magistrale\Tesi\Energy_Plus\Simulazioni\Prova_PCM_2_DR\1ZoneUncontrolledWithHysteresisPCM2_DR.csv"

#IMPORTA FILE
df = pd.read_csv(percorso_file, sep=',')

#PERCORSO FILE DI RIFERIMENTO
percorso_file_rif = r"C:\Users\Federico\Desktop\Uni\Magistrale\Tesi\Energy_Plus\Simulazioni\Prova_PCM_2\1ZoneUncontrolledWithHysteresisPCM2.csv"

#IMPORTA FILE
df_rif = pd.read_csv(percorso_file_rif, sep=',')


df=correzione_struttura(df)

df_clean=correzione_outliers(df)

# Lista delle colonne da graficare
columns_to_plot = ['Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)',
                    'ZONE ONE:Zone Mean Air Temperature [C](Hourly)',
                    'ZONE ONE IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Rate [W](Hourly) ']
plot_lineare_multigiorno(df_clean, columns_to_plot)


df_rif=correzione_struttura(df_rif)


df_rif_clean=correzione_outliers(df_rif)


rebound_energy_column = 'ZONE ONE IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Supply Air Total Heating Rate [W](Hourly) '
calo_potenza_DR, aumento_rebound_DR, energia_risparmiata, energia_rebound = rebound_energy(df_rif_clean, df_clean, rebound_energy_column)


df_clean.to_csv(r"C:\Users\Federico\Desktop\Uni\file_datetime_2025_hourindex.csv", index=False)

