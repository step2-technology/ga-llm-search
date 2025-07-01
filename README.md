# GA-LLM-Search System

## Overview

The **GA-LLM-Search** system combines **Genetic Algorithm (GA)** and **Large Language Model (LLM)** to optimize search queries, extract meaningful information, and generate a comprehensive **InfoPack** for deeper analysis and visualization. The system optimizes user queries, filters search results, performs web scraping, extracts structured data, and builds knowledge graphs. The final output is an **InfoPack** containing the search query, structured data, evidence chains, and knowledge graphs.

### Key Features:
- **Search Query Optimization**: Uses Genetic Algorithm (GA) to generate optimized search queries.
- **Search Results Filtering**: LLM filters and ranks search results based on relevance to the user query.
- **Web Scraping**: Supports scraping content from HTML and PDF documents.
- **Structured Data Extraction**: Extracts structured data from web pages using LLM.
- **Knowledge Graph Construction**: Builds knowledge graphs based on the extracted structured data.
- **InfoPack Generation**: Combines all extracted data into a unified **InfoPack**, ready for analysis and visualization.

### Applications:
- **Market Intelligence**: Automatically extract and structure market data, policies, and more for decision-making.
- **Legal Text Analysis**: Analyze legal documents and case studies to extract structured data, such as legal clauses and verdicts.
- **Academic Research**: Helps researchers perform precise document searches, extract useful data, and summarize findings.

## Workflow

```mermaid
graph TD
    A[User Query] --> B[Genetic Algorithm Optimization]
    B --> C[Search Gene Evolution]
    C --> D[Search Results]
    D --> E[Filter Search Results via LLM]
    E --> F[Retain Best Results]
    F --> G[Run Web Scraper for Full Texts]
    G --> H[Text Extraction]
    H --> I[Generate Structured Data via LLM]
    I --> J[Build Knowledge Graph]
    J --> K[Build InfoPack<br>final output]
    K --> L[Export InfoPack to log directory]

    subgraph GA
        A
        B
        C
    end

    subgraph Web Scraping and Data Extraction
        G
        H
        I
        J
    end
````

## Directory Structure

```
ga-llm-search/
├── search_query/                           # Genetic Algorithm and Query Optimization
│   ├── run.py                              # Entry point, runs GA and generates InfoPack
│   ├── search_gene.py                      # Defines search gene and evaluation logic
│   ├── evaluator_with_info_store.py        # Evaluator, scores and stores relevant search results
│   ├── prompts.py                          # Contains various LLM prompt templates
│   └── config.py                           # Configuration file, defines model settings
├── info_store/                             # Stores and processes InfoItems
│   ├── crawler.py                          # Web scraper for fetching content from URLs
│   ├── extractor.py                        # Structured data extractor from fetched content
│   ├── information_store.py                # Information storage, manages and stores InfoItems
│   ├── export_logger.py                    # Export logs, saves fetched data to files
│   ├── info_pack_builder.py                # Builds InfoPack, organizes and saves final info package
│   └── filter_llm_selector.py              # LLM selector to filter the most relevant search results
├── ga_llm/                                 # Genetic Algorithm related code
│   ├── engine.py                           # GA engine, executes the GA process
│   ├── base_gene.py                        # Gene class, defines how to represent a search gene in GA
│   ├── config.py                           # GA configuration, defines parameters like population size, max iterations
│   ├── llm_utils.py                       # LLM utility functions, wraps calls to the LLM interface
│   ├── logging_utils.py                    # Logging utilities for output
│   └── llm_utils.py                       # LLM calling related utilities
└── search_query/config.py                  # Configuration files
```

## Detailed File Descriptions

### 1. **`run.py`**

* **Purpose**: Main entry point to execute the entire pipeline. Runs the genetic algorithm, filters search results, performs web scraping, and extracts structured data. It also generates and saves the InfoPack.
* **Core Functions**:

  * `main(user_query_override=None)` — Starts the entire process: query optimization, search filtering, web scraping, data extraction, and InfoPack creation.
  * `llm_callback(prompt)` — Calls the LLM model to process prompts.

### 2. **`search_gene.py`**

* **Purpose**: Defines `SearchQueryGene`, representing a search gene in GA and handles the gene evolution process.
* **Core Functions**:

  * `rebuild_from_keywords()` — Reconstructs the search query based on keywords.
  * `to_info_item(score)` — Converts the search result into an `InfoItem` object.
  * `to_info_items(score)` — Returns multiple `InfoItem` objects for a set of search results.

### 3. **`evaluator_with_info_store.py`**

* **Purpose**: Evaluates the search gene's performance and stores relevant search results in `InformationStore`.
* **Core Functions**:

  * `score(gene)` — Scores the gene, filters relevant results, and saves them to `InformationStore`.

### 4. **`filter_llm_selector.py`**

* **Purpose**: Filters and ranks search results using LLM, ensuring the most relevant results are returned to the user.
* **Core Functions**:

  * `filter_info_items_via_llm(user_query, llm_fn, num_results=5)` — Filters search results using LLM and ranks them by relevance.

### 5. **`crawler.py`**

* **Purpose**: Web scraper to fetch the content of URLs and extract text. Supports HTML and PDF formats.
* **Core Functions**:

  * `crawl_single(info_item, timeout=15)` — Fetches a single webpage and extracts content.
  * `crawl_all(items, delay=1.0)` — Crawls multiple items and processes each one.

### 6. **`extractor.py`**

* **Purpose**: Extracts structured data from the crawled content using LLM.
* **Core Functions**:

  * `extract_structured_data(item, llm_fn)` — Extracts structured data for a single `InfoItem`.
  * `extract_all(items, llm_fn)` — Extracts structured data for multiple items.

### 7. **`info_pack_builder.py`**

* **Purpose**: Builds the final InfoPack, which includes the query, structured data, knowledge graph, and evidence chain.
* **Core Functions**:

  * `build_info_pack(user_query)` — Builds the final InfoPack from the results.
  * `save_info_pack(info_pack)` — Saves the generated InfoPack as a JSON file.

### 8. **`export_logger.py`**

* **Purpose**: Exports the fetched `InfoItems` to a text file for manual inspection and verification.
* **Core Functions**:

  * `export_info_items(items, log_dir)` — Exports the `InfoItems` to a specified directory.

## System Setup and Running

1. **Prepare the Environment**:

   * Install dependencies: `pip install -r requirements.txt`
   * Configure parameters like `llm_model`, `population_size`, etc., in `config.py`.

2. **Run the System**:

   * Execute the system with a user query:

   ```bash
   python -m search_query.run --query "Impact of US-China trade tariffs on 2025 exports"
   ```

3. **Export InfoItems**:

   * Manually export the processed results:

   ```bash
   python -m info_store.export_logger --export
   ```

## FAQ

1. **How to modify the number of results returned?**

   * Change the `num_results` parameter in `filter_info_items_via_llm` to control how many results the system returns.

2. **How to change the LLM's behavior?**

   * Modify `llm_model`, `llm_temperature`, and `llm_timeout` in `config.py`.

3. **How to debug errors?**

   * Enable debug mode by setting `DEBUG=true` when running the system.

4. **How to optimize GA parameters?**

   * Modify `population_size`, `max_generations`, and other parameters in `config.py`.

---

## Conclusion

The GA-LLM-Search system provides an automated and intelligent approach to search query optimization, web scraping, data extraction, and knowledge graph construction. By leveraging Genetic Algorithms and Large Language Models, this system streamlines the process of gathering, structuring, and visualizing data for various domains such as market intelligence, legal analysis, and academic research.
