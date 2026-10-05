# Duke Clinical Microbiology announcements → RSS

A GitHub Action runs `build_feed.py` daily, scrapes the "Recent Announcements and
Updates" table on https://clinlabs.duke.edu/clinical-microbiology, and commits
`feed.xml` only when announcements change. GitHub Pages serves it at a stable URL.
