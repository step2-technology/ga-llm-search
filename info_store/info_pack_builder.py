# File: info_store/info_pack_builder.py

import os
import json
from datetime import datetime
from info_store.information_store import InformationStore
from info_store.export_logger import ensure_log_dir
from ga_llm.llm_utils import llm_call
from search_query.config import llm_model, llm_temperature, llm_timeout

def build_kg_schema_prompt(user_query: str, structured_data: list) -> str:
    return f"""
    You are a knowledge graph schema designer.

    Based on the structured data below and the original user query, define a GraphQL SDL schema that represents key entities and relationships. Use @node and @relationship directives properly.

    ## User Query:
    {user_query}

    ## Structured Data (JSON):
    {json.dumps(structured_data, indent=2)}

    ## Output Requirements:
    - Output only the GraphQL SDL code
    - Use valid syntax: type definitions, @node, and @relationship(type, direction)
    - Do **NOT** include markdown or code block delimiters (e.g., ` ```graphql `, ` ``` `)
    - Do not include comments, explanations, or extra text
    - Use English for all field and type names

    ## Output:
    """.strip()

def build_evidence_chain_prompt(user_query: str, items_for_llm: list) -> str:
    return f"""
    You are an expert in information retrieval and reasoning. Given the following search results (InfoItems), please generate a structured evidence chain that links each relevant piece of evidence (i.e. search result) to the final conclusion.

    For each InfoItem, evaluate how it supports or contradicts the final conclusion based on the information provided. 

    Please follow the output format strictly to ensure consistency. The output should be a dictionary of evidence, where each item includes:
    - The item_id (unique identifier of the InfoItem).
    - The reasoning for its inclusion (e.g., "supports the claim", "provides background information", etc.).
    - The relationship of the evidence to the overall conclusion (e.g., "directly supports", "indirectly supports", "contradicts", etc.).

    ## User Query:
    {user_query}

    ## InfoItems (Search Results):
    {json.dumps(items_for_llm, indent=2)}

    ## Output Format:
    {{
    "evidence_chain": [
        {{
        "item_id": "<Unique ID of the InfoItem>",
        "reasoning": "<How this evidence supports/contradicts the conclusion>",
        "relationship": "<Directly supports, provides background, contradicts, etc.>"
        }},
        ...
    ]
    }}

    ## Notes:
    - The output should be a well-structured JSON object, formatted as shown above.
    - Do not include markdown, explanations, or extra text.
    - Provide concise, clear reasoning for each piece of evidence.
    """

def llm(prompt: str) -> str:
    return llm_call(
        prompt=prompt,
        model=llm_model,
        temperature=llm_temperature,
        timeout=llm_timeout
    )


def build_info_pack(user_query: str) -> dict:
    info_items = InformationStore.get_all()

    if not info_items:
        raise ValueError("InformationStore is empty. Cannot build InfoPack.")

    # Collect top-level metadata
    dimension = info_items[0].dimension
    keywords = info_items[0].keywords
    structured_data = [item.structured_data for item in info_items if item.structured_data]

    print("📐 Generating GraphQL knowledge graph schema...")
    kg_prompt = build_kg_schema_prompt(user_query, structured_data)
    knowledge_graph_schema = llm(kg_prompt).strip()

    # Prepare the InfoItems for LLM input
    items_for_llm = [{
        "item_id": item.id,
        "snippet": item.snippet,
        "structured_data": item.structured_data
    } for item in info_items]

    # Generate the evidence chain from the LLM
    print("📐 Generating evidence chain...")
    evidence_chain_prompt = build_evidence_chain_prompt(user_query, items_for_llm)
    evidence_chain = llm(evidence_chain_prompt).strip()

    # Construct info pack object
    info_pack = {
        "user_query": user_query,
        "dimension": dimension,
        "keywords": keywords,
        "info_items": [item.to_dict() for item in info_items],
        "structured_data": structured_data,
        "knowledge_graph_schema": knowledge_graph_schema, 
        "evidence_chain": evidence_chain
    }

    return info_pack

def save_info_pack(info_pack: dict):
    ensure_log_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join("info_store/log", f"info_pack_{ts}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(info_pack, f, ensure_ascii=False, indent=2)

    print(f"✅ InfoPack saved to {path}")


# Optional CLI entry point
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python info_store/info_pack_builder.py '<User Query>'")
    else:
        user_query = sys.argv[1]
        pack = build_info_pack(user_query)
        save_info_pack(pack)
