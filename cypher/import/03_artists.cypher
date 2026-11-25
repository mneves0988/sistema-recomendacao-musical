UNWIND $rows AS row
MERGE (:Artist {name: row.name})
RETURN count(*) AS processed;
