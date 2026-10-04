# Importing this project into a Claude account

1. Unzip the package somewhere permanent (for example ~/Projects/karmic-map).
2. Start Claude Code in that folder and say: "Read HANDOFF.md, README.md and docs/design/Karmic-Map-Design-Document.md,
   then save a project memory from claude-import/project-karmic-map.md." The memory file is already in the
   frontmatter format Claude Code's memory directory uses (name / description / metadata.type), so it can be
   copied into the memory folder as is.
3. Run `uv sync`, `scripts/fetch_data.sh`, then `uv run python3 src/build.py` to regenerate the full outputs.
   The package already contains the small viewer layers, so `python3 -m http.server 8765` and
   http://localhost:8765/viewer/index.html work before the build.
