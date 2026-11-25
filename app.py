"""SoundGraph: a small Streamlit client for the Cypher recommendation engine."""
import os
import re
from collections import Counter
from pathlib import Path

import graphviz
import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase, READ_ACCESS
from neo4j.exceptions import Neo4jError, DriverError

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
st.set_page_config(page_title="SoundGraph | Music Discovery", page_icon="🎵", layout="wide", initial_sidebar_state="collapsed")


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
def query(name, params, database, connection_id, _driver):
    cypher = (ROOT / "cypher" / (name + ".cypher")).read_text(encoding="utf-8")
    with _driver.session(database=database, default_access_mode=READ_ACCESS) as session:
        return session.execute_read(lambda tx: tx.run(cypher, **params).data())


def graph(source_artist, source_track, result):
    # Visualize the actual shared tags returned by Cypher, not invented edges.
    dot = graphviz.Digraph()
    dot.attr(rankdir="LR", bgcolor="transparent", nodesep="0.25", ranksep="0.45")
    dot.attr("node", shape="box", style="rounded,filled", fontname="Arial", fontcolor="#10231c")
    dot.attr("edge", color="#83938c", fontcolor="#A7B9AF", fontsize="9")
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


def track_labels(tracks):
    """Hide technical identifiers; distinguish recordings with identical labels."""
    labels = [f"{t['track']} · {t['year']}" if t.get("year") else t["track"] for t in tracks]
    totals = Counter(labels)
    seen = Counter()
    result = {}
    for track, label in zip(tracks, labels):
        seen[label] += 1
        result[track["track_id"]] = (
            f"{label} (versão {seen[label]})" if totals[label] > 1 else label
        )
    return result


def percent(value):
    return f"{value:.2f}%".replace(".", ",")


def track_card(row, position):
    with st.container(border=True):
        left, right = st.columns([3, 1], gap="small")
        left.markdown(f"**{position:02d}.**")
        left.write(row["track"])
        left.caption(row["artist"])
        if "hybrid_score" in row:
            right.metric("Híbrido", percent(row["hybrid_score"]))
            left.caption(f"Estilo {percent(row['tag_similarity'])} · Áudio {percent(row['audio_similarity'])}")
        elif "tag_similarity" in row:
            right.metric("Jaccard", percent(row["tag_similarity"]))
        else:
            right.metric("Tags em comum", row["shared_tags"])
        st.caption(f"{row['shared_tags']} tags compartilhadas de {row['target_total']} da candidata")
        st.write(" · ".join(tag.replace("_", " ") for tag in sorted(row["explanation"])))
        spotify_id = row.get("spotify_id") or ""
        if re.fullmatch(r"[A-Za-z0-9]{22}", spotify_id):
            st.markdown(f"[Ouvir no Spotify ↗](https://open.spotify.com/track/{spotify_id})")


