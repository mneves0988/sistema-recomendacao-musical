// Hybrid ranking: graph-based Jaccard + normalized audio features.
MATCH (t:Track {track_id: $track_id})-[:PERFORMED_BY]->(original:Artist)
MATCH (t)-[:HAS_TAG]->(tag:Tag)<-[:HAS_TAG]-(rec:Track)-[:PERFORMED_BY]->(artist:Artist)
WHERE rec <> t AND artist <> original
WITH t, rec, artist, count(DISTINCT tag) AS shared,
     collect(DISTINCT tag.name) AS common_tags
WITH t, rec, artist, shared, common_tags,
     COUNT { (t)-[:HAS_TAG]->(:Tag) } AS source_total,
     COUNT { (rec)-[:HAS_TAG]->(:Tag) } AS target_total
WITH t, rec, artist, shared, common_tags, target_total,
     toFloat(shared)/(source_total + target_total - shared) AS jaccard
WITH rec, artist, shared, common_tags, target_total, jaccard,
     1.0 - (abs(t.energy-rec.energy) + abs(t.danceability-rec.danceability)
     + abs(t.valence-rec.valence) + abs(t.acousticness-rec.acousticness)
     + abs(t.instrumentalness-rec.instrumentalness))/5.0 AS audio_similarity
WHERE audio_similarity IS NOT NULL
WITH rec, artist, shared, common_tags, target_total, jaccard, audio_similarity,
     $tag_weight*jaccard + (1.0-$tag_weight)*audio_similarity AS final_score
RETURN rec.track_id AS track_id, rec.name AS track, artist.name AS artist,
       rec.spotify_id AS spotify_id, shared AS shared_tags,
       target_total, round(jaccard*100,2) AS tag_similarity,
       round(audio_similarity*100,2) AS audio_similarity,
       round(final_score*100,2) AS hybrid_score, common_tags AS explanation
ORDER BY final_score DESC, shared_tags DESC, track_id ASC
LIMIT $limit;