// Only Artist nodes, with the size of their catalog.
// The optional match retains artists even if they have no tracks.
MATCH (a:Artist)
OPTIONAL MATCH (a)<-[:PERFORMED_BY]-(t:Track)
RETURN a.name AS artist, count(DISTINCT t) AS track_count
ORDER BY toLower(artist), artist;
