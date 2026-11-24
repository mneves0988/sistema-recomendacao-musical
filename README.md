# SoundGraph | Sistema de recomendação musical

Projeto do bootcamp Neo4j e DIO. Recomendação de músicas por características de conteúdo, especialmente tags compartilhadas, utilizando Neo4j AuraDB e Cypher.

## Dataset

Fonte: [Million Song Dataset – Spotify / Last.fm (Kaggle)](https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm). Utilizamos somente `Music Info.csv`. Os CSVs tratados são importados localmente pela interface do Aura; credenciais e dados brutos não devem ser publicados. A licença da fonte deverá ser confirmada antes de redistribuir amostras.

## Modelo do grafo

```mermaid
flowchart LR
  T[Track] -->|PERFORMED_BY| A[Artist]
  T -->|IN_GENRE| G[Genre]
  T -->|HAS_TAG| X[Tag]
```

## Importação no Aura

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

Contagens esperadas com os seis CSVs verificados, em uma instância vazia: 50.683 Track, 8.317 Artist, 15 Genre, 100 Tag; 50.683 PERFORMED_BY, 22.348 IN_GENRE e 185.313 HAS_TAG. Total: 59.115 nós e 258.344 relacionamentos. A carga ainda deve ser executada e validada no Aura.

## Status

Modelagem e arquivos de entrada definidos. Importação, consultas de recomendação e evidências visuais pendentes de validação.
