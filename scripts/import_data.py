"""Load prepared CSVs into a NEW/empty Aura instance using parameterized Cypher."""
import argparse
import csv
import os
from pathlib import Path
from itertools import islice

from dotenv import load_dotenv
from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "cypher" / "import"
FLOAT_FIELDS = "danceability energy loudness speechiness acousticness instrumentalness liveness valence tempo".split()
INT_FIELDS = "year duration_ms key mode time_signature".split()
STEPS = [
    ("tracks.csv", "02_tracks.cypher"),
    ("artists.csv", "03_artists.cypher"),
    ("genres.csv", "04_genres.cypher"),
    ("tags.csv", "05_tags.cypher"),
    ("tracks.csv", "06_performed_by.cypher"),
    ("track_genres.csv", "07_in_genre.cypher"),
    ("track_tags.csv", "08_has_tag.cypher"),
]


def batches(path, size):
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        while batch := list(islice(reader, size)):
            yield batch


def typed_track(row):
    result = {k: row[k] for k in ("track_id", "name", "spotify_id")}
    result.update({k: float(row[k]) for k in FLOAT_FIELDS})
    result.update({k: int(row[k]) for k in INT_FIELDS})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    for name in {name for name, _ in STEPS}:
        if not (args.directory / name).is_file():
            parser.error(f"Missing file: {name}")
    load_dotenv(ROOT / ".env")
    uri, password = os.getenv("NEO4J_URI"), os.getenv("NEO4J_PASSWORD")
    if not uri or not password:
        parser.error("Set NEO4J_URI and NEO4J_PASSWORD in .env")
    with GraphDatabase.driver(uri, auth=(os.getenv("NEO4J_USERNAME", "neo4j"), password)) as driver:
        driver.verify_connectivity()
        with driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as session:
            # Avoid accidentally importing the full catalog a second time.
            if session.run("MATCH (n) RETURN count(n) AS total").single()["total"]:
                parser.error("Target is not empty. Use a separate empty database for this loader.")
            for query in (QUERIES / "01_constraints.cypher").read_text().split(";"):
                if query.strip():
                    session.run(query).consume()
            for filename, script in STEPS:
                query = (QUERIES / script).read_text(encoding="utf-8")
                count = 0
                for rows in batches(args.directory / filename, args.batch_size):
                    if script == "02_tracks.cypher":
                        rows = [typed_track(row) for row in rows]
                    elif script == "06_performed_by.cypher":
                        rows = [{"track_id": row["track_id"], "artist": row["artist"]} for row in rows]
                    processed = session.execute_write(lambda tx: tx.run(query, rows=rows).single()["processed"])
                    if processed != len(rows):
                        raise RuntimeError(f"{script}: expected {len(rows)} rows, matched {processed}")
                    count += processed
                print(f"{script}: {count:,} rows")
    print("Import completed. Run cypher/validate.cypher to confirm counts.")


if __name__ == "__main__":
    main()
