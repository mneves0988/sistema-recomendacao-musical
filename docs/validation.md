# Validação no AuraDB

Contagens confirmadas pelo usuário: 59.115 nós (50.683 Track, 8.317 Artist, 100 Tag, 15 Genre) e 258.344 relacionamentos (185.313 HAS_TAG, 50.683 PERFORMED_BY, 22.348 IN_GENRE).

## Testes qualitativos V3

Pesos 70% tags, 30% áudio. Resultados observados na instância, não exemplos inventados.

| Referência | Recomendação #1 | Jaccard | Áudio | Híbrido |
|---|---|---:|---:|---:|
| Frank Zappa / Willie the Pimp | Captain Beefheart & His Magic Band / Zig Zag Wanderer | 54,55% | 81,75% | 62,71% |
| Daft Punk / Something About Us | Moby / Another Woman | 53,85% | 80,62% | 61,88% |
| Madonna / Justify My Love | Lady Gaga / Americano | 62,50% | 80,99% | 68,05% |
| Miles Davis / Saeta | Jaco Pastorius / Continuum | 100% | 91% | 97,30% |

Miles Davis tem somente duas tags na faixa de referência (instrumental e jazz); Jaccard perfeito significa igualdade dos conjuntos, não identidade sonora. Outros casos com pouca ou nenhuma tag são uma limitação. Os scores não são probabilidades de preferência. Não há histórico de usuários ou avaliação estatística de relevância.

V1, V2 e V3 foram executadas no Aura; V3 reproduziu o ranking após normalização. Artist Discovery de Frank Zappa: Traffic (62,5%), Jefferson Airplane (61,9%), Jimi Hendrix (57,14%). Graph Explorer de Willie the Pimp e Zig Zag Wanderer: 10 nós, 14 relacionamentos, 6 tags compartilhadas. A aplicação ainda requer teste de integração.

## Troubleshooting

- 42N44: ORDER BY referenciava rec.track_id após RETURN com agregações. Correção: projetar o identificador com alias.
- 22N01: acousticness e instrumentalness importados como STRING. Primeiro contornado com toFloatOrNull, depois normalizado via SET após validar conversibilidade e intervalo. mode foi convertido de BOOLEAN para INTEGER. Todos os 50.683 nós Track foram atualizados e os tipos revalidados. Ver cypher/normalize_types.cypher.
- 42N81: parâmetros ausentes na sessão Aura. Usar o comando separado :param {track_id: "TRLNZUR128F426B8D9", tag_weight: 0.7, limit: 10}. Em Python, os parâmetros são enviados pelo driver.

Não houve GDS, modelos de ML ou serviços de IA. Os pesos são heurísticos e não foram calibrados estatisticamente.
