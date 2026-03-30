import pandas as pd
import streamlit as st

from history_store import compute_kpis, load_history


st.title("Dashboard KPI - Détection de fraude")
st.caption("KPI basés sur l'historique des analyses effectuées dans l'application.")


def _detect_amount_column(df: pd.DataFrame) -> str:
    for col in ["Amount", "amount", "Montant", "montant"]:
        if col in df.columns:
            return col
    raise ValueError("Colonne montant introuvable (ex: Amount).")


def _detect_fraud_flag(df: pd.DataFrame) -> pd.Series:
    candidate = None
    for col in ["fraude_predite", "Class", "class", "fraud", "is_fraud"]:
        if col in df.columns:
            candidate = col
            break

    if candidate is None:
        raise ValueError("Colonne fraude introuvable (ex: Class ou fraude_predite).")

    series = df[candidate]

    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce").fillna(0).astype(int).clip(0, 1)

    normalized = (
        series.astype(str)
        .str.strip()
        .str.lower()
        .replace(
            {
                "true": "1",
                "false": "0",
                "fraude": "1",
                "fraud": "1",
                "légitime": "0",
                "legitime": "0",
                "legit": "0",
            }
        )
    )
    return normalized.isin(["1", "yes", "y", "oui", "o", "true", "fraude", "fraud"]).astype(int)


def _build_hour_column(df: pd.DataFrame) -> pd.Series:
    if "Time" in df.columns:
        time_num = pd.to_numeric(df["Time"], errors="coerce").fillna(0)
        return ((time_num // 3600) % 24).astype(int)
    return pd.Series(df.index % 24, index=df.index, dtype="int64")


entries = load_history()

if not entries:
    st.info("Aucune analyse enregistrée pour le moment. Lancez d'abord une prédiction.")
else:
    kpis = compute_kpis(entries)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Nombre analyses", f"{kpis['total_analyses']:,}".replace(",", " "))
    c2.metric("Transactions analysées", f"{kpis['total_transactions']:,}".replace(",", " "))
    c3.metric("Fraudes détectées", f"{kpis['total_frauds']:,}".replace(",", " "))
    c4.metric("Montant total bloqué (XOF)", f"{kpis['total_blocked_amount']:,.0f}".replace(",", " "))

    st.metric("Taux de fraude global (%)", f"{kpis['fraud_rate']:.2f}")

    history_df = pd.DataFrame(entries)
    history_df["date"] = pd.to_datetime(history_df["date"], errors="coerce")

    st.subheader("Fraudes détectées par jour")
    daily_frauds = (
        history_df.groupby(history_df["date"].dt.date, as_index=True)["frauds"]
        .sum()
        .rename("Fraudes")
        .to_frame()
    )
    st.bar_chart(daily_frauds)

    st.subheader("Transactions analysées par mode")
    by_mode = (
        history_df.groupby("mode", as_index=True)["total_transactions"]
        .sum()
        .rename("Transactions")
        .to_frame()
    )
    st.bar_chart(by_mode)

if st.session_state.get("csv_analysis") is not None:
    st.subheader("Détails de la dernière analyse (session courante)")
    latest_df = st.session_state["csv_analysis"]
    fraud_flag = _detect_fraud_flag(latest_df)
    amount_col = _detect_amount_column(latest_df)
    amount = pd.to_numeric(latest_df[amount_col], errors="coerce").fillna(0.0)
    hours = _build_hour_column(latest_df)

    total_transactions = int(len(latest_df))
    total_frauds = int(fraud_flag.sum())
    taux_fraude = (total_frauds / total_transactions * 100) if total_transactions else 0.0

    l1, l2, l3 = st.columns(3)
    l1.metric("Transactions session", total_transactions)
    l2.metric("Fraudes session", total_frauds)
    l3.metric("Taux session (%)", f"{taux_fraude:.2f}")

    st.subheader("Fraudes par heure (dernière analyse)")
    fraude_par_heure = (
        pd.DataFrame({"heure": hours, "fraude": fraud_flag})
        .query("fraude == 1")
        .groupby("heure")
        .size()
        .reindex(range(24), fill_value=0)
        .rename("Nombre de fraudes")
        .to_frame()
    )
    st.bar_chart(fraude_par_heure)

    st.subheader("Montant moyen fraude vs légitime (dernière analyse)")
    montant_moyen = (
        pd.DataFrame({"flag": fraud_flag, "amount": amount})
        .groupby("flag", as_index=False)["amount"]
        .mean()
    )
    montant_moyen["Type"] = montant_moyen["flag"].map({0: "LÉGITIME", 1: "FRAUDE"})
    montant_moyen = montant_moyen.set_index("Type")[["amount"]].rename(columns={"amount": "Montant moyen (XOF)"})
    st.bar_chart(montant_moyen)
