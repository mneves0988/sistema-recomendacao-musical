// Connect tracks to existing artists by stable identifiers.
UNWIND $rows AS row
MATCH (t:Track {track_id: row.track_id}), (a:Artist {name: row.artist})
MERGE (t)-[:PERFORMED_BY]->(a)
RETURN count(*) AS processed;
