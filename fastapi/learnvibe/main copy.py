#main.py

from fastapi import FastAPI, HTTPException,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import random
import asyncio
import ollama
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from datetime import datetime
from roadmap_integration import roadmap_generator
import logging



logger = logging.getLogger(__name__)
router = APIRouter()


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class GoalInput(BaseModel):
    goal: str
    session_id: str

class AnswersInput(BaseModel):
    goal: str
    answers: List[int]
    questions: List[Dict]
    session_id: str

class MockTestRequest(BaseModel):
    session_id: str
    selected_skills: List[int]
    total_questions: int

class TopicsTestRequest(BaseModel):
    session_id: str
    selected_topics: List[int]
    total_questions: int

class TestSubmission(BaseModel):
    test_id: str
    answers: Dict[int, int]
    time_taken_seconds: int

# ============================================================================
# IN-MEMORY STORES
# ============================================================================

QUESTION_STORE: Dict[str, List[Dict]] = {}
CAREER_DATA_STORE: Dict[str, Dict] = {}
SESSION_STORE: Dict[str, Dict] = {}
MOCK_TEST_STORE: Dict[str, Dict] = {}

# ============================================================================
# DATA SCIENTIST CAREER FRAMEWORK
# ============================================================================

# Prerequisites (Before Data Science)
DATA_SCIENTIST_PREREQUISITES = {
    "Mathematics Foundations": {
        "category": "Mathematics",
        "difficulty": "Beginner",
        "skills": [
            {
                "name": "Arithmetic & Algebra",
                "description": "Master fundamental operations with numbers, fractions, exponents, and algebraic manipulation",
                "topics": [
                    "Numbers, fractions, exponents, roots",
                    "Equations & inequalities",
                    "Algebraic manipulation"
                ]
            },
            {
                "name": "Functions & Graphs",
                "description": "Understand various function types and their graphical representations",
                "topics": [
                    "Linear, quadratic, exponential, logarithmic functions",
                    "Coordinate geometry",
                    "Transformations of functions"
                ]
            },
            {
                "name": "Probability Basics",
                "description": "Learn fundamental probability concepts and counting principles",
                "topics": [
                    "Experiments & events",
                    "Permutations & combinations",
                    "Conditional probability"
                ]
            },
            {
                "name": "Statistics Basics",
                "description": "Understand descriptive statistics and data distributions",
                "topics": [
                    "Mean, median, mode",
                    "Variance & standard deviation",
                    "Frequency distributions"
                ]
            },
            {
                "name": "Linear Equations & Inequalities",
                "description": "Solve systems of equations and interpret them graphically",
                "topics": [
                    "Solving systems of equations",
                    "Graphical interpretation"
                ]
            }
        ]
    },
    "Programming Foundations (Python)": {
        "category": "Programming",
        "difficulty": "Beginner",
        "skills": [
            {
                "name": "Python Basics",
                "description": "Learn fundamental Python syntax and basic programming concepts",
                "topics": [
                    "Variables & data types",
                    "Operators & expressions",
                    "Input/output"
                ]
            },
            {
                "name": "Control Structures",
                "description": "Master flow control with conditionals and loops",
                "topics": [
                    "If-else statements",
                    "Loops (for, while)",
                    "Nested control structures"
                ]
            },
            {
                "name": "Functions in Python",
                "description": "Create reusable code with functions and understand scope",
                "topics": [
                    "Arguments & return values",
                    "Recursion basics",
                    "Lambda functions"
                ]
            },
            {
                "name": "Data Structures",
                "description": "Work with built-in data structures effectively",
                "topics": [
                    "Lists & tuples",
                    "Dictionaries & sets",
                    "Nested structures"
                ]
            },
            {
                "name": "File Handling",
                "description": "Read and write files in various formats",
                "topics": [
                    "Read/write files",
                    "CSV & JSON basics",
                    "Exception handling"
                ]
            },
            {
                "name": "OOP Concepts",
                "description": "Understand Object-Oriented Programming principles",
                "topics": [
                    "Classes & objects",
                    "Inheritance & polymorphism",
                    "Encapsulation & abstraction"
                ]
            }
        ]
    },
    "Computer Science Basics": {
        "category": "CS Fundamentals",
        "difficulty": "Intermediate",
        "skills": [
            {
                "name": "Memory & Systems",
                "description": "Understand computer architecture fundamentals",
                "topics": [
                    "RAM, CPU, Disk basics",
                    "Binary representation"
                ]
            },
            {
                "name": "Algorithms",
                "description": "Learn algorithm analysis and common algorithms",
                "topics": [
                    "Big-O notation",
                    "Searching (linear, binary)",
                    "Sorting (bubble, merge, quick)"
                ]
            },
            {
                "name": "Data Structures Fundamentals",
                "description": "Implement and use fundamental data structures",
                "topics": [
                    "Stack & Queue",
                    "Linked lists",
                    "Trees (binary, BST basics)",
                    "Graphs (intro to nodes & edges)"
                ]
            }
        ]
    },
    "Tools & Environment": {
        "category": "Development Tools",
        "difficulty": "Beginner",
        "skills": [
            {
                "name": "Git & GitHub",
                "description": "Master version control and collaboration",
                "topics": [
                    "Git init, add, commit",
                    "Branching & merging",
                    "GitHub remote push/pull"
                ]
            },
            {
                "name": "Command Line",
                "description": "Navigate and work efficiently with terminal",
                "topics": [
                    "Basic navigation & file operations"
                ]
            },
            {
                "name": "IDEs",
                "description": "Work with modern development environments",
                "topics": [
                    "Jupyter Notebook",
                    "VS Code"
                ]
            },
            {
                "name": "Environments",
                "description": "Manage packages and virtual environments",
                "topics": [
                    "pip & conda",
                    "Virtual environments"
                ]
            }
        ]
    }
}

# Data Scientist Career Levels
DATA_SCIENTIST_LEVELS = [
    "Beginner Level",
    "Moderate Level",
    "Advanced Level"
]

# Topics for Each Level
LEVEL_TOPICS = {
    "Beginner Level": [
        {
            "name": "Mathematics for Data Science",
            "description": "Master fundamental mathematical concepts required for data science",
            "subtopics": {
                "Probability Theory": [
                    "Independent & dependent events",
                    "Conditional probability",
                    "Bayes' theorem"
                ],
                "Descriptive Statistics": [
                    "Central tendency (mean, median, mode)",
                    "Dispersion (range, variance, std dev)",
                    "Skewness & kurtosis"
                ],
                "Inferential Statistics": [
                    "Sampling methods",
                    "Hypothesis testing",
                    "Confidence intervals",
                    "P-values"
                ],
                "Correlation & Covariance": []
            }
        },
        {
            "name": "Python for Data Science",
            "description": "Learn essential Python libraries for data manipulation and analysis",
            "subtopics": {
                "NumPy": [
                    "Arrays & indexing",
                    "Broadcasting",
                    "Linear algebra basics"
                ],
                "Pandas": [
                    "Series & DataFrame",
                    "Indexing & slicing",
                    "GroupBy, merges, joins",
                    "Aggregations"
                ],
                "Visualization": [
                    "Matplotlib (line, scatter, bar, pie)",
                    "Seaborn (heatmap, histogram, boxplot)"
                ]
            }
        },
        {
            "name": "Data Collection & Cleaning",
            "description": "Master data acquisition and preprocessing techniques",
            "subtopics": {
                "File Formats": ["CSV & Excel", "JSON"],
                "Data Issues": ["Missing values", "Duplicates", "Outliers"],
                "Data Transformations": [
                    "Normalization & Standardization",
                    "Encoding categorical data"
                ]
            }
        },
        {
            "name": "Basic Data Analysis",
            "description": "Perform exploratory data analysis and feature engineering",
            "subtopics": {
                "EDA": [
                    "Summary statistics",
                    "Data distributions",
                    "Correlation analysis"
                ],
                "Feature Engineering Basics": []
            }
        }
    ],
    "Moderate Level": [
        {
            "name": "SQL & Databases",
            "description": "Master database querying and data manipulation",
            "subtopics": {
                "Queries": ["SELECT, WHERE, ORDER BY", "GROUP BY, HAVING"],
                "Joins": ["INNER, LEFT, RIGHT, FULL"],
                "Subqueries & CTEs": [],
                "Window Functions": ["ROW_NUMBER, RANK", "LAG, LEAD"],
                "Optimization": ["Indexing", "Query tuning basics"]
            }
        },
        {
            "name": "Mathematics for ML",
            "description": "Advanced mathematics for machine learning algorithms",
            "subtopics": {
                "Linear Algebra": [
                    "Vectors & matrices",
                    "Dot product & matrix multiplication",
                    "Determinants & inverses",
                    "Eigenvalues & eigenvectors"
                ],
                "Calculus": ["Derivatives", "Partial derivatives", "Gradient"],
                "Probability Distributions": ["Normal, Binomial", "Poisson, Bernoulli"],
                "Optimization": ["Gradient Descent", "Convex functions"]
            }
        },
        {
            "name": "Machine Learning Basics",
            "description": "Introduction to supervised and unsupervised learning",
            "subtopics": {
                "ML Paradigms": ["Supervised", "Unsupervised", "Reinforcement (intro)"],
                "Regression": ["Linear regression", "Multiple regression"],
                "Classification": ["Logistic regression", "k-NN", "Decision Trees"],
                "Evaluation Metrics": [
                    "Accuracy, Precision, Recall, F1",
                    "Confusion matrix",
                    "ROC & AUC"
                ],
                "Model Selection": ["Cross-validation", "Bias-variance tradeoff"]
            }
        },
        {
            "name": "Data Preprocessing & Feature Engineering",
            "description": "Advanced data preparation techniques",
            "subtopics": {
                "Outlier Detection": [],
                "Feature Scaling": ["Min-max scaling", "Z-score normalization"],
                "Encoding": ["One-hot", "Label encoding"],
                "Data Splits": ["Train-test", "Stratified sampling"]
            }
        },
        {
            "name": "Advanced Data Visualization",
            "description": "Create interactive and advanced visualizations",
            "subtopics": {
                "Seaborn Advanced": ["pairplot", "violinplot"],
                "Plotly": ["Interactive plots"]
            }
        }
    ],
    "Advanced Level": [
        {
            "name": "Advanced Machine Learning",
            "description": "Master ensemble methods and advanced ML techniques",
            "subtopics": {
                "Ensembles": [
                    "Random Forest",
                    "Gradient Boosting",
                    "XGBoost",
                    "LightGBM",
                    "CatBoost"
                ],
                "SVM": ["Linear SVM", "Kernel methods"],
                "Clustering": ["K-Means", "Hierarchical", "DBSCAN"],
                "Dimensionality Reduction": ["PCA", "t-SNE", "UMAP"],
                "Time Series": ["ARIMA & SARIMA", "Prophet", "Feature engineering"]
            }
        },
        {
            "name": "Deep Learning (Neural Networks)",
            "description": "Build and train deep neural networks",
            "subtopics": {
                "Foundations": [
                    "Perceptron",
                    "Forward & backpropagation",
                    "Activation functions (ReLU, Sigmoid, Tanh, Softmax)",
                    "Loss functions (MSE, Cross-Entropy, Hinge)",
                    "Optimizers (SGD, Adam, RMSProp)"
                ],
                "CNNs": [
                    "Convolution, pooling, padding",
                    "Transfer learning (ResNet, VGG)",
                    "Object detection (YOLO, Faster R-CNN)"
                ],
                "RNNs": ["Vanilla RNNs", "LSTM & GRU", "Seq2Seq models"],
                "Transformers": [
                    "Attention mechanism",
                    "Encoder-decoder",
                    "BERT & GPT basics"
                ]
            }
        },
        {
            "name": "Natural Language Processing (NLP)",
            "description": "Process and analyze text data with modern NLP techniques",
            "subtopics": {
                "Classical NLP": [
                    "Tokenization, stemming, lemmatization",
                    "Bag-of-Words",
                    "TF-IDF"
                ],
                "Word Embeddings": ["Word2Vec", "GloVe", "FastText"],
                "Deep Learning NLP": [
                    "RNN/LSTM-based models",
                    "Attention & Seq2Seq",
                    "Transformer-based models"
                ],
                "Modern NLP": [
                    "BERT, RoBERTa, DistilBERT",
                    "GPT-family models",
                    "HuggingFace ecosystem"
                ]
            }
        },
        {
            "name": "Big Data & Cloud",
            "description": "Work with large-scale data processing and cloud platforms",
            "subtopics": {
                "Hadoop": ["HDFS", "MapReduce"],
                "Spark": ["RDDs, DataFrames", "MLlib"],
                "Cloud ML": [
                    "AWS (S3, SageMaker)",
                    "GCP (BigQuery, Vertex AI)",
                    "Azure ML"
                ],
                "Data Pipelines": ["ETL concepts", "Airflow basics"]
            }
        },
        {
            "name": "Deployment & MLOps",
            "description": "Deploy models to production and manage ML lifecycle",
            "subtopics": {
                "Model Packaging": ["Pickle & Joblib", "ONNX"],
                "API Development": ["Flask", "FastAPI"],
                "Containerization": ["Docker", "Kubernetes (intro)"],
                "CI/CD": [],
                "Monitoring": [
                    "Concept drift detection",
                    "Retraining pipelines"
                ],
                "Experiment Tracking": ["MLflow", "Weights & Biases"],
                "Data/Model Versioning": ["DVC"]
            }
        }
    ]
}

