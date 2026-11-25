// First confirm that invalid_acousticness and invalid_instrumentalness are zero.
MATCH (t:Track)
WITH t, toFloatOrNull(t.acousticness) AS a, toFloatOrNull(t.instrumentalness) AS i
RETURN count(t) AS total_tracks,
       sum(CASE WHEN a >= 0 AND a <= 1 THEN 0 ELSE 1 END) AS invalid_acousticness,
       sum(CASE WHEN i >= 0 AND i <= 1 THEN 0 ELSE 1 END) AS invalid_instrumentalness;

// Run separately, after confirming the preflight results.
MATCH (t:Track)
WITH t, toFloatOrNull(t.acousticness) AS a, toFloatOrNull(t.instrumentalness) AS i
WHERE a >= 0 AND a <= 1 AND i >= 0 AND i <= 1 AND t.mode IS NOT NULL
SET t.acousticness = a, t.instrumentalness = i, t.mode = toInteger(t.mode)
RETURN count(t) AS updated_tracks;

// Recheck.
MATCH (t:Track)
UNWIND ["acousticness","instrumentalness","mode"] AS property
RETURN property, valueType(t[property]) AS data_type, count(*) AS total
ORDER BY property;