def main():
    st.title("SoundGraph")
    st.caption("Descubra música através de conexões · Neo4j AuraDB + Cypher")
    uri = setting("NEO4J_URI")
    username = setting("NEO4J_USERNAME", "neo4j")
    password = setting("NEO4J_PASSWORD")
    database = setting("NEO4J_DATABASE", "neo4j")
    if not uri or not password:
        st.info("Configure NEO4J_URI e NEO4J_PASSWORD no arquivo .env (veja .env.example) ou nos secrets do Streamlit.")
        st.stop()
    driver = connect(uri, username, password)

    def run(name, **params):
        return query(name, params, database, (uri, username), driver)

    # One artist-only catalog, with aggregated track counts (no track titles).
    catalog = {r["artist"]: r["track_count"] for r in run("list_artists")}
    artists = list(catalog)
    if not artists:
        st.warning("O catálogo está vazio. Confira a importação do grafo.")
        return

    st.caption(f"● Neo4j conectado  |  {len(artists):,}".replace(",", ".") + " artistas disponíveis")
    page = st.radio("Explorar", ["Track Discovery", "Artist Discovery", "Musical DNA"],
                    horizontal=True, label_visibility="collapsed", key="discovery_page")
    with st.container(border=True):
        if page == "Track Discovery":
            artist_col, track_col = st.columns([1, 1])
        else:
            artist_col = st.container()
        with artist_col:
            labels_by_page = {
                "Track Discovery": "Artista da música de referência",
                "Artist Discovery": "Artista de referência",
                "Musical DNA": "Artista para analisar",
            }
            artist = st.selectbox(
                labels_by_page[page], artists, index=None,
                placeholder="Digite o nome de um artista ou banda",
                format_func=lambda name: f"{name} · {catalog[name]} {'faixa' if catalog[name] == 1 else 'faixas'}",
                key=f"reference_artist_{page}",
                help="Somente artistas e bandas do catálogo. A quantidade indica as faixas disponíveis.",
            )
        if artist is None:
            if page == "Track Discovery":
                with track_col:
                    st.selectbox("Música de referência", [], index=None,
                                 placeholder="Selecione primeiro um artista", disabled=True,
                                 key="track_waiting")
            st.info("Escolha um artista para começar. Ex.: Pink Floyd, Daft Punk ou Frank Zappa.")
            return
        if page == "Track Discovery":
            tracks = run("artist_tracks", artist=artist)
            if not tracks:
                st.info("Nenhuma música encontrada para este artista.")
                return
            by_id = {t["track_id"]: t for t in tracks}
            labels = track_labels(tracks)
            ids = list(by_id)
            with track_col:
                selected_id = st.selectbox("Música de referência", ids,
                                           index=None,
                                           placeholder="Digite o nome de uma música",
                                           format_func=labels.__getitem__,
                                           key=f"track_{artist}",
                                           help="Apenas músicas do artista selecionado.")
            if selected_id is None:
                st.info(f"Escolha uma das {len(tracks)} faixas de {artist}.")
                return
            source = by_id[selected_id]
            st.caption(f"{source['total_tags']} tags disponíveis na música de referência")
            if source["total_tags"] == 0:
                st.info("Esta música não possui tags. Escolha outra faixa para descobrir conexões.")
                return
            if source["total_tags"] <= 2:
                st.warning("Poucas tags disponíveis: um score alto pode refletir metadados escassos, não identidade musical.")
            mode_col, weight_col, limit_col = st.columns([2, 2, 1], gap="medium")
            with mode_col:
                mode = st.selectbox("Método de recomendação", ["Híbrido", "Jaccard", "Tags compartilhadas"],
                                    help="Híbrido (V3) combina tags e áudio; Jaccard (V2) compara conjuntos; V1 conta tags.")
            with limit_col:
                limit = st.selectbox("Resultados", [5, 10, 20], index=1)
            weight = 70
            with weight_col:
                if mode == "Híbrido":
                    weight = st.slider("Peso do estilo musical (%)", 0, 100, 70, 5)
                    st.caption(f"Estilo {weight}% · Sonoridade {100-weight}%")
                else:
                    st.caption("O método selecionado utiliza apenas conexões por tags.")
            st.caption("O ranking é atualizado ao alterar os filtros. Todos os candidatos compartilham ao menos uma tag.")

    if page == "Track Discovery":
        methods = {"Híbrido": "recommend_v3", "Jaccard": "recommend_v2",
                   "Tags compartilhadas": "recommend_v1"}
        params = dict(track_id=source["track_id"], limit=limit)
        if mode == "Híbrido":
            params["tag_weight"] = weight / 100
        with st.spinner("Explorando conexões no Neo4j..."):
            rows = run(methods[mode], **params)
        if not rows:
            st.info("Nenhuma recomendação encontrada. Escolha outra faixa.")
            return
        results_col, explorer_col = st.columns([1.15, 1], gap="large")
        with explorer_col:
            st.subheader("Graph Explorer")
            with st.container(border=True):
                by_rec_id = {r["track_id"]: r for r in rows}
                rec_ids = list(by_rec_id)
                selected = st.selectbox("Explicar uma recomendação", rec_ids,
                                        format_func=lambda i: f"{by_rec_id[i]['track']} · {by_rec_id[i]['artist']}",
                                        key=f"explain_{source['track_id']}_{mode}_{weight}_{limit}")
                chosen = by_rec_id[selected]
                st.caption(f"{chosen['shared_tags']} conexões por tags compartilhadas")
                graph(artist, source["track"], chosen)
                st.caption("Verde: música · Lima: artista · Amarelo: tag")
        with results_col:
            st.subheader("Recomendações")
            st.caption(f"{len(rows)} músicas semelhantes a {source['track']}")
            for i, row in enumerate(rows, 1):
                track_card(row, i)
        st.caption("Scores são medidas de similaridade, não probabilidades de gostar. A disponibilidade no Spotify pode variar.")
    elif page == "Artist Discovery":
        with st.spinner("Comparando perfis musicais..."):
            rows = run("related_artists", artist=artist, limit=10)
        if not rows:
            st.info("Nenhum artista semelhante encontrado.")
            return
        st.subheader("Artistas semelhantes")
        st.caption("Jaccard entre conjuntos de tags do repertório disponível na base.")
        if rows[0]["source_total"] <= 2:
            st.warning("O artista possui poucas tags. Interprete a similaridade com cautela.")
        for start in range(0, len(rows), 2):
            cols = st.columns(2)
            for col, row in zip(cols, rows[start:start+2]):
                with col:
                    with st.container(border=True):
                        left, right = st.columns([3, 1])
                        left.write(row["artist"])
                        right.metric("Jaccard", percent(row["similarity_pct"]))
                        st.caption(f"{row['shared_tags']} tags em comum · {row['target_total']} tags na candidata")
                        st.write(" · ".join(tag.replace("_", " ") for tag in sorted(row["explanation"])))
    else:
        total_tracks = catalog[artist]
        rows = run("musical_dna", artist=artist, limit=10)
        st.subheader("Musical DNA")
        st.metric("Músicas na base", total_tracks)
        if not rows:
            st.info("Nenhuma tag disponível.")
            return
        chart_col, table_col = st.columns([1, 1], gap="large")
        with chart_col:
            st.bar_chart(rows, x="tag", y="tracks", horizontal=True)
        with table_col:
            st.dataframe([{"Tag": r["tag"], "Músicas": r["tracks"],
                           "Cobertura (%)": round(100*r["tracks"]/total_tracks, 2)} for r in rows],
                         hide_index=True)
        st.caption("Percentual de músicas associadas a cada tag. Uma música pode possuir múltiplas tags.")

    st.divider()
    st.caption("SoundGraph · Projeto Neo4j + DIO · Motor de recomendação em Cypher, sem GDS ou APIs de IA.")


try:
    main()
except (Neo4jError, DriverError, OSError, ValueError):
    st.error("Não foi possível consultar o Neo4j. Confira as credenciais, a instância ativa e a importação do grafo.")
