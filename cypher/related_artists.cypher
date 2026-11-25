// Compare the union of tags across the tracks of each artist.
MATCH (a:Artist {name: $artist})<-[:PERFORMED_BY]-(:Track)-[:HAS_TAG]->(tag:Tag)
WITH a, collect(DISTINCT tag) AS source_tags
UNWIND source_tags AS tag
MATCH (tag)<-[:HAS_TAG]-(:Track)-[:PERFORMED_BY]->(related:Artist)
WHERE related <> a
WITH related, source_tags, collect(DISTINCT tag) AS common_tags
MATCH (related)<-[:PERFORMED_BY]-(:Track)-[:HAS_TAG]->(other_tag:Tag)
WITH related, source_tags, common_tags, count(DISTINCT other_tag) AS target_total
WITH related, common_tags, target_total, size(source_tags) AS source_total,
     toFloat(size(common_tags))/(size(source_tags)+target_total-size(common_tags)) AS similarity
RETURN related.name AS artist, size(common_tags) AS shared_tags,
       source_total, target_total, round(similarity*100,2) AS similarity_pct,
       [tag IN common_tags | tag.name] AS explanation
ORDER BY similarity DESC, shared_tags DESC, artist ASC
LIMIT $limit;