"""Tableau de bord de suivi de l'adoption des skills IA.

Lancement : streamlit run dashboard/app.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SKILL_LABELS = {
    "compte-rendu-reunion": "📝 Compte rendu de réunion",
    "reponse-reclamation": "✉️ Réponse à une réclamation",
    "synthese-reglementaire": "📚 Synthèse réglementaire",
    "analyse-retours-clients": "📊 Analyse de retours clients",
}
SATISFACTION_TARGET = 4.0

st.set_page_config(page_title="Adoption des skills IA", page_icon="🧠", layout="wide")


REQUIRED_COLUMNS = ["date", "user_id", "direction", "skill", "satisfaction", "minutes_gagnees", "commentaire"]
FEEDBACK_FILE = DATA_DIR / "feedback.csv"
DIRECTIONS = ["Banque de détail", "Conformité", "Finance", "Marketing", "Opérations", "RH"]


def prepare(usage: pd.DataFrame) -> pd.DataFrame:
    """Vérifie le format et ajoute les colonnes calculées."""
    missing = [c for c in REQUIRED_COLUMNS if c not in usage.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes : {', '.join(missing)}")
    usage = usage[REQUIRED_COLUMNS].copy()
    usage["date"] = pd.to_datetime(usage["date"], errors="coerce")
    usage["satisfaction"] = pd.to_numeric(usage["satisfaction"], errors="coerce")
    usage["minutes_gagnees"] = pd.to_numeric(usage["minutes_gagnees"], errors="coerce").fillna(0)
    usage = usage.dropna(subset=["date", "user_id", "skill", "satisfaction"])
    usage["commentaire"] = usage["commentaire"].fillna("").astype(str)
    usage["skill_label"] = usage["skill"].map(SKILL_LABELS).fillna(usage["skill"])
    usage["semaine"] = usage["date"].dt.to_period("W-SUN").dt.start_time
    return usage


@st.cache_data
def load_demo() -> tuple[pd.DataFrame, pd.DataFrame]:
    usage = pd.read_csv(DATA_DIR / "usage.csv")
    users = pd.read_csv(DATA_DIR / "users.csv")
    return usage, users


def load_feedback() -> pd.DataFrame:
    if FEEDBACK_FILE.exists():
        return pd.read_csv(FEEDBACK_FILE)
    return pd.DataFrame(columns=REQUIRED_COLUMNS)


def save_feedback(row: dict) -> None:
    pd.DataFrame([row], columns=REQUIRED_COLUMNS).to_csv(
        FEEDBACK_FILE, mode="a", header=not FEEDBACK_FILE.exists(), index=False
    )


# ---------------------------------------------------------------- Source de données
st.sidebar.header("📂 Données")
source = st.sidebar.radio("Source", ["Données de démonstration", "Importer mes fichiers CSV"])
users: pd.DataFrame | None = None

if source == "Données de démonstration":
    try:
        raw_usage, users = load_demo()
    except FileNotFoundError:
        st.error("Données introuvables. Lancez d'abord : `python data/generate_usage.py`")
        st.stop()
    st.sidebar.caption("⚠️ Données fictives générées à des fins de démonstration.")
else:
    usage_file = st.sidebar.file_uploader("Fichier d'usage (obligatoire)", type="csv")
    users_file = st.sidebar.file_uploader(
        "Liste des collaborateurs ciblés (facultatif)", type="csv",
        help="Colonnes : user_id, direction. Sert à calculer le taux d'adoption.",
    )
    st.sidebar.download_button(
        "⬇️ Télécharger le modèle CSV",
        data=(DATA_DIR / "modele_usage.csv").read_bytes(),
        file_name="modele_usage.csv",
        mime="text/csv",
    )
    if usage_file is None:
        st.title("🧠 Adoption des skills IA")
        st.info(
            "Importez un fichier CSV d'usage dans le panneau de gauche. "
            f"Colonnes attendues : `{', '.join(REQUIRED_COLUMNS)}`. "
            "Téléchargez le modèle pour voir le format."
        )
        st.stop()
    raw_usage = pd.read_csv(usage_file)
    if users_file is not None:
        users = pd.read_csv(users_file)
        if not {"user_id", "direction"} <= set(users.columns):
            st.sidebar.error("La liste des collaborateurs doit contenir les colonnes user_id et direction.")
            users = None

include_feedback = st.sidebar.toggle("Inclure les feedbacks saisis dans l'appli", value=True)
frames = [raw_usage]
feedback = load_feedback()
if include_feedback and not feedback.empty:
    frames.append(feedback)

try:
    usage = prepare(pd.concat(frames, ignore_index=True))
except ValueError as err:
    st.error(f"Fichier invalide. {err}")
    st.stop()

if usage.empty:
    st.warning("Le fichier ne contient aucune ligne exploitable.")
    st.stop()

# ---------------------------------------------------------------- Formulaire de feedback
with st.sidebar.expander("➕ Donner un feedback", expanded=False):
    with st.form("feedback", clear_on_submit=True):
        f_user = st.text_input("Identifiant (facultatif)", placeholder="ex. matricule")
        f_direction = st.selectbox("Direction", DIRECTIONS)
        f_skill = st.selectbox("Skill utilisé", list(SKILL_LABELS), format_func=SKILL_LABELS.get)
        f_note = st.slider("Satisfaction", 1, 5, 4)
        f_minutes = st.number_input("Temps gagné (minutes)", min_value=0, max_value=480, value=15, step=5)
        f_comment = st.text_area("Commentaire", placeholder="Ce qui a bien marché, ce qui manquait…")
        if st.form_submit_button("Envoyer", type="primary"):
            save_feedback(
                {
                    "date": pd.Timestamp.today().normalize().date().isoformat(),
                    "user_id": f_user.strip() or "anonyme",
                    "direction": f_direction,
                    "skill": f_skill,
                    "satisfaction": f_note,
                    "minutes_gagnees": f_minutes,
                    "commentaire": f_comment.strip(),
                }
            )
            st.toast("Merci ! Votre feedback a été ajouté au tableau de bord. ✅")
            st.rerun()
    st.caption(f"{len(feedback)} feedback(s) saisi(s) dans l'appli.")

# ---------------------------------------------------------------- Filtres
st.sidebar.header("🔎 Filtres")
min_d, max_d = usage["date"].min().date(), usage["date"].max().date()
periode = st.sidebar.date_input("Période", (min_d, max_d), min_value=min_d, max_value=max_d)
directions = st.sidebar.multiselect("Directions", sorted(usage["direction"].astype(str).unique()))
skills = st.sidebar.multiselect(
    "Skills", sorted(usage["skill"].unique()), format_func=lambda s: SKILL_LABELS.get(s, s)
)

df = usage
if isinstance(periode, tuple) and len(periode) == 2:
    df = df[(df["date"].dt.date >= periode[0]) & (df["date"].dt.date <= periode[1])]
if directions:
    df = df[df["direction"].isin(directions)]
if skills:
    df = df[df["skill"].isin(skills)]

st.title("🧠 Adoption des skills IA")
st.caption("Suivi du déploiement de l'IA générative auprès des collaborateurs non-développeurs")

if df.empty:
    st.warning("Aucune donnée pour ces filtres.")
    st.stop()

# ---------------------------------------------------------------- KPI
last_week = df["semaine"].max()
active_last_4w = df[df["semaine"] > last_week - pd.Timedelta(weeks=4)]["user_id"].nunique()
active_prev_4w = df[
    (df["semaine"] <= last_week - pd.Timedelta(weeks=4))
    & (df["semaine"] > last_week - pd.Timedelta(weeks=8))
]["user_id"].nunique()
if users is not None:
    eligible = users if not directions else users[users["direction"].isin(directions)]
    adoption = f"{df['user_id'].nunique() / max(len(eligible), 1):.0%}"
else:
    adoption = "—"

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(
    "Utilisateurs actifs (4 sem.)",
    f"{active_last_4w}",
    f"{active_last_4w - active_prev_4w:+d} vs 4 sem. préc.",
)
c2.metric("Taux d'adoption", adoption, help="Collaborateurs ayant utilisé au moins un skill / population cible (nécessite la liste des collaborateurs)")
c3.metric("Utilisations", f"{len(df):,}".replace(",", " "))
c4.metric("Satisfaction moyenne", f"{df['satisfaction'].mean():.2f} / 5")
c5.metric("Temps gagné estimé", f"{df['minutes_gagnees'].sum() / 60:,.0f} h".replace(",", " "))

st.divider()

# ---------------------------------------------------------------- Courbe d'adoption
left, right = st.columns([3, 2])
with left:
    st.subheader("📈 Courbe d'adoption")
    weekly = (
        df.groupby("semaine")
        .agg(utilisateurs_actifs=("user_id", "nunique"), utilisations=("user_id", "size"))
        .reset_index()
    )
    fig = px.line(
        weekly,
        x="semaine",
        y="utilisateurs_actifs",
        markers=True,
        labels={"semaine": "Semaine", "utilisateurs_actifs": "Utilisateurs actifs"},
    )
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("🧩 Usage par skill")
    by_skill = df["skill_label"].value_counts().rename_axis("Skill").reset_index(name="Utilisations")
    fig = px.bar(by_skill, x="Utilisations", y="Skill", orientation="h")
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), yaxis={"categoryorder": "total ascending"}, yaxis_title=None)
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- Directions & satisfaction
left, right = st.columns(2)
with left:
    st.subheader("🏢 Adoption par direction")
    by_dir = (
        df.groupby(["direction", "skill_label"]).size().reset_index(name="Utilisations")
    )
    fig = px.bar(
        by_dir,
        x="direction",
        y="Utilisations",
        color="skill_label",
        labels={"direction": "", "skill_label": "Skill"},
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("⭐ Satisfaction par skill (mensuelle)")
    sat = (
        df.assign(mois=df["date"].dt.to_period("M").dt.start_time)
        .groupby(["mois", "skill_label"])["satisfaction"]
        .mean()
        .reset_index()
    )
    fig = px.line(
        sat,
        x="mois",
        y="satisfaction",
        color="skill_label",
        markers=True,
        labels={"mois": "", "satisfaction": "Satisfaction /5", "skill_label": "Skill"},
    )
    fig.add_hline(y=SATISFACTION_TARGET, line_dash="dash", annotation_text="Objectif")
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), yaxis_range=[1, 5], legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- Points d'attention
st.subheader("🚦 Points d'attention")
recent = df[df["semaine"] > last_week - pd.Timedelta(weeks=4)]
summary = (
    recent.groupby("skill_label")
    .agg(satisfaction=("satisfaction", "mean"), utilisations=("user_id", "size"), utilisateurs=("user_id", "nunique"))
    .reset_index()
)
alerts = []
for row in summary.itertuples():
    if row.satisfaction < SATISFACTION_TARGET:
        alerts.append(f"🔴 **{row.skill_label}** : satisfaction de {row.satisfaction:.2f}/5 sur les 4 dernières semaines, sous l'objectif. Analyser les retours et itérer sur le skill.")
low_dirs = pd.Series(dtype=float)
if users is not None:
    low_dirs = (
        recent.groupby("direction")["user_id"].nunique()
        / users.groupby("direction")["user_id"].nunique()
    ).dropna().sort_values()
if not low_dirs.empty and low_dirs.iloc[0] < 0.6:
    alerts.append(f"🟠 **{low_dirs.index[0]}** : seulement {low_dirs.iloc[0]:.0%} des collaborateurs actifs récemment. Prévoir un atelier ou un relais dans la communauté.")
if alerts:
    for a in alerts:
        st.markdown(a)
else:
    st.success("Tous les indicateurs sont au vert sur les 4 dernières semaines.")

# ---------------------------------------------------------------- Retours qualitatifs
st.subheader("💬 Retours des utilisateurs")
comments = df[df["commentaire"] != ""].sort_values("date", ascending=False)
tab_neg, tab_pos = st.tabs(["À améliorer 👎", "Points forts 👍"])
cols = {"date": "Date", "direction": "Direction", "skill_label": "Skill", "satisfaction": "Note", "commentaire": "Commentaire"}
with tab_neg:
    st.dataframe(
        comments[comments["satisfaction"] <= 3][list(cols)].rename(columns=cols).head(50),
        hide_index=True,
        width="stretch",
    )
with tab_pos:
    st.dataframe(
        comments[comments["satisfaction"] >= 4][list(cols)].rename(columns=cols).head(50),
        hide_index=True,
        width="stretch",
    )

top = comments[comments["satisfaction"] <= 3]["commentaire"].value_counts().head(3)
if not top.empty:
    st.markdown("**Irritants les plus cités :** " + " · ".join(f"« {c} » ({n})" for c, n in top.items()))