# ============================================================================
# ENHANCED HELPER FUNCTIONS FOR SKILLS MOCK TEST
# ============================================================================

def generate_skill_specific_questions(skill_data: Dict, num_questions: int = 2) -> List[Dict]:
    """Generate high-quality, skill-aligned questions using enhanced prompts"""
    
    skill_name = skill_data["name"]
    skill_description = skill_data["description"]
    skill_topics = skill_data["topics"]
    skill_category = skill_data["category"]
    skill_difficulty = skill_data["difficulty"]
    
    # Enhanced prompt for skill-specific questions
    prompt = f"""
Generate exactly {num_questions} high-quality multiple-choice questions to assess practical knowledge of the skill: "{skill_name}"

SKILL CONTEXT:
- Description: {skill_description}
- Category: {skill_category}
- Difficulty: {skill_difficulty}
- Key Topics: {', '.join(skill_topics)}

QUESTION REQUIREMENTS:
1. Questions must be PRACTICAL and REAL-WORLD focused, not theoretical
2. Each question should test APPLICATION of knowledge, not memorization
3. Questions should cover different aspects of the skill (conceptual, practical, troubleshooting)
4. Make questions challenging but fair for {skill_difficulty.lower()} level
5. Include scenario-based questions where appropriate

QUESTION FORMAT (STRICT):
Question 1: [Clear, practical question text that tests real understanding]
A. [Plausible but incorrect option that tests common misunderstandings]
B. [Correct answer - the most appropriate solution]
C. [Plausible but suboptimal option]
D. [Clearly wrong option that tests fundamental understanding]
Correct: B

Question 2: [Next question...]
A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]
Correct: [Correct letter]

Generate all {num_questions} questions now, ensuring diversity in question types and coverage of different skill aspects.
"""

    try:
        response = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.7}  # Add some creativity
        )['message']['content']

        # Enhanced parsing with better error handling
        questions = []
        lines = response.strip().split('\n')
        current_question = None
        question_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect question start
            if line.lower().startswith('question') and ':' in line:
                if current_question and len(current_question.get('options', [])) == 4:
                    questions.append(current_question)
                    question_count += 1
                
                current_question = {
                    'id': question_count,
                    'text': line.split(':', 1)[1].strip(),
                    'options': [],
                    'skill_context': {
                        'name': skill_name,
                        'category': skill_category,
                        'difficulty': skill_difficulty,
                        'topics': skill_topics
                    }
                }
            
            # Detect options
            elif line.upper().startswith(('A.', 'B.', 'C.', 'D.')):
                if current_question and len(current_question['options']) < 4:
                    option_text = line[2:].strip()
                    # Validate option isn't empty
                    if option_text and len(option_text) > 1:
                        current_question['options'].append(option_text)
            
            # Detect correct answer
            elif line.lower().startswith('correct:'):
                if current_question:
                    correct_letter = line.split(':', 1)[1].strip().upper()
                    if correct_letter in ['A', 'B', 'C', 'D']:
                        current_question['correct_letter'] = correct_letter
        
        # Add final question if complete
        if current_question and len(current_question.get('options', [])) == 4:
            questions.append(current_question)
        
        # Process and validate questions
        valid_questions = []
        for q in questions:
            if (len(q.get('options', [])) == 4 and 
                'correct_letter' in q and 
                len(q['text']) > 10):  # Basic quality check
                
                try:
                    correct_index = ord(q['correct_letter']) - ord('A')
                    if 0 <= correct_index < 4:
                        correct_text = q['options'][correct_index]
                        # Shuffle options but track correct answer
                        original_options = q['options'].copy()
                        random.shuffle(q['options'])
                        q['correct'] = q['options'].index(correct_text)
                        valid_questions.append(q)
                except (IndexError, ValueError):
                    continue
        
        # Enhanced fallback questions if generation fails
        if len(valid_questions) < num_questions:
            needed = num_questions - len(valid_questions)
            enhanced_fallbacks = generate_enhanced_fallback_questions(
                skill_data, needed
            )
            valid_questions.extend(enhanced_fallbacks)
        
        return valid_questions[:num_questions]

    except Exception as e:
        print(f"Error generating questions for {skill_name}: {str(e)}")
        # Enhanced fallback
        return generate_enhanced_fallback_questions(skill_data, num_questions)

def generate_enhanced_fallback_questions(skill_data: Dict, num_questions: int) -> List[Dict]:
    """Generate better fallback questions when Ollama fails"""
    skill_name = skill_data["name"]
    skill_topics = skill_data["topics"]
    
    # Contextual fallback questions based on skill type
    fallback_questions = []
    
    for i in range(num_questions):
        # Different question templates based on skill category
        if "programming" in skill_data["category"].lower():
            question_templates = [
                f"What is the most efficient way to handle {random.choice(skill_topics)} in a production environment?",
                f"When working with {skill_name}, what common mistake should developers avoid?",
                f"In a real-world scenario involving {random.choice(skill_topics)}, what approach would be most maintainable?",
                f"How would you debug a typical issue related to {skill_name}?",
                f"What best practice is most important when implementing {random.choice(skill_topics)}?"
            ]
        elif "mathematics" in skill_data["category"].lower():
            question_templates = [
                f"What practical application does {random.choice(skill_topics)} have in data science?",
                f"How would you explain {random.choice(skill_topics)} to a non-technical stakeholder?",
                f"What common misconception exists about {skill_name}?",
                f"In what real-world scenario would you apply {random.choice(skill_topics)}?",
                f"What is the most important concept to understand about {random.choice(skill_topics)}?"
            ]
        else:
            question_templates = [
                f"What is the most practical aspect of {skill_name} for daily work?",
                f"How does {random.choice(skill_topics)} contribute to project success?",
                f"What key consideration is often overlooked when working with {skill_name}?",
                f"In a team setting, what approach to {skill_name} is most effective?",
                f"What real-world problem does {random.choice(skill_topics)} help solve?"
            ]
        
        question_text = random.choice(question_templates)
        
        # Contextual options based on skill
        if "programming" in skill_data["category"].lower():
            options = [
                "Using the most complex solution available",
                "Following best practices and documentation",
                "Copy-pasting code from online without understanding",
                "Ignoring error handling for simplicity"
            ]
            correct_index = 1
        elif "mathematics" in skill_data["category"].lower():
            options = [
                "Memorizing formulas without understanding",
                "Understanding the underlying principles",
                "Avoiding practical applications",
                "Focusing only on theoretical aspects"
            ]
            correct_index = 1
        else:
            options = [
                "Beginner - Basic understanding, needs guidance",
                "Intermediate - Can work independently on standard tasks",
                "Proficient - Can handle complex scenarios and mentor others",
                "Expert - Deep mastery, can innovate and lead"
            ]
            correct_index = random.randint(1, 2)
        
        fallback_questions.append({
            'id': i,
            'text': question_text,
            'options': options,
            'correct': correct_index,
            'skill_context': {
                'name': skill_data["name"],
                'category': skill_data["category"],
                'difficulty': skill_data["difficulty"],
                'topics': skill_data["topics"],
                'is_fallback': True
            }
        })
    
    return fallback_questions

