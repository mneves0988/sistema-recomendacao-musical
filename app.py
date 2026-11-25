"""SoundGraph: a small Streamlit client for the Cypher recommendation engine."""
import os
import re
from pathlib import Path

import graphviz
import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase, READ_ACCESS
from neo4j.exceptions import Neo4jError, DriverError

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="SoundGraph | Music Discovery", page_icon="🎵", layout="wide")


def setting(name, default=""):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name, default)
    except (FileNotFoundError, KeyError):
        return default


@st.cache_resource
def connect(uri, username, password):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        driver.verify_connectivity()
    except Exception:
        driver.close()
        raise
    return driver


@st.cache_data(ttl=120, show_spinner=False)
def query(name, params, database, _driver):
    cypher = (ROOT / "cypher" / (name + ".cypher")).read_text(encoding="utf-8")
    with _driver.session(database=database, default_access_mode=READ_ACCESS) as session:
        return session.execute_read(lambda tx: tx.run(cypher, **params).data())


def graph(source_artist, source_track, result):
    # Visualize the actual shared tags returned by Cypher, not invented edges.
    dot = graphviz.Digraph()
    dot.attr(rankdir="LR", bgcolor="transparent", nodesep="0.35")
    dot.attr("node", shape="box", style="rounded,filled", fontname="Arial", fontcolor="#10231c")
    dot.attr("edge", color="#83938c")
    dot.node("source_artist", graphviz.escape(source_artist), fillcolor="#b6df72")
    dot.node("source_track", graphviz.escape(source_track), fillcolor="#81b982")
    dot.node("target_track", graphviz.escape(result["track"]), fillcolor="#81b982")
    dot.node("target_artist", graphviz.escape(result["artist"]), fillcolor="#b6df72")
    dot.edge("source_track", "source_artist", label="PERFORMED_BY")
    dot.edge("target_track", "target_artist", label="PERFORMED_BY")
    for i, tag in enumerate(sorted(result["explanation"])):
        node = f"tag_{i}"
        dot.node(node, graphviz.escape(tag), fillcolor="#facc66", shape="ellipse")
        dot.edge("source_track", node)
        dot.edge("target_track", node)
    st.graphviz_chart(dot.source)
    st.caption("Cada seta entre uma música e uma tag representa HAS_TAG. O grafo é construído com as tags compartilhadas retornadas pelo Neo4j.")


