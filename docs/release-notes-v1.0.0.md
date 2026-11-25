# SoundGraph v1.0.0

Primeira versão estável do projeto educacional Neo4j + DIO.

- Demo: https://soundgraph.streamlit.app/
- 50.683 músicas, 8.317 artistas, 59.115 nós e 258.344 relacionamentos.
- Três métodos de recomendação em Cypher: tags compartilhadas, Jaccard e híbrido.
- Track Discovery, Artist Discovery, Musical DNA e Graph Explorer.
- Interface Streamlit com identidade visual própria e documentação PT/EN.
- Preparação de dados reproduzível, guia Aura Import e alternativa de carga por scripts.
- Monitoramento público com Playwright e GitHub Actions; [smoke test final aprovado](https://github.com/mneves0988/sistema-recomendacao-musical/actions/runs/45541511765).

## Limitações conhecidas

Pesos heurísticos, sem avaliação estatística de relevância ou testes de carga. QA complementar de pesos, métodos e links ainda não registrado na interface; permissões efetivas da conta Aura não confirmadas. Carregador programático alternativo não testado em instância vazia. A demo usa planos gratuitos sujeitos a hibernação. Não há dados de álbum, GDS ou recomendação baseada em histórico de ouvintes.

A branch feat/streamlit-discovery deve ser mantida enquanto a aplicação publicada estiver vinculada a ela. O monitoramento agendado na main não realiza escritas no grafo e tem janela temporária até 01/12/2026 (Brasília).
