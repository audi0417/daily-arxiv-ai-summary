# Project Rewrite Complete - Google Gemini Integration

## What was done

This project has been completely rewritten to fix the crawler issues and implement a more robust architecture based on the reference project `dw-dengwei/daily-arXiv-ai-enhanced`, **with Google Gemini integration**.

### Key Improvements

1. **Replaced Custom Crawler with Scrapy Framework**
   - The original `arxiv_crawler.py` was inefficient and error-prone
   - New implementation uses Scrapy spider for robust web scraping
   - Better error handling and retry mechanisms

2. **Google Gemini Integration**
   - Uses `langchain-google-genai` for AI-powered paper analysis
   - Supports latest Gemini models (gemini-2.0-flash-exp by default)
   - Structured output using Pydantic models

3. **Modular Architecture**
   - `daily_arxiv/`: Scrapy-based crawler for arXiv papers
   - `ai/`: LangChain + Google Gemini AI enhancement module
   - `to_md/`: Markdown generation from processed data

4. **Structured AI Output**
   - Uses Pydantic models for consistent AI analysis
   - Structured fields: TL;DR, motivation, method, result, conclusion

5. **Improved Workflow**
   - Single, clean GitHub Actions workflow
   - Better environment variable handling
   - Automatic README updates

### New Project Structure

```
├── .github/workflows/run.yml     # New simplified workflow
├── daily_arxiv/                  # Scrapy crawler module
│   ├── daily_arxiv/
│   │   ├── spiders/arxiv.py      # ArXiv spider
│   │   ├── items.py              # Data items
│   │   ├── pipelines.py          # Processing pipeline
│   │   └── settings.py           # Scrapy settings
│   ├── config.yaml               # Configuration file
│   └── scrapy.cfg                # Scrapy config
├── ai/                           # AI enhancement module (Google Gemini)
│   ├── enhance.py                # Main AI processor
│   ├── structure.py              # Pydantic models
│   ├── system.txt                # AI system prompt
│   └── template.txt              # AI user prompt
├── to_md/                        # Markdown generation
│   ├── convert.py                # Converter script
│   └── paper_template.md         # Paper template
├── data/                         # Generated data files
├── assets/                       # Asset files
├── run.sh                        # Main execution script
├── update_readme.py              # README updater
├── template.md                   # README template
├── readme_content_template.md    # Content template
└── requirements.txt              # Updated dependencies
```

### Configuration Required

To use this rewritten project, you need to set up the following GitHub repository secrets and variables:

**Secrets:**
- `GOOGLE_API_KEY`: Your Google AI API key (get from https://ai.google.dev/)

**Variables:**
- `CATEGORIES`: Comma-separated categories (e.g., "cs.AI,cs.LG,cs.CV,cs.CL")  
- `LANGUAGE`: Output language (e.g., "English", "Chinese", "Traditional Chinese")
- `MODEL_NAME`: Gemini model to use (e.g., "gemini-2.0-flash-exp", "gemini-1.5-pro")
- `EMAIL`: Your email for Git commits
- `NAME`: Your name for Git commits

### Available Gemini Models

You can use the following models by setting the `MODEL_NAME` variable:
- `gemini-2.0-flash-exp` (default, latest experimental model)
- `gemini-1.5-pro` (stable, high-quality model)
- `gemini-1.5-flash` (fast, efficient model)

### What was removed/changed

The following changes were made to integrate Google Gemini:
- Replaced OpenAI integration with Google Gemini
- Updated `requirements.txt` to include `langchain-google-genai`
- Modified `ai/enhance.py` to use `ChatGoogleGenerativeAI`
- Updated workflow to use `GOOGLE_API_KEY` instead of `OPENAI_API_KEY`
- Updated all documentation to reflect Gemini usage

### Next Steps

1. Set up your `GOOGLE_API_KEY` secret in GitHub repository settings
2. Configure the repository variables as described above
3. The new workflow will run daily at 16:30 UTC
4. You can manually trigger the workflow to test it
5. The system will generate daily markdown reports in the `data/` directory
6. README.md will be automatically updated with links to new reports

The project is now ready to run with Google Gemini and should be much more reliable than the previous implementation.

### Getting Google AI API Key

1. Go to https://ai.google.dev/
2. Click "Get API key"
3. Create a new project or select existing one
4. Generate your API key
5. Add it as `GOOGLE_API_KEY` secret in your GitHub repository
