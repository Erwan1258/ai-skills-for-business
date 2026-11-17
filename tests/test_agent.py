"""Tests de l'agent de cadrage, sans appel à un vrai LLM.

Lancement : pytest
"""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

import agent.tools as tools
from agent.graph import build_graph, run_config


@pytest.fixture(autouse=True)
def isolated_output_dirs(tmp_path, monkeypatch):
    """Les fichiers écrits par les tests vont dans un dossier temporaire."""
    monkeypatch.setattr(tools, "CADRAGES_DIR", tmp_path / "cadrages")
    monkeypatch.setattr(tools, "PROPOSED_SKILLS_DIR", tmp_path / "skills_proposes")
    monkeypatch.setattr(tools, "ROOT", tmp_path)
    return tmp_path


# ---------------------------------------------------------------- Outils
def test_lister_skills_trouve_les_4_skills():
    names = {s["name"] for s in tools.list_skills_impl()}
    assert names == {"compte-rendu-reunion", "reponse-reclamation", "synthese-reglementaire", "analyse-retours-clients"}


def test_lire_skill_inconnu_liste_les_skills_disponibles():
    result = tools.read_skill_impl("n-existe-pas")
    assert "introuvable" in result and "compte-rendu-reunion" in result


@pytest.mark.parametrize(
    ("notes", "total", "verdict"),
    [((5, 5, 4, 3), 17, "Candidat prioritaire"), ((3, 3, 3, 2), 11, "À approfondir"), ((1, 2, 2, 1), 6, "À écarter ou à repenser")],
)
def test_score_et_verdict(notes, total, verdict):
    result = tools.score_impl(*notes)
    assert result["total"] == total and result["verdict"] == verdict


def test_score_refuse_une_note_hors_bornes():
    assert "Erreur" in tools.calculer_score.invoke({"volume": 7, "gain_de_temps": 3, "faisabilite": 3, "faible_risque": 3})


def test_fiche_enregistree(isolated_output_dirs):
    path = tools.save_fiche_impl("Synthèse des retours agences", "# Fiche")
    assert path.parent == isolated_output_dirs / "cadrages"
    assert path.name.endswith("synthese-des-retours-agences.md")


def test_nouveau_skill_ecrit_un_en_tete_valide(isolated_output_dirs):
    path = tools.draft_skill_impl("Synthèse Hebdo Agences", "Compile les retours\n des agences.", "# Rôle\n...")
    content = path.read_text(encoding="utf-8")
    assert path == isolated_output_dirs / "skills_proposes" / "synthese-hebdo-agences" / "SKILL.md"
    assert tools.parse_frontmatter(content) == {
        "name": "synthese-hebdo-agences",
        "description": "Compile les retours des agences.",
    }


def test_nouveau_skill_ne_peut_pas_ecraser_un_skill_existant():
    assert "Erreur" in tools.proposer_nouveau_skill.invoke(
        {"nom": "compte-rendu-reunion", "description": "x", "instructions_markdown": "y"}
    )


# ---------------------------------------------------------------- Graphe complet avec un faux LLM
class ScriptedChatModel(BaseChatModel):
    """Faux modèle qui renvoie une suite de réponses prédéfinies (dont des appels d'outils)."""

    responses: list[AIMessage]
    calls: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedChatModel":
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        response = self.responses[self.calls]
        self.calls += 1
        return ChatResult(generations=[ChatGeneration(message=response)])


def test_parcours_complet_de_cadrage(isolated_output_dirs):
    llm = ScriptedChatModel(
        responses=[
            AIMessage("Combien de personnes font cette tâche, et à quelle fréquence ?"),
            AIMessage("", tool_calls=[{"name": "lister_skills", "args": {}, "id": "1"}]),
            AIMessage(
                "",
                tool_calls=[
                    {"name": "calculer_score", "args": {"volume": 4, "gain_de_temps": 4, "faisabilite": 5, "faible_risque": 4}, "id": "2"},
                    {"name": "enregistrer_fiche_cadrage", "args": {"titre": "Synthèse agences", "contenu_markdown": "# Fiche de cadrage"}, "id": "3"},
                ],
            ),
            AIMessage("Score 17/20 : candidat prioritaire. La fiche est enregistrée."),
        ]
    )
    graph = build_graph(llm)
    config = run_config("test")

    first = graph.invoke({"messages": [HumanMessage("Je compile les retours des agences chaque lundi.")]}, config)
    assert "fréquence" in first["messages"][-1].content

    final = graph.invoke({"messages": [HumanMessage("12 responsables, chaque semaine, 1 h.")]}, config)
    tool_results = [m.content for m in final["messages"] if isinstance(m, ToolMessage)]

    assert any("compte-rendu-reunion" in r for r in tool_results)
    assert any("17/20" in r for r in tool_results)
    assert len(list((isolated_output_dirs / "cadrages").glob("*synthese-agences.md"))) == 1
    assert final["messages"][-1].content.startswith("Score 17/20")
    # La mémoire de conversation conserve les deux échanges
    assert sum(isinstance(m, HumanMessage) for m in final["messages"]) == 2


def test_config_signale_une_cle_manquante(monkeypatch):
    from agent.config import ConfigError, get_llm

    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ConfigError, match="GROQ_API_KEY"):
        get_llm()


def test_config_ollama_sans_cle(monkeypatch):
    from agent.config import get_llm

    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    assert "11434" in str(get_llm().openai_api_base)
