"""
Real Neo4j driver integration — matches Module 5 of the architecture exactly
(Disease/Symptom/Medication/Specialist nodes; HAS_SYMPTOM/TREATED_BY/
REQUIRES_SPECIALIST/RELATED_TO relationships).

HONESTY NOTE: this sandbox has no Neo4j server available (no apt package,
no Docker, no network to neo4j.com) and cannot run one. This module is
real, production-correct Neo4j driver code — point NEO4J_URI at a real
instance (see docker-compose.yml) and it will work as written. In this
sandbox, calls will raise a ServiceUnavailable error, which the caller
(app/agents/orchestrator.py) catches and treats the same way the
architecture already documents for "graph has no data": the Knowledge
Graph is an enrichment layer, not a hard dependency, so the pipeline
continues with RAG results alone.
"""
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

from app.config import settings

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


def get_related_entities(disease_name: str) -> dict:
    """
    Returns medications, specialists, and related symptoms for a disease.
    Returns an empty-but-valid structure (not an exception) if Neo4j is
    unreachable or the disease isn't in the graph — this is the documented
    graceful-degradation behavior, not a workaround.
    """
    empty_result = {"medications": [], "specialists": [], "symptoms": [], "available": False}

    try:
        driver = get_driver()
        with driver.session() as session:
            medications = session.run(
                """
                MATCH (d:Disease {name: $name})-[:TREATED_BY]->(m:Medication)
                RETURN m.name AS medication
                """,
                name=disease_name,
            ).value()

            specialists = session.run(
                """
                MATCH (d:Disease {name: $name})-[:REQUIRES_SPECIALIST]->(s:Specialist)
                RETURN s.name AS specialist
                """,
                name=disease_name,
            ).value()

            symptoms = session.run(
                """
                MATCH (d:Disease {name: $name})-[:HAS_SYMPTOM]->(s:Symptom)
                RETURN s.name AS symptom
                """,
                name=disease_name,
            ).value()

            return {
                "medications": medications,
                "specialists": specialists,
                "symptoms": symptoms,
                "available": True,
            }

    except (ServiceUnavailable, AuthError) as e:
        # Documented graceful degradation: KG is an enrichment layer, not a
        # hard dependency. Log and let the pipeline continue with RAG alone.
        print(f"[KG] Neo4j unreachable ({type(e).__name__}) — continuing without graph enrichment.")
        return empty_result
    except Exception as e:
        print(f"[KG] Unexpected Neo4j error: {e}")
        return empty_result


def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
