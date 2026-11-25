# Temporary public smoke monitoring

Public URL: https://soundgraph.streamlit.app/

The workflow opens the public app in Chromium, verifies that the Neo4j catalog loads, selects Frank Zappa / Willie the Pimp and checks Zig Zag Wanderer (62.71%) and Graph Explorer. It uses the ordinary visitor flow, including Streamlit's wake button when shown. No database credentials, writes or artificial changes to the music graph.

Schedule: 02:17, 10:17 and 18:17 UTC (23:17, 07:17, 15:17 Brasília). Scheduled checks stop contacting the app at 2026-12-02 03:00 UTC (midnight after December 1 in Brasília). The workflow remains scheduled as a no-op until manually disabled; manual runs are still allowed. GitHub may delay scheduled jobs. Disable the workflow in Actions after the evaluation period.

## Verify installation

1. Open Actions → SoundGraph smoke test → Run workflow (main).
2. Inspect the job log. A successful run must include public HTTP, connected catalog and recommendation PASS messages.
3. For failure, inspect the failing step and open the public URL manually. If Aura is paused, resume it in Aura Console, then rerun.
4. Enable GitHub Actions failure notifications in account settings if desired.

The monitoring cannot guarantee continuous uptime. Aura Free may pause after 72 hours without updates or writes; read-only recommendations do not guarantee prevention. Do not generate artificial database writes. Streamlit can hibernate and must be allowed to wake normally. No direct monitoring of the Aura admin API is configured.

References:
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
- https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- https://support.neo4j.com/s/article/4406830696083-Why-is-my-AuraDB-Free-Instance-Paused

The workflow belongs on the default branch, main, even though the deployed app currently uses feat/streamlit-discovery. The application code and production deployment are unchanged. Initial smoke execution is pending.
