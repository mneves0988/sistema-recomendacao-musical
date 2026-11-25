# Executar a interface

Requisitos: Python 3.11+ recomendado e instância AuraDB com o grafo importado e normalizado.

PowerShell, na raiz do projeto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Use a URI e as credenciais da sua instância. Nunca publique o .env. O app usa sessões de leitura, consultas parametrizadas e cache temporário de resultados. Não publica dados nem credenciais automaticamente.

Teste manual: selecione Frank Zappa / Willie the Pimp, V3, 70%, 10 recomendações. A primeira deve ser Zig Zag Wanderer (62,71%). Confira o Graph Explorer e as outras áreas. A interface foi executada localmente e na demonstração pública; o fluxo híbrido padrão passou no smoke test E2E.

A [demonstração pública](https://soundgraph.streamlit.app/) está hospedada no Streamlit Community Cloud. Use os secrets do Streamlit com as mesmas variáveis ao publicar sua própria instância. A aplicação usa sessões de leitura; os privilégios de leitura no servidor ainda precisam ser confirmados.
