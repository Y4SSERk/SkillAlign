# tests/test_neo4j_connectivity.py
import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()


def test_neo4j_returns_one():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS x")
            record = result.single()
        assert record is not None
        assert record["x"] == 1
    finally:
        driver.close()