def validate_question_quality(question: Dict) -> bool:
    """Validate that generated questions meet quality standards"""
    if not question.get('text') or len(question['text']) < 15:
        return False
    
    options = question.get('options', [])
    if len(options) != 4:
        return False
    
    # Check for duplicate or empty options
    unique_options = set(opt.strip().lower() for opt in options if opt.strip())
    if len(unique_options) < 4:
        return False
    
    # Check for reasonable option lengths
    for option in options:
        if len(option.strip()) < 5 or len(option.strip()) > 200:
            return False
    
    # Check correct answer is valid
    correct_idx = question.get('correct')
    if correct_idx not in [0, 1, 2, 3]:
        return False
    
    return True

def calculate_question_quality(question: Dict) -> float:
    """Calculate a quality score for generated questions"""
    score = 0.0
    
    # Text length score
    text_length = len(question.get('text', ''))
    if text_length > 50:
        score += 0.3
    elif text_length > 25:
        score += 0.2
    else:
        score += 0.1
    
    # Options quality score
    options = question.get('options', [])
    if len(options) == 4:
        option_lengths = [len(opt.strip()) for opt in options if opt.strip()]
        avg_option_length = sum(option_lengths) / len(option_lengths) if option_lengths else 0
        
        if avg_option_length > 20:
            score += 0.4
        elif avg_option_length > 10:
            score += 0.3
        else:
            score += 0.2
        
        # Check for option diversity
        unique_chars = set(''.join(opt.lower() for opt in options))
        if len(unique_chars) > 50:
            score += 0.3
    
    # Context score
    if question.get('skill_context'):
        score += 0.2
    
    # Fallback penalty
    if question.get('skill_context', {}).get('is_fallback'):
        score *= 0.7
    
    return min(1.0, score)

def generate_questions_with_ollama(skill_or_topic_name: str, context: str, num_questions: int = 2) -> List[Dict]:
    """Generate questions for topics and initial assessment using Ollama"""
    
    prompt = f"""
Generate exactly {num_questions} multiple-choice questions to test knowledge of "{skill_or_topic_name}" in the context of {context}.

Questions should be practical and test real understanding, not just memorization.

For each question, provide:
1. A clear question
2. Exactly 4 options (A, B, C, D)
3. The correct answer letter

Format each question EXACTLY as:

Question 1: [question text]
A. [option A]
B. [option B]
C. [option C]
D. [option D]
Correct: [A/B/C/D]

Generate all {num_questions} questions now.
"""

    try:
        response = ollama.chat(
            model='mistral',
            messages=[{'role': 'user', 'content': prompt}]
        )['message']['content']

        # Parse response
        questions = []
        lines = response.strip().split('\n')
        current_question = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith('question'):
                if current_question and len(current_question.get('options', [])) == 4:
                    questions.append(current_question)
                
                question_id = len(questions)
                current_question = {
                    'id': question_id,
                    'text': line.split(':', 1)[1].strip() if ':' in line else line,
                    'options': []
                }
            elif line.upper().startswith(('A.', 'B.', 'C.', 'D.')):
                if current_question:
                    current_question['options'].append(line[2:].strip())
            elif line.lower().startswith('correct:'):
                if current_question:
                    correct_letter = line.split(':', 1)[1].strip().upper()
                    if correct_letter in ['A', 'B', 'C', 'D']:
                        current_question['correct_letter'] = correct_letter
        
        # Add final question
        if current_question and len(current_question.get('options', [])) == 4:
            questions.append(current_question)
        
        # Process questions - shuffle options but track correct answer
        valid_questions = []
        for q in questions:
            if len(q.get('options', [])) == 4 and 'correct_letter' in q:
                correct_text = q['options'][ord(q['correct_letter']) - ord('A')]
                random.shuffle(q['options'])
                q['correct'] = q['options'].index(correct_text)
                valid_questions.append(q)
        
        # Fill with fallback if needed
        while len(valid_questions) < num_questions:
            valid_questions.append({
                'id': len(valid_questions),
                'text': f'Rate your understanding of {skill_or_topic_name}',
                'options': ['Beginner', 'Intermediate', 'Proficient', 'Expert'],
                'correct': 1
            })

        return valid_questions[:num_questions]

    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        # Fallback questions
        return [{
            'id': i,
            'text': f'Assess your knowledge of {skill_or_topic_name} - Question {i+1}',
            'options': ['Beginner', 'Intermediate', 'Proficient', 'Expert'],
            'correct': 1
        } for i in range(num_questions)]

def flatten_subtopics(subtopics_dict: Dict) -> List[str]:
    """Flatten nested subtopics into a simple list"""
    all_topics = []
    for category, items in subtopics_dict.items():
        if isinstance(items, list) and items:
            all_topics.extend(items)
        else:
            all_topics.append(category)
    return all_topics

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/submit_goal")
async def submit_goal(input: GoalInput):
    """Process goal submission and generate initial assessment"""
    try:
        goal = input.goal.strip().title()
        session_id = input.session_id
        
        # Check if this is Data Scientist goal
        if "data scientist" not in goal.lower():
            return {
                "error": "Currently only 'Data Scientist' career path is supported",
                "message": "Please enter 'Data Scientist' as your goal"
            }
        
        # Store session data
        SESSION_STORE[session_id] = {
            "goal": goal,
            "levels": DATA_SCIENTIST_LEVELS,
            "created_at": datetime.now().isoformat()
        }
        
        # Store career data
        CAREER_DATA_STORE[session_id] = {
            "goal": goal,
            "levels": DATA_SCIENTIST_LEVELS,
            "context": "data science and analytics"
        }
        
        # Generate initial assessment questions
        questions = generate_questions_with_ollama(
            "Data Science Fundamentals",
            "data science",
            10
        )
        
        # Store questions
        QUESTION_STORE[session_id] = questions
        
        # Prepare questions for client (without correct answers)
        client_questions = [{
            'id': q['id'],
            'text': q['text'],
            'options': q['options']
        } for q in questions]
        
        return {
            "goal": goal,
            "custom_levels": DATA_SCIENTIST_LEVELS,
            "questions": client_questions,
            "total_questions": len(questions),
            "points_per_question": round(100 / len(questions), 1),
            "has_prerequisites": True,
            "prerequisites_count": sum(
                len(section["skills"]) 
                for section in DATA_SCIENTIST_PREREQUISITES.values()
            )
        }
        
    except Exception as e:
        print(f"Error in submit_goal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit_answers")
async def submit_answers(input: AnswersInput):
    """Evaluate initial assessment answers"""
    try:
        session_id = input.session_id
        
        if session_id not in QUESTION_STORE or session_id not in CAREER_DATA_STORE:
            raise HTTPException(status_code=400, detail="Session not found")
        
        questions = QUESTION_STORE[session_id]
        career_data = CAREER_DATA_STORE[session_id]
        
        if len(input.answers) != len(questions):
            raise HTTPException(status_code=400, detail="Answer count mismatch")
        
        # Calculate score
        total_questions = len(questions)
        points_per_question = 100 / total_questions
        score = 0
        
        for i, answer in enumerate(input.answers):
            if answer == questions[i].get('correct', -1):
                score += points_per_question
        
        score = round(score)
        
        # Assign level based on score
        levels = career_data["levels"]
        if score >= 75:
            level_index = len(levels) - 1  # Advanced
        elif score >= 50:
            level_index = 1  # Moderate
        else:
            level_index = 0  # Beginner
        
        assigned_level = levels[level_index]
        
        feedback = f"Based on your assessment (Score: {score}%), you're recommended to start at the {assigned_level}. "
        feedback += "You'll first complete prerequisite skills, then advance to your target level topics."
        
        return {
            "score": score,
            "assigned_level": assigned_level,
            "feedback": feedback,
            "total_questions": total_questions,
            "correct_answers": round(score / points_per_question)
        }
        
    except Exception as e:
        print(f"Error in submit_answers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get-skills/{session_id}")
async def get_skills(session_id: str):
    """Get prerequisite skills for Data Scientist"""
    try:
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate skill list from prerequisites
        skills = []
        skill_id = 0
        
        for section_name, section_data in DATA_SCIENTIST_PREREQUISITES.items():
            for skill in section_data["skills"]:
                skills.append({
                    "id": skill_id,
                    "name": skill["name"],
                    "description": skill["description"],
                    "category": section_data["category"],
                    "difficulty": section_data["difficulty"],
                    "section": section_name,
                    "topics": skill["topics"]
                })
                skill_id += 1
        
        # Store skills in session
        SESSION_STORE[session_id]["prerequisite_skills"] = skills
        
        return {"skills": skills, "total": len(skills)}
        
    except Exception as e:
        print(f"Error in get_skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-skills-mock-test")
