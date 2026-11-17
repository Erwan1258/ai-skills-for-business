"""Page Streamlit : discuter avec l'agent de cadrage de cas d'usage IA."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage  # noqa: E402

from agent.config import ConfigError, provider_name  # noqa: E402
from agent.graph import build_graph, run_config  # noqa: E402
from agent.prompts import WELCOME_MESSAGE  # noqa: E402

TOOL_LABELS = {
    "lister_skills": "📚 Consultation des skills existants",
    "lire_skill": "📖 Lecture d'un skill",
    "calculer_score": "🧮 Calcul du score de priorisation",
    "enregistrer_fiche_cadrage": "📝 Enregistrement de la fiche de cadrage",
    "proposer_nouveau_skill": "✨ Rédaction d'un nouveau skill",
}

st.set_page_config(page_title="Agent de cadrage", page_icon="💬", layout="centered")
st.title("💬 Agent de cadrage de cas d'usage IA")
st.caption("Décrivez une tâche pénible : l'agent l'analyse, la score et propose une solution IA.")


@st.cache_resource(show_spinner=False)
def get_graph():
    return build_graph()


try:
    graph = get_graph()
except ConfigError as err:
    st.error(f"⚙️ {err}")
    st.info("Copiez `.env.example` en `.env`, choisissez un fournisseur gratuit et ajoutez votre clé, puis relancez l'application.")
    st.stop()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.history = []  # [(role, contenu, étapes d'outils)]
    st.session_state.files = []

with st.sidebar:
    st.markdown(f"**Modèle :** `{provider_name()}`")
    if st.button("🔄 Nouvelle conversation"):
        for key in ("thread_id", "history", "files"):
            st.session_state.pop(key, None)
        st.rerun()
    if st.session_state.files:
        st.markdown("**📁 Fichiers créés**")
        for rel_path in st.session_state.files:
            path = ROOT / rel_path
            if path.exists():
                st.download_button(f"⬇️ {path.name}", path.read_bytes(), file_name=path.name, key=rel_path)

with st.chat_message("assistant"):
    st.markdown(WELCOME_MESSAGE)

for role, content, steps in st.session_state.history:
    with st.chat_message(role):
        if steps:
            with st.expander(f"🔧 {len(steps)} action(s) de l'agent"):
                for step in steps:
                    st.markdown(f"- {step}")
        st.markdown(content)

if prompt := st.chat_input("Décrivez votre tâche…"):
    st.session_state.history.append(("user", prompt, []))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        steps: list[str] = []
        answer = ""
        with st.status("L'agent réfléchit…", expanded=False) as status:
            try:
                for update in graph.stream(
                    {"messages": [HumanMessage(prompt)]},
                    run_config(st.session_state.thread_id),
                    stream_mode="updates",
                ):
                    for node, payload in update.items():
                        for msg in payload.get("messages", []):
                            if isinstance(msg, AIMessage) and msg.tool_calls:
                                for call in msg.tool_calls:
                                    label = TOOL_LABELS.get(call["name"], call["name"])
                                    status.update(label=label + "…")
                            elif isinstance(msg, ToolMessage):
                                result = str(msg.content)
                                steps.append(f"{TOOL_LABELS.get(msg.name, msg.name)} → {result.splitlines()[0][:140]}")
                                for marker in ("Fiche enregistrée : ", "Brouillon de skill créé : "):
                                    if result.startswith(marker):
                                        st.session_state.files.append(result[len(marker):].split(" ")[0])
                            elif isinstance(msg, AIMessage) and node == "agent":
                                answer = str(msg.content)
                status.update(label=f"Terminé · {len(steps)} action(s)", state="complete")
            except Exception as err:  # erreur réseau, quota, modèle sans appel d'outils…
                status.update(label="Erreur", state="error")
                answer = f"⚠️ Erreur lors de l'appel au modèle : `{err}`"
        if steps:
            with st.expander(f"🔧 {len(steps)} action(s) de l'agent"):
                for step in steps:
                    st.markdown(f"- {step}")
        st.markdown(answer)
    st.session_state.history.append(("assistant", answer, steps))
    if steps:
        st.rerun()  # rafraîchit la liste des fichiers créés dans la barre latérale
