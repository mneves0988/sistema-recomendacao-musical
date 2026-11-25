// The Python loader supplies typed numeric properties and track identifiers.
UNWIND $rows AS row
MERGE (t:Track {track_id: row.track_id})
SET t += row
RETURN count(*) AS processed;
