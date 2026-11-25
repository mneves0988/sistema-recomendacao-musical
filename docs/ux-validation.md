# Revisão de UX

A primeira versão funcionou no Aura: Frank Zappa / Willie the Pimp retornou Zig Zag Wanderer (62,71%). O usuário tentou buscar Pink Floyd no seletor principal, mas a lista estava filtrada pelo texto Frank Zappa na barra lateral. O seletor não pesquisava o catálogo completo.

A revisão usa um único seletor pesquisável, carregando os 8.317 artistas do Neo4j com cache temporário. Os IDs das faixas são preservados internamente; opções com nome e ano iguais recebem números de versão. A navegação e os controles foram compactados, o Graph Explorer foi movido para junto do ranking e as três estratégias continuam em Cypher, sem alterações nos algoritmos.

## Checklist de teste local (pendente)

- Buscar Pink Floyd diretamente no seletor principal e escolher uma faixa.
- Buscar Daft Punk, selecionar Something About Us e confirmar Another Woman (61,88%) no modo híbrido padrão.
- Voltar a Frank Zappa / Willie the Pimp e confirmar Zig Zag Wanderer (62,71%).
- Alterar algoritmo, peso e número de resultados, verificando atualização do ranking e do grafo.
- Trocar entre Track Discovery, Artist Discovery e Musical DNA; testar busca em todos.
- Verificar música sem tags, música com até duas tags e links Spotify.
- Conferir responsividade e legibilidade do grafo em tela menor.

## Revisão dos filtros por funcionalidade

O screenshot de Artist Discovery mostrava nomes como 10cc, 112 e 12 Stones. Conferimos os CSVs tratados: os oito nomes visíveis são registros de artists.csv e possuem faixas correspondentes em tracks.csv. Exemplos: 10cc (8), 112 (1), 12 Stones (3), 1200 Micrograms (16). O catálogo de origem tem 8.317 artistas e nenhum artista sem faixa.

A nova versão usa seletores inicialmente vazios com rótulos específicos de cada área e opções do tipo artista/banda + número de faixas. Track Discovery exige seleção explícita de artista e música; sua lista de músicas usa apenas os Track ligados ao Artist selecionado por PERFORMED_BY. Artist Discovery executa related_artists, sem carregar repertórios para a interface. Musical DNA utiliza a contagem agregada do catálogo e musical_dna, sem buscar a lista de músicas. O algoritmo de recomendação não foi alterado. Seletores de artista têm chaves específicas de cada área.

### Testes manuais da revisão (pendentes no Aura/Streamlit)

1. Abrir Track Discovery sem seleção: o seletor de faixa deve estar desativado; nenhum ranking deve ser mostrado.
2. Selecionar Pink Floyd: apenas suas faixas aparecem; selecionar uma faixa, trocar para Daft Punk e confirmar que a música anterior não é usada.
3. Em Artist Discovery, buscar 10cc: deve constar como artista com 8 faixas (CSV original) e exibir somente recomendações de artistas.
4. Em Musical DNA, buscar Frank Zappa: confirmar 20 faixas e rock em 19 delas. Não deve aparecer seletor de músicas.
5. Testar artista inexistente e retorno à área inicial; nenhuma consulta de recomendação deve ser executada sem referência selecionada.

A verificação de pertinência no código e nos arquivos de entrada não substitui o teste de integração na instância.
