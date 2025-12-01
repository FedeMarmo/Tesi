import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
from datetime import datetime
from scipy.stats import zscore

import matplotlib.dates as mdates


# PERCORSO FILE
percorso_file_GME = r"C:\Users\Federico\Desktop\Uni\Magistrale\Tesi\Energy_Plus\Simulazioni\Prezzi_Elettricità_GME\Giu_Lug_Ago_2024.xlsx"

# IMPORTA FILE
df_GME = pd.read_excel(percorso_file_GME)

df_GME['Datetime'] = pd.to_datetime(
    df_GME.iloc[:, 0].astype(str) + ' ' + (df_GME.iloc[:, 1] - 1).astype(str) + ':00',
    format="%d/%m/%Y %H:%M",
    errors='coerce'
)

df_GME = df_GME.drop(df_GME.columns[:2], axis=1)


# =========================================================
# SPLIT TEMPORALE
# =========================================================

# =========================================================
# ESTRAZIONE DATE E TIME DA DATETIME
# =========================================================

df_GME['date'] = df_GME['Datetime'].dt.date
df_GME['time'] = df_GME['Datetime'].dt.time


spl_3 = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00", "23:59"]
#spl_3 = ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00", "23:59"]
spl_times = [datetime.strptime(t, "%H:%M").time() for t in spl_3]

def assign_period(row):
    time = row['time']
    if time < spl_times[1]:
        return "Period_1"
    elif time < spl_times[2]:
        return "Period_2"
    elif time < spl_times[3]:
        return "Period_3"
    elif time < spl_times[4]:
        return "Period_4"
    elif time < spl_times[5]:
        return "Period_5"
    elif time < spl_times[6]:
        return "Period_6"
    elif time < spl_times[7]:
        return "Period_7"
    else:
        return "Period_8"

# Assegna i periodi
df_GME['period'] = df_GME.apply(assign_period, axis=1)

# =========================================================
# Z-NORMALIZATION
# =========================================================

# Rimuovi simboli di euro e spazi
df_GME['€_MWh'] = df_GME['€_MWh'].astype(str).str.replace('€', '', regex=False).str.replace(' ', '', regex=False)

# Sostituisci la virgola con il punto se usi notazione decimale europea
df_GME['€_MWh'] = df_GME['€_MWh'].str.replace(',', '.', regex=False)

# Converti in numerico
df_GME['€_MWh'] = pd.to_numeric(df_GME['€_MWh'], errors='coerce')


df_GME['znorm'] = zscore(df_GME['€_MWh'], nan_policy='omit')


# =========================================================
# PAA
# =========================================================

df_PAA = df_GME.groupby(['date', 'period']).agg({'znorm': 'mean'}).reset_index()
df_PAA.rename(columns={'znorm': 'znorm_mean'}, inplace=True)

# =========================================================
# SAX
# =========================================================

breakpoints = [-0.84, 0.00, 0.84]

def assign_symbol(value):
    if value <= breakpoints[0]:
        return 'A'
    elif value <= breakpoints[1]:
        return 'B'
    elif value <= breakpoints[2]:
        return 'C'
    else:
        return 'D'
df_PAA['symbol'] = df_PAA['znorm_mean'].apply(assign_symbol)

# =========================================================
# MERGE
# =========================================================

pydata = pd.merge(
    df_GME,
    df_PAA[['date', 'period', 'symbol']],
    on=['date', 'period'],
    how='left'
)

# =========================================================
# PIVOT PER HEATMAP
# =========================================================

pivot_df = pydata.pivot_table(
    index='date',
    columns='time',
    values='symbol',
    aggfunc='first'
)

# =========================================================
# COLORI SAX
# =========================================================

symbol_colors = {
    'A': '#5591ff',
    'B': '#40c8ff',
    'C': '#ffd954',
    'D': '#7fdd56'
}

cmap = ListedColormap([symbol_colors[key] for key in sorted(symbol_colors.keys())])

symbol_to_num = {symbol: idx for idx, symbol in enumerate(sorted(symbol_colors.keys()))}
numeric_data = pivot_df.replace(symbol_to_num)

# =========================================================
# PLOT
# =========================================================

