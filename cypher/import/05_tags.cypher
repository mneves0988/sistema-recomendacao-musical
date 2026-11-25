UNWIND $rows AS row
MERGE (:Tag {name: row.name})
RETURN count(*) AS processed;
