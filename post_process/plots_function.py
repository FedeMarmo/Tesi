
#QUESTA FUNZIONE PRENDE IN INPUT IL DATAFRAME E UNA SERIE DI NOMI DI COLONNE DA PLOTTARE SU UN GRAFICO LINEARE
#L'UNITÀ DI MISURA VIENE ESTRATTA DAL NOME (FRA PARENTESI QUADRE) E VENGONO AUTOMATICAMENTE GESTITI PIù GIORNI
#PLOTTATI CON COLORI DIVERSI

def plot_lineare_multigiorno(df_clean, columns_to_plot):
    import matplotlib.pyplot as plt
    import pandas as pd
    import numpy as np
    import re

    """
    Crea grafici lineari delle colonne specificate del DataFrame, gestendo più giorni.

    Parametri:
        df_clean: pd.DataFrame già pulito, deve contenere le colonne 'Hour_index' e 'Datetime'
        columns_to_plot: lista di nomi delle colonne da graficare
    """
    # Assicurati che la colonna Datetime sia di tipo datetime
    if not pd.api.types.is_datetime64_any_dtype(df_clean['Datetime']):
        df_clean['Datetime'] = pd.to_datetime(df_clean['Datetime'])

    # Estrae la data senza ora per raggruppare i dati
    df_clean['Date_only'] = df_clean['Datetime'].dt.date

    for col in columns_to_plot:
        if col not in df_clean.columns:
            print(f"⚠️ Attenzione: la colonna '{col}' non esiste nel DataFrame.")
            continue

        # Estrae l'unità di misura fra parentesi quadre
        match = re.search(r'\[(.*?)\]', col)
        unit = match.group(1) if match else ''

        plt.figure(figsize=(12, 5))
        unique_dates = df_clean['Date_only'].unique()

        # Colori automatici differenti per ogni giorno
        colors = plt.cm.get_cmap('tab10', len(unique_dates))

        for i, date in enumerate(unique_dates):
            day_data = df_clean[df_clean['Date_only'] == date]
            plt.plot(day_data['Hour_index'], day_data[col],
                     marker='o', linestyle='-', color=colors(i), label=str(date))

        plt.title(f'Andamento di {col}')
        plt.xlabel('Ore')
        plt.ylabel(unit if unit else col)
        plt.grid(True)
        plt.legend(title='Data')
        plt.tight_layout()
        plt.show()




