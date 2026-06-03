import streamlit as st
import pandas as pd
import altair as alt

st.title("Dashboard Magazzino")

file = st.file_uploader("Carica file magazzino")

# ✅ Messaggio iniziale
if not file:
    st.info("📂 Carica il file CSV per l'analisi")

if file:
    df = pd.read_csv(file)

    # Calcoli
    df['vendite_giornaliere'] = df['vendite_30gg'] / 30
    df['giorni_copertura'] = df['stock'] / df['vendite_giornaliere'].replace(0, 0.01)

    # Decisioni
    def decisione(row):
        if row['vendite_30gg'] == 0 and row['stock'] > 0:
            return "🛑 Dismettere"
        elif row['giorni_copertura'] > 90:
            return "❗Troppo stock"
        elif row['giorni_copertura'] < 15:
            return "🔥 Riordinare"
        else:
            return "✅ OK"

    df['azione'] = df.apply(decisione, axis=1)

    # KPI
    totale_stock = df['stock'].sum()
    da_dismettere = df[df['azione'] == "🛑 Dismettere"].shape[0]
    troppo_stock = df[df['azione'] == "❗Troppo stock"].shape[0]
    da_riordinare = df[df['azione'] == "🔥 Riordinare"].shape[0]

    st.subheader("KPI principali")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Stock totale", totale_stock)
    col2.metric("Da dismettere", da_dismettere)
    col3.metric("Troppo stock", troppo_stock)
    col4.metric("Da riordinare", da_riordinare)

    # Tabella
    st.subheader("Analisi dettagliata")
    st.dataframe(df)

    # SEZIONI
    st.subheader("🛑 Prodotti da dismettere")
    df_dism = df[df['azione'] == "🛑 Dismettere"]
    st.dataframe(df_dism if not df_dism.empty else pd.DataFrame({"Info": ["✅ Nessun prodotto da dismettere"]}))

    st.subheader("❗ Prodotti con troppo stock")
    df_stock = df[df['azione'] == "❗Troppo stock"]
    st.dataframe(df_stock if not df_stock.empty else pd.DataFrame({"Info": ["✅ Stock sotto controllo"]}))

    st.subheader("🔥 Prodotti da riordinare")
    df_riord = df[df['azione'] == "🔥 Riordinare"]
    st.dataframe(df_riord if not df_riord.empty else pd.DataFrame({"Info": ["✅ Nessun riordino urgente"]}))

    # ========= GRAFICO CORRETTO =========
    st.subheader("📊 Top prodotti per vendite")

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('prodotto:N', sort='-y', title="Prodotto"),
        y=alt.Y('vendite_30gg:Q', title="Vendite ultimi 30gg"),
        tooltip=['prodotto', 'vendite_30gg']
    )

    st.altair_chart(chart, use_container_width=True)