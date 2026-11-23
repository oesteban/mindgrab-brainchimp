# mindgrab-brainchimp

Fine-tuning [BrainChop](https://github.com/neuroneural/brainchop-cli)'s skull-stripping model,
[MindGrab](https://arxiv.org/abs/2506.11860), for macaque brain MRI.

MindGrab is a tiny network (146,237 parameters) that finds the brain in a human head MRI, in
the terminal or in the web browser. It was trained on human heads only, and on a macaque it
fails: the monkey brain is about 13 times smaller in volume. This project measures how MindGrab
does on macaques, adapts it with fine-tuning on [PRIME-DE](https://fcon_1000.projects.nitrc.org/indi/indiPRIME.html),
an open collection of monkey MRI, and evaluates the result on scanning sites the model never
saw.

It started as an ISC semester project (HES-SO Valais-Wallis, November to December 2026). The
work is planned as GitHub issues; start with the pinned ones.

## Quickstart

You need Python 3.11 or 3.12 and git.

```bash
git clone https://github.com/<your-user>/mindgrab-brainchimp.git
cd mindgrab-brainchimp
git remote add upstream https://github.com/oesteban/mindgrab-brainchimp.git

python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

ruff format --check && ruff check  # style
pytest                             # tests; fixtures download small files once
python -m brainchimp.fetch data/   # example images and MindGrab's weights, about 50 MB
```

Always activate the environment first: `brainchop` calls a helper program, `niimath`, that is
installed inside it.

## Layout

| Path | What |
|---|---|
| `src/brainchimp/` | the Python package; `fetch.py` downloads the public files |
| `tests/` | pytest tests; `conftest.py` holds shared fixtures |
| `docs/primer.md` | the background you need, one section per topic, with a glossary |
| `data/` | your local data (ignored by git) |

## Data

No image ever goes into this repository. The public files (an example human brain, the NMT v2
macaque template, MindGrab's weights) come from `python -m brainchimp.fetch`. The macaque scans
come from a DataLad dataset prepared from PRIME-DE; its licences require every user to
register with NITRC first.

## Credits

- MindGrab and BrainChop: the [neuroneural](https://github.com/neuroneural) lab (MIT licence).
  `src/brainchimp/meshnet.py` will come from their
  [catalyst_example](https://github.com/neuroneural/catalyst_example) training code.
- NMT v2 macaque template (public domain), through [TemplateFlow](https://www.templateflow.org).
- PRIME-DE (INDI), and the released macaque brain masks of
  [NHP-BrainExtraction](https://github.com/HumanBrainED/NHP-BrainExtraction).

## Licence

MIT, see [LICENSE](LICENSE).
