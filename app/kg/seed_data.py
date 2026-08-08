"""
Seeds the Neo4j knowledge graph with sample Disease/Symptom/Medication/
Specialist nodes and relationships, matching Module 5 of the architecture.

Run this AFTER you have a real Neo4j instance running (see docker-compose.yml
in the project root) and NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD are set correctly
in your .env file.

Run: python3 -m app.kg.seed_data
"""
from app.kg.neo4j_client import get_driver, close_driver

SEED_CYPHER = """
MERGE (flu:Disease {name: 'Influenza'})
MERGE (fever:Symptom {name: 'Fever'})
MERGE (cough:Symptom {name: 'Cough'})
MERGE (bodyache:Symptom {name: 'Body Ache'})
MERGE (paracetamol:Medication {name: 'Paracetamol'})
MERGE (gp:Specialist {name: 'General Physician'})
MERGE (flu)-[:HAS_SYMPTOM]->(fever)
MERGE (flu)-[:HAS_SYMPTOM]->(cough)
MERGE (flu)-[:HAS_SYMPTOM]->(bodyache)
MERGE (flu)-[:TREATED_BY]->(paracetamol)
MERGE (flu)-[:REQUIRES_SPECIALIST]->(gp)

MERGE (cold:Disease {name: 'Common Cold'})
MERGE (runnynose:Symptom {name: 'Runny Nose'})
MERGE (sorethroat:Symptom {name: 'Sore Throat'})
MERGE (cold)-[:HAS_SYMPTOM]->(runnynose)
MERGE (cold)-[:HAS_SYMPTOM]->(sorethroat)
MERGE (cold)-[:HAS_SYMPTOM]->(cough)
MERGE (cold)-[:TREATED_BY]->(paracetamol)
MERGE (cold)-[:REQUIRES_SPECIALIST]->(gp)

MERGE (covid:Disease {name: 'COVID-19'})
MERGE (sob:Symptom {name: 'Shortness of Breath'})
MERGE (pulmonologist:Specialist {name: 'Pulmonologist'})
MERGE (covid)-[:HAS_SYMPTOM]->(fever)
MERGE (covid)-[:HAS_SYMPTOM]->(cough)
MERGE (covid)-[:HAS_SYMPTOM]->(sob)
MERGE (covid)-[:REQUIRES_SPECIALIST]->(pulmonologist)
MERGE (covid)-[:REQUIRES_SPECIALIST]->(gp)

MERGE (dengue:Disease {name: 'Dengue'})
MERGE (jointpain:Symptom {name: 'Joint Pain'})
MERGE (rash:Symptom {name: 'Rash'})
MERGE (dengue)-[:HAS_SYMPTOM]->(fever)
MERGE (dengue)-[:HAS_SYMPTOM]->(jointpain)
MERGE (dengue)-[:HAS_SYMPTOM]->(rash)
MERGE (dengue)-[:REQUIRES_SPECIALIST]->(gp)
"""


def seed():
    driver = get_driver()
    with driver.session() as session:
        session.run(SEED_CYPHER)
    print("Neo4j seeded with sample Disease/Symptom/Medication/Specialist graph.")
    close_driver()


if __name__ == "__main__":
    seed()
