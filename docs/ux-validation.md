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
