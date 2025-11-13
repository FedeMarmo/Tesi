
#FUNZIONE CHE AGGIUSTA IL FORMATO DATETIME DELLA PRIMA COLONNA, AGGIUNGE COLONNA CON INDICE DELLE ORE,
# ELIMINA LE PRIME 48 RIGHE (GIORNI WARMUP),

import pandas as pd

def correzione_struttura(df):
    # ============================================================
    # 🔍 CREAZIONE COLONNA DATETIME COMPLETA CON ANNO 2025
    # ============================================================
    prima_colonna = df.columns[0]

    # Dividiamo la prima colonna in data e ora
    date_time_split = df[prima_colonna].astype(str).str.split(expand=True)
    date_time_split.columns = ['Date', 'Time']

    # --- 🔧 CORREZIONE ORARI 24:00:00 ---
    # Convertiamo 24:00:00 in 23:59:59 (per evitare NaT)
    mask_24 = date_time_split['Time'] == '24:00:00'
    date_time_split.loc[mask_24, 'Time'] = '23:59:59'

    # Combiniamo data e ora con anno 2025
    datetime_str = '2025/' + date_time_split['Date'] + ' ' + date_time_split['Time']

    # Conversione in oggetto datetime completo (senza NaT)
    df['Datetime'] = pd.to_datetime(datetime_str, format='%Y/%m/%d %H:%M:%S', errors='coerce')

    # ============================================================
    # 🕓 AGGIUNTA COLONNA Hour_index
    # ============================================================
    # Ora base
    df['Hour_index'] = df['Datetime'].dt.hour

    # Per le righe che erano originariamente "24:00:00" assegna 24
    df.loc[mask_24, 'Hour_index'] = 24

    # ============================================================
    # 🧹 RIMOZIONE DELLA COLONNA ORIGINALE E RIORDINO
    # ============================================================
    df = df.drop(columns=[prima_colonna])
    df = df[['Datetime', 'Hour_index'] + [col for col in df.columns if col not in ['Datetime', 'Hour_index']]]

    # Elimina le prime 48 righe
    df = df.drop(index=df.index[:48]).reset_index(drop=True)
    return df

#------------------------------------------------------------------------------------------------------------


#QUESTA FUNZIONE CONTROLLA TUTTE LE COLONNE (ESCLUSE LE PRIME DUE DOVE SONO PRESENTI DATA ORA E INDICE ORARIO)
#E VERIFICA LA PRESENZA DI OUTLIERS CON IL METODO DELL'INTERQUARTILE
#MODIFICA IL TERMINE FALSE CON TRUE PER FAR FARE I BOX PLOT DI OGNI SINGOLA COLONNA
#RESTITUISCE LA COPIA DEL DATAFRAME PULITO CHIMATO df_clean

def correzione_outliers(df, plot_box=False):


    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    # ============================================================
    # 🔧 COEFFICIENTI IQR PERSONALIZZABILI
    # ============================================================
    iqr_lower_coeff = 1.5  # moltiplicatore per il lower bound
    iqr_upper_coeff = 1.5  # moltiplicatore per l'upper bound

    """
        plot_box: bool, se True disegna un box plot per ogni colonna
    """
    df_clean = df.copy()

    # Seleziona solo colonne numeriche escluse le prime 3
    cols_to_check = df_clean.columns[2:]

    for col in cols_to_check:
        # converte in numerico se necessario
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

        # calcolo IQR
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - iqr_lower_coeff * IQR
        upper_bound = Q3 + iqr_upper_coeff * IQR

        # individua outlier
        outliers = (df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)
        df_clean.loc[outliers, col] = np.nan

        # interpolazione lineare
        df_clean[col] = df_clean[col].interpolate(method='linear')
        df_clean[col] = df_clean[col].bfill().ffill()

        # box plot opzionale
        if plot_box:
            plt.figure(figsize=(10, 4))
            sns.boxplot(x=df_clean[col], color='lightblue', showfliers=False)
            plt.title(f'Box plot colonna {col}')
            plt.show()

    return df_clean








