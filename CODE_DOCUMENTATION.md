# Legal Document Review System - Complete Code Documentation

This document provides detailed explanations of every component, class, and method in the Legal Document Review and Contract Analysis Agent.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Cell-by-Cell Explanation](#cell-by-cell-explanation)
3. [Class Documentation](#class-documentation)
4. [Key Algorithms](#key-algorithms)
5. [Data Flow](#data-flow)

---

## Architecture Overview

The system consists of 6 main components:

```
┌─────────────────────────────────────────────────────────────┐
│                  LegalAgentConfig                           │
│  (Central configuration for all components)                 │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬─────────────┬──────────────┬─────────┐
    │                 │             │              │         │
    v                 v             v              v         v
┌──────────┐  ┌─────────────┐  ┌─────────┐  ┌──────────┐  ┌───────────┐
│  Data    │  │   LLM Fine  │  │   RAG   │  │   Risk   │  │ Evaluator │
│Collector │  │   Tuner     │  │  System │  │ Assessor │  │           │
└──────────┘  └─────────────┘  └─────────┘  └──────────┘  └───────────┘
```

---

## Cell-by-Cell Explanation

### Cell 1: Library Installation

**Purpose**: Install all required Python packages

**What it does**:
```python
!{sys.executable} -m pip install -q ...
```
- Uses `sys.executable` to ensure packages install for correct Python version
- `-q` flag = quiet mode (less verbose output)
- Installs 10 packages: pdfminer.six, transformers, nltk, datasets, sentence-transformers, faiss-cpu, torch, scikit-learn, tensorboard, accelerate

**Why each library**:
- `pdfminer.six`: Extract text from PDF legal documents
- `transformers`: Access pre-trained AI models (BERT, etc.)
- `nltk`: Text processing (tokenization, stopword removal)
- `datasets`: Manage training data efficiently
- `sentence-transformers`: Convert text to numerical vectors for similarity
- `faiss-cpu`: Fast vector search (millions of documents in milliseconds)
- `torch`: Deep learning framework (backend for transformers)
- `scikit-learn`: Evaluation metrics (precision, recall, F1)
- `tensorboard`: Visualize training progress
- `accelerate`: Speed up model training

---

### Cell 2: Import Libraries

**Purpose**: Import all libraries and download NLTK data

**Import Categories**:

1. **Standard Library** (os, re, json, etc.)
   - Built-in Python modules for file operations and data handling

2. **PDF Processing** (pdfminer)
   - `extract_text(file_path)`: Extracts text from PDF files

3. **NLP** (nltk)
   - `word_tokenize`: Splits text into words
   - `sent_tokenize`: Splits text into sentences
   - `stopwords`: Common words to filter (the, is, at)

4. **Machine Learning** (transformers, datasets, etc.)
   - `AutoTokenizer`: Automatically loads correct tokenizer for any model
   - `AutoModelForMaskedLM`: Loads models for language understanding
   - `Trainer`: High-level interface for training models
   - `SentenceTransformer`: Creates semantic embeddings
   - `faiss`: Vector similarity search engine

**NLTK Downloads**:
```python
nltk.download('punkt', quiet=True)  # Tokenization models
nltk.download('stopwords', quiet=True)  # Common words list
nltk.download('averaged_perceptron_tagger', quiet=True)  # POS tagging
```

---

### Cell 3: Configuration Class

**Purpose**: Centralize all configurable parameters

**Class**: `LegalAgentConfig`

**Parameters Explained**:

```python
data_dir: str = "./legal_data"
# Where to find/store legal documents
# Relative path = works anywhere

model_dir: str = "./models"
# Where to save trained models and FAISS indexes
# Separate from data for organization

output_dir: str = "./output"
# Where to save generated reports
# Easy to find and share results

base_model_name: str = "nlpaueb/legal-bert-base-uncased"
# Legal-specific BERT model from Hugging Face
# Pre-trained on legal text = better understanding of legal language

embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
# Converts sentences to 384-dimensional vectors
# Lightweight but accurate for similarity search

num_train_epochs: int = 3
# How many times to go through entire dataset
# 3 = good balance (not too little, not overfitting)

per_device_train_batch_size: int = 8
# Process 8 documents at once during training
# Larger = faster but needs more memory

learning_rate: float = 2e-5
# How much to adjust model weights per step
# 0.00002 = standard for fine-tuning BERT

max_seq_length: int = 512
# Maximum tokens per document
# BERT's max = 512, longer documents are truncated

top_k_retrieval: int = 3
# Retrieve top 3 most similar documents
# Provides context without overwhelming

confidence_threshold: float = 0.7
# Only flag risks with 70%+ confidence
# Reduces false positives
```

**__post_init__ Method**:
```python
def __post_init__(self):
    for directory in [self.data_dir, self.model_dir, self.output_dir]:
        Path(directory).mkdir(parents=True, exist_ok=True)
```
- Runs automatically after `__init__`
- Creates all directories if they don't exist
- `parents=True`: Creates parent directories too
- `exist_ok=True`: Doesn't error if already exists

---

## Class Documentation

### 1. LegalDataCollector

**Purpose**: Load, collect, and preprocess legal documents

#### Methods:

##### `__init__(self, config)`
Initializes the collector with configuration

**Instance Variables**:
```python
self.config = config  # Store config for later use
self.supported_extensions = ['.txt', '.md', '.pdf']  # Accepted file types
self.legal_texts = []  # Will store document text content
self.metadata = []  # Will store document info (filename, source, etc.)
```

##### `load_text_content(self, file_path) -> Optional[str]`
Loads text from a single file

**Algorithm**:
```
1. Check file extension
2. If PDF:
   - Use pdfminer.extract_text()
   - Handles complex PDF layouts
3. If TXT/MD:
   - Open with UTF-8 encoding
   - Read entire file
4. If error:
   - Print warning
   - Return None (don't crash)
5. Return text content
```

**Error Handling**:
- `try-except`: Catches all errors
- `errors='ignore'`: Skips undecodable characters
- Returns `None` on failure (graceful degradation)

##### `collect_documents(self, source_path) -> int`
Collects documents from file or directory

**Algorithm**:
```
1. Check if path exists
   - If not: warn and return 0

2. If path is a FILE:
   - Load the single file
   - Add to legal_texts list
   - Add metadata (source, type)
   - Return 1

3. If path is a DIRECTORY:
   - Use rglob('*') to find all files recursively
   - For each file:
     - Check if supported extension
     - Load content
     - Add to legal_texts and metadata
     - Increment counter
   - Return total count

4. Return number of documents loaded
```

**Recursive Search**:
```python
for file_path in source.rglob('*'):
```
- `rglob('*')`: Recursive glob - finds ALL files in all subdirectories
- Unlike `glob()`, which only searches current directory
- Example: finds `./legal_data/contracts/2024/file.pdf`

##### `preprocess_text(self, text, remove_stopwords=False) -> str`
Cleans and prepares text for analysis

**Steps**:

1. **Remove Extra Whitespace**:
```python
text = re.sub(r'\s+', ' ', text).strip()
```
- `\s+`: Matches one or more whitespace chars (spaces, tabs, newlines)
- Replaces with single space
- `.strip()`: Removes leading/trailing whitespace

2. **Remove Special Characters** (but keep legal punctuation):
```python
text = re.sub(r'[^a-zA-Z0-9\s.,;:()\-\'\"]+', '', text)
```
- `[^...]`: Match anything NOT in brackets (negation)
- Keeps: letters, numbers, spaces, and important legal punctuation
- Removes: emoji, weird symbols, control characters

3. **Optionally Remove Stopwords**:
```python
if remove_stopwords:
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    text = ' '.join([w for w in words if w not in stop_words])
```
- Gets list of common English words (the, is, at, which, on, etc.)
- Tokenizes text into words
- Filters out stopwords
- Rejoins remaining words
- **Note**: Usually NOT used for legal text (context matters)

##### `create_sample_documents(self)`
Creates 4 realistic sample legal documents

**Sample Documents**:
1. **Employment Contract**: Has IP clause, non-compete, termination
2. **Residential Lease**: Missing liability clause (intentional for testing)
3. **Software License**: Has "AS IS" clause and GDPR warning
4. **NDA**: Missing breach handling provisions

**Why These Samples**:
- Cover different legal document types
- Include both complete and incomplete clauses
- Intentionally have risks for testing detection
- Realistic language and structure

---

### 2. LegalLLMFineTuner

**Purpose**: Fine-tune language models on legal text

#### Key Concepts:

**Masked Language Modeling (MLM)**:
- Training task: Predict masked words
- Example: "The [MASK] shall terminate with 30 days notice"
- Model learns: [MASK] = "agreement" or "contract"
- Improves understanding of legal language patterns

#### Methods:

##### `load_model(self)`
Loads pre-trained model with fallback

**Algorithm**:
```
1. Try to load legal-bert (legal-specific model)
2. If fails:
   - Print warning
   - Fallback to distilbert-base-uncased
3. Load both:
   - Tokenizer (converts text to numbers)
   - Model (the actual AI)
4. Print confirmation
```

**Why Fallback**:
- legal-bert might not be available
- Requires large download
- distilbert works well as general alternative

##### `prepare_dataset(self, texts) -> Tuple[Dataset, Dataset]`
Converts text documents into training data

**Steps**:

1. **Create Dataset Object**:
```python
data = {'text': texts}
raw_dataset = Dataset.from_dict(data)
```
- Wraps list in Hugging Face Dataset format
- Enables efficient batching and processing

2. **Tokenize**:
```python
def tokenize_function(examples):
    return self.tokenizer(
        examples['text'],
        truncation=True,  # Cut off at max_length
        padding='max_length',  # Pad shorter sequences
        max_length=self.config.max_seq_length  # 512 tokens
    )
```
- Converts words to token IDs
- `truncation`: Cuts long documents at 512 tokens
- `padding`: Adds special [PAD] tokens to short documents
- Result: All sequences are exactly 512 tokens

3. **Split Train/Eval**:
```python
if len(tokenized_dataset) > 1:
    split = tokenized_dataset.train_test_split(test_size=0.2, seed=42)
    train_dataset = split['train']  # 80% for training
    eval_dataset = split['test']  # 20% for evaluation
```
- 80/20 split is standard
- `seed=42`: Ensures same split every time (reproducibility)
- Need at least 2 documents for meaningful split

##### `train(self, train_dataset, eval_dataset)`
Executes the fine-tuning process

**Training Arguments Explained**:
```python
TrainingArguments(
    output_dir="./models/checkpoints",  # Save checkpoints here
    overwrite_output_dir=True,  # Replace old checkpoints
    num_train_epochs=3,  # 3 passes through data
    per_device_train_batch_size=8,  # 8 docs per batch
    eval_strategy="epoch",  # Evaluate after each epoch
    save_strategy="epoch",  # Save after each epoch
    logging_steps=10,  # Log metrics every 10 steps
    save_total_limit=2,  # Keep only 2 recent checkpoints
    load_best_model_at_end=True,  # Load best performing model
    report_to="tensorboard"  # Send metrics to TensorBoard
)
```

**Data Collator**:
```python
DataCollatorForLanguageModeling(
    tokenizer=self.tokenizer,
    mlm=True,  # Masked Language Modeling
    mlm_probability=0.15  # Mask 15% of tokens
)
```
- Automatically creates training examples
- Randomly masks 15% of tokens
- Model learns to predict masked tokens

**Training Process**:
```
For each epoch:
    For each batch:
        1. Get 8 documents
        2. Randomly mask 15% of tokens
        3. Feed to model
        4. Model predicts masked tokens
        5. Calculate loss (how wrong was it?)
        6. Adjust model weights
        7. Log metrics

    After epoch:
        - Evaluate on eval set
        - Save checkpoint
        - Update best model if improved
```

---

### 3. LegalRAGSystem

**Purpose**: Retrieval-Augmented Generation for document similarity

**RAG Concept**:
- **Retrieval**: Find similar documents from knowledge base
- **Augmentation**: Add retrieved docs as context
- **Generation**: Use context to improve analysis

#### How It Works:

**Document Embedding**:
```
Legal Document (text)
         ↓
  SentenceTransformer
         ↓
  384-dimensional vector
  [0.12, -0.43, 0.87, ...]
         ↓
  FAISS Index (fast search)
```

**Similarity Search**:
```
Query: "intellectual property clause"
         ↓
  Convert to vector
         ↓
  FAISS finds nearest neighbors
         ↓
  Returns top-k most similar documents
```

#### Methods:

##### `initialize_embedding_model(self)`
Loads the sentence transformer model

```python
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```
- Model converts sentences to 384-D vectors
- Trained on millions of sentence pairs
- Captures semantic meaning (not just keywords)

**Example**:
- "terminate agreement" and "end contract" → similar vectors
- "terminate agreement" and "software bug" → different vectors

##### `create_index(self, documents, metadata)`
Creates searchable index from documents

**Algorithm**:
```
1. For each document:
   - Convert to 384-D vector using embedding model

2. Create FAISS index:
   - IndexFlatL2 = exact search using L2 distance
   - Add all vectors to index

3. Store:
   - Original documents (for retrieval)
   - Metadata (for reference)
```

**FAISS IndexFlatL2**:
- **Flat**: No compression (exact search)
- **L2**: Euclidean distance metric
- Formula: distance = √(Σ(a[i] - b[i])²)
- Smaller distance = more similar

##### `retrieve(self, query, k) -> List[Dict]`
Finds k most similar documents to query

**Steps**:
```
1. Convert query to vector
   query = "non-compete clause"
   vector = [0.23, -0.15, 0.67, ...]

2. Search FAISS index
   distances, indices = index.search(vector, k=3)

3. Get top-3 results:
   - Index 5: distance=0.12 (very similar)
   - Index 2: distance=0.45 (somewhat similar)
   - Index 7: distance=0.89 (less similar)

4. Retrieve actual documents
   - Get documents[5], documents[2], documents[7]
   - Get metadata for each

5. Calculate similarity score
   similarity = 1 / (1 + distance)
   - distance=0 → similarity=1.0 (identical)
   - distance=1 → similarity=0.5
   - distance=10 → similarity=0.09

6. Return results with metadata
```

##### `save_index(self, path)` and `load_index(self, path)`
Persist index to disk for reuse

**Save Process**:
```
1. Save FAISS index binary file
   - Contains all vectors and search structure
   - Fast to load (no recomputation)

2. Save JSON file with:
   - Original documents
   - Metadata

Directory structure:
./models/faiss_index/
├── index.faiss  (binary vector index)
└── documents.json  (original text + metadata)
```

**Benefits**:
- Don't need to re-embed documents
- Can distribute pre-built indexes
- Faster startup time

---

### 4. LegalRiskAssessor

**Purpose**: Identify legal risks in documents

#### Risk Detection Strategy:

**Two Types of Risks**:
1. **Presence Risks** (inverse=False): Flag if pattern IS found
   - Example: "AS IS" clause → warranty disclaimer risk

2. **Absence Risks** (inverse=True): Flag if pattern NOT found
   - Example: No "termination" clause → missing termination risk

#### Risk Categories Explained:

##### 1. Missing Termination Clause (High Severity)
```python
{
    "patterns": [r"\b(termination|terminate|cancel|cancellation)\b"],
    "inverse": True
}
```
**What it detects**: Contracts WITHOUT termination language
**Why it matters**: Parties need clear exit strategy
**Detection**: Searches for termination-related words; flags if NONE found

##### 2. Missing Liability Clause (High Severity)
```python
{
    "patterns": [r"\b(liability|liable|indemnif|damages)\b"],
    "inverse": True
}
```
**What it detects**: Contracts WITHOUT liability limits
**Why it matters**: Unlimited liability = major financial risk
**Detection**: Searches for liability language; flags if NONE found

##### 3. Ambiguous Language (Medium Severity)
```python
{
    "patterns": [
        r"\b(may|might|could|possibly|perhaps)\b",
        r"\b(TBD|as agreed)\b"
    ],
    "inverse": False
}
```
**What it detects**: Vague or uncertain terms
**Why it matters**: Ambiguity leads to disputes
**Examples**:
- "Party may provide service" → unclear obligation
- "Price TBD" → undefined critical term

##### 4. Compliance Warning (High Severity)
```python
{
    "patterns": [
        r"\b(WARNING|NOTICE|CAUTION)\b",
        r"\b(GDPR|compliance|violation)\b"
    ]
}
```
**What it detects**: Explicit warnings or regulatory mentions
**Why it matters**: Could indicate legal compliance issues
**Examples**:
- "WARNING: May not comply with GDPR"
- "NOTICE: Potential regulatory violation"

#### Methods:

##### `analyze_document(self, document) -> Dict`
Performs comprehensive risk analysis

**Algorithm**:
```
For each risk category:
    1. Initialize pattern_found = False
    2. Initialize matched_snippets = []

    3. For each pattern in category:
       - Search document for pattern
       - If match found:
         * Set pattern_found = True
         * Extract surrounding context (±100 chars)
         * Add to matched_snippets

    4. Determine if should flag:
       - If inverse=True: flag if pattern_found is False
       - If inverse=False: flag if pattern_found is True

    5. If flagging:
       - Create risk entry
       - Include matched text snippets
       - Use RAG to find similar documents
       - Add RAG context to entry

    6. Add to risks_found list

Return summary:
    - Total risks
    - Breakdown by severity
    - Detailed risk entries
```

**RAG Integration**:
```python
if self.rag_system and matched_snippets:
    query = matched_snippets[0]  # Use first matched text
    rag_results = self.rag_system.retrieve(query, k=2)
```
- Takes matched text as query
- Finds 2 similar documents
- Provides additional context/examples
- Helps understand if risk is common

##### `generate_report(self, analysis_results, document_name) -> str`
Creates formatted report

**Report Structure**:
```
================================================================================
LEGAL DOCUMENT RISK ASSESSMENT REPORT
Document: employment_contract.txt
================================================================================

EXECUTIVE SUMMARY
----------------------------------------
Total Risks Identified: 3
  • High Severity: 1
  • Medium Severity: 2
  • Low Severity: 0

DETAILED FINDINGS
================================================================================

1. Ambiguous Language [Medium Severity]
----------------------------------------
Description: Contains ambiguous or uncertain terms

Relevant Text Excerpts:
  [1] ...Employee may be eligible for bonuses at management's discretion...
  [2] ...Company could modify benefits as needed...

Related Legal Documents (RAG):
  • employment_contract_2.txt (Similarity: 0.92)
    This Employment Agreement contains provisions for...
  • contract_template.txt (Similarity: 0.87)
    Standard employment terms include clear definitions...

================================================================================
END OF REPORT
================================================================================
```

**Why This Format**:
- Executive summary for quick overview
- Detailed findings for thorough review
- RAG context for reference/comparison
- Clear severity indicators for prioritization

---

### 5. LegalAgentEvaluator

**Purpose**: Measure system accuracy using ground truth data

#### Evaluation Metrics:

##### Precision
```
Precision = True Positives / (True Positives + False Positives)
          = Correctly flagged risks / All flagged risks
```
**Meaning**: Of all risks we flagged, what % were real?
**Example**: Flagged 10 risks, 8 were real → 80% precision

##### Recall
```
Recall = True Positives / (True Positives + False Negatives)
       = Correctly flagged risks / All actual risks
```
**Meaning**: Of all real risks, what % did we find?
**Example**: Document had 12 risks, we found 8 → 67% recall

##### F1 Score
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```
**Meaning**: Balanced measure of precision and recall
**Best value**: 1.0 (perfect)
**Worst value**: 0.0 (terrible)

#### Methods:

##### `create_ground_truth_dataset(self)`
Creates test cases with known expected risks

**Example Test Case**:
```python
{
    "document": """This agreement is made between Party A and Party B.
                   Party A provides services for $10,000.
                   IP remains with Party A.""",
    "expected_risks": [
        "missing_termination_clause",
        "missing_liability_clause",
        "missing_governing_law"
    ],
    "name": "Incomplete Service Agreement"
}
```

**Why These Tests**:
- Known outcomes (we know what should be detected)
- Cover different risk types
- Test both presence and absence detection
- Realistic document fragments

##### `evaluate(self, assessor, test_dataset) -> Dict`
Runs evaluation and calculates metrics

**Process**:
```
For each test case:
    1. Run risk assessment
    2. Get detected risks
    3. Compare with expected risks
    4. Count:
       - True Positives (TP): Correctly flagged
       - False Positives (FP): Incorrectly flagged
       - False Negatives (FN): Missed risks

    5. Track totals

Calculate metrics:
    Precision = TP / (TP + FP)
    Recall = TP / (TP + FN)
    F1 = 2 × (Precision × Recall) / (Precision + Recall)

Return detailed results
```

**Example Calculation**:
```
Test 1: Expected [A, B, C], Detected [A, B, D]
    TP = 2 (A, B correctly found)
    FP = 1 (D incorrectly flagged)
    FN = 1 (C missed)

Test 2: Expected [E], Detected [E, F]
    TP = 1 (E correctly found)
    FP = 1 (F incorrectly flagged)
    FN = 0 (no misses)

Totals:
    TP = 3
    FP = 2
    FN = 1

Metrics:
    Precision = 3 / (3+2) = 0.60 = 60%
    Recall = 3 / (3+1) = 0.75 = 75%
    F1 = 2 × (0.60 × 0.75) / (0.60 + 0.75) = 0.67 = 67%
```

---

## Key Algorithms

### 1. Regex Pattern Matching

**What is Regex?**
Regular expressions = pattern matching language

**Common Patterns Used**:

```python
r"\b(word1|word2)\b"
```
- `\b`: Word boundary (match whole words only)
- `(word1|word2)`: Match either word1 OR word2
- Example: Matches "terminate" but not "terminated" or "determination"

```python
r"[^a-zA-Z0-9\s.,;:()\-'\"]+", ''
```
- `[^...]`: Match anything NOT in brackets
- `+`: One or more times
- Removes all special characters except listed ones

```python
r"\s+"
```
- `\s`: Whitespace character (space, tab, newline)
- `+`: One or more
- Matches any amount of whitespace

### 2. Vector Similarity Search

**L2 Distance (Euclidean)**:
```python
distance = sqrt(sum((a[i] - b[i])^2 for i in range(384)))
```

**Example**:
```
Vector A: [0.5, 0.3, 0.8]
Vector B: [0.6, 0.2, 0.9]

Distance = sqrt((0.5-0.6)² + (0.3-0.2)² + (0.8-0.9)²)
         = sqrt(0.01 + 0.01 + 0.01)
         = sqrt(0.03)
         = 0.173

Similarity = 1 / (1 + 0.173) = 0.852 (85% similar)
```

### 3. Masked Language Modeling

**Training Process**:
```
Original: "The agreement shall terminate with 30 days notice"
Masked:   "The agreement shall [MASK] with 30 days notice"

Model predicts: "terminate" (correct!)

Loss calculation:
    - Model outputs probabilities for all words
    - Compare with actual word "terminate"
    - High probability for correct word = low loss
    - Adjust weights to improve prediction

Repeat millions of times with different masks
```

---

## Data Flow

### Complete System Flow:

```
1. DOCUMENT LOADING
   ┌─────────────────┐
   │ User uploads or │
   │ samples created │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ LegalDataCollector
   │ - Loads PDF/TXT/MD
   │ - Extracts text
   │ - Stores metadata
   └────────┬────────┘
            │
            ▼
   [legal_texts, metadata]

2. FINE-TUNING (Optional)
            │
            ▼
   ┌─────────────────┐
   │ LegalLLMFineTuner
   │ - Tokenizes text
   │ - Creates dataset
   │ - Trains model
   │ - Saves weights
   └────────┬────────┘
            │
            ▼
   [Fine-tuned model]

3. RAG INDEX CREATION
            │
            ▼
   ┌─────────────────┐
   │ LegalRAGSystem  │
   │ - Embeds docs   │
   │ - Creates FAISS │
   │ - Saves index   │
   └────────┬────────┘
            │
            ▼
   [Vector index]

4. RISK ASSESSMENT
            │
            ▼
   ┌─────────────────┐
   │ LegalRiskAssessor
   │ - Pattern match │
   │ - RAG retrieval │
   │ - Generate report
   └────────┬────────┘
            │
            ▼
   [Risk reports]

5. EVALUATION
            │
            ▼
   ┌─────────────────┐
   │ LegalAgentEvaluator
   │ - Test cases    │
   │ - Calculate metrics
   │ - Performance report
   └────────┬────────┘
            │
            ▼
   [Precision, Recall, F1]
```

---

## Performance Considerations

### Memory Usage:
- **Each Document**: ~10-50 KB text
- **Embeddings**: 384 floats × 4 bytes = 1.5 KB per document
- **1000 Documents**: ~50 MB text + 1.5 MB embeddings = manageable

### Speed:
- **Loading PDFs**: 1-5 seconds per document
- **Embedding**: 100 docs/second on CPU
- **FAISS Search**: <1ms for 1000 docs
- **Risk Analysis**: 0.1-0.5 seconds per document

### Scalability:
- **Current**: 1-100 documents (perfect)
- **Scales to**: 10,000+ documents (still fast)
- **Limit**: FAISS can handle millions, but model fine-tuning needs GPU for large datasets

---

## Common Issues and Solutions

### Issue 1: PDF Extraction Fails
**Symptom**: Empty text from PDF
**Cause**: PDF has images, not text
**Solution**: Use OCR (pytesseract) or request text-based PDFs

### Issue 2: Out of Memory
**Symptom**: Crash during training
**Cause**: Batch size too large
**Solution**: Reduce `per_device_train_batch_size` to 4 or 2

### Issue 3: Low Precision
**Symptom**: Many false positives
**Cause**: Patterns too broad
**Solution**: Make regex more specific or increase confidence threshold

### Issue 4: Low Recall
**Symptom**: Missing many risks
**Cause**: Patterns too narrow
**Solution**: Add more pattern variations or use LLM-based detection

---

## Best Practices

1. **Start with samples** - Test system before adding your data
2. **Monitor metrics** - Check precision/recall regularly
3. **Tune patterns** - Adjust regex based on your document types
4. **Use RAG** - Context improves accuracy significantly
5. **Save checkpoints** - Don't lose training progress
6. **Version indexes** - Keep old FAISS indexes when updating
7. **Document changes** - Track pattern modifications
8. **Test incrementally** - Add features one at a time

---

## Extending the System

### Adding New Risk Categories:
```python
"new_risk": {
    "name": "Descriptive Name",
    "severity": "High",
    "patterns": [r"\byour_pattern\b"],
    "inverse": False,  # or True
    "description": "What this risk means"
}
```

### Adding New Document Types:
```python
# In LegalDataCollector.load_text_content():
elif file_path.lower().endswith('.docx'):
    from docx import Document
    doc = Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs])
```

### Using Different Models:
```python
# In LegalAgentConfig:
base_model_name = "roberta-base"  # Or any Hugging Face model
embedding_model_name = "sentence-transformers/paraphrase-MiniLM-L6-v2"
```

---

## Glossary

- **Token**: Subword unit (word or word piece) that models process
- **Embedding**: Vector representation of text
- **Fine-tuning**: Training a pre-trained model on specific data
- **RAG**: Retrieval-Augmented Generation
- **FAISS**: Facebook AI Similarity Search (vector database)
- **Precision**: Accuracy of flagged risks
- **Recall**: Coverage of actual risks
- **F1 Score**: Harmonic mean of precision and recall
- **Masked LM**: Predicting hidden words in text
- **Stopwords**: Common words like "the", "is", "at"
- **Regex**: Regular expression pattern matching

---

This documentation provides a complete understanding of every component in the Legal Document Review System. For specific implementation details, refer to the inline comments in the notebook cells.
