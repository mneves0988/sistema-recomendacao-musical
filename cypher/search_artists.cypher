MATCH (a:Artist)
WHERE toLower(a.name) CONTAINS toLower($search)
RETURN a.name AS artist
ORDER BY CASE WHEN toLower(a.name) = toLower($search) THEN 0 ELSE 1 END, artist
LIMIT 30;