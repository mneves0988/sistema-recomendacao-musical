MATCH (a:Artist {name: $artist})<-[:PERFORMED_BY]-(t:Track)-[:HAS_TAG]->(tag:Tag)
RETURN tag.name AS tag, count(DISTINCT t) AS tracks
ORDER BY tracks DESC, tag ASC
LIMIT $limit;