# Clash_Mac_Compile Copilot Instructions

- Read `AGENTS.md` and `.ai/AI-START-HERE.md` before changing files.
- The native app is built from `ProjectClash/Clash-Client`; do not substitute a third-party client.
- Keep `UPSTREAM_CLIENT_REF` explicit and pin it to a 40-character SHA before Release.
- The Client's `Dependencies.lock.json` is the authority for Kernel and Adapter revisions.
- Do not claim Xcode or macOS build success unless a real macOS Runner log confirms it.
- Keep signing secrets out of Git and workflow logs.
- Update version documents, repository catalog, structure, source manifest and tests for every project change.
