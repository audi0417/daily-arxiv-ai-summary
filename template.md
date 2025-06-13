# About
This tool will daily crawl https://arxiv.org and use LLMs to summarize them.

# How to use
This repo will daily crawl arXiv papers about **cs.AI, cs.LG, cs.CV, cs.CL**, and use **OpenAI GPT-4o-mini** to summarize the papers in **English**.
If you wish to crawl other arXiv categories, use other LLMs or other languages, please follow the below instructions.

**Instructions:**
1. Fork this repo to your own account
2. Go to: your-own-repo -> Settings -> Secrets and variables -> Actions
3. Go to Secrets. Secrets are encrypted and are used for sensitive data
4. Create repository secrets named `OPENAI_API_KEY` and `OPENAI_BASE_URL` (optional), and input corresponding values.
5. Go to Variables. Variables are shown as plain text and are used for non-sensitive data
6. Create the following repository variables:
   1. `CATEGORIES`: separate the categories with ",", such as "cs.AI,cs.LG,cs.CV,cs.CL"
   2. `LANGUAGE`: such as "Chinese" or "English"
   3. `MODEL_NAME`: such as "gpt-4o-mini"
   4. `EMAIL`: your email for push to github
   5. `NAME`: your name for push to github
7. Go to your-own-repo -> Actions -> arXiv-daily-ai-enhanced
8. You can manually click **Run workflow** to test if it works well (it may take about one hour). 
By default, this action will automatically run every day
You can modify it in `.github/workflows/run.yml`
9. If you wish to modify the content in `README.md`, do not directly edit README.md. You should edit `template.md`.

# Content
{readme_content}

# Related tools
- Original inspiration: https://github.com/dw-dengwei/daily-arXiv-ai-enhanced

# Star history

[![Star History Chart](https://api.star-history.com/svg?repos=audi0417/daily-arxiv-ai-summary&type=Date)](https://www.star-history.com/#audi0417/daily-arxiv-ai-summary&Date)
