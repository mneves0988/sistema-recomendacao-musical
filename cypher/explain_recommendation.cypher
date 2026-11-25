// Return real paths in Aura Query (Graph view).
MATCH p = (:Artist)<-[:PERFORMED_BY]-(t:Track {track_id: $track_id})
          -[:HAS_TAG]->(:Tag)<-[:HAS_TAG]-(rec:Track {track_id: $recommended_id})
          -[:PERFORMED_BY]->(:Artist)
RETURN p;