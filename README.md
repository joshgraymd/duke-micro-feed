# Duke Clinical Microbiology announcements → RSS

A GitHub Action runs `build_feed.py` daily, scrapes the "Recent Announcements and
Updates" table on https://clinlabs.duke.edu/clinical-microbiology, and commits
`feed.xml` only when announcements change. GitHub Pages serves it at a stable URL.

## Setup (one time, ~5 minutes)
1. Create a new **public** GitHub repo (e.g. `duke-micro-feed`).
2. Upload `build_feed.py`, `README.md`, and the `.github/workflows/update-feed.yml`
   file (keep that folder path exactly).
3. Settings → Actions → General → Workflow permissions → **Read and write**.
4. Actions tab → "Update RSS feed" → **Run workflow** (creates `feed.xml`).
5. Settings → Pages → Source: *Deploy from a branch* → `main` / `(root)` → Save.
6. Add this URL to your reader:
   `https://<your-username>.github.io/duke-micro-feed/feed.xml`

## Notes
- GitHub pauses scheduled workflows in public repos after 60 days with no repo
  activity. Since announcements are infrequent, check the Actions tab if the feed
  goes quiet; GitHub emails you first and re-enabling is one click.
- If the page layout changes, the run fails (you'll get an email) instead of
  publishing an empty feed.
