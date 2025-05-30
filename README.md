# GA-LLM: Hybrid Optimization Framework for Structured Tasks

> Genetic Algorithm + LLM + Task-Aware Encoding

**Author:** Jonas Lin & Jacky Cen  
**Version:** 0.2  
**License:** MIT

---

## 🔍 What is GA-LLM?

GA-LLM is a modular hybrid optimization framework that combines **Genetic Algorithms (GA)** with **Large Language Models (LLMs)** to solve complex, structure-oriented content generation tasks. The system supports tasks like travel itinerary planning, academic proposal writing, and business reporting.

This project is designed to **harness the creativity of LLMs** and the **convergence efficiency of evolutionary strategies**, enabling automatic generation, mutation, and selection of structured outputs under constraints.

---

## ✨ Core Features

- ✅ Modular GA framework with abstract `Gene` class
- ✅ LLM-driven population generation, mutation, and crossover
- ✅ Prompt templating system with variable injection
- ✅ Multi-level logging with per-run `.log` files
- ✅ Parallelized scoring and generation with thread pools
- ✅ Constraint validator plug-in architecture
- ✅ Customizable scoring via LLM prompts

---

## 🗂️ Project Structure

```

ga-llm/  
├── ga_llm/ # Core GA-LLM framework  
│ ├── base_gene.py # Abstract base class  
│ ├── config.py # Evolution strategy configuration  
│ ├── engine.py # Hybrid evolutionary engine  
│ ├── evaluation.py # LLM-based scoring mechanism  
│ ├── constraints.py # Constraint checker interface  
│ ├── llm_utils.py # LLM calling interface  
│ ├── logging_utils.py # Console + file logger  
│ └── prompts/ # Prompt template manager  
│ └── template_manager.py  
├── demo/ # Task-specific examples  
│ └── travel_demo.py # Travel itinerary optimization  
├── logs/ # Auto-generated log files  
├── requirements.txt  
├── README.md  
└── LICENSE

````

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
````

### 2. Run the travel itinerary example

```bash
python demo/travel_demo.py
```

You will get an optimized 4-day trip to Shanghai using LLM-guided mutation and crossover.

---

## 🧠 Sample Output (Excerpt)

```text
Travel Itinerary:
- Days: 4 day program
- Hotels: Shanghai Family Hotel
- Total Cost: ¥4890.00
Detailed Schedule:
[
  {
    "date": "2024-07-01",
    "activities": [
      {"time": "09:00", "location": "Shanghai Museum", "description": "..."}
    ]
  },
  ...
]
```

---

## 🧩 Add Your Own Task

To support a new task:

- Implement a new `YourTaskGene(BaseGene)` class
    
- Define `to_text`, `parse_from_text`, `crossover`, `mutate`
    
- Provide appropriate prompt templates and constraints
    
- Plug into the framework via `HybridEvolutionEngine`
    

---

## 🤝 Contributing

Contributions are welcome! Please:

- Fork the repo
    
- Create a feature branch
    
- Open a pull request with detailed description
    

We welcome new task types, new scoring logic, prompt improvements, and performance enhancements.

---

## 📄 License

This project is licensed under the MIT License.  
© 2025 Jonas Lin & Jacky Cen
