# Colab full scoring for BadBlueprint

## What this notebook does
The notebook in `notebooks/badblueprint_full_scoring_colab.ipynb` prepares the environment, downloads the open-weight model, starts a local OpenAI-compatible endpoint, builds the submission bundle, installs the vendored harness, runs full scoring, and packages results for download.

## Open in Colab
1. Open Google Colab.
2. Choose to open a notebook from GitHub or upload the file manually.
3. Select `notebooks/badblueprint_full_scoring_colab.ipynb` from this repository.
4. Run the notebook cells from top to bottom.

## Secrets
If the model requires authentication, set the `HF_TOKEN` environment variable in Colab before the model download cell. Do not print the token in outputs.

## Expected outputs
After a successful run, the notebook writes results under `results/badblueprint/`, including:
- `full_score.log`
- `score_status.json`
- `agent-card-*.json` (if generated)
- `results_badblueprint_colab.tgz`
