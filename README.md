# AI-Driven Automated Test Case Generation with RAG

A comprehensive system for automatically generating test cases for software applications using Retrieval Augmented Generation (RAG) and Large Language Models (LLMs).

## Overview

This project implements an intelligent test generation system that:
- **Understands code context** through semantic search and embeddings
- **Retrieves relevant examples** using RAG-based retrieval
- **Generates comprehensive tests** including unit, integration, and edge case tests
- **Evaluates test quality** with automated metrics
- **Supports multiple languages** (Python, JavaScript, Java, C++, TypeScript)

## Architecture

```
┌─────────────────┐
│  Source Code    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Code Parser    │ (Extract functions, classes, docs)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text Chunking  │ (Split into semantic chunks)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Embeddings     │ (Create vector representations)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vector Store   │ (FAISS/ChromaDB)
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────┐
│  RAG Retrieval  │────▶│     LLM      │
└─────────────────┘     │ (GPT-4/Claude)│
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Generated   │
                        │    Tests     │
                        └──────────────┘
```

## Features

### 1. Code Understanding
- **AST-based parsing** for accurate code structure extraction
- **Function and class detection** with metadata
- **Dependency analysis** (imports, decorators)
- **Docstring extraction** for context

### 2. RAG-Based Retrieval
- **Semantic code search** using embeddings
- **Context-aware retrieval** of relevant code snippets
- **Similarity-based ranking** of code examples
- **Multi-language support**

### 3. Test Generation
- **Unit tests**: Test individual functions/methods
- **Integration tests**: Test component interactions
- **Edge case tests**: Boundary conditions, error handling
- **Negative tests**: Invalid inputs and error scenarios

### 4. Quality Evaluation
- **Automated metrics**: Test count, assertion count
- **Best practice detection**: Fixtures, mocks, parametrization
- **Quality scoring**: 0-100 score based on test characteristics
- **Coverage analysis**: Identify untested code paths

## Installation

### Prerequisites
- Python 3.9+
- pip or conda
- OpenAI API key or Anthropic API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-execution
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys:
```bash
# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env
# Or for Anthropic Claude
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

## Usage

### Quick Start with Jupyter Notebook

1. Launch Jupyter:
```bash
jupyter notebook rag_test_generation.ipynb
```

2. Run all cells or follow the step-by-step guide in the notebook

### Basic Usage

```python
from rag_test_generation import RAGTestGenerationPipeline, RAGConfig

# Initialize configuration
config = RAGConfig(
    llm_model="gpt-4-turbo-preview",
    embedding_model="sentence-transformers/all-mpnet-base-v2",
    top_k_retrieval=5
)

# Create pipeline
pipeline = RAGTestGenerationPipeline(config)

# Index your codebase
pipeline.index_codebase("./your_code_directory")

# Generate tests for a function
code = """
def calculate_average(numbers: List[float]) -> float:
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
"""

tests = pipeline.generate_tests_for_function(
    code=code,
    function_name="calculate_average",
    test_types=["unit", "edge_case"]
)

# Tests are automatically saved to ./generated_tests/
```

### Generate Tests for Entire File

```python
# Generate tests for all functions in a file
all_tests = pipeline.generate_tests_for_file(
    file_path="./my_module.py",
    output_dir="./tests"
)
```

### Search Codebase

```python
# Search for relevant code examples
results = pipeline.vector_manager.retrieve_relevant_context(
    query="error handling for division by zero",
    k=5
)
```

## Configuration Options

```python
@dataclass
class RAGConfig:
    # Model settings
    llm_model: str = "gpt-4-turbo-preview"
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    temperature: float = 0.7
    max_tokens: int = 2000

    # Chunking settings
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # RAG settings
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7

    # Vector store
    vector_store_type: str = "faiss"  # "faiss" or "chroma"
    persist_directory: str = "./vector_store"

    # Test generation
    test_types: List[str] = ["unit", "integration", "edge_case"]
    include_edge_cases: bool = True
    include_negative_tests: bool = True
```

## Project Structure

```
ai-execution/
├── rag_test_generation.ipynb  # Main Jupyter notebook
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .env                        # API keys (create this)
├── sample_code/               # Example code for testing
│   └── calculator.py
├── generated_tests/           # Generated test files
├── vector_store/              # Persisted embeddings
└── reports/                   # Evaluation reports
```

## Examples

### Example 1: Simple Function

Input:
```python
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

Generated Test:
```python
import pytest

def test_add_positive_numbers():
    """Test addition of positive numbers"""
    assert add(2, 3) == 5
    assert add(10, 20) == 30

def test_add_negative_numbers():
    """Test addition with negative numbers"""
    assert add(-5, 3) == -2
    assert add(-10, -20) == -30

def test_add_zero():
    """Test addition with zero"""
    assert add(0, 5) == 5
    assert add(5, 0) == 5
    assert add(0, 0) == 0

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (100, 200, 300),
    (-50, 50, 0)
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected
```

### Example 2: Class with Methods

