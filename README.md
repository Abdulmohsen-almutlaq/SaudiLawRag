# Saudi Law RAG Assistant (Arabic Legal AI)

A smart Arabic-speaking legal assistant using **RAG (Retrieval-Augmented Generation)** to provide precise legal insights based on structured Saudi regulations.

## Core Idea

The assistant is designed to enhance access to legal knowledge by leveraging:
- **Structured Saudi regulations** (parsed from official websites and saved as JSON)
- **Fast and efficient vector search** (FAISS) for retrieving the most relevant legal articles
- **Advanced Arabic-native language model**: **[ALLaM-7B-Instruct](https://huggingface.co/ALLaM-AI/ALLaM-7B-Instruct-preview)** from SDAIA

By combining these components, the system ensures that users receive accurate, legally grounded answers with proper citations to the original law name, chapter, and article number.

## Features

- Accepts Arabic legal questions (no domain selection required)
- Automatically identifies and retrieves the most relevant **articles**
- Answers questions using structured Saudi laws with Arabic legal reasoning
- Cites the original law name, chapter, and article number
- Optimized for **ALLaM-7B-Instruct** model

## Data Source and Format

**Source**: Official Saudi Ministry of Justice website  
**Workflow**:
- Scrape or download regulations from: [https://laws.moj.gov.sa](https://laws.moj.gov.sa)
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
