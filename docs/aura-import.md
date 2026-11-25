# Importação visual no Neo4j Aura

Em [Aura Console](https://console.neo4j.io/), abra Import e escolha CSV/TSV local. Adicione os seis arquivos tratados e crie os nós:

| Label | CSV | ID |
|---|---|---|
| Track | tracks.csv | track_id |
| Artist | artists.csv | name |
| Genre | genres.csv | name |
| Tag | tags.csv | name |

Preserve os nomes das colunas nas propriedades. Track: track_id, name, spotify_id como String; year, duration_ms, key, mode, time_signature como Integer; danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo como Float. Artist, Genre e Tag: name como String. As colunas artist e genre de tracks.csv servem para mapeamento, sem necessidade de duplicá-las como propriedades.

| Relação (origem → destino) | CSV | Coluna de origem | Coluna de destino |
|---|---|---|---|
| Track → Artist: PERFORMED_BY | tracks.csv | track_id | artist |
| Track → Genre: IN_GENRE | track_genres.csv | track_id | genre |
| Track → Tag: HAS_TAG | track_tags.csv | track_id | tag |

Execute Run import após completar o mapeamento e selecione a instância do projeto.

## Validação após carga

```cypher
MATCH (n)
RETURN labels(n) AS label, count(*) AS total
ORDER BY total DESC;
```

```cypher
MATCH ()-[r]->()
RETURN type(r) AS relationship, count(*) AS total
ORDER BY total DESC;
```

Contagens esperadas com os seis CSVs verificados, em uma instância vazia: 50.683 Track, 8.317 Artist, 15 Genre, 100 Tag; 50.683 PERFORMED_BY, 22.348 IN_GENRE e 185.313 HAS_TAG. Total: 59.115 nós e 258.344 relacionamentos. A carga e essas contagens foram confirmadas no AuraDB.

Antes da importação, gere os seis CSVs conforme [a documentação de dados](../data/README.md). A carga original foi realizada pelo Aura Import. Use uma instância vazia para reproduzir a carga; não reimporte na instância pública.
