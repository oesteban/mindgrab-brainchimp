# AGENTS instructions

## AI policy (read first)
This repository hosts an ISC semester project run at **AI level 1**. The student does not use
AI tools. An agent working in this repository is therefore run by a maintainer, and:
- **must not** write, complete or rewrite code, tests, documentation or reports on a student's
  branch, nor open pull requests or comments on a student's behalf;
- **may** explain concepts, point to documentation and source files, and help interpret error
  messages, when the maintainer asks.

## Layout
- Source code lives under `src/brainchimp/`, tests under `tests/`, background in
  `docs/primer.md`.
- Code pointers in issues are permalinks to pinned commits:
  - [neuroneural/catalyst_example@629cb45](https://github.com/neuroneural/catalyst_example/tree/629cb45a43edad482551dd7015446c9089ad5e67)
  - [neuroneural/brainchop-models@528f2d8](https://github.com/neuroneural/brainchop-models/tree/528f2d8d2ca937968b2d4b2b9ef9fa9170f4b9cf)
  - [neuroneural/brainchop-cli@31150c3](https://github.com/neuroneural/brainchop-cli/tree/31150c39dae90dba3d18b00d05d32eba273056af)
    (archived on 2026-11-22; `brainchop` is pinned to 0.2.5)

## Checks
```bash
ruff format --check
ruff check
pytest
```

## Conventions
See `CONTRIBUTING.md` for branch names, Conventional Commits and pull request titles.
