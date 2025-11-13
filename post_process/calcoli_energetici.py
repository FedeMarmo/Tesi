import pandas as pd
import matplotlib.pyplot as plt
import re


def rebound_energy(df_rif_clean, df_clean, colonna_da_analizzare):
    """
    Confronta i consumi energetici tra due DataFrame (con e senza DR)
    in una fascia oraria scelta dall'utente per valutare il calo e il rebound di potenza.

    Parametri:
        df_clean: DataFrame con la simulazione DR (Demand Response)
        df_rif_clean: DataFrame di riferimento (senza DR)
        colonna_da_analizzare: nome della colonna (identica in entrambi i DataFrame)

    Output:
        - Stampa a schermo i valori calo_potenza_DR e aumento_rebound_DR
        - Mostra un grafico comparativo dell’intero giorno scelto
    """

    # --- Controllo che la colonna Datetime sia nel formato datetime ---
    for df in [df_clean, df_rif_clean]:
        if not pd.api.types.is_datetime64_any_dtype(df['Datetime']):
            df['Datetime'] = pd.to_datetime(df['Datetime'])

    # --- Identificazione dei giorni disponibili ---
    unique_dates = df_clean['Datetime'].dt.date.unique()

    if len(unique_dates) > 1:
        print("📅 Sono stati trovati dati per più giorni:")
        for d in unique_dates:
            print(f"  - {d.strftime('%m/%d')}")

        data_scelta = input("👉 Inserisci la data da considerare (formato MM/DD): ")
    else:
        data_scelta = unique_dates[0].strftime("%m/%d")
        print(f"✅ Dati disponibili per un solo giorno ({data_scelta})")

    ora_inizio = input("⏰ Inserisci l’ora di inizio del DR (es. 06:00): ")
    ora_fine = input("⏰ Inserisci l’ora di fine del DR (es. 08:00): ")

    # --- Conversioni ---
    mese, giorno = map(int, data_scelta.split('/'))
    data_filtrata = None
    for d in unique_dates:
        if d.month == mese and d.day == giorno:
            data_filtrata = d
            break

    if data_filtrata is None:
        print("⚠️ Data non trovata nei dati. Nessuna analisi eseguita.")
        return

    ora_inizio = pd.to_datetime(ora_inizio, format='%H:%M').time()
    ora_fine = pd.to_datetime(ora_fine, format='%H:%M').time()

    # --- Filtraggio per la data selezionata ---
    df_day = df_clean[df_clean['Datetime'].dt.date == data_filtrata].copy()
    df_rif_day = df_rif_clean[df_rif_clean['Datetime'].dt.date == data_filtrata].copy()

    # --- Conversione colonne a valori numerici ---
    df_day[colonna_da_analizzare] = pd.to_numeric(df_day[colonna_da_analizzare], errors='coerce')
    df_rif_day[colonna_da_analizzare] = pd.to_numeric(df_rif_day[colonna_da_analizzare], errors='coerce')

    # --- Creazione maschere temporali ---
    mask_DR = (
            (df_day['Datetime'].dt.time >= ora_inizio) &
            (df_day['Datetime'].dt.time <= ora_fine)
    )

    ore_rebound = 4  # ⏱️ numero di ore successive da considerare per l'analisi del rebound
    ora_fine_rebound = (pd.Timestamp.combine(pd.Timestamp.today(), ora_fine) + pd.Timedelta(hours=ore_rebound)).time()


    mask_rebound = (
            (df_day['Datetime'].dt.time > ora_fine) &
            (df_day['Datetime'].dt.time <= ora_fine_rebound)
    )

    # --- Calcolo calo potenza (durante DR) ---
    potenza_DR = df_day.loc[mask_DR, colonna_da_analizzare].mean()
    potenza_rif = df_rif_day.loc[mask_DR, colonna_da_analizzare].mean()
    calo_potenza_DR = potenza_rif - potenza_DR

    # --- Calcolo rebound potenza media (4h successive) ---
    potenza_reb_DR = df_day.loc[mask_rebound, colonna_da_analizzare].mean()
    potenza_reb_rif = df_rif_day.loc[mask_rebound, colonna_da_analizzare].mean()
    aumento_rebound_DR = potenza_reb_DR - potenza_reb_rif

    # --- Calcolo energia durante DR e rebound (integrazione punto per punto) ---
    # 1️⃣ Energia risparmiata durante DR
    df_DR_DR = df_day.loc[mask_DR, ['Datetime', colonna_da_analizzare]].copy()
    df_DR_rif = df_rif_day.loc[mask_DR, ['Datetime', colonna_da_analizzare]].copy()
    df_DR = pd.merge(df_DR_DR, df_DR_rif, on='Datetime', suffixes=('_DR', '_rif'))
    df_DR['delta_potenza'] = df_DR[f'{colonna_da_analizzare}_DR'] - df_DR[f'{colonna_da_analizzare}_rif']
    delta_t_ore = (df_DR['Datetime'].diff().dt.total_seconds().mean()) / 3600
    energia_risparmiata = abs(df_DR['delta_potenza'].sum() * delta_t_ore)

    # 2️⃣ Energia in eccesso (rebound)
    df_reb_DR = df_day.loc[mask_rebound, ['Datetime', colonna_da_analizzare]].copy()
    df_reb_rif = df_rif_day.loc[mask_rebound, ['Datetime', colonna_da_analizzare]].copy()
    df_reb = pd.merge(df_reb_DR, df_reb_rif, on='Datetime', suffixes=('_DR', '_rif'))
    df_reb['delta_potenza'] = df_reb[f'{colonna_da_analizzare}_DR'] - df_reb[f'{colonna_da_analizzare}_rif']
    delta_t_reb_ore = (df_reb['Datetime'].diff().dt.total_seconds().mean()) / 3600
    energia_rebound = df_reb['delta_potenza'].sum() * delta_t_reb_ore

    # --- Stampa risultati ---
    print(f"\n📊 Analisi flessibilità energetica ({data_filtrata.strftime('%m/%d')})")
    print(f"Fascia DR: {ora_inizio} - {ora_fine}")
    print(f"⏬ Calo di potenza medio durante il DR: {calo_potenza_DR:.2f}")
    print(f"⏫ Aumento medio di potenza nel rebound (4h): {aumento_rebound_DR:.2f}")
    print(f"🔹 Energia risparmiata durante DR: {energia_risparmiata:.2f} kWh")
    print(f"🔹 Energia in eccesso nel rebound: {energia_rebound:.2f} kWh")
    print(f"⚖️ Bilancio netto (DR - rebound): {(energia_risparmiata - energia_rebound):.2f} kWh")

    # --- Estrazione unità di misura dal nome della colonna ---
    match = re.search(r'\[(.*?)\]', colonna_da_analizzare)
    unita = match.group(1) if match else ""

    # --- Grafico comparativo ---
    plt.figure(figsize=(12, 6))
    plt.plot(df_day['Hour_index'], df_day[colonna_da_analizzare], label='Con DR', color='tab:blue', linewidth=2)
    plt.plot(df_rif_day['Hour_index'], df_rif_day[colonna_da_analizzare], label='Riferimento', color='tab:orange',
             linestyle='--', linewidth=2)
    plt.title(f"Confronto giornaliero {data_filtrata.strftime('%m/%d')} - {colonna_da_analizzare}")
    plt.xlabel("Ore [h]")
    plt.ylabel(f"Potenza [{unita}]")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

    return calo_potenza_DR, aumento_rebound_DR, energia_risparmiata, energia_rebound