async def generate_skills_mock_test(request: MockTestRequest):
    """Generate enhanced mock test for selected prerequisite skills"""
    try:
        session_id = request.session_id
        selected_skills = request.selected_skills
        total_questions = request.total_questions
        
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if "prerequisite_skills" not in SESSION_STORE[session_id]:
            raise HTTPException(status_code=400, detail="Skills not loaded")
        
        all_skills = SESSION_STORE[session_id]["prerequisite_skills"]
        
        # Get selected skills
        selected_skill_objects = [s for s in all_skills if s["id"] in selected_skills]
        
        if not selected_skill_objects:
            raise HTTPException(status_code=400, detail="No valid skills selected")
        
        # Enhanced question distribution logic
        questions_per_skill = max(2, total_questions // len(selected_skill_objects))
        remaining_questions = total_questions - (questions_per_skill * len(selected_skill_objects))
        
        all_questions = []
        question_id = 0
        
        print(f"🎯 Generating enhanced questions for {len(selected_skill_objects)} skills...")
        
        for skill in selected_skill_objects:
            # Use enhanced question generation
            skill_questions = generate_skill_specific_questions(
                skill, 
                questions_per_skill + (1 if remaining_questions > 0 else 0)
            )
            
            if remaining_questions > 0:
                remaining_questions -= 1
            
            # Add enhanced metadata to questions
            for q in skill_questions:
                q['id'] = question_id
                q['skill_id'] = skill['id']
                q['skill_name'] = skill['name']
                q['category'] = skill['category']
                q['difficulty'] = skill['difficulty']
                q['section'] = skill['section']
                q['quality_score'] = calculate_question_quality(q)
                question_id += 1
            
            # Filter out low-quality questions
            valid_questions = [q for q in skill_questions if validate_question_quality(q)]
            all_questions.extend(valid_questions)
            
            print(f"  ✅ {skill['name']}: {len(valid_questions)} quality questions")
        
        # Ensure we have enough questions
        if len(all_questions) < total_questions:
            print(f"⚠️  Generated {len(all_questions)} questions, need {total_questions}")
            # Generate additional questions from skills that produced the best questions
            quality_scores = {}
            for q in all_questions:
                skill_id = q['skill_id']
                quality_scores[skill_id] = quality_scores.get(skill_id, 0) + q.get('quality_score', 0)
            
            # Get top-performing skills
            top_skills = sorted(quality_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            
            for skill_id, _ in top_skills:
                if len(all_questions) >= total_questions:
                    break
                    
                skill = next(s for s in selected_skill_objects if s["id"] == skill_id)
                extra_questions = generate_skill_specific_questions(skill, 1)
                
                for q in extra_questions:
                    if validate_question_quality(q) and len(all_questions) < total_questions:
                        q['id'] = question_id
                        q['skill_id'] = skill['id']
                        q['skill_name'] = skill['name']
                        q['category'] = skill['category']
                        q['difficulty'] = skill['difficulty']
                        q['section'] = skill['section']
                        q['quality_score'] = calculate_question_quality(q)
                        question_id += 1
                        all_questions.append(q)
        
        # Final quality check and shuffle
        all_questions = [q for q in all_questions if validate_question_quality(q)]
        random.shuffle(all_questions)
        all_questions = all_questions[:total_questions]
        
        print(f"🎉 Final test: {len(all_questions)} quality questions across {len(selected_skill_objects)} skills")
        
        # Create test with enhanced metadata
        test_id = str(uuid4())
        test_data = {
            "test_id": test_id,
            "session_id": session_id,
            "type": "skills",
            "questions": all_questions,
            "total_questions": len(all_questions),
            "selected_skills": selected_skills,
            "skill_coverage": {
                skill['id']: skill['name'] for skill in selected_skill_objects
            },
            "quality_metrics": {
                'total_questions': len(all_questions),
                'skills_covered': len(selected_skill_objects),
                'average_quality_score': sum(q.get('quality_score', 0) for q in all_questions) / len(all_questions) if all_questions else 0
            },
            "created_at": datetime.now().isoformat()
        }
        
        MOCK_TEST_STORE[test_id] = test_data
        
        # Return enhanced test data without correct answers
        client_questions = [{
            'id': q['id'],
            'question': q['text'],
            'text': q['text'],
            'options': q['options'],
            'skill_id': q.get('skill_id'),
            'skill_name': q.get('skill_name'),
            'category': q.get('category'),
            'difficulty': q.get('difficulty', 'medium'),
            'section': q.get('section'),
            'has_context': bool(q.get('skill_context'))
        } for q in all_questions]
        
        return {
            "test_id": test_id,
            "questions": client_questions,
            "total_questions": len(all_questions),
            "type": "skills",
            "quality_metrics": test_data["quality_metrics"],
            "skill_coverage": len(selected_skill_objects)
        }
        
    except Exception as e:
        print(f"Error generating enhanced skills test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get-level-topics/{session_id}")
async def get_level_topics(session_id: str, target_level: str = None):
    """Get topics for all levels or specific target level"""
    try:
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # MODIFIED: If no specific target level provided, return topics from ALL levels
        if target_level is None:
            # Return topics from all levels
            all_topics = []
            topic_id = 0
            
            for level_name, level_topics in LEVEL_TOPICS.items():
                for topic in level_topics:
                    topic_with_id = topic.copy()
                    topic_with_id["id"] = topic_id
                    topic_with_id["level"] = level_name  # Add level information
                    
                    # Flatten subtopics for easier access
                    if "subtopics" in topic_with_id:
                        topic_with_id["all_subtopics"] = flatten_subtopics(
                            topic_with_id["subtopics"]
                        )
                    
                    all_topics.append(topic_with_id)
                    topic_id += 1
            
            # Store in session
            SESSION_STORE[session_id]["all_level_topics"] = all_topics
            
            return {
                "topics": all_topics,
                "level": "All Levels",
                "total_topics": len(all_topics),
                "levels_covered": list(LEVEL_TOPICS.keys())
            }
        
        # If specific target level is provided, return topics for that level only
        if target_level not in LEVEL_TOPICS:
            raise HTTPException(status_code=400, detail="Invalid target level")
        
        topics = LEVEL_TOPICS[target_level]
        
        # Add IDs and flatten subtopics
        topics_with_ids = []
        for i, topic in enumerate(topics):
            topic_with_id = topic.copy()
            topic_with_id["id"] = i
            topic_with_id["level"] = target_level  # Add level information
            
            # Flatten subtopics for easier access
            if "subtopics" in topic_with_id:
                topic_with_id["all_subtopics"] = flatten_subtopics(
                    topic_with_id["subtopics"]
                )
            
            topics_with_ids.append(topic_with_id)
        
        # Store in session
        SESSION_STORE[session_id]["target_level"] = target_level
        SESSION_STORE[session_id]["level_topics"] = topics_with_ids
        
        return {
            "topics": topics_with_ids,
            "level": target_level,
            "total_topics": len(topics_with_ids)
        }
        
    except Exception as e:
        print(f"Error getting level topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-topics-mock-test")
async def generate_topics_mock_test(request: TopicsTestRequest):
    """Generate mock test for selected topics"""
    try:
        session_id = request.session_id
        selected_topics = request.selected_topics
        total_questions = request.total_questions
        
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # MODIFIED: Check both level_topics and all_level_topics
        if "level_topics" not in SESSION_STORE[session_id] and "all_level_topics" not in SESSION_STORE[session_id]:
            raise HTTPException(status_code=400, detail="Topics not loaded")
        
        # Use either level-specific topics or all topics
        if "all_level_topics" in SESSION_STORE[session_id]:
            all_topics = SESSION_STORE[session_id]["all_level_topics"]
            target_level = "All Levels"
        else:
            all_topics = SESSION_STORE[session_id]["level_topics"]
            target_level = SESSION_STORE[session_id]["target_level"]
        
        # Get selected topics
        selected_topic_objects = [t for t in all_topics if t["id"] in selected_topics]
        
        if not selected_topic_objects:
            raise HTTPException(status_code=400, detail="No valid topics selected")
        
        # Generate questions for each topic
        questions_per_topic = max(1, total_questions // len(selected_topic_objects))
        all_questions = []
        question_id = 0
        
        for topic in selected_topic_objects:
            topic_questions = generate_questions_with_ollama(
                topic["name"],
                f"Data Science at {topic.get('level', target_level)} level",
                questions_per_topic
            )
            
            # Add metadata
            for q in topic_questions:
                q['id'] = question_id
                q['topic_id'] = topic['id']
                q['topic_name'] = topic['name']
                q['level'] = topic.get('level', target_level)
                q['difficulty'] = 'medium'
                question_id += 1
            
            all_questions.extend(topic_questions)
        
        random.shuffle(all_questions)
        all_questions = all_questions[:total_questions]
        
        # Create test
        test_id = str(uuid4())
        test_data = {
            "test_id": test_id,
            "session_id": session_id,
            "type": "topics",
            "questions": all_questions,
            "total_questions": len(all_questions),
            "selected_topics": selected_topics,
            "target_level": target_level,
            "created_at": datetime.now().isoformat()
        }
        
        MOCK_TEST_STORE[test_id] = test_data
        
        # Return without correct answers
        client_questions = [{
            'id': q['id'],
            'question': q['text'],
            'text': q['text'],
            'options': q['options'],
            'topic_id': q.get('topic_id'),
            'topic_name': q.get('topic_name'),
            'level': q.get('level', target_level),
            'difficulty': q.get('difficulty', 'medium')
        } for q in all_questions]
        
        return {
            "test_id": test_id,
            "questions": client_questions,
            "total_questions": len(all_questions),
            "type": "topics",
            "target_level": target_level
        }
        
    except Exception as e:
        print(f"Error generating topics test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submit-mock-test")
async def submit_mock_test(submission: TestSubmission):
    """Evaluate and return test results"""
    try:
        test_id = submission.test_id
        
        if test_id not in MOCK_TEST_STORE:
            raise HTTPException(status_code=404, detail="Test not found")
        
        test_data = MOCK_TEST_STORE[test_id]
        questions = test_data["questions"]
        test_type = test_data["type"]
        
        # Calculate results
        total_correct = 0
        total_questions = len(questions)
        item_scores = {}  # skill_id/topic_id -> (correct, total)
        
        for question in questions:
            q_id = question['id']
            user_answer = submission.answers.get(q_id)
            correct_answer = question['correct']
            
            is_correct = user_answer == correct_answer
            if is_correct:
                total_correct += 1
            
            # Track by skill or topic
            item_id = question.get('skill_id') if test_type == 'skills' else question.get('topic_id')
            item_name = question.get('skill_name') if test_type == 'skills' else question.get('topic_name')
            
            if item_id is not None:
                if item_id not in item_scores:
                    item_scores[item_id] = {"name": item_name, "correct": 0, "total": 0}
                item_scores[item_id]["total"] += 1
                if is_correct:
                    item_scores[item_id]["correct"] += 1
        
        # Calculate overall score
        overall_score = (total_correct / total_questions) * 100 if total_questions > 0 else 0
        
        # Determine performance level
        if overall_score >= 85:
            level = "excellent"
        elif overall_score >= 70:
            level = "good"
        elif overall_score >= 50:
            level = "moderate"
        else:
            level = "needs_improvement"
        
        # Identify good and needs improvement items
        good_items = []
        needs_improvement_items = []
        
        for item_id, scores in item_scores.items():
            item_score = (scores["correct"] / scores["total"]) * 100 if scores["total"] > 0 else 0
            if item_score >= 70:
                good_items.append(scores["name"])
            else:
                needs_improvement_items.append(scores["name"])
        
        # Format time
        minutes = submission.time_taken_seconds // 60
        seconds = submission.time_taken_seconds % 60
        time_display = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        
        # Generate next steps
        next_steps = []
        if test_type == "skills":
            if overall_score >= 70:
                next_steps.append("✓ Strong prerequisite foundation demonstrated")
                next_steps.append("→ Ready to select your target Data Scientist level")
                next_steps.append("→ Continue to level-specific topics assessment")
            else:
                next_steps.append("⚠ Strengthen prerequisite skills before advancing")
                next_steps.append("→ Review and practice weak areas")
                next_steps.append("→ Focus on fundamentals in low-scoring categories")
                if needs_improvement_items:
                    next_steps.append(f"→ Priority areas: {', '.join(needs_improvement_items[:3])}")
        else:
            if overall_score >= 70:
                next_steps.append(f"✓ Ready for {test_data.get('target_level', 'this level')}!")
                next_steps.append("→ Start working on real-world projects")
                next_steps.append("→ Build portfolio showcasing these skills")
                next_steps.append("→ Consider relevant certifications")
            else:
                next_steps.append(f"⚠ More preparation needed for {test_data.get('target_level', 'this level')}")
                next_steps.append("→ Deepen understanding of weak topics")
                next_steps.append("→ Complete hands-on projects in these areas")
                if needs_improvement_items:
                    next_steps.append(f"→ Focus on: {', '.join(needs_improvement_items[:3])}")
        
        # Prepare results
        results = {
            "overall_score": round(overall_score, 1),
            "total_correct": total_correct,
            "total_questions": total_questions,
            "overall_level": level,
            "time_taken_seconds": submission.time_taken_seconds,
            "time_taken_display": time_display,
            "next_steps": next_steps,
            "test_type": test_type
        }
        
        if test_type == "skills":
            results["good_skills"] = good_items
            results["needs_improvement_skills"] = needs_improvement_items
            # Add quality metrics for skills test
            if "quality_metrics" in test_data:
                results["quality_metrics"] = test_data["quality_metrics"]
        else:
            results["good_topics"] = good_items
            results["needs_improvement_topics"] = needs_improvement_items
            results["target_level"] = test_data.get("target_level")
        
        return results
        
    except Exception as e:
        print(f"Error submitting test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "message": "Data Scientist Career Framework API",
        "version": "3.0",
        "career_path": "Data Scientist",
        "framework": "Prerequisites → Beginner → Moderate → Advanced"
    }

@app.get("/supported-careers")
async def get_supported_careers():
    return {
        "predefined_frameworks": ["Data Scientist"],
        "supports_custom_goals": False,
        "message": "Comprehensive Data Scientist career framework with prerequisites",
        "prerequisite_sections": list(DATA_SCIENTIST_PREREQUISITES.keys()),
        "total_prerequisite_skills": sum(
            len(section["skills"]) 
            for section in DATA_SCIENTIST_PREREQUISITES.values()
        ),
        "career_levels": DATA_SCIENTIST_LEVELS,
        "total_topics": sum(len(LEVEL_TOPICS[level]) for level in DATA_SCIENTIST_LEVELS)
    }

@app.get("/api/prerequisites-overview")
async def get_prerequisites_overview():
    """Get overview of all prerequisites"""
    overview = {}
    total_skills = 0
    
    for section_name, section_data in DATA_SCIENTIST_PREREQUISITES.items():
        skills_count = len(section_data["skills"])
        total_skills += skills_count
        overview[section_name] = {
            "category": section_data["category"],
            "difficulty": section_data["difficulty"],
            "skills_count": skills_count,
            "skills": [
                {
                    "name": skill["name"],
                    "description": skill["description"],
                    "topics_count": len(skill["topics"])
                }
                for skill in section_data["skills"]
            ]
        }
    
    return {
        "overview": overview,
        "total_sections": len(DATA_SCIENTIST_PREREQUISITES),
        "total_skills": total_skills
    }

@app.get("/api/level-structure")
async def get_level_structure():
    """Get complete level structure with topics"""
    structure = {}
    
    for level in DATA_SCIENTIST_LEVELS:
        if level in LEVEL_TOPICS:
            topics_info = []
            for topic in LEVEL_TOPICS[level]:
                subtopics_count = 0
                if "subtopics" in topic:
                    for category_items in topic["subtopics"].values():
                        if isinstance(category_items, list):
                            subtopics_count += len(category_items)
                        else:
                            subtopics_count += 1
                
                topics_info.append({
                    "name": topic["name"],
                    "description": topic["description"],
                    "subtopics_count": subtopics_count,
                    "categories": list(topic.get("subtopics", {}).keys())
                })
            
            structure[level] = {
                "topics": topics_info,
                "total_topics": len(LEVEL_TOPICS[level])
            }
    
    return {
        "levels": DATA_SCIENTIST_LEVELS,
        "structure": structure
    }

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session data"""
    try:
        # Remove from all stores
        SESSION_STORE.pop(session_id, None)
        QUESTION_STORE.pop(session_id, None)
        CAREER_DATA_STORE.pop(session_id, None)
        
        # Remove associated tests
        tests_to_remove = [
            test_id for test_id, test_data in MOCK_TEST_STORE.items()
            if test_data.get("session_id") == session_id
        ]
        for test_id in tests_to_remove:
            MOCK_TEST_STORE.pop(test_id, None)
        
        return {
            "message": "Session cleared successfully",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}/status")
async def get_session_status(session_id: str):
    """Get current session status"""
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = SESSION_STORE[session_id]
    
    return {
        "session_id": session_id,
        "goal": session.get("goal"),
        "created_at": session.get("created_at"),
        "has_skills": "prerequisite_skills" in session,
        "has_target_level": "target_level" in session,
        "has_topics": "level_topics" in session or "all_level_topics" in session,
        "target_level": session.get("target_level"),
        "has_all_levels": "all_level_topics" in session,
        "progress": {
            "prerequisites_loaded": "prerequisite_skills" in session,
            "level_selected": "target_level" in session,
            "topics_loaded": "level_topics" in session or "all_level_topics" in session
        }
    }

# ============================================================================
# ADDITIONAL UTILITY ENDPOINTS
# ============================================================================

@app.get("/api/skill-details/{session_id}/{skill_id}")
async def get_skill_details(session_id: str, skill_id: int):
    """Get detailed information about a specific skill"""
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if "prerequisite_skills" not in SESSION_STORE[session_id]:
        raise HTTPException(status_code=400, detail="Skills not loaded")
    
    skills = SESSION_STORE[session_id]["prerequisite_skills"]
    skill = next((s for s in skills if s["id"] == skill_id), None)
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return skill

@app.get("/api/topic-details/{session_id}/{topic_id}")
async def get_topic_details(session_id: str, topic_id: int):
    """Get detailed information about a specific topic"""
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # MODIFIED: Check both level_topics and all_level_topics
    if "level_topics" not in SESSION_STORE[session_id] and "all_level_topics" not in SESSION_STORE[session_id]:
        raise HTTPException(status_code=400, detail="Topics not loaded")
    
    # Try all_level_topics first, then level_topics
    if "all_level_topics" in SESSION_STORE[session_id]:
        topics = SESSION_STORE[session_id]["all_level_topics"]
    else:
        topics = SESSION_STORE[session_id]["level_topics"]
    
    topic = next((t for t in topics if t["id"] == topic_id), None)
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return topic

@app.post("/api/generate-custom-test")
async def generate_custom_test(request: dict):
    """Generate a custom test with mixed skills and topics"""
    try:
        session_id = request.get("session_id")
        skill_ids = request.get("skill_ids", [])
        topic_ids = request.get("topic_ids", [])
        questions_per_item = request.get("questions_per_item", 3)
        
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        all_questions = []
        question_id = 0
        
        # Generate questions for skills
        if skill_ids and "prerequisite_skills" in SESSION_STORE[session_id]:
            skills = SESSION_STORE[session_id]["prerequisite_skills"]
            for skill_id in skill_ids:
                skill = next((s for s in skills if s["id"] == skill_id), None)
                if skill:
                    questions = generate_skill_specific_questions(
                        skill,
                        questions_per_item
                    )
                    for q in questions:
                        q['id'] = question_id
                        q['skill_id'] = skill['id']
                        q['skill_name'] = skill['name']
                        q['category'] = skill['category']
                        question_id += 1
                    all_questions.extend(questions)
        
        # Generate questions for topics
        if topic_ids:
            # MODIFIED: Check both level_topics and all_level_topics
            if "all_level_topics" in SESSION_STORE[session_id]:
                topics = SESSION_STORE[session_id]["all_level_topics"]
                target_level = "All Levels"
            elif "level_topics" in SESSION_STORE[session_id]:
                topics = SESSION_STORE[session_id]["level_topics"]
                target_level = SESSION_STORE[session_id].get("target_level", "Data Scientist")
            else:
                raise HTTPException(status_code=400, detail="Topics not loaded")
                
            for topic_id in topic_ids:
                topic = next((t for t in topics if t["id"] == topic_id), None)
                if topic:
                    questions = generate_questions_with_ollama(
                        topic["name"],
                        f"{target_level} level",
                        questions_per_item
                    )
                    for q in questions:
                        q['id'] = question_id
                        q['topic_id'] = topic['id']
                        q['topic_name'] = topic['name']
                        q['level'] = topic.get('level', target_level)
                        question_id += 1
                    all_questions.extend(questions)
        
        if not all_questions:
            raise HTTPException(status_code=400, detail="No questions generated")
        
        random.shuffle(all_questions)
        
        # Create test
        test_id = str(uuid4())
        test_data = {
            "test_id": test_id,
            "session_id": session_id,
            "type": "custom",
            "questions": all_questions,
            "total_questions": len(all_questions),
            "created_at": datetime.now().isoformat()
        }
        
        MOCK_TEST_STORE[test_id] = test_data
        
        client_questions = [{
            'id': q['id'],
            'question': q['text'],
            'text': q['text'],
            'options': q['options'],
            'skill_id': q.get('skill_id'),
            'skill_name': q.get('skill_name'),
            'topic_id': q.get('topic_id'),
            'topic_name': q.get('topic_name'),
            'level': q.get('level'),
            'difficulty': q.get('difficulty', 'medium')
        } for q in all_questions]
        
        return {
            "test_id": test_id,
            "questions": client_questions,
            "total_questions": len(all_questions),
            "type": "custom"
        }
        
    except Exception as e:
        print(f"Error generating custom test: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-path/{session_id}")
async def get_learning_path(session_id: str):
    """Get recommended learning path based on session progress"""
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = SESSION_STORE[session_id]
    
    # MODIFIED: Determine current phase considering all levels
    if "target_level" not in session and "all_level_topics" not in session:
        current_phase = "prerequisites"
    elif "level_topics" in session or "all_level_topics" in session:
        current_phase = "level_topics"
    else:
        current_phase = "level_selection"
    
    learning_path = {
        "current_phase": current_phase,
        "completed_steps": [],
        "next_steps": [],
        "recommended_duration": {
            "prerequisites": "2-4 months",
            "beginner_level": "3-6 months",
            "moderate_level": "6-9 months",
            "advanced_level": "9-12 months"
        }
    }
    
    # Track completed steps
    if "prerequisite_skills" in session:
        learning_path["completed_steps"].append("✓ Prerequisites framework loaded")
    
    if "target_level" in session:
        learning_path["completed_steps"].append(f"✓ Target level selected: {session['target_level']}")
        learning_path["target_level"] = session["target_level"]
    
    if "level_topics" in session:
        learning_path["completed_steps"].append("✓ Level topics loaded")
    
    if "all_level_topics" in session:
        learning_path["completed_steps"].append("✓ All level topics loaded")
        learning_path["has_all_levels"] = True
    
    # Generate next steps
    if current_phase == "prerequisites":
        learning_path["next_steps"] = [
            "1. Complete prerequisite skills assessment",
            "2. Achieve 70%+ score to proceed",
            "3. Select target Data Scientist level or view all levels",
            "4. Begin level-specific learning"
        ]
    elif current_phase == "level_selection":
        learning_path["next_steps"] = [
            "1. Review available levels",
            "2. Select appropriate target level or view all levels",
            "3. Load level-specific topics",
            "4. Take topics assessment"
        ]
    else:
        if "all_level_topics" in session:
            learning_path["next_steps"] = [
                "1. Master topics across all levels",
                "2. Complete topics assessment for selected topics",
                "3. Score 70%+ to advance",
                "4. Build portfolio projects",
                "5. Consider certifications"
            ]
        else:
            learning_path["next_steps"] = [
                f"1. Master topics for {session.get('target_level', 'your level')}",
                "2. Complete topics assessment",
                "3. Score 70%+ to advance",
                "4. Build portfolio projects",
                "5. Consider certifications"
            ]
    
    return learning_path

@app.get("/api/framework-summary")
async def get_framework_summary():
    """Get complete framework summary"""
    prerequisite_skills_count = sum(
        len(section["skills"]) 
        for section in DATA_SCIENTIST_PREREQUISITES.values()
    )
    
    level_topics_count = {
        level: len(topics)
        for level, topics in LEVEL_TOPICS.items()
    }
    
    return {
        "framework_name": "Data Scientist Career Framework",
        "version": "3.0",
        "structure": {
            "prerequisites": {
                "sections": len(DATA_SCIENTIST_PREREQUISITES),
                "total_skills": prerequisite_skills_count,
                "sections_list": list(DATA_SCIENTIST_PREREQUISITES.keys())
            },
            "career_levels": {
                "levels": DATA_SCIENTIST_LEVELS,
                "topics_per_level": level_topics_count,
                "total_topics": sum(level_topics_count.values())
            }
        },
        "learning_path": [
            "1. Complete Prerequisites (All foundational skills)",
            "2. Master Beginner Level (Data Science fundamentals)",
            "3. Advance to Moderate Level (ML & databases)",
            "4. Reach Advanced Level (Deep Learning & deployment)"
        ],
        "estimated_timeline": "12-24 months total (varies by background)"
    }

@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics"""
    return {
        "active_sessions": len(SESSION_STORE),
        "active_tests": len(MOCK_TEST_STORE),
        "total_questions_generated": len(QUESTION_STORE),
        "framework": {
            "prerequisite_sections": len(DATA_SCIENTIST_PREREQUISITES),
            "career_levels": len(DATA_SCIENTIST_LEVELS),
            "total_beginner_topics": len(LEVEL_TOPICS.get("Beginner Level", [])),
            "total_moderate_topics": len(LEVEL_TOPICS.get("Moderate Level", [])),
            "total_advanced_topics": len(LEVEL_TOPICS.get("Advanced Level", [])),
            "total_topics": sum(len(LEVEL_TOPICS[l]) for l in DATA_SCIENTIST_LEVELS)
        }
    }

# NEW ENDPOINT: Get all topics from all levels
@app.get("/api/get-all-topics/{session_id}")
async def get_all_topics(session_id: str):
    """Get topics from ALL levels - comprehensive view"""
    try:
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        all_topics = []
        topic_id = 0
        
        for level_name, level_topics in LEVEL_TOPICS.items():
            for topic in level_topics:
                topic_with_id = topic.copy()
                topic_with_id["id"] = topic_id
                topic_with_id["level"] = level_name
                topic_with_id["level_index"] = DATA_SCIENTIST_LEVELS.index(level_name)
                
                # Flatten subtopics for easier access
                if "subtopics" in topic_with_id:
                    topic_with_id["all_subtopics"] = flatten_subtopics(
                        topic_with_id["subtopics"]
                    )
                    topic_with_id["subtopics_count"] = len(topic_with_id["all_subtopics"])
                else:
                    topic_with_id["subtopics_count"] = 0
                    topic_with_id["all_subtopics"] = []
                
                all_topics.append(topic_with_id)
                topic_id += 1
        
        # Store in session
        SESSION_STORE[session_id]["all_level_topics"] = all_topics
        
        # Group by level for easier frontend consumption
        topics_by_level = {}
        for topic in all_topics:
            level = topic["level"]
            if level not in topics_by_level:
                topics_by_level[level] = []
            topics_by_level[level].append(topic)
        
        return {
            "topics": all_topics,
            "topics_by_level": topics_by_level,
            "level": "All Levels",
            "total_topics": len(all_topics),
            "levels_covered": list(LEVEL_TOPICS.keys())
        }
        
    except Exception as e:
        print(f"Error getting all topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    


# ============================================================================
# ROADMAP GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/generate-roadmap")
async def generate_roadmap_endpoint(request: dict):
    """Generate truly personalized learning roadmap with daily tasks"""
    try:
        # Extract and validate inputs
        session_id = request.get("session_id")
        user_goal = request.get("goal", "Data Scientist")
        current_level = request.get("current_level", "Beginner Level")
        target_level = request.get("target_level", "Advanced Level")
        assessment_score = float(request.get("assessment_score", 50))
        weak_skills = request.get("weak_skills", [])
        weak_topics = request.get("weak_topics", [])
        strong_areas = request.get("strong_areas", [])
        timeline_preference = request.get("timeline_preference", "standard")
        
        # Validate inputs
        if not user_goal or not session_id:
            raise HTTPException(status_code=400, detail="Missing required fields: goal and session_id")
        
        # Ensure lists
        if not isinstance(weak_skills, list):
            weak_skills = []
        if not isinstance(weak_topics, list):
            weak_topics = []
        if not isinstance(strong_areas, list):
            strong_areas = []
        
        logger.info(f"Generating daily roadmap for {user_goal}: {current_level} -> {target_level}")
        logger.info(f"Weak areas: {len(weak_skills + weak_topics)}, Strong areas: {len(strong_areas)}")
        
        # Generate personalized roadmap with timeout
        try:
            roadmap_data = await asyncio.wait_for(
                roadmap_generator.generate_ai_enhanced_roadmap(
                    user_goal=user_goal,
                    current_level=current_level,
                    target_level=target_level,
                    assessment_score=assessment_score,
                    weak_skills=weak_skills,
                    weak_topics=weak_topics,
                    strong_areas=strong_areas,
                    timeline_preference=timeline_preference
                ),
                timeout=300  # 5 minute timeout
            )
        except asyncio.TimeoutError:
            logger.error("Roadmap generation timed out after 5 minutes")
            raise HTTPException(status_code=504, detail="Roadmap generation timed out. Please try again.")
        
        # Store roadmap in session
        if session_id not in SESSION_STORE:
            SESSION_STORE[session_id] = {}
        
        SESSION_STORE[session_id]["roadmap"] = roadmap_data
        SESSION_STORE[session_id]["roadmap_generated_at"] = datetime.now().isoformat()
        SESSION_STORE[session_id]["goal"] = user_goal
        SESSION_STORE[session_id]["current_level"] = current_level
        SESSION_STORE[session_id]["target_level"] = target_level
        SESSION_STORE[session_id]["weak_skills"] = weak_skills
        SESSION_STORE[session_id]["weak_topics"] = weak_topics
        SESSION_STORE[session_id]["strong_areas"] = strong_areas
        
        logger.info(f"Daily roadmap stored for session {session_id}")
        
        # Log success metrics
        total_weeks = len(roadmap_data.get("weekly_schedule", []))
        total_days = sum(len(week.get("days", [])) for week in roadmap_data.get("weekly_schedule", []))
        total_tasks = sum(
            sum(len(day.get("tasks", [])) for day in week.get("days", []))
            for week in roadmap_data.get("weekly_schedule", [])
        )
        
        logger.info(f"Daily roadmap generated: {total_weeks} weeks, {total_days} days, {total_tasks} tasks")
        
        return roadmap_data
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Roadmap generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate roadmap: {str(e)}")

@app.get("/api/roadmap/{session_id}")
async def get_roadmap(session_id: str):
    """Get stored roadmap for session"""
    try:
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        roadmap = SESSION_STORE[session_id].get("roadmap")
        if not roadmap:
            raise HTTPException(status_code=404, detail="No roadmap found for this session")
        
        # Add retrieval metadata
        roadmap["retrieved_at"] = datetime.now().isoformat()
        roadmap["session_id"] = session_id
        
        return roadmap
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving roadmap: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve roadmap")

@app.post("/api/regenerate-roadmap/{session_id}")
async def regenerate_roadmap(session_id: str, request: dict = None):
    """Regenerate roadmap with different timeline"""
    try:
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = SESSION_STORE[session_id]
        
        # Get timeline preference from request or use default
        if request and "timeline_preference" in request:
            timeline_preference = request["timeline_preference"]
        else:
            timeline_preference = "standard"
        
        # Validate timeline preference
        valid_timelines = ["relaxed", "standard", "accelerated"]
        if timeline_preference not in valid_timelines:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid timeline. Choose from: {', '.join(valid_timelines)}"
            )
        
        # Get previous assessment data
        old_roadmap = session.get("roadmap", {})
        
        assessment_data = {
            "user_goal": session.get("goal") or old_roadmap.get("goal", "Data Scientist"),
            "current_level": old_roadmap.get("current_level", "Beginner Level"),
            "target_level": old_roadmap.get("target_level", "Advanced Level"),
            "assessment_score": old_roadmap.get("assessment_summary", {}).get("readiness_score", 50),
            "weak_skills": session.get("weak_skills", []),
            "weak_topics": session.get("weak_topics", []),
            "strong_areas": session.get("strong_areas", []),
            "timeline_preference": timeline_preference
        }
        
        logger.info(f"Regenerating roadmap for session {session_id} with timeline: {timeline_preference}")
        
        # Generate new roadmap with timeout
        try:
            new_roadmap = await asyncio.wait_for(
                roadmap_generator.generate_ai_enhanced_roadmap(**assessment_data),
                timeout=300
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Roadmap regeneration timed out")
        
        # Store updated roadmap
        SESSION_STORE[session_id]["roadmap"] = new_roadmap
        SESSION_STORE[session_id]["roadmap_regenerated_at"] = datetime.now().isoformat()
        SESSION_STORE[session_id]["timeline_preference"] = timeline_preference
        
        logger.info(f"Roadmap regenerated successfully: {len(new_roadmap.get('weekly_schedule', []))} weeks")
        
        return new_roadmap
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Roadmap regeneration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to regenerate roadmap")
    
@app.post("/api/roadmap/update-task/{session_id}")
async def update_task_status(session_id: str, task_update: dict):
    """Update task completion status"""
    try:
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        roadmap = SESSION_STORE[session_id].get("roadmap")
        if not roadmap:
            raise HTTPException(status_code=404, detail="No roadmap found")
        
        week_idx = task_update.get("week_index")
        day_idx = task_update.get("day_index")
        task_idx = task_update.get("task_index")
        completed = task_update.get("completed", False)
        
        if (week_idx is not None and day_idx is not None and task_idx is not None and
            week_idx < len(roadmap["weekly_schedule"]) and
            day_idx < len(roadmap["weekly_schedule"][week_idx]["days"]) and
            task_idx < len(roadmap["weekly_schedule"][week_idx]["days"][day_idx]["tasks"])):
            
            roadmap["weekly_schedule"][week_idx]["days"][day_idx]["tasks"][task_idx]["completed"] = completed
            roadmap["last_updated"] = datetime.now().isoformat()
            
            return {"message": "Task status updated successfully", "completed": completed}
        else:
            raise HTTPException(status_code=400, detail="Invalid task indices")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Task update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update task")

@app.get("/api/roadmap/progress/{session_id}")
async def get_roadmap_progress(session_id: str):
    """Get roadmap progress statistics"""
    try:
        if session_id not in SESSION_STORE:
            raise HTTPException(status_code=404, detail="Session not found")
        
        roadmap = SESSION_STORE[session_id].get("roadmap")
        if not roadmap:
            raise HTTPException(status_code=404, detail="No roadmap found")
        
        total_tasks = 0
        completed_tasks = 0
        
        for week in roadmap.get("weekly_schedule", []):
            for day in week.get("days", []):
                for task in day.get("tasks", []):
                    total_tasks += 1
                    if task.get("completed", False):
                        completed_tasks += 1
        
        progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress_percentage": round(progress_percentage, 1),
            "remaining_tasks": total_tasks - completed_tasks,
            "current_week": len(roadmap.get("weekly_schedule", [])),
            "total_weeks": roadmap.get("total_weeks", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Progress calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate progress")

@app.delete("/api/roadmap/{session_id}")
async def delete_roadmap(session_id: str):
    """Delete roadmap for session"""
    try:
        if session_id in SESSION_STORE:
            del SESSION_STORE[session_id]
            return {"message": "Roadmap deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Roadmap deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete roadmap")



# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "sessions_active": len(SESSION_STORE)
    }






# ========================================
# AUTHENTICATION CODE
# ========================================



#new code 
from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.errors import DuplicateKeyError
from typing import List, Optional
from fastapi.responses import JSONResponse
import database
import auth
from models import (
    UserCreate, UserLogin, UserResponse, UserInDB, Token,
    StudentProfileCreate, StudentProfileUpdate, StudentProfileResponse, StudentProfileInDB,
    ForgotPasswordRequest, VerifyResetCode, ResetPassword,
    AuthProvider, ContactForm, ContactResponse
)
from datetime import timedelta, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import asyncio
import logging
from jose import JWTError, jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# app = FastAPI(title="LearnVibe API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kolaprasad2507@gmail.com"
SMTP_PASSWORD = "yetf anfm wree eabf"

# For development - if email fails, log to console
DEVELOPMENT_MODE = True

# ========================================
# DEPENDENCIES & MIDDLEWARE
# ========================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = get_user_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ========================================
# EMAIL SERVICE
# ========================================

async def send_reset_code_email(email: str, code: str):
    """Send password reset code via email"""
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = SMTP_USERNAME
        message["To"] = email
        message["Subject"] = "LearnVibe - Password Reset Code"
        
        # Email body
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #2563eb; text-align: center;">Password Reset Request</h2>
                    <p>You requested a password reset for your LearnVibe account.</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <div style="font-size: 32px; font-weight: bold; color: #2563eb; letter-spacing: 5px; padding: 20px; background: #f3f4f6; border-radius: 8px; display: inline-block;">
                            {code}
                        </div>
                    </div>
                    <p><strong>This code will expire in 1 hour.</strong></p>
                    <p>If you didn't request this reset, please ignore this email.</p>
                    <br>
                    <p>Best regards,<br><strong>LearnVibe Team</strong></p>
                </div>
            </body>
        </html>
        """
        
        message.attach(MIMEText(body, "html"))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
            
        logger.info(f"Reset code sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        
        # In development mode, log the code to console but don't show in response
        if DEVELOPMENT_MODE:
            logger.info(f"DEVELOPMENT MODE - Reset code for {email}: {code}")
            # Don't return True here - let the user know email failed
            return False
        
        return False

# ========================================
# USER AUTHENTICATION HELPERS
# ========================================

def get_user_by_email(email: str):
    """Get user by email from database"""
    try:
        user_data = database.user_registration_collection.find_one({"email": email})
        if user_data:
            return UserInDB(**user_data)
        return None
    except Exception as e:
        logger.error(f"Error fetching user by email {email}: {str(e)}")
        return None

def create_user(user: UserCreate):
    """Create a new user in the database"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password for email/password users
        hashed_password = None
        if user.auth_provider == AuthProvider.EMAIL:
            hashed_password = auth.get_password_hash(user.password)
        
        # Create user document
        user_dict = {
            "name": user.name,
            "email": user.email,
            "hashed_password": hashed_password,
            "auth_provider": user.auth_provider,
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        result = database.user_registration_collection.insert_one(user_dict)
        
        # Get the created user
        created_user = database.user_registration_collection.find_one({"_id": result.inserted_id})
        
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created user"
            )
        
        return UserInDB(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )

def create_token_response(user: UserInDB):
    """Create token response for successful authentication"""
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    user_response = UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        auth_provider=user.auth_provider,
        profile_picture=user.profile_picture,
        created_at=user.created_at
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

# ========================================
# AUTHENTICATION ENDPOINTS
# ========================================

@app.post("/api/auth/signup", response_model=Token)
async def signup(user_data: UserCreate):
    """Handle user signup"""
    try:
        # Validate input
        if not user_data.email or not user_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Create user
        user = create_user(user_data)
        return create_token_response(user)
        
    except HTTPException:
        raise
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    except Exception as e:
        logger.error(f"Signup error for {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during signup"
        )

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Handle user login"""
    try:
        # Validate input
        if not user_credentials.email or not user_credentials.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Check if user exists
        user = get_user_by_email(user_credentials.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check authentication method
        if user.auth_provider != AuthProvider.EMAIL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This account uses different authentication method."
            )
        
        # Verify password
        if not user.hashed_password or not auth.verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create token response
        return create_token_response(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {user_credentials.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@app.post("/api/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """Send password reset code to email"""
    try:
        # Validate input
        if not request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
        # Check if user exists (but don't reveal information)
        user = get_user_by_email(request.email)
        if not user:
            # Return success even if user doesn't exist for security
            return {
                "message": "If the email exists in our system, a reset code has been sent"
            }
        
        # Generate reset code
        reset_code = auth.generate_reset_code()
        
        # Store reset code in database with expiry
        reset_data = {
            "email": request.email,
            "code": reset_code,
            "created_at": datetime.utcnow()
        }
        
        # Delete any existing reset codes for this email
        database.password_reset_collection.delete_many({"email": request.email})
        
        # Insert new reset code
        database.password_reset_collection.insert_one(reset_data)
        
        # Send email in background
        email_sent = await send_reset_code_email(request.email, reset_code)
        
        if not email_sent:
            # Delete the reset code if email failed
            database.password_reset_collection.delete_many({"email": request.email})
            if DEVELOPMENT_MODE:
                # In development mode, we'll let it succeed but log the code
                logger.info(f"DEVELOPMENT: Email failed but code is: {reset_code}")
                return {
                    "message": "If the email exists in our system, a reset code has been sent"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send reset email. Please try again later."
                )
        
        # Always return the same message for security
        return {
            "message": "If the email exists in our system, a reset code has been sent"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forgot password error for {request.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing forgot password request"
        )

@app.post("/api/auth/verify-reset-code")
async def verify_reset_code(verification: VerifyResetCode):
    """Verify reset code"""
    try:
        # Validate input
        if not verification.email or not verification.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and code are required"
            )
        
        # Find valid reset code
        reset_data = database.password_reset_collection.find_one({
            "email": verification.email,
            "code": verification.code
        })
        
        if not reset_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset code"
            )
        
        # Check if code is expired (additional safety)
        code_created = reset_data["created_at"]
        if datetime.utcnow() - code_created > timedelta(hours=1):
            database.password_reset_collection.delete_one({"_id": reset_data["_id"]})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset code has expired"
            )
        
        return {"message": "Reset code verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Verify reset code error for {verification.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error verifying reset code"
        )

@app.post("/api/auth/reset-password")
async def reset_password(reset_data: ResetPassword):
    """Reset password with verified code"""
    try:
        # Validate input
        if not reset_data.email or not reset_data.code or not reset_data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email, code, and new password are required"
            )
        
        if len(reset_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Verify reset code first
        reset_record = database.password_reset_collection.find_one({
            "email": reset_data.email,
            "code": reset_data.code
        })
        
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset code"
            )
        
        # Get user
        user = get_user_by_email(reset_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        hashed_password = auth.get_password_hash(reset_data.new_password)
        database.user_registration_collection.update_one(
            {"email": reset_data.email},
            {"$set": {"hashed_password": hashed_password}}
        )
        
        # Delete used reset code
        database.password_reset_collection.delete_one({
            "email": reset_data.email,
            "code": reset_data.code
        })
        
        # Delete all other reset codes for this email
        database.password_reset_collection.delete_many({"email": reset_data.email})
        
        logger.info(f"Password reset successfully for {reset_data.email}")
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error for {reset_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error resetting password"
        )
    


# Add this to your existing signup.py file, in the AUTHENTICATION ENDPOINTS section

@app.post("/api/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user by blacklisting the token
    """
    try:
        token = credentials.credentials
        
        # Verify the token is valid before blacklisting
        try:
            payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
            
            # Add token to blacklist
            auth.token_blacklist.add(token)
            
            logger.info(f"User {payload.get('sub')} logged out successfully")
            
            return {"message": "Logged out successfully"}
            
        except JWTError as e:
            # Even if token is invalid, we should still process logout
            # but don't add invalid tokens to blacklist
            logger.warning(f"Logout with invalid token: {str(e)}")
            return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# Update the get_current_user dependency to check blacklisted tokens
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token with blacklist check"""
    try:
        token = credentials.credentials
        
        # Check if token is blacklisted
        if token in auth.token_blacklist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated"
            )
        
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = get_user_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# ========================================
# PROTECTED ROUTES
# ========================================

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        email=current_user.email,
        auth_provider=current_user.auth_provider,
        profile_picture=current_user.profile_picture,
        created_at=current_user.created_at
    )

# ========================================
# STUDENT PROFILE ENDPOINTS
# ========================================

@app.post("/api/students", response_model=StudentProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_student_profile(profile: StudentProfileCreate):
    """Create a new student profile"""
    try:
        # Check if student ID already exists
        existing_profile = database.users_profile_collection.find_one({"studentId": profile.studentId})
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student ID '{profile.studentId}' already exists"
            )
        
        # Create profile document
        profile_dict = profile.dict()
        profile_dict["created_at"] = datetime.utcnow()
        profile_dict["updated_at"] = datetime.utcnow()
        
        # Insert into database
        result = database.users_profile_collection.insert_one(profile_dict)
        
        # Get the created profile
        created_profile = database.users_profile_collection.find_one({"_id": result.inserted_id})
        
        if not created_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created profile"
            )
        
        # Convert to response model
        return StudentProfileResponse(
            id=str(created_profile["_id"]),
            name=created_profile["name"],
            email=created_profile["email"],
            dob=created_profile.get("dob"),
            phone=created_profile.get("phone"),
            studentId=created_profile["studentId"],
            major=created_profile.get("major"),
            year=created_profile["year"],
            gpa=created_profile.get("gpa"),
            address=created_profile.get("address"),
            enrollmentDate=created_profile.get("enrollmentDate"),
            expectedGraduation=created_profile.get("expectedGraduation"),
            profilePic=created_profile.get("profilePic"),
            created_at=created_profile["created_at"],
            updated_at=created_profile["updated_at"]
        )
        
    except HTTPException:
        raise
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student ID '{profile.studentId}' already exists"
        )
    except Exception as e:
        logger.error(f"Error creating student profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating student profile"
        )

# ========================================
# CONTACT ENDPOINTS - UPDATED
# ========================================

async def send_contact_notification_email(contact_data: ContactForm):
    """Send notification email for contact form submission to domain email"""
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = SMTP_USERNAME
        message["To"] = SMTP_USERNAME  # Send to your domain email
        message["Reply-To"] = contact_data.email  # Allow replying directly to the user
        message["Subject"] = f"LearnVibe Contact: {contact_data.subject}"
        
        # Email body with better formatting
        body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px 8px 0 0; color: white; text-align: center; }}
                    .content {{ padding: 20px; background: #f8fafc; }}
                    .detail-section {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #667eea; }}
                    .message-section {{ background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #bae6fd; }}
                    .footer {{ margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb; text-align: center; color: #6b7280; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2 style="margin: 0; color: white;">📧 New Contact Form Submission</h2>
                        <p style="margin: 5px 0 0 0; opacity: 0.9;">LearnVibe Platform</p>
                    </div>
                    
                    <div class="content">
                        <div class="detail-section">
                            <h3 style="margin-top: 0; color: #374151; border-bottom: 2px solid #f3f4f6; padding-bottom: 10px;">Contact Details</h3>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px 0; width: 100px; font-weight: bold; color: #4b5563;">Name:</td>
                                    <td style="padding: 8px 0;">{contact_data.name}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #4b5563;">Email:</td>
                                    <td style="padding: 8px 0;">
                                        <a href="mailto:{contact_data.email}" style="color: #2563eb; text-decoration: none;">
                                            {contact_data.email}
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #4b5563;">Phone:</td>
                                    <td style="padding: 8px 0;">{contact_data.phone or 'Not provided'}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px 0; font-weight: bold; color: #4b5563;">Subject:</td>
                                    <td style="padding: 8px 0; color: #059669; font-weight: 500;">{contact_data.subject}</td>
                                </tr>
                            </table>
                        </div>
                        
                        <div class="message-section">
                            <h3 style="margin-top: 0; color: #374151; border-bottom: 2px solid #dbeafe; padding-bottom: 10px;">Message Content</h3>
                            <div style="white-space: pre-line; line-height: 1.8; color: #1e40af;">
                                {contact_data.message}
                            </div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>
                            This message was sent from the LearnVibe contact form<br>
                            <strong>Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d at %H:%M:%S UTC')}
                        </p>
                        <p style="margin-top: 10px;">
                            💡 <em>You can reply directly to this email to respond to {contact_data.name}</em>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        message.attach(MIMEText(body, "html"))
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
            
        logger.info(f"Contact notification sent successfully to {SMTP_USERNAME} from {contact_data.email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending contact notification: {str(e)}")
        
        # In development mode, log the contact details
        if DEVELOPMENT_MODE:
            logger.info(f"DEVELOPMENT MODE - Contact form submission:")
            logger.info(f"Name: {contact_data.name}")
            logger.info(f"Email: {contact_data.email}")
            logger.info(f"Phone: {contact_data.phone}")
            logger.info(f"Subject: {contact_data.subject}")
            logger.info(f"Message: {contact_data.message}")
            # In development, we'll consider it successful for testing
            return True
        
        return False

@app.post("/api/contact")
async def submit_contact_form(contact_data: ContactForm, background_tasks: BackgroundTasks):
    """Handle contact form submission with enhanced response"""
    try:
        # Validate input
        if not contact_data.name or not contact_data.email or not contact_data.subject or not contact_data.message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All fields are required"
            )
        
        # Validate email format
        if "@" not in contact_data.email or "." not in contact_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please enter a valid email address"
            )
        
        # Validate message length
        if len(contact_data.message) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message should be at least 10 characters long"
            )
        
        # Create contact document
        contact_dict = contact_data.dict()
        contact_dict["status"] = "pending"
        contact_dict["created_at"] = datetime.utcnow()
        
        # Insert into database
        result = database.contact_collection.insert_one(contact_dict)
        
        # Get the created contact
        created_contact = database.contact_collection.find_one({"_id": result.inserted_id})
        
        if not created_contact:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit contact form"
            )
        
        # Send notification email in background
        email_sent = await send_contact_notification_email(contact_data)
        
        if not email_sent:
            # Update status to failed
            database.contact_collection.update_one(
                {"_id": result.inserted_id},
                {"$set": {"status": "email_failed"}}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email notification. Please try again later."
            )
        
        # Update status to sent
        database.contact_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"status": "sent"}}
        )
        
        logger.info(f"Contact form submitted successfully by {contact_data.email}")
        
        # Return success response
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Message sent successfully!",
                "data": {
                    "id": str(created_contact["_id"]),
                    "name": created_contact["name"],
                    "email": created_contact["email"],
                    "subject": created_contact["subject"],
                    "status": "sent"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contact form submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error submitting contact form"
        )

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        database.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Data Scientist Career Framework API")
    print("=" * 60)
    print(f"Prerequisites: {sum(len(s['skills']) for s in DATA_SCIENTIST_PREREQUISITES.values())} skills")
    print(f"Career Levels: {len(DATA_SCIENTIST_LEVELS)}")
    print(f"Total Topics: {sum(len(LEVEL_TOPICS[l]) for l in DATA_SCIENTIST_LEVELS)}")
    print("=" * 60)
    print("🎯 Enhanced Skills Mock Test Generation: ACTIVE")
    print("📊 Quality Scoring & Validation: ENABLED")
    print("🔧 Enhanced Fallback Questions: READY")
    print("🌐 All Levels Topic Display: ENABLED")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)