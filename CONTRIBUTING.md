# Contributing to mindgrab-brainchimp

## Picking work
- Every piece of work has an issue. Its footer gives the tier (core or stretch), the planned
  week, an estimate, and the issues it is blocked by.
- Start an issue only when every issue in its *Blocked by* line is closed.
- Assign yourself before you start. If you are stuck for more than half a day, comment on the
  issue: say what you tried and what happened.
- If the issue does not tell you what is being asked, or what "done" means, ask on the issue
  before writing code. That is a good use of your time, not a failure.

## Branches, commits and pull requests
- Work on your fork. Before starting a new branch, update `main` from `upstream`:
  `git switch main && git pull upstream main && git push origin main`.
- **Branch:** `<type>/<short-description>-gh<issue>`, for example `enh/conform-gh5`.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), for
  example `feat(conform): scale the affine before resampling`.
- **Pull request title:** `TYPE: Short summary`, with the type in capitals (ENH, FIX, TST, DOC,
  MNT, CI), for example `ENH: Add the conform step with voxel scaling`.
- **Pull request body:** what changed, why, the exact commands you ran to test it, and any
  question for the supervisor. End with `Closes #<issue>`.
- One issue per pull request, unless the issue says otherwise. Small pull requests are
  reviewed faster.

## Before opening a pull request
With your environment activated:
```bash
ruff format          # rewrites your files in the project's style
ruff check           # must report no error; `ruff check --fix` repairs most findings,
                     # such as the order of imports
pytest               # must pass
```
Optionally, `pre-commit install` runs the two ruff steps on every commit.

GitHub runs the same checks on every pull request. A red check means the pull request is not
ready for review.

## Data and results
- Never commit images, masks, model weights or other large files. `data/`, `outputs/` and
  `checkpoints/` are ignored by git; keep them there.
- Commit the small things that let others check your results: tables (`.tsv`, `.csv`), plots
  (`.png`), and the exact command that produced them.

## Weekly status report
Every Friday, post a comment of at most 300 words on the pinned *Weekly status reports* issue,
with three headings: **Done**, **Next**, **Risks**. Link the issues and pull requests you
mention.

## Use of AI tools
This repository hosts an ISC semester project run at **AI level 1**. In this project you do
not use AI tools yourself: no chat assistants, no code completion, no agents. Code, tests,
documentation and reports are your own work, and you must be able to explain every line.

## Licence
By contributing you agree that your contributions are licensed under the [MIT Licence](LICENSE).
