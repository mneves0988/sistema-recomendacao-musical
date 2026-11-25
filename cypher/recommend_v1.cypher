// Baseline: number of shared tags.
MATCH (t:Track {track_id: $track_id})-[:PERFORMED_BY]->(original:Artist)
MATCH (t)-[:HAS_TAG]->(tag:Tag)<-[:HAS_TAG]-(rec:Track)-[:PERFORMED_BY]->(artist:Artist)
WHERE rec <> t AND artist <> original
WITH t, rec, artist, count(DISTINCT tag) AS shared_tags,
     collect(DISTINCT tag.name) AS explanation
RETURN rec.track_id AS track_id, rec.name AS track, artist.name AS artist,
       rec.spotify_id AS spotify_id, shared_tags, explanation,
       COUNT { (rec)-[:HAS_TAG]->(:Tag) } AS target_total
ORDER BY shared_tags DESC, track ASC, track_id ASC
LIMIT $limit;