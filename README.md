# QnA System - Retrieval-Augmented Generation with Graph RAG for Intelligent Question Answering

## Problem Statement

"To develop a GraphRAG-based Question Answering system for High School Malayalam medium curriculum."

---

## Objectives

1. To create a digitized and cleaned dataset from the SCERT Malayalam medium 9th grade Social Science textbook.
2. To implement a RAG System that retrieves and generates answers strictly based on textbook knowledge.
3. To construct a comprehensive knowledge graph capturing entities and their relationships from the curriculum.
4. To implement a GraphRAG retrieval mechanism for fetching relevant contextual information.
5. To evaluate the system’s performance against baseline RAG models using quantitative and qualitative metrics.

---

## System Architecture

The QnA System follows a multi-stage pipeline:

1. Document Processing

   * Text extracted from textbook PDFs using Unstructured.io library and preprocessing tools
   * Handles text, tables, and structured content

2. Embedding Generation

   * Text divided into chunks (600 words with 80-word overlap)
   * Embeddings generated using multilingual models
   * Stored in ChromaDB for efficient retrieval

3. RAG Pipeline

   * User query converted into embedding
   * Top relevant chunks retrieved using similarity search
   * Context passed to LLM (Gemini Flash 2.5) for answer generation

4. Graph RAG Enhancement

   * Knowledge graph constructed using entities and relationships
   * Enables better contextual understanding and multi-hop reasoning

5. Answer Generation

   * Combines retrieved chunks and graph relationships
   * Generates accurate answers in Malayalam

---

## Dataset

The system uses:

* SCERT Malayalam medium 9th grade Social Science textbook
* Extracted and cleaned using Unstructured.io library and preprocessing tools

Key Details:

* Chunk size: 600 words
* Overlap: 80 words
* Approximately 100+ text chunks
* Supports tables and structured content

Preprocessing includes:

* Text cleaning
* Chunking
* Embedding generation

---

## Project Structure

Qna_system/
│
├── Graph_RAG/
│   ├── batch_nodes/
│   ├── data/
│   │   ├── ss_1.txt
│   │   └── ss_2.txt
│   ├── graph_storage/
│   ├── notebooks/
│   │   ├── Graph_RAG.ipynb
│   │   ├── Evaluation.ipynb
│   │   └── evaluation_set.csv
│   └── knowledge_graph.html
│
├── RAG/
│   ├── app.py
│   ├── login.py
│   ├── malayalam_docs/
│   │   └── history.pdf
│   └── src/
│       ├── config.py
│       ├── main.py
│       ├── pages/
│       │   ├── chatbot.py
│       │   └── login.py
│
└── README.md

---

Here’s a clean and professional section you can **add to your README** to describe the important files in your project 👇

---

# Important Files Description

## RAG Module
* malayalam_docs/History.pdf
   Dataset - SCERT Malayalam medium 9th standard social science textbook.
    
* app.py
  Main entry point for running the RAG-based QnA system. Handles user queries and connects all components.

* src/main.py
  Core pipeline implementation of the RAG system including document loading, chunking, embedding, and retrieval.

* src/config.py
  Contains configuration settings such as API keys, model parameters, and database paths.

---

## Graph_RAG Module

* notebooks/Graph_RAG.ipynb
  Main notebook implementing the GraphRAG pipeline including graph construction and querying.

* notebooks/Evaluation.ipynb
  Evaluates system performance using different metrics and comparisons with baseline RAG.

* notebooks/evaluation_fixed.csv
  Dataset used for evaluating results and metrics.

* data/ss_1.txt, data/ss_2.txt
  Preprocessed textbook data used for building the knowledge graph.

* graph_storage/
  Stores serialized graph data for reuse and faster loading.

* batch_nodes/
  Contains intermediate node representations used during graph construction.

* knowledge_graph.html
  Visual representation of the constructed knowledge graph for analysis.

---


## Installation

1. Clone the repository

```
git clone https://github.com/AnsuKurian40/Qna_system.git
cd Qna_system
```

2. Install dependencies

```
pip install -r requirements.txt
```

---

## Usage

### Run RAG-based QnA System

```
```
cd RAG
Run chatbot interface
  * streamlit run app.py

---

### Run Graph RAG (Notebook-based)

```
```
* Login to HPC Environment
* Navigate to project folder
  * cd Qna_system/Graph_RAG/notebooks
* jupyter notebook
* Open `Graph_RAG.ipynb`
* Run all cells step-by-step

---

## Technologies Used

* Python
* LangChain / LLM APIs (Gemini, Llama-3.3-70B)
* ChromaDB (Vector Database)
* LlamaIndex
* NetworkX
* Pandas, NumPy
* Streamlit


---

## Future Work

* Reduce response time 
* Expand dataset to more subjects and grades
* Deploy as real-time web application
* Improve efficiency of GraphRAG pipeline
* Expand to other domains.

---

## Contributors

Guide: Dr. Dhanya S. Pankaj

* Ansu Kurian
* Bijisha P B
* Devika Saji
* Jijo V J