plt.figure(figsize=(15, 10))
sns.heatmap(
    numeric_data,
    cmap=cmap,
    cbar_kws={'ticks': list(symbol_to_num.values()), 'label': 'SAX Symbol'},
    yticklabels=30
)

plt.title('Carpet Plot of Energy Consumption (SAX Symbols)')
plt.xlabel('Time')
plt.ylabel('Date')

plt.xticks(rotation=45)
plt.show()





# CREAZIONE PAROLE


df_PAA_pivot = df_PAA.pivot(index='date', columns='period', values='symbol').reset_index()


periods = ['Period_1', 'Period_2', 'Period_3', 'Period_4', 'Period_5', 'Period_6', 'Period_7', 'Period_8']
df_PAA_pivot = df_PAA_pivot[['date'] + periods]


df_PAA_pivot['word'] = df_PAA_pivot[periods].apply(lambda row: ''.join(row.values.astype(str)), axis=1)


word_counts = df_PAA_pivot['word'].value_counts().reset_index()
word_counts.columns = ['word', 'count']

df_PAA_pivot = pd.merge(df_PAA_pivot, word_counts, on='word')


df_PAA_pivot['word'] = pd.Categorical(df_PAA_pivot['word'], categories=word_counts['word'], ordered=True)


plt.figure(figsize=(14, 12))
sns.countplot(y='word', data=df_PAA_pivot, order=word_counts['word'])
plt.axvline(0.2 * df_PAA_pivot['word'].value_counts().max(), color='blue', linestyle='--')
plt.title('Frequency of Daily Words')
plt.xlabel('Count')
plt.ylabel('Word')
plt.show()






threshold = 0.2 * df_PAA_pivot['count'].max()

df_PAA_pivot['pattern'] = df_PAA_pivot['count'].apply(lambda x: 'discord' if x < threshold else 'motif')

pydata = pd.merge(pydata, df_PAA_pivot[['date', 'word', 'pattern']], on='date', how='left')

pydata['time_dt'] = pd.to_datetime(pydata['time'].astype(str), format='%H:%M:%S')


palette = sns.color_palette("husl", len(pydata['pattern'].unique()))

pattern_colors = {"motif": "green", "discord": "red"}

g = sns.FacetGrid(pydata, col='word', col_wrap=4, height=4, sharey=False, hue='pattern', palette=pattern_colors)
g.map_dataframe(sns.lineplot, x='time_dt', y='€_MWh', estimator=None, units='date', lw=0.7, alpha=0.7)

# Adjust plot aesthetics
for ax in g.axes.flatten():
    ax.set_xlabel('Hour')
    ax.set_ylabel('Energy Consumption')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=8))
    plt.setp(ax.get_xticklabels(), rotation=45)

# Add a legend for 'pattern'
g.add_legend(title="Pattern")

plt.tight_layout()
plt.show()











# Importa le librerie necessarie
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import scipy.cluster.hierarchy as sch
from scipy.cluster.hierarchy import fcluster
from datetime import datetime
from sklearn.cluster import KMeans  # Aggiungi KMeans per il metodo a gomito

# Filtra i profili "discord" basandosi sulla colonna 'pattern'
discord_profiles = pydata[pydata['pattern'] == 'discord']

# Prepara i dati per il clustering: utilizziamo i profili di consumo dalla colonna 'power_C'
discord_pivot = discord_profiles.pivot_table(index='date', columns='time', values='€_MWh', aggfunc='mean').fillna(0)

# Standardizzazione dei dati
scaler = StandardScaler()
discord_scaled = scaler.fit_transform(discord_pivot)

# Metodo a gomito per determinare il numero ottimale di cluster
sse = []  # Lista per la somma delle distanze al quadrato
cluster_range = range(1, 11)  # Testa i numeri di cluster da 1 a 10

for k in cluster_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(discord_scaled)  # Fitting del modello
    sse.append(kmeans.inertia_)  # Aggiungi la somma delle distanze al quadrato

# Grafico del metodo a gomito
plt.figure(figsize=(10, 6))
plt.plot(cluster_range, sse, marker='o')
plt.title('Metodo a Gomito per la Selezione del Numero di Cluster')
plt.xlabel('Numero di Cluster')
plt.ylabel('Somma delle Distanze al Quadrato (SSE)')
plt.grid(True)
plt.show()

