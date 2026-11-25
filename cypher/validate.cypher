MATCH (n) RETURN labels(n) AS label, count(n) AS total ORDER BY total DESC;
MATCH ()-[r]->() RETURN type(r) AS relationship, count(r) AS total ORDER BY total DESC;
CALL db.schema.visualization();