def main():
    st.title("SoundGraph")
    st.caption("Descubra música através de conexões | Neo4j AuraDB + Cypher")
    uri = setting("NEO4J_URI")
    username = setting("NEO4J_USERNAME", "neo4j")
    password = setting("NEO4J_PASSWORD")
    database = setting("NEO4J_DATABASE", "neo4j")
    if not uri or not password:
        st.info("Configure NEO4J_URI e NEO4J_PASSWORD no arquivo .env (veja .env.example) ou nos secrets do Streamlit.")
        st.stop()
    driver = connect(uri, username, password)

    def run(name, **params):
        return query(name, params, database, driver)

    with st.sidebar:
        st.header("Explorar")
        page = st.radio("Modo", ["Track Discovery", "Artist Discovery", "Musical DNA"])
        search = st.text_input("Buscar artista", "Frank Zappa").strip()
        st.caption("Motor de recomendação executado no Neo4j. Nenhum GDS ou API externa.")
    if not search:
        st.info("Digite o nome de um artista.")
        return
    artists = run("search_artists", search=search)
    if not artists:
        st.warning("Nenhum artista encontrado.")
        return
    artist = st.selectbox("Artista de referência", [r["artist"] for r in artists])
    if page == "Track Discovery":
        tracks = run("artist_tracks", artist=artist)
        if not tracks:
            st.info("Nenhuma música encontrada.")
            return
        default = next((i for i, t in enumerate(tracks) if t["track"] == "Willie the Pimp"), 0)
        idx = st.selectbox("Música de referência", range(len(tracks)), index=default,
                           format_func=lambda i: f"{tracks[i]['track']} | {tracks[i]['year']} | {tracks[i]['track_id']}",
                           key=f"track_{artist}")
        source = tracks[idx]
        st.caption(f"Tags disponíveis: {source['total_tags']}")
        if source["total_tags"] == 0:
            st.info("Esta música não possui tags. O recomendador atual precisa de pelo menos uma conexão HAS_TAG.")
            return
        if source["total_tags"] <= 2:
            st.warning("Poucas tags disponíveis: um score alto pode refletir metadados escassos, não identidade musical.")
        mode = st.radio("Algoritmo", ["V3 · Híbrido", "V2 · Jaccard", "V1 · Tags compartilhadas"], horizontal=True)
        weight = 70
        if mode.startswith("V3"):
            weight = st.slider("Peso das tags (%)", 0, 100, 70, 5)
            st.caption(f"Sonoridade: {100-weight}%. Todos os candidatos precisam compartilhar pelo menos uma tag.")
        limit = st.selectbox("Quantidade", [5, 10, 20], index=1)
        params = dict(track_id=source["track_id"], limit=limit)
        if mode.startswith("V3"):
            params["tag_weight"] = weight / 100
        with st.spinner("Consultando o grafo..."):
            rows = run("recommend_" + mode[:2].lower(), **params)
        if not rows:
            st.info("Nenhuma recomendação encontrada.")
            return
        st.subheader("Recomendações")
        for i, row in enumerate(rows, 1):
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.text(f"{i}. {row['track']}")
                left.text(row["artist"])
                if "hybrid_score" in row:
                    right.metric("Score híbrido", f"{row['hybrid_score']:.2f}%")
                    left.caption(f"Tags: {row['tag_similarity']:.2f}% | Áudio: {row['audio_similarity']:.2f}%")
                elif "tag_similarity" in row:
                    right.metric("Jaccard", f"{row['tag_similarity']:.2f}%")
                else:
                    right.metric("Tags em comum", row["shared_tags"])
                left.caption(f"{row['shared_tags']} tags em comum | {row['target_total']} tags na candidata")
                left.text(" · ".join(sorted(row["explanation"])))
                spotify_id = row.get("spotify_id") or ""
                if re.fullmatch(r"[A-Za-z0-9]{22}", spotify_id):
                    left.link_button("Abrir no Spotify", "https://open.spotify.com/track/" + spotify_id)
        st.caption("Scores de similaridade, não probabilidades de gostar. A disponibilidade no Spotify pode variar.")
        st.subheader("Graph Explorer")
        selected = st.selectbox("Explicar recomendação", range(len(rows)),
                                format_func=lambda i: f"{rows[i]['track']} | {rows[i]['artist']}",
                                key=f"explain_{source['track_id']}_{mode}_{weight}_{limit}")
        graph(artist, source["track"], rows[selected])
    elif page == "Artist Discovery":
        rows = run("related_artists", artist=artist, limit=10)
        if not rows:
            st.info("Nenhum artista semelhante encontrado.")
            return
        st.caption("Jaccard entre conjuntos de tags do repertório disponível na base.")
        if rows[0]["source_total"] <= 2:
            st.warning("O artista possui poucas tags. Interprete a similaridade com cautela.")
        for row in rows:
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.text(row["artist"])
                right.metric("Jaccard", f"{row['similarity_pct']:.2f}%")
                left.caption(f"{row['shared_tags']} tags em comum | {row['target_total']} tags na candidata")
                left.text(" · ".join(sorted(row["explanation"])))
    else:
        tracks = run("artist_tracks", artist=artist)
        rows = run("musical_dna", artist=artist, limit=10)
        st.metric("Músicas na base", len(tracks))
        if not rows:
            st.info("Nenhuma tag disponível.")
            return
        st.bar_chart(rows, x="tag", y="tracks", horizontal=True)
        st.dataframe([{"Tag": r["tag"], "Músicas": r["tracks"],
                       "Cobertura (%)": round(100*r["tracks"]/len(tracks), 2)} for r in rows],
                     hide_index=True)
        st.caption("Percentual de músicas associadas a cada tag. Uma música pode possuir múltiplas tags.")


try:
    main()
except (Neo4jError, DriverError, OSError, ValueError):
    st.error("Não foi possível consultar o Neo4j. Confira as credenciais, a instância ativa e a importação do grafo.")
