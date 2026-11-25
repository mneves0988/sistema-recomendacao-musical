UNWIND $rows AS row
MERGE (:Genre {name: row.name})
RETURN count(*) AS processed;
