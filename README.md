# Institution-to-ROR Mapping System

This project focuses on extracting institution names from raw LaTeX files and mapping them to the correct [ROR IDs](https://ror.org/), using a Retrieval-Augmented Generation (RAG)-based pipeline implemented with LangChain and Gemini via VertexAI.

------

## Requirements

To run the code, the following two files are required:

1. **`ror_index`**: The method for generating this index is provided in `tex_files/Gemini_version.ipynb`.
2. **`v1.63-2025-04-03-ror-data_schema_v2.json`**: This is the open-source ROR dataset, which can be found at [Zenodo - ROR Data](https://zenodo.org/communities/ror-data/records?q=&l=list&p=1&s=10&sort=newest).

------

## Features Implemented

### 1. Raw LaTeX Preprocessing

- Remove LaTeX comments.
- Handle nested braces and inconsistent encodings.
- Extract relevant content before the abstract section.

### 2. Institution Name Extraction

- Support multiple LaTeX commands (e.g., `\affil{}`, `\institute{}`, etc.).
- Regex-based recursive matching.
- Fallback: extract text before abstract if no institution patterns are found.

### 3. Retrieval System (RAG-based)

- Convert all ROR institution names into vector embeddings using `all-MiniLM-L6-v2`.
- Build a FAISS index for fast top-k similarity search.
- Given an input name (e.g., "MIT"), find the most relevant ROR entries.

### 4. Institution-to-ROR ID Mapping with LangChain

- Uses LangChain’s `RetrievalQA` to combine the query + ROR context + prompt.
- Gemini (via VertexAI) selects the most likely matching ROR ID.
- Supports batch and parallel processing.

------

## ❗ Known Challenges

### ⚠️ 1. Null Values After Institution Extraction

- Some LaTeX files do not contain extractable institution names.
- Need more robust heuristics for fallback logic.

### ⚠️ 2. Sub-Institution Ambiguity

- Departments, labs, and sub-units (e.g., "School of Engineering, Stanford") may interfere with ROR resolution.

------

## Acknowledgments

- [ROR](https://ror.org/) — Research Organization Registry
- [LangChain](https://www.langchain.com/)
- [Google Vertex AI](https://cloud.google.com/vertex-ai)
- Hugging Face `MiniLM` Embeddings
- FAISS for efficient similarity search