// Complete catalog for the searchable artist selector.
MATCH (a:Artist)
RETURN a.name AS artist
ORDER BY toLower(artist), artist;
