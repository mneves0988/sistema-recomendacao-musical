// Connect tracks to deduplicated tag nodes.
UNWIND $rows AS row
MATCH (t:Track {track_id: row.track_id}), (tag:Tag {name: row.tag})
MERGE (t)-[:HAS_TAG]->(tag)
RETURN count(*) AS processed;
