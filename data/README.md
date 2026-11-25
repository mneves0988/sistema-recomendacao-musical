# Dados

Fonte real: [Music Info.csv (Kaggle)](https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm). O projeto não utiliza o histórico de ouvintes nem dados de álbuns.

Baixe e extraia o arquivo original em data/raw/. Gere os seis CSVs tratados:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_data.py "data/raw/Music Info.csv" data/processed
```

Para gerar uma amostra real apenas no seu computador, acrescente --limit 1000. O autor confirmou a liberação do dataset para uso no projeto. Os termos específicos não foram verificados independentemente; mantenha a atribuição e observe a licença da fonte. Os CSVs reais não são incluídos para manter o repositório leve. O arquivo data/sample/music_info_synthetic.csv é uma fixture **sintética**, com três faixas fictícias, para estudar a estrutura e testar a preparação sem baixar o dataset. Não representa os resultados reais.

Contagens esperadas da base completa: 50.683 faixas, 8.317 artistas, 15 gêneros, 100 tags, 185.313 associações faixa-tag e 22.348 associações faixa-gênero. As 1.127 faixas sem tags e as 28.335 sem gênero são mantidas.

As consultas em cypher/import/ são uma alternativa programática ao importador visual do Aura. Use exclusivamente uma instância vazia de teste, nunca a instância já preenchida do projeto:

```powershell
.\.venv\Scripts\python.exe scripts/import_data.py data/processed
```

O carregador usa UNWIND, parâmetros, constraints e MERGE; os campos numéricos são convertidos em Python. A carga original do projeto ocorreu pelo Aura Import, e não por esse carregador alternativo. A alternativa precisa de validação em uma instância vazia. Se ocorrer falha parcial, não apague a instância do projeto: use outro ambiente de teste. Veja cypher/validate.cypher após a carga.
