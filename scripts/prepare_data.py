"""Generate the six Aura CSVs from the original Kaggle Music Info.csv."""
import argparse
import csv
from pathlib import Path

TRACK_FIELDS = (
    "track_id name artist spotify_id genre year duration_ms danceability energy "
    "key loudness mode speechiness acousticness instrumentalness liveness valence tempo time_signature"
).split()


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(rows)


def prepare(source, output, limit=None):
    with source.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        missing = (set(TRACK_FIELDS) | {"tags"}) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")
        tracks = []
        seen = set()
        track_tags = []
        track_genres = []
        artists, genres, tags = set(), set(), set()
        for row in reader:
            track_id = row["track_id"]
            if not track_id or not row["artist"] or not row["name"]:
                raise ValueError("Missing track ID, name or artist")
            if track_id in seen:
                raise ValueError(f"Duplicate track ID: {track_id}")
            seen.add(track_id)
            tracks.append([row[k] for k in TRACK_FIELDS])
            artists.add(row["artist"])
            if row["genre"]:
                genres.add(row["genre"])
                track_genres.append((track_id, row["genre"]))
            row_tags = {tag.strip() for tag in row["tags"].split(",") if tag.strip()}
            tags.update(row_tags)
            track_tags.extend((track_id, tag) for tag in sorted(row_tags))
            if limit is not None and len(tracks) >= limit:
                break
    output.mkdir(parents=True, exist_ok=True)
    files = {
        "tracks.csv": (TRACK_FIELDS, tracks),
        "artists.csv": (["name"], [(name,) for name in sorted(artists)]),
        "genres.csv": (["name"], [(name,) for name in sorted(genres)]),
        "tags.csv": (["name"], [(name,) for name in sorted(tags)]),
        "track_tags.csv": (["track_id", "tag"], track_tags),
        "track_genres.csv": (["track_id", "genre"], track_genres),
    }
    for name, (fields, rows) in files.items():
        write_csv(output / name, fields, rows)
        print(f"{name}: {len(rows):,} rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--limit", type=int, help="Optional local sample size")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be positive")
    prepare(args.source, args.output, args.limit)