# Calcola la differenza tra i valori SSE consecutivi per trovare il punto di inflection
differences = [sse[i] - sse[i - 1] for i in range(1, len(sse))]
second_differences = [differences[i] - differences[i - 1] for i in range(1, len(differences))]

# Trova il punto dove la seconda derivata è minima (cambio di pendenza)
optimal_clusters = second_differences.index(min(second_differences))-1  # +2 perché abbiamo una seconda differenza

print(f"Numero ottimale di cluster: {optimal_clusters}")

# Clustering gerarchico
linkage_matrix = sch.linkage(discord_scaled, method='ward')

# Visualizza il dendrogramma con la linea di taglio
plt.figure(figsize=(12, 8))
sch.dendrogram(linkage_matrix, labels=discord_pivot.index.astype(str), leaf_rotation=90, leaf_font_size=8)
plt.axhline(y=linkage_matrix[-optimal_clusters + 1, 2], color='r', linestyle='--', label=f'{optimal_clusters} Clusters')
plt.title("Dendrogram of Discord Profiles")
plt.xlabel("Profiles (Dates)")
plt.ylabel("Distance")
plt.legend()
plt.show()

# Creazione dei cluster usando il numero ottimale trovato dal metodo a gomito
clusters = fcluster(linkage_matrix, t=optimal_clusters, criterion='maxclust')

# Aggiungi i cluster al pivot
discord_pivot['Cluster'] = clusters

df_centroid = pd.DataFrame()
df_std_dev = pd.DataFrame()

# Plot dei cluster con profili normalizzati
for cluster_id in sorted(discord_pivot['Cluster'].unique()):
    # Filtra i profili del cluster corrente
    cluster_data = discord_pivot[discord_pivot['Cluster'] == cluster_id].drop(columns=['Cluster'])

    # Normalizza i profili rispetto al valore massimo del cluster
    max_value = cluster_data.max().max()
    normalized_cluster_data = cluster_data / max_value  # Normalizzazione dei profili

    # Calcola il centroide del cluster normalizzato
    centroid = normalized_cluster_data.mean(axis=0)
    std_dev = normalized_cluster_data.std(axis=0)

    # Append to the DataFrames using pd.concat
    df_centroid = pd.concat([df_centroid, (centroid * max_value).to_frame().T], ignore_index=True)

    df_std_dev = pd.concat([df_std_dev, std_dev.to_frame().T], ignore_index=True)

    # Estrai gli orari
    time_columns = list(cluster_data.columns)  # Converti l'Index in una lista

    # Determina se i valori di time_columns sono datetime.time o stringhe
    if isinstance(time_columns[0], datetime):
        time_as_minutes = [t.hour * 60 + t.minute for t in time_columns]
    else:  # Se sono stringhe, convertili prima in datetime.time
        time_as_minutes = [
            datetime.strptime(str(t), "%H:%M:%S").time().hour * 60 + datetime.strptime(str(t), "%H:%M:%S").time().minute
            for t in time_columns
        ]

    # Traccia i profili del cluster normalizzato
    plt.figure(figsize=(10, 6))
    for profile in normalized_cluster_data.index:
        plt.plot(time_as_minutes, normalized_cluster_data.loc[profile], color='gray', alpha=0.3)

    # Traccia il centroide e la banda di deviazione standard
    plt.plot(time_as_minutes, centroid, color='red', linewidth=2, label='Centroid')
    plt.fill_between(
        time_as_minutes, centroid - std_dev, centroid + std_dev, color='red', alpha=0.2, label='Std. Deviation'
    )

    # Aggiungi etichette e titolo
    plt.title(f'Cluster {cluster_id}')
    plt.xlabel('Time of Day')
    plt.ylabel('Normalized Power Consumption')

    # Aggiungi le etichette sull'asse delle ascisse con intervalli di 4 ore
    time_ticks = range(0, 1440, 240)  # Intervalli di 240 minuti (4 ore)
    time_labels = [f'{t // 60:02d}:{t % 60:02d}' for t in time_ticks]
    plt.xticks(ticks=time_ticks, labels=time_labels)

    plt.legend()
    plt.show()