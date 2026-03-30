from pathlib import Path

import streamlit as st

from history_store import compute_kpis, load_history


st.set_page_config(page_title="AfriBank - Détection de fraude", layout="wide")


def apply_navy_white_theme():
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #FFFFFF;
                color: #001F3F;
            }

            h1, h2, h3, h4, h5, h6, p, label, span {
                color: #001F3F;
            }

            [data-testid="stSidebar"] {
                background-color: #001F3F;
            }

            [data-testid="stSidebar"] * {
                color: #FFFFFF !important;
            }

            div[data-testid="stMetric"] {
                background-color: #FFFFFF;
                border: 1px solid rgba(0, 31, 63, 0.2);
                border-radius: 12px;
                padding: 10px;
            }

            div.stAlert {
                border-left: 4px solid #001F3F;
            }

            div.stButton > button {
                background-color: #001F3F;
                color: #FFFFFF;
                border: 1px solid #001F3F;
                border-radius: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    apply_navy_white_theme()

    logo_path = Path(__file__).resolve().parent / "image.jpg"

    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), width=110)
    with col_title:
        st.title("AfriBank")
        st.caption("Plateforme de détection de fraude bancaire")

    entries = load_history()
    kpis = compute_kpis(entries)

    st.markdown("### Tableau de bord")

    c1, c2, c3 = st.columns(3)
    c1.metric("Analyses effectuées", f"{kpis['total_analyses']:,}".replace(",", " "))
    c2.metric("Transactions analysées", f"{kpis['total_transactions']:,}".replace(",", " "))
    c3.metric("Fraudes détectées", f"{kpis['total_frauds']:,}".replace(",", " "))

    s1, s2 = st.columns(2)
    s1.metric("Montant total bloqué (XOF)", f"{kpis['total_blocked_amount']:,.0f}".replace(",", " "))
    s2.metric("Taux de fraude", f"{kpis['fraud_rate']:.3f}%")

    if not entries:
        st.info(
            "Le tableau de bord est vide pour le moment. "
            "Les indicateurs apparaîtront après vos premières prédictions (mode manuel ou CSV)."
        )
    else:
        st.success("Historique chargé avec succès.")
        st.caption(f"Dernière mise à jour: {entries[-1].get('timestamp', 'N/A')}")

    st.markdown(
        """
        ### Description
        AfriBank est un outil d'aide à la détection de transactions frauduleuses.
        Les KPI affichés ici sont calculés à partir de l'historique des analyses réalisées dans l'application.
        """
    )

    st.success("Utilisez le menu de gauche pour accéder aux modules de prédiction, performance et dashboard KPI.")


if __name__ == "__main__":
    main()
