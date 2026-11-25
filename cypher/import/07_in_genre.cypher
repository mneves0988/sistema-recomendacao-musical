// Only rows with a known genre are prepared.
UNWIND $rows AS row
MATCH (t:Track {track_id: row.track_id}), (g:Genre {name: row.genre})
MERGE (t)-[:IN_GENRE]->(g)
RETURN count(*) AS processed;
