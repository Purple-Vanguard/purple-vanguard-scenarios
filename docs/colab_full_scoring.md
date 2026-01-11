# BadBlueprint full scoring in Colab

## What the notebook does
The notebook in `notebooks/badblueprint_full_scoring_colab.ipynb` performs end-to-end full scoring for the BadBlueprint scenario using the open-weight `gpt-oss-20b` model, the local OpenAI-compatible endpoint, and the vendored harness. It also exports and validates the submission bundle, records status metadata, and packages results for download.

## How to open in Colab
1. Open Google Colab in your browser.
2. Use the **File → Open notebook** menu.
3. Select the **GitHub** tab, then search for the `Purple-Vanguard/purple-vanguard-scenarios` repository.
4. Open `notebooks/badblueprint_full_scoring_colab.ipynb` and run the cells from top to bottom.

## Secrets
If the model requires gated access, set the `HF_TOKEN` environment variable in Colab before running the model download cell. Do not print the token in notebook output.

## Expected outputs
After a successful run, these files are created under `results/badblueprint/`:
- `full_score.log`
- `score_status.json`
- `agent-card-*.json` (when produced by the harness)

A tarball named `results_badblueprint_colab.tgz` is also generated at the repository root for easy download.