Input:
```python
class Calculator:
    def __init__(self):
        self.history = []

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        result = a / b
        self.history.append(result)
        return result
```

Generated Test:
```python
import pytest
from unittest.mock import Mock

class TestCalculator:
    @pytest.fixture
    def calculator(self):
        return Calculator()

    def test_divide_normal(self, calculator):
        """Test normal division"""
        assert calculator.divide(10, 2) == 5.0
        assert calculator.divide(15, 3) == 5.0

    def test_divide_by_zero(self, calculator):
        """Test division by zero raises error"""
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
            calculator.divide(10, 0)

    def test_divide_updates_history(self, calculator):
        """Test that division updates history"""
        calculator.divide(10, 2)
        assert len(calculator.history) == 1
        assert calculator.history[0] == 5.0

    def test_divide_edge_cases(self, calculator):
        """Test edge cases"""
        assert calculator.divide(0, 5) == 0.0
        assert calculator.divide(1, 3) == pytest.approx(0.333, rel=1e-2)
```

## Evaluation Metrics

The system automatically evaluates generated tests on:

- **Test Count**: Number of test functions generated
- **Assertion Count**: Number of assertions per test
- **Best Practices**: Use of fixtures, mocks, parametrization
- **Quality Score**: Overall score from 0-100
- **Coverage**: Estimated code coverage

Example Report:
```
Test Evaluation Report
Function: calculate_average

┌───────────┬───────┬────────────┬───────────────┐
│ Test Type │ Tests │ Assertions │ Quality Score │
├───────────┼───────┼────────────┼───────────────┤
│ unit      │   5   │     12     │    85.0/100   │
│ edge_case │   4   │     10     │    78.0/100   │
└───────────┴───────┴────────────┴───────────────┘

Overall Metrics:
  Total Tests: 9
  Total Assertions: 22
  Average Quality: 81.5/100
```

## Advanced Features

### 1. Batch Test Generation
```python
functions = [
    {'name': 'func1', 'code': '...'},
    {'name': 'func2', 'code': '...'}
]
results = batch_generate_tests(functions)
```

### 2. Fine-tuning Dataset Preparation
```python
# Prepare dataset for LLM fine-tuning
prepare_finetuning_dataset(code_test_pairs, "training_data.jsonl")
```

### 3. Custom Prompts
```python
# Customize test generation prompts
generator.prompts['custom'] = PromptTemplate(
    input_variables=["context", "code"],
    template="Your custom prompt here..."
)
```

### 4. Integration with CI/CD
```python
# Run in CI/CD pipeline
if __name__ == "__main__":
    pipeline = RAGTestGenerationPipeline(config)
    pipeline.index_codebase("./src")

    # Generate tests for changed files
    changed_files = get_changed_files()  # From git
    for file in changed_files:
        pipeline.generate_tests_for_file(file)
```

## Supported Languages

- ✅ Python
- ✅ JavaScript/TypeScript
- ✅ Java
- ✅ C++
- 🚧 Go (coming soon)
- 🚧 Rust (coming soon)

## Performance Tips

1. **Use local embeddings**: HuggingFace models are free and fast
2. **Persist vector store**: Save and reuse embeddings
3. **Batch processing**: Generate tests for multiple files at once
4. **Cache results**: Avoid regenerating tests for unchanged code
5. **Use appropriate chunk sizes**: Adjust based on code complexity

## Troubleshooting

### API Rate Limits
- Use exponential backoff
- Switch to cheaper models for embeddings
- Batch requests when possible

### Memory Issues
- Reduce chunk_size
- Process files individually
- Use FAISS instead of ChromaDB for large codebases

### Poor Test Quality
- Increase top_k_retrieval for more context
- Provide better code documentation
- Fine-tune on your specific codebase
- Adjust temperature for more creative/conservative tests

## Contributing

Contributions are welcome! Areas for improvement:

- Support for more programming languages
- Integration with test runners (pytest, jest, junit)
- Coverage analysis and gap detection
- Test maintenance and updating
- Performance optimizations
- Better evaluation metrics

## License

MIT License - See LICENSE file for details

## Citation

If you use this work in your research, please cite:

```bibtex
@software{rag_test_generation,
  title={AI-Driven Automated Test Case Generation with RAG},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/ai-execution}
}
```

## Acknowledgments

- LangChain for RAG framework
- OpenAI/Anthropic for LLM APIs
- HuggingFace for embedding models
- The open-source community

## Support

For questions and issues:
- Open an issue on GitHub
- Check the documentation in the notebook
- Review examples in the `examples/` directory

## Roadmap

- [ ] Multi-language support expansion
- [ ] Integration with popular test frameworks
- [ ] Real-time test execution and validation
- [ ] Coverage-guided test generation
- [ ] Test mutation and evolution
- [ ] Web UI for easier interaction
- [ ] VS Code extension
- [ ] GitHub Actions integration

## References

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [Retrieval Augmented Generation Paper](https://arxiv.org/abs/2005.11401)
- [Software Testing Best Practices](https://pytest.org/)
