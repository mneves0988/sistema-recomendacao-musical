MATCH (t:Track)-[:PERFORMED_BY]->(:Artist {name: $artist})
RETURN t.track_id AS track_id, t.name AS track, t.year AS year,
       COUNT { (t)-[:HAS_TAG]->(:Tag) } AS total_tags
ORDER BY track, track_id;