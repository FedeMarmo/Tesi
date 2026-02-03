
import pandas as pd
from post_process_functions import correzione_struttura
from plots_function import plot_lineare_multigiorno

# Percorso file
file_path = r"C:\Users\Federico\Desktop\Uni\Magistrale\Tesi\Energy_Plus\Simulazioni\Mio\Torino\Torino_DSF\Torino_DSF_Vent_DSF\Torino_DSF_Vent_DSF.csv"

# Import CSV
df = pd.read_csv(file_path)

df=correzione_struttura(df)

# Estrae le prime due date
t1 = df.iloc[0, 0]
t2 = df.iloc[1, 0]

# Calcola il timestep in secondi
timestep = (t2 - t1).total_seconds()

print("Timestep (secondi):", timestep)

# Nomi colonne da sommare
col1 = "FINESTRA_1_DSF:Surface Window Gap Convective Heat Transfer Rate [W](TimeStep)"
col2 = "FINESTRA_2_DSF:Surface Window Gap Convective Heat Transfer Rate [W](TimeStep)"

# Controllo che esistano
if col1 not in df.columns or col2 not in df.columns:
    raise ValueError("Una o entrambe le colonne DSF non trovate nel file.")


# Creazione nuova colonna: somma
df["Potenza ceduta all'aria da dsf totale [W]"] = df[col1].fillna(0) + df[col2].fillna(0)

# densità aria kg/m3
dens_aria = 1.225
# calore specifico aria j/kg*k
calore_spec_aria = 1005
# portata aria con 0,5 l/s*m2 in m3/s
portata_aria = 0.024
portata_aria_finestra =portata_aria / 2


col3 = "Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)"
col4 = "FINESTRA_1_DSF:Surface Window Gap Convective Heat Transfer Energy [J](TimeStep)"

# Controllo che esistano
if col3 not in df.columns or col4 not in df.columns:
    raise ValueError("Una o entrambe le colonne DSF non trovate nel file.")

# Creazione nuova colonna: Temperatura aria in uscita dalla cavità DSF
df["Temperatura aria uscita da cavita [C]"] = df[col4].fillna(0) / (dens_aria * calore_spec_aria * portata_aria_finestra * timestep) + df[col3].fillna(0)


col5 = "UFFICIO_BESTEST_ZONA:Zone Mean Air Temperature [C](TimeStep)"

# Controllo che esistano
if col5 not in df.columns:
    raise ValueError("Una o entrambe le colonne DSF non trovate nel file.")

# Creazione colonna potenza scambiata dal flusso di aria entrante dalla doppia pelle con l'ambiente interno
df["Potenza totale ceduta dalle cavità DSF all ambiente [W]"] = (dens_aria * portata_aria * calore_spec_aria * (df[col3].fillna(0) - df[col5].fillna(0)))

col6 = "UFFICIO_BESTEST_ZONA:Zone Air Heat Balance Outdoor Air Transfer Rate [W](TimeStep)"
col7 = "Potenza totale ceduta dalle cavità DSF all ambiente [W]"

# Controllo che esistano
if col6 not in df.columns or col7 not in df.columns:
    raise ValueError("Una o entrambe le colonne DSF non trovate nel file.")

#Creazione colonna somma contributi aria ventilazione e infiltrazioni

df["Potenza aria ventilazione DSF e infiltrazioni [W]"] = df[col6].fillna(0) + df[col7].fillna(0)


# Lista delle colonne da graficare
columns_to_plot = ['Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)',
                   'UFFICIO_BESTEST_ZONA IDEAL LOADS AIR SYSTEM:Zone Ideal Loads Zone Total Heating Rate [W](TimeStep)',
                   'Potenza totale ceduta dalle cavità DSF all ambiente [W]']
plot_lineare_multigiorno(df, columns_to_plot)





print("Timestep (secondi):", timestep)