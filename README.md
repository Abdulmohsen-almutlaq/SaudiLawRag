# Saudi Law RAG Assistant (Arabic Legal AI)

A smart Arabic-speaking legal assistant using **RAG (Retrieval-Augmented Generation)** built on:

- Structured Saudi regulations (parsed from official websites and saved as JSON)
- Fast vector search (FAISS)
- Powerful Arabic-native language model: **[ALLaM-7B-Instruct](https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview)** from SDAIA

## Features

- Accepts Arabic legal questions (no domain selection required)
- Automatically identifies and retrieves the most relevant **articles**
- Answers questions using structured Saudi laws with Arabic legal reasoning
- Cites the original law name, chapter, and article number
- Works offline using a 3070 Ti (via quantization or 4-bit inference)
- Optimized for **ALLaM-7B-Instruct** model

## Data Source and Format

**Source**: Official Saudi Ministry of Justice website  
**Workflow**:
- Scrape or download regulations from: https://laws.moj.gov.sa
- Convert into structured JSON format like:

```json
[
  {
    "law_title": "نظام العمل",
    "chapters": [
      {
        "chapter_title": "الفصل الأول",
        "articles": [
          {
            "article_number": 74,
            "text": "يجوز لأي من الطرفين إنهاء العقد خلال فترة التجربة بدون إشعار..."
          }
        ]
      }
    ]
  }
]
