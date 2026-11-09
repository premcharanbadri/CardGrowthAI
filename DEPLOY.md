# Free or low-maintenance deployment

## Recommended: GitHub Pages /docs (static, no Python process)

1. Extract `CardGrowth_AI_Project3_Complete.zip` and create a GitHub repository, e.g. `cardgrowth-ai`.
2. Upload the **contents** of the folder, not just the ZIP file, including `docs/index.html` and `docs/assets`.
3. In GitHub: Settings → Pages → Deploy from a branch → `main` → `/docs` → Save.
4. The public URL will be `https://<github-username>.github.io/cardgrowth-ai/` (depending on repository configuration).
5. The webpage embeds synthetic test scores and re-solves scenario selection in the visitor's browser; it does not need a computer or server kept running. GitHub Pages is a static host; follow GitHub policy and ongoing availability terms.

## Alternative: Streamlit Community Cloud

1. Push the repository to GitHub.
2. Visit https://share.streamlit.io/ and select repository, branch `main`, main file `app.py`.
3. Share the issued `*.streamlit.app` URL. Free tiers may sleep while idle; visitors can wake the app.
4. Project dependencies are in `requirements.txt`; no credentials or external data are required.

## Privacy and scope

No real data is stored in the site. This is a synthetic educational case. Never upload actual card-account, personal or bank data to public repositories or external AI services without written authorization and appropriate controls.
