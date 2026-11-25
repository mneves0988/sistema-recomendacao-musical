// Jaccard: shared tags / union of tags.
MATCH (t:Track {track_id: $track_id})-[:PERFORMED_BY]->(original:Artist)
MATCH (t)-[:HAS_TAG]->(tag:Tag)<-[:HAS_TAG]-(rec:Track)-[:PERFORMED_BY]->(artist:Artist)
WHERE rec <> t AND artist <> original
WITH t, rec, artist, count(DISTINCT tag) AS shared_tags,
     collect(DISTINCT tag.name) AS explanation
WITH rec, artist, shared_tags, explanation,
     COUNT { (t)-[:HAS_TAG]->(:Tag) } AS source_total,
     COUNT { (rec)-[:HAS_TAG]->(:Tag) } AS target_total
WITH rec, artist, shared_tags, explanation, target_total,
     toFloat(shared_tags)/(source_total + target_total - shared_tags) AS score
RETURN rec.track_id AS track_id, rec.name AS track, artist.name AS artist,
       rec.spotify_id AS spotify_id, shared_tags, explanation, target_total,
       round(score * 100, 2) AS tag_similarity
ORDER BY score DESC, shared_tags DESC, track ASC, track_id ASC
LIMIT $limit;