# from fastapi import FastAPI, HTTPException, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional, Any, Literal
# import random
# import ollama
# from uuid import UUID, uuid4
# import json
# from datetime import datetime, timedelta
# import re
# import asyncio
# from enum import Enum

# app = FastAPI(title="Enhanced Skills Mock Test API", version="4.0")

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Enhanced Data Structures
# class DifficultyLevel(str, Enum):
#     EASY = "easy"
#     MEDIUM = "medium"
#     HARD = "hard"

# class QuestionType(str, Enum):
#     MULTIPLE_CHOICE = "multiple_choice"
#     CODE = "code"
#     THEORETICAL = "theoretical"

# class AssessmentType(str, Enum):
#     SKILLS = "skills"
#     TOPICS = "topics"

# class ProficiencyLevel(str, Enum):
#     BEGINNER = "beginner"
#     INTERMEDIATE = "intermediate"
#     ADVANCED = "advanced"

# # Pydantic Models
# class GoalInput(BaseModel):
#     goal: str = Field(..., min_length=1, max_length=100)
#     session_id: str

# class AnswersInput(BaseModel):
#     goal: str
#     answers: List[int]
#     questions: List[Dict]
#     session_id: str

# class SessionData(BaseModel):
#     session_id: str
#     goal: str
#     current_level: str
#     target_level: str
#     custom_levels: List[str]
#     topics: List[str]
#     assessment_score: Optional[int] = Field(None, ge=0, le=100)

# class MockTestRequest(BaseModel):
#     session_id: str
#     prerequisite_ids: List[str]
#     questions_per_skill: int = Field(default=5, ge=1, le=10)

# class MockTestSubmission(BaseModel):
#     test_id: str
#     answers: Dict[str, int]
#     time_taken_seconds: int = Field(..., ge=0)

# class UserSkillsInput(BaseModel):
#     session_id: str
#     selected_skills: List[str]
#     proficiency_level: ProficiencyLevel

# class TargetTopicsInput(BaseModel):
#     session_id: str
#     target_level: str
#     selected_topics: List[str]

# class QuestionGenerationConfig(BaseModel):
#     difficulty_distribution: Dict[DifficultyLevel, float] = {
#         DifficultyLevel.EASY: 0.4,
#         DifficultyLevel.MEDIUM: 0.4,
#         DifficultyLevel.HARD: 0.2
#     }
#     practical_focus: bool = True
#     include_code_questions: bool = False

# class SkillsMockTestRequest(BaseModel):
#     session_id: str
#     selected_skills: List[str]
#     total_questions: int = Field(default=15, ge=5, le=50)

# class TopicsMockTestRequest(BaseModel):
#     session_id: str
#     selected_topics: List[str]
#     total_questions: int = Field(default=15, ge=5, le=50)

# # Enhanced Data Science Roadmap with detailed topics
# DATA_SCIENCE_ROADMAP = {
#     "goal": "Data Scientist",
#     "levels": {
#         "beginner_level": {
#             "name": "Beginner Level",
#             "description": "Entry-level position focusing on foundational skills",
#             "experience_range": "0-2 years",
#             "rank": 0,
#             "required_skills": ["Python", "Statistics", "Data Cleaning", "SQL"]
#         },
#         "moderate_level": {
#             "name": "Moderate Level", 
#             "description": "Independent work with moderate complexity",
#             "experience_range": "2-4 years",
#             "rank": 1,
#             "required_skills": ["Supervised Learning", "Feature Engineering", "R", "Git"]
#         },
#         "advanced_level": {
#             "name": "Advanced Level",
#             "description": "Lead complex projects and mentor teams",
#             "experience_range": "4-7 years", 
#             "rank": 2,
#             "required_skills": ["Deep Learning", "Unsupervised Learning", "Model Evaluation", "Linear Algebra"]
#         },
#         "expert_level": {
#             "name": "Expert Level",
#             "description": "Expert-level leadership and strategy",
#             "experience_range": "7+ years",
#             "rank": 3,
#             "required_skills": ["ML System Design", "Advanced Calculus", "Probability", "ETL"]
#         }
#     },
#     "skills": {
#         "programming": {
#             "Python": {
#                 "description": "Python programming for data analysis",
#                 "difficulty": "beginner",
#                 "category": "core",
#                 "subtopics": ["Syntax", "Data Structures", "Libraries", "OOP"]
#             },
#             "R": {
#                 "description": "Statistical programming with R",
#                 "difficulty": "beginner", 
#                 "category": "core",
#                 "subtopics": ["Data Frames", "Statistical Tests", "Visualization"]
#             },
#             "SQL": {
#                 "description": "Database querying and management",
#                 "difficulty": "beginner",
#                 "category": "core",
#                 "subtopics": ["Queries", "Joins", "Indexing", "Optimization"]
#             },
#             "Git": {
#                 "description": "Version control and collaboration",
#                 "difficulty": "beginner",
#                 "category": "tools",
#                 "subtopics": ["Branching", "Merging", "CI/CD", "Collaboration"]
#             }
#         },
#         "mathematics": {
#             "Statistics": {
#                 "description": "Statistical analysis and inference",
#                 "difficulty": "beginner",
#                 "category": "foundation",
#                 "subtopics": ["Descriptive Stats", "Inferential Stats", "Hypothesis Testing", "Distributions"]
#             },
#             "Linear Algebra": {
#                 "description": "Vectors, matrices, and linear transformations",
#                 "difficulty": "intermediate",
#                 "category": "foundation",
#                 "subtopics": ["Vectors", "Matrices", "Eigenvalues", "Transformations"]
#             },
#             "Calculus": {
#                 "description": "Differential and integral calculus",
#                 "difficulty": "intermediate",
#                 "category": "foundation",
#                 "subtopics": ["Derivatives", "Integrals", "Optimization", "Multivariate"]
#             },
#             "Probability": {
#                 "description": "Probability theory and distributions",
#                 "difficulty": "intermediate",
#                 "category": "foundation",
#                 "subtopics": ["Probability Rules", "Distributions", "Bayesian", "Random Variables"]
#             }
#         },
#         "machine_learning": {
#             "Supervised Learning": {
#                 "description": "Classification and regression algorithms",
#                 "difficulty": "intermediate",
#                 "category": "ml",
#                 "subtopics": ["Linear Regression", "Logistic Regression", "Decision Trees", "SVM"]
#             },
#             "Unsupervised Learning": {
#                 "description": "Clustering and dimensionality reduction",
#                 "difficulty": "intermediate",
#                 "category": "ml",
#                 "subtopics": ["K-Means", "PCA", "Hierarchical Clustering", "Anomaly Detection"]
#             },
#             "Deep Learning": {
#                 "description": "Neural networks and deep architectures",
#                 "difficulty": "advanced",
#                 "category": "ml",
#                 "subtopics": ["Neural Networks", "CNN", "RNN", "Transfer Learning"]
#             },
#             "Model Evaluation": {
#                 "description": "Performance metrics and validation techniques",
#                 "difficulty": "intermediate",
#                 "category": "ml",
#                 "subtopics": ["Cross-Validation", "Metrics", "Hyperparameter Tuning", "Bias-Variance"]
#             }
#         },
#         "data_processing": {
#             "Data Cleaning": {
#                 "description": "Handling missing values and outliers",
#                 "difficulty": "beginner",
#                 "category": "processing",
#                 "subtopics": ["Missing Data", "Outlier Detection", "Data Transformation", "Normalization"]
#             },
#             "Feature Engineering": {
#                 "description": "Creating and selecting features",
#                 "difficulty": "intermediate",
#                 "category": "processing",
#                 "subtopics": ["Feature Creation", "Feature Selection", "Dimensionality Reduction", "Encoding"]
#             },
#             "Data Visualization": {
#                 "description": "Creating insightful visualizations",
#                 "difficulty": "beginner",
#                 "category": "processing",
#                 "subtopics": ["Matplotlib", "Seaborn", "Plotly", "Dashboarding"]
#             },
#             "ETL": {
#                 "description": "Extract, transform, load processes",
#                 "difficulty": "intermediate",
#                 "category": "processing",
#                 "subtopics": ["Data Extraction", "Data Transformation", "Data Loading", "Pipeline Design"]
#             }
#         }
#     },
#     "topics": {
#         "beginner_level": {
#             "Mathematics for Data Science": {
#                 "description": "Fundamental mathematical concepts for data analysis",
#                 "subtopics": [
#                     "Probability Theory - Independent & dependent events, Conditional probability, Bayes' theorem",
#                     "Descriptive Statistics - Central tendency, Dispersion, Skewness & kurtosis", 
#                     "Inferential Statistics - Sampling methods, Hypothesis testing, Confidence intervals, P-values",
#                     "Correlation & Covariance - Pearson correlation, Covariance interpretation"
#                 ],
#                 "priority": "high",
#                 "required_skills": ["Statistics", "Probability"]
#             },
#             "Python for Data Science": {
#                 "description": "Essential Python libraries and tools for data analysis",
#                 "subtopics": [
#                     "Numpy - Arrays, indexing, Broadcasting, Linear algebra basics",
#                     "Pandas - Series & DataFrame, Indexing, slicing, GroupBy, merges, joins, Aggregations",
#                     "Visualization - Matplotlib (line, scatter, bar, pie), Seaborn (heatmap, histogram, boxplot)"
#                 ],
#                 "priority": "high",
#                 "required_skills": ["Python", "Data Visualization"]
#             }
#         },
#         "moderate_level": {
#             "SQL & Databases": {
#                 "description": "Database management and querying skills", 
#                 "subtopics": [
#                     "Queries - SELECT, WHERE, ORDER BY, GROUP BY, HAVING",
#                     "Joins - INNER, LEFT, RIGHT, FULL",
#                     "Subqueries & CTEs - Common table expressions, Nested queries",
#                     "Window Functions - ROW_NUMBER, RANK, LAG, LEAD"
#                 ],
#                 "priority": "medium",
#                 "required_skills": ["SQL", "Data Cleaning"]
#             },
#             "Machine Learning Basics": {
#                 "description": "Fundamental machine learning algorithms and techniques",
#                 "subtopics": [
#                     "Regression - Linear regression, Multiple regression",
#                     "Classification - Logistic regression, k-NN, Decision Trees", 
#                     "Evaluation Metrics - Accuracy, Precision, Recall, F1, Confusion matrix, ROC, AUC",
#                     "Model Selection - Cross-validation, Bias-variance tradeoff"
#                 ],
#                 "priority": "high",
#                 "required_skills": ["Supervised Learning", "Model Evaluation"]
#             }
#         },
#         "advanced_level": {
#             "Advanced Machine Learning": {
#                 "description": "Complex machine learning algorithms and ensemble methods",
#                 "subtopics": [
#                     "Ensembles - Random Forest, Gradient Boosting, XGBoost, LightGBM, CatBoost",
#                     "SVM - Linear, Kernel methods",
#                     "Clustering - K-Means, Hierarchical, DBSCAN",
#                     "Dimensionality Reduction - PCA, t-SNE, UMAP"
#                 ],
#                 "priority": "high",
#                 "required_skills": ["Unsupervised Learning", "Model Evaluation"]
#             }
#         },
#         "expert_level": {
#             "ML System Design": {
#                 "description": "Designing and deploying machine learning systems at scale",
#                 "subtopics": [
#                     "System Architecture - Microservices, Data pipelines, Model serving",
#                     "Scalability - Distributed computing, Parallel processing, Cloud infrastructure", 
#                     "Monitoring - Model performance tracking, Data drift detection, System health"
#                 ],
#                 "priority": "medium",
#                 "required_skills": ["Git", "ETL"]
#             }
#         }
#     }
# }

# # Storage
# QUESTION_STORE: Dict[str, List[Dict]] = {}
# SESSION_STORE: Dict[str, Dict] = {}
# MOCK_TEST_STORE: Dict[str, Dict] = {}
# USER_SKILLS_STORE: Dict[str, Dict] = {}
# USER_PROGRESS_STORE: Dict[str, Dict] = {}
# SKILL_STACK_STORE: Dict[str, List[str]] = {}
# TOPIC_STACK_STORE: Dict[str, List[str]] = {}

# class AIQuestionGenerator:
#     """Enhanced AI-powered question generator with robust parsing and validation"""
    
#     @staticmethod
#     async def generate_questions(
#         goal: str, 
#         context: Dict, 
#         num_questions: int = 10,
#         model: str = 'llama3.2:1b'
#     ) -> List[Dict]:
#         """
#         Generate diverse, high-quality questions using Llama model
        
#         Args:
#             goal: Career goal (e.g., "Data Scientist")
#             context: Dict with skill_name/topic_name, category, level, assessment_type
#             num_questions: Number of questions to generate
#             model: Ollama model to use
            
#         Returns:
#             List of validated question dictionaries
#         """
        
#         # Extract context
#         assessment_type = context.get('assessment_type', AssessmentType.SKILLS)
#         is_skill_assessment = assessment_type == AssessmentType.SKILLS
        
#         if is_skill_assessment:
#             subject = context.get('skill_name', 'General Skill')
#             category = context.get('category', 'General')
#             level = context.get('level', 'beginner')
#             subtopics = context.get('subtopics', [])
#         else:
#             subject = context.get('topic_name', 'General Topic')
#             category = context.get('category', 'General')
#             level = context.get('level', 'Beginner')
#             subtopics = context.get('subtopics', [])
        
#         # Build contextual prompt
#         prompt = AIQuestionGenerator._build_prompt(
#             goal=goal,
#             subject=subject,
#             category=category,
#             level=level,
#             num_questions=num_questions,
#             is_skill=is_skill_assessment,
#             subtopics=subtopics
#         )
        
#         try:
#             # Call Ollama model
#             response = ollama.chat(
#                 model=model,
#                 messages=[{'role': 'user', 'content': prompt}]
#             )
            
#             generated_text = response['message']['content']
            
#             # Parse questions from response
#             questions = AIQuestionGenerator._parse_questions(
#                 generated_text, 
#                 subject, 
#                 category, 
#                 level,
#                 is_skill_assessment
#             )
            
#             # Validate and ensure diversity
#             valid_questions = AIQuestionGenerator._validate_questions(questions, num_questions)
            
#             # Add final metadata
#             for i, q in enumerate(valid_questions):
#                 q['id'] = f"q_{uuid4().hex[:8]}"
#                 q['question_number'] = i + 1
                
#                 if is_skill_assessment:
#                     q['skill_name'] = subject
#                     q['skill_id'] = context.get('skill_id')
#                 else:
#                     q['topic_name'] = subject
#                     q['topic_id'] = context.get('topic_id')
            
#             print(f"✓ Generated {len(valid_questions)} questions for {subject}")
#             return valid_questions
            
#         except Exception as e:
#             print(f"✗ Error with AI generation: {str(e)}")
#             # Fallback to manual generation
#             return AIQuestionGenerator._generate_fallback_questions(
#                 subject, assessment_type, num_questions, context
#             )
    
#     @staticmethod
#     def _build_prompt(goal: str, subject: str, category: str, level: str, 
#                      num_questions: int, is_skill: bool, subtopics: List[str] = None) -> str:
#         """Build optimized prompt for question generation"""
        
#         assessment_focus = "skill" if is_skill else "topic"
#         subtopics_text = ""
        
#         if subtopics:
#             subtopics_text = f"\n**Key Subtopics to Cover**:\n" + "\n".join([f"- {subtopic}" for subtopic in subtopics[:5]])
        
#         prompt = f"""You are an expert assessment designer for {goal} professionals.

# **Task**: Generate exactly {num_questions} unique, practical multiple-choice questions to assess {subject} knowledge.

# **Context**: 
# - Subject: {subject}
# - Category: {category}
# - Level: {level}
# - Goal: {goal}
# {subtopics_text}

# **Requirements**:
# 1. Each question must be UNIQUE - no repetition or similar wording
# 2. Test practical, real-world knowledge (not just definitions)
# 3. Progress from foundational to advanced concepts
# 4. Provide exactly 4 options (A, B, C, D) per question
# 5. Include diverse question types: conceptual, application-based, scenario-based
# 6. Ensure question independence - answering one should not help answer others

# **Difficulty Distribution**:
# - 40% Easy (foundational concepts)
# - 40% Medium (application and analysis)
# - 20% Hard (advanced synthesis and evaluation)

# **Output Format** (strictly follow):

# Question 1: [Clear, specific question testing practical knowledge]
# A. [First option]
# B. [Second option]
# C. [Third option]
# D. [Fourth option]
# Correct: [A/B/C/D]
# Difficulty: [easy/medium/hard]

# Question 2: [Different aspect of {subject}]
# A. [First option]
# B. [Second option]
# C. [Third option]
# D. [Fourth option]
# Correct: [A/B/C/D]
# Difficulty: [easy/medium/hard]

# [Continue for all {num_questions} questions...]

# **Example**:
# Question 1: In a data science project, what is the primary reason to perform exploratory data analysis (EDA) before model building?
# A. To increase the size of the dataset
# B. To understand patterns, detect anomalies, and form hypotheses
# C. To make the data look more presentable
# D. To reduce the need for feature engineering
# Correct: B
# Difficulty: medium

# **Important**: 
# - Each question MUST cover a different aspect of {subject}
# - Avoid repetitive phrasing or concepts
# - Make all questions practical and scenario-based when possible
# - Ensure questions are independent - no question gives away answers to others

# Generate all {num_questions} questions now:"""
        
#         return prompt
    
#     @staticmethod
#     def _parse_questions(text: str, subject: str, category: str, level: str, 
#                         is_skill: bool) -> List[Dict]:
#         """Parse AI-generated text into structured questions"""
        
#         questions = []
#         lines = text.strip().split('\n')
#         current_q = None
#         option_count = 0
        
#         for line in lines:
#             line = line.strip()
#             if not line:
#                 continue
            
#             # Detect question start
#             if re.match(r'^Question\s+\d+:', line, re.IGNORECASE):
#                 # Save previous question
#                 if current_q and AIQuestionGenerator._is_complete_question(current_q):
#                     questions.append(current_q)
                
#                 # Start new question
#                 question_text = re.sub(r'^Question\s+\d+:\s*', '', line, flags=re.IGNORECASE)
#                 current_q = {
#                     'text': question_text,
#                     'options': [],
#                     'category': category,
#                     'level': level,
#                     'difficulty': 'medium'  # Default
#                 }
#                 option_count = 0
            
#             # Parse options
#             elif re.match(r'^[A-D]\.', line, re.IGNORECASE):
#                 if current_q:
#                     option_text = re.sub(r'^[A-D]\.\s*', '', line, flags=re.IGNORECASE)
#                     current_q['options'].append(option_text)
#                     option_count += 1
            
#             # Parse correct answer
#             elif re.match(r'^Correct:', line, re.IGNORECASE):
#                 if current_q:
#                     match = re.search(r'Correct:\s*([A-D])', line, re.IGNORECASE)
#                     if match:
#                         current_q['correct_letter'] = match.group(1).upper()
            
#             # Parse difficulty
#             elif re.match(r'^Difficulty:', line, re.IGNORECASE):
#                 if current_q:
#                     match = re.search(r'Difficulty:\s*(easy|medium|hard)', line, re.IGNORECASE)
#                     if match:
#                         current_q['difficulty'] = match.group(1).lower()
        
#         # Add last question
#         if current_q and AIQuestionGenerator._is_complete_question(current_q):
#             questions.append(current_q)
        
#         return questions
    
#     @staticmethod
#     def _is_complete_question(q: Dict) -> bool:
#         """Check if question has all required fields"""
#         return (
#             'text' in q and q['text'] and
#             'options' in q and len(q['options']) == 4 and
#             'correct_letter' in q and q['correct_letter'] in ['A', 'B', 'C', 'D']
#         )
    
#     @staticmethod
#     def _validate_questions(questions: List[Dict], target_count: int) -> List[Dict]:
#         """Validate, deduplicate, and prepare questions"""
        
#         valid_questions = []
#         seen_texts = set()
        
#         for q in questions:
#             # Skip if incomplete
#             if not AIQuestionGenerator._is_complete_question(q):
#                 continue
            
#             # Deduplicate by text similarity
#             text_lower = q['text'].lower()
#             if text_lower in seen_texts:
#                 continue
#             seen_texts.add(text_lower)
            
#             # Calculate correct answer index
#             correct_text = q['options'][ord(q['correct_letter']) - ord('A')]
            
#             # Shuffle options
#             random.shuffle(q['options'])
#             q['correct_answer'] = q['options'].index(correct_text)
            
#             # Add question type
#             q['question_type'] = QuestionType.MULTIPLE_CHOICE.value
            
#             valid_questions.append(q)
        
#         # Ensure we have enough questions
#         if len(valid_questions) < target_count:
#             print(f"⚠ Only {len(valid_questions)}/{target_count} valid questions, generating fallbacks...")
        
#         return valid_questions
    
#     @staticmethod
#     def _generate_fallback_questions(subject: str, assessment_type: AssessmentType, 
#                                     num_questions: int, context: Dict) -> List[Dict]:
#         """Generate fallback questions when AI fails"""
        
#         questions = []
#         is_skill = assessment_type == AssessmentType.SKILLS
        
#         templates = [
#             {
#                 "text": f"What is a key principle when working with {subject}?",
#                 "options": [
#                     "Understanding core fundamentals",
#                     "Practical hands-on experience",
#                     "Advanced theoretical knowledge",
#                     "Industry best practices"
#                 ]
#             },
#             {
#                 "text": f"Which approach is most effective for mastering {subject}?",
#                 "options": [
#                     "Reading documentation thoroughly",
#                     "Building real-world projects",
#                     "Watching tutorial videos",
#                     "Taking structured courses"
#                 ]
#             },
#             {
#                 "text": f"In a professional setting, how is {subject} typically applied?",
#                 "options": [
#                     "Following standard procedures",
#                     "Adapting to specific requirements",
#                     "Using predefined templates",
#                     "Consulting with experts"
#                 ]
#             },
#             {
#                 "text": f"What distinguishes proficiency in {subject} from basic knowledge?",
#                 "options": [
#                     "Ability to solve complex problems",
#                     "Memorization of syntax",
#                     "Speed of execution",
#                     "Tool familiarity"
#                 ]
#             },
#             {
#                 "text": f"When evaluating competence in {subject}, what matters most?",
#                 "options": [
#                     "Years of experience",
#                     "Quality of work output",
#                     "Number of certifications",
#                     "Speed of learning"
#                 ]
#             }
#         ]
        
#         for i in range(num_questions):
#             template = templates[i % len(templates)]
#             options = template["options"].copy()
#             random.shuffle(options)
            
#             q = {
#                 'id': f"fallback_{i}",
#                 'text': template["text"],
#                 'options': options,
#                 'correct_answer': random.randint(0, 3),
#                 'difficulty': random.choice(['easy', 'medium', 'hard']),
#                 'question_type': QuestionType.MULTIPLE_CHOICE.value,
#                 'category': context.get('category', 'General'),
#                 'level': context.get('level', 'beginner')
#             }
            
#             if is_skill:
#                 q['skill_name'] = subject
#                 q['skill_id'] = context.get('skill_id')
#             else:
#                 q['topic_name'] = subject
#                 q['topic_id'] = context.get('topic_id')
            
#             questions.append(q)
        
#         print(f"✓ Generated {len(questions)} fallback questions")
#         return questions

# class QuestionBuilder:
#     """Orchestrates question generation with configuration management"""
    
#     @staticmethod
#     async def build_question_set(config: QuestionGenerationConfig, context: Dict) -> List[Dict]:
#         """Build balanced question set using AI generator"""
        
#         total_questions = context.get('total_questions', 10)
#         goal = context.get('goal', 'Data Scientist')
        
#         try:
#             # Generate questions using AI
#             questions = await AIQuestionGenerator.generate_questions(
#                 goal=goal,
#                 context=context,
#                 num_questions=total_questions
#             )
            
#             # If we don't have enough, generate more
#             if len(questions) < total_questions:
#                 additional_needed = total_questions - len(questions)
#                 fallback_questions = AIQuestionGenerator._generate_fallback_questions(
#                     subject=context.get('skill_name', context.get('topic_name', 'General')),
#                     assessment_type=context.get('assessment_type', AssessmentType.SKILLS),
#                     num_questions=additional_needed,
#                     context=context
#                 )
#                 questions.extend(fallback_questions)
            
#             # Apply difficulty distribution if needed
#             questions = QuestionBuilder._balance_difficulty(questions, config.difficulty_distribution)
            
#             # Ensure exact count
#             return questions[:total_questions]
            
#         except Exception as e:
#             print(f"✗ Error in question generation: {str(e)}")
#             return AIQuestionGenerator._generate_fallback_questions(
#                 subject=context.get('skill_name', context.get('topic_name', 'General')),
#                 assessment_type=context.get('assessment_type', AssessmentType.SKILLS),
#                 num_questions=total_questions,
#                 context=context
#             )
    
#     @staticmethod
#     def _balance_difficulty(questions: List[Dict], distribution: Dict[DifficultyLevel, float]) -> List[Dict]:
#         """Balance questions according to difficulty distribution"""
        
#         if len(questions) < 3:  # Too few to balance
#             return questions
        
#         # Categorize by difficulty
#         by_difficulty = {
#             'easy': [q for q in questions if q.get('difficulty') == 'easy'],
#             'medium': [q for q in questions if q.get('difficulty') == 'medium'],
#             'hard': [q for q in questions if q.get('difficulty') == 'hard']
#         }
        
#         # Calculate target counts
#         total = len(questions)
#         target_easy = int(total * distribution[DifficultyLevel.EASY])
#         target_medium = int(total * distribution[DifficultyLevel.MEDIUM])
#         target_hard = total - target_easy - target_medium
        
#         # Select according to distribution
#         balanced = []
#         balanced.extend(by_difficulty['easy'][:target_easy])
#         balanced.extend(by_difficulty['medium'][:target_medium])
#         balanced.extend(by_difficulty['hard'][:target_hard])
        
#         # Fill remaining slots with any available questions
#         while len(balanced) < total:
#             remaining = [q for q in questions if q not in balanced]
#             if remaining:
#                 balanced.append(remaining[0])
#             else:
#                 break
        
#         random.shuffle(balanced)
#         return balanced

# def normalize_goal(goal: str) -> str:
#     """Normalize goal to match predefined roadmap"""
#     goal_lower = goal.lower().strip()
    
#     data_science_keywords = ["data scien", "data-scien", "ds", "datascien"]
#     if any(keyword in goal_lower for keyword in data_science_keywords):
#         return "Data Scientist"
    
#     return goal.title()

# def get_roadmap_for_goal(goal: str) -> Optional[Dict]:
#     """Get predefined roadmap for a goal"""
#     normalized_goal = normalize_goal(goal)
    
#     if normalized_goal == "Data Scientist":
#         return DATA_SCIENCE_ROADMAP
    
#     return None

# def determine_current_level(score: int, total_questions: int) -> str:
#     """Determine user's current level based on assessment score"""
#     percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
#     if percentage >= 85:
#         return "advanced_level"
#     elif percentage >= 70:
#         return "moderate_level" 
#     elif percentage >= 50:
#         return "beginner_level"
#     else:
#         return "beginner_level"

# def get_all_levels_for_goal(goal: str) -> List[Dict]:
#     """Get all levels for a given goal"""
#     roadmap = get_roadmap_for_goal(goal)
#     if not roadmap:
#         return []
    
#     return [
#         {
#             "id": level_key,
#             "name": level_data["name"],
#             "description": level_data["description"],
#             "experience_range": level_data["experience_range"],
#             "rank": level_data["rank"],
#             "required_skills": level_data.get("required_skills", [])
#         }
#         for level_key, level_data in roadmap["levels"].items()
#     ]

# def get_topics_for_level(level_name: str) -> List[Dict]:
#     """Get topics for a specific level"""
#     roadmap = DATA_SCIENCE_ROADMAP
#     level_key = next(
#         (key for key, level in roadmap["levels"].items() 
#          if level["name"] == level_name),
#         None
#     )
    
#     if not level_key:
#         return []
    
#     topics_data = roadmap["topics"].get(level_key, {})
    
#     return [
#         {
#             "id": f"topic_{level_key}_{topic_name}",
#             "name": topic_name,
#             "description": topic_info["description"],
#             "subtopics": topic_info["subtopics"],
#             "priority": topic_info["priority"],
#             "required_skills": topic_info.get("required_skills", [])
#         }
#         for topic_name, topic_info in topics_data.items()
#     ]

# # API Endpoints

# @app.post("/submit_goal")
# async def submit_goal(goal_input: GoalInput):
#     """Step 1: User enters goal and system creates assessment draft"""
#     try:
#         roadmap = get_roadmap_for_goal(goal_input.goal)
        
#         if not roadmap:
#             raise HTTPException(status_code=400, detail="Goal not supported")
        
#         # Create session data
#         session_data = {
#             "goal": goal_input.goal,
#             "roadmap": roadmap,
#             "created_at": datetime.now().isoformat(),
#             "current_level": "beginner_level",
#             "skills": roadmap["skills"],
#             "topics": roadmap["topics"],
#             "custom_levels": [level["name"] for level in roadmap["levels"].values()]
#         }
        
#         SESSION_STORE[goal_input.session_id] = session_data
        
#         # Generate initial assessment questions
#         config = QuestionGenerationConfig()
#         context = {
#             "goal": goal_input.goal,
#             "total_questions": 10,
#             "assessment_type": AssessmentType.SKILLS,
#             "skill_name": "Data Science Fundamentals",
#             "category": "core",
#             "level": "beginner"
#         }
        
#         questions = await QuestionBuilder.build_question_set(config, context)
#         QUESTION_STORE[goal_input.session_id] = questions
        
#         return {
#             "goal": goal_input.goal,
#             "custom_levels": session_data["custom_levels"],
#             "questions": questions,
#             "total_questions": len(questions),
#             "points_per_question": 100 / len(questions) if questions else 0,
#             "available_skills": session_data["skills"]
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing goal: {str(e)}")

# @app.post("/submit_answers")  
# async def submit_answers(answers_input: AnswersInput):
#     """Step 2: Evaluate answers and determine current level"""
#     try:
#         session_id = answers_input.session_id
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         # Calculate score
#         correct_answers = sum(
#             1 for i, answer in enumerate(answers_input.answers)
#             if answer == answers_input.questions[i].get('correct_answer', -1)
#         )
        
#         total_questions = len(answers_input.questions)
#         score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
#         # Determine current level
#         current_level_key = determine_current_level(correct_answers, total_questions)
#         current_level_name = DATA_SCIENCE_ROADMAP["levels"][current_level_key]["name"]
        
#         # Update session
#         SESSION_STORE[session_id]["current_level"] = current_level_key
#         SESSION_STORE[session_id]["assessment_score"] = score
        
#         # Get all levels for display
#         all_levels = get_all_levels_for_goal(answers_input.goal)
        
#         # Generate feedback
#         if score >= 85:
#             feedback = "Excellent! You have strong foundational knowledge."
#             assigned_level = "Advanced Level"
#         elif score >= 70:
#             feedback = "Good! You have solid understanding with room for growth."
#             assigned_level = "Moderate Level"
#         elif score >= 50:
#             feedback = "Developing! Focus on strengthening core concepts."
#             assigned_level = "Beginner Level"
#         else:
#             feedback = "Beginning! Start with foundational learning."
#             assigned_level = "Beginner Level"
        
#         return {
#             "score": round(score, 2),
#             "correct_answers": correct_answers,
#             "total_questions": total_questions,
#             "assigned_level": assigned_level,
#             "feedback": feedback,
#             "current_level_key": current_level_key,
#             "all_levels": all_levels  # Return all levels for frontend display
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error evaluating answers: {str(e)}")

# @app.get("/api/get-skills/{session_id}")
# async def get_skills(session_id: str):
#     """Step 3: Get available skills for user selection"""
#     try:
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         session_data = SESSION_STORE[session_id]
#         skills_data = session_data.get("skills", {})
        
#         # Convert to frontend format
#         skills_list = []
#         for category, skills in skills_data.items():
#             for skill_name, skill_info in skills.items():
#                 skills_list.append({
#                     "id": f"{category}_{skill_name}",
#                     "name": skill_name,
#                     "category": category.replace('_', ' ').title(),
#                     "description": skill_info.get("description", f"{skill_name} skill"),
#                     "difficulty": skill_info.get("difficulty", "beginner"),
#                     "subtopics": skill_info.get("subtopics", [])
#                 })
        
#         return {"skills": skills_list}
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/store-user-skills")
# async def store_user_skills(input: UserSkillsInput):
#     """Step 4: Store user's selected skills and create skill stack"""
#     try:
#         session_id = input.session_id
        
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         # Get all available skills
#         all_skills_response = await get_skills(session_id)
#         all_skill_ids = [skill["id"] for skill in all_skills_response["skills"]]
        
#         # Calculate remaining skills for stack
#         remaining_skills = [skill for skill in all_skill_ids if skill not in input.selected_skills]
        
#         # Store user skills
#         USER_SKILLS_STORE[session_id] = {
#             "selected_skills": input.selected_skills,
#             "remaining_skills": remaining_skills,
#             "proficiency_level": input.proficiency_level,
#             "timestamp": datetime.now().isoformat()
#         }
        
#         # Store skill stack for future tests
#         SKILL_STACK_STORE[session_id] = remaining_skills
        
#         # Update session
#         SESSION_STORE[session_id]["user_skills"] = USER_SKILLS_STORE[session_id]
#         SESSION_STORE[session_id]["skill_stack"] = remaining_skills
        
#         return {
#             "status": "success",
#             "selected_count": len(input.selected_skills),
#             "remaining_skills": remaining_skills,
#             "skill_stack_count": len(remaining_skills)
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/generate-skills-mock-test")
# async def generate_skills_mock_test(request: SkillsMockTestRequest):
#     """Step 5: Generate comprehensive skills mock test using AI question generator"""
#     try:
#         session_id = request.session_id
        
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         if not request.selected_skills:
#             raise HTTPException(status_code=400, detail="No skills selected")
        
#         session_data = SESSION_STORE[session_id]
#         goal = session_data.get("goal", "Data Scientist")
        
#         # Calculate questions per skill (distribute total questions among selected skills)
#         total_questions = min(request.total_questions, 50)  # Cap at 50
#         questions_per_skill = max(3, total_questions // len(request.selected_skills))
        
#         print(f"\n🚀 Generating skills mock test for {len(request.selected_skills)} skills...")
#         print(f"   Total questions: {total_questions}, Questions per skill: ~{questions_per_skill}")
        
#         all_questions = []
#         skill_question_counts = {}
        
#         # Generate questions for each selected skill
#         for skill_id in request.selected_skills:
#             # Extract skill info
#             category, skill_name = skill_id.split('_', 1)
            
#             # Get skill details from roadmap
#             skill_info = DATA_SCIENCE_ROADMAP["skills"].get(category, {}).get(skill_name, {})
            
#             print(f"  📝 Generating {questions_per_skill} questions for: {skill_name}")
            
#             # Build context for question generation
#             config = QuestionGenerationConfig()
#             context = {
#                 "skill_name": skill_name,
#                 "skill_id": skill_id,
#                 "category": category,
#                 "total_questions": questions_per_skill,
#                 "assessment_type": AssessmentType.SKILLS,
#                 "goal": goal,
#                 "level": skill_info.get("difficulty", "beginner"),
#                 "subtopics": skill_info.get("subtopics", [])
#             }
            
#             # Generate questions using AI
#             skill_questions = await QuestionBuilder.build_question_set(config, context)
#             skill_question_counts[skill_id] = len(skill_questions)
            
#             # Add skill metadata to each question
#             for q in skill_questions:
#                 q['skill_id'] = skill_id
#                 q['skill_name'] = skill_name
#                 q['category'] = category
            
#             all_questions.extend(skill_questions)
        
#         # If we have fewer questions than requested, generate more for larger skills
#         if len(all_questions) < total_questions:
#             additional_needed = total_questions - len(all_questions)
#             # Distribute additional questions to skills that can handle more
#             for skill_id in request.selected_skills:
#                 if additional_needed <= 0:
#                     break
#                 # Generate 1-2 additional questions per skill
#                 extra_questions = min(2, additional_needed)
                
#                 category, skill_name = skill_id.split('_', 1)
#                 skill_info = DATA_SCIENCE_ROADMAP["skills"].get(category, {}).get(skill_name, {})
                
#                 context = {
#                     "skill_name": skill_name,
#                     "skill_id": skill_id,
#                     "category": category,
#                     "total_questions": extra_questions,
#                     "assessment_type": AssessmentType.SKILLS,
#                     "goal": goal,
#                     "level": skill_info.get("difficulty", "beginner")
#                 }
                
#                 extra_skill_questions = await QuestionBuilder.build_question_set(config, context)
                
#                 for q in extra_skill_questions:
#                     q['skill_id'] = skill_id
#                     q['skill_name'] = skill_name
#                     q['category'] = category
                
#                 all_questions.extend(extra_skill_questions)
#                 additional_needed -= len(extra_skill_questions)
        
#         # Ensure we don't exceed total_questions
#         all_questions = all_questions[:total_questions]
        
#         # Shuffle questions to ensure independence
#         random.shuffle(all_questions)
        
#         # Create test record
#         test_id = str(uuid4())
#         test_data = {
#             "test_id": test_id,
#             "session_id": session_id,
#             "questions": all_questions,
#             "total_questions": len(all_questions),
#             "test_type": AssessmentType.SKILLS.value,
#             "created_at": datetime.now().isoformat(),
#             "skills_covered": request.selected_skills,
#             "skill_question_counts": skill_question_counts
#         }
        
#         MOCK_TEST_STORE[test_id] = test_data
        
#         print(f"✅ Skills mock test created: {len(all_questions)} total questions")
#         print(f"   Skills covered: {[skill.split('_')[1] for skill in request.selected_skills]}\n")
        
#         return {
#             "test_id": test_id,
#             "questions": all_questions,
#             "total_questions": len(all_questions),
#             "skills_covered": request.selected_skills,
#             "skill_question_counts": skill_question_counts
#         }
        
#     except Exception as e:
#         print(f"✗ Error creating skills mock test: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/store-session-data")
# async def store_session_data(data: SessionData):
#     """Store session data including target level"""
#     try:
#         session_id = data.session_id
        
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         # Validate target level is higher than current
#         current_level = SESSION_STORE[session_id]["current_level"]
#         target_level_key = next(
#             key for key, level in DATA_SCIENCE_ROADMAP["levels"].items() 
#             if level["name"] == data.target_level
#         )
        
#         current_rank = DATA_SCIENCE_ROADMAP["levels"][current_level]["rank"]
#         target_rank = DATA_SCIENCE_ROADMAP["levels"][target_level_key]["rank"]
        
#         if target_rank <= current_rank:
#             raise HTTPException(
#                 status_code=400, 
#                 detail="Target level must be higher than current level"
#             )
        
#         # Update session
#         SESSION_STORE[session_id].update({
#             "current_level": current_level,
#             "target_level": target_level_key,
#             "target_level_name": data.target_level,
#             "assessment_score": data.assessment_score
#         })
        
#         return {"status": "success", "message": "Session data updated"}
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/get-level-topics/{session_id}")
# async def get_level_topics(session_id: str, target_level: str):
#     """Step 6: Get topics for selected target level"""
#     try:
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         # Get topics for the target level
#         topics_data = get_topics_for_level(target_level)
        
#         return {"topics": topics_data, "target_level": target_level}
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/store-target-topics")
# async def store_target_topics(input: TargetTopicsInput):
#     """Step 7: Store selected topics and create topic stack"""
#     try:
#         session_id = input.session_id
        
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         # Get all topics for target level
#         topics_response = await get_level_topics(session_id, input.target_level)
#         all_topic_ids = [topic["id"] for topic in topics_response["topics"]]
        
#         # Calculate remaining topics for stack
#         remaining_topics = [topic for topic in all_topic_ids if topic not in input.selected_topics]
        
#         # Store target topics
#         SESSION_STORE[session_id]["target_topics"] = {
#             "target_level": input.target_level,
#             "selected_topics": input.selected_topics,
#             "remaining_topics": remaining_topics
#         }
        
#         # Store topic stack for future learning
#         TOPIC_STACK_STORE[session_id] = remaining_topics
        
#         SESSION_STORE[session_id]["topic_stack"] = remaining_topics
        
#         return {
#             "status": "success",
#             "selected_count": len(input.selected_topics),
#             "remaining_topics": remaining_topics
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/generate-topics-mock-test")
# async def generate_topics_mock_test(request: TopicsMockTestRequest):
#     """Step 8: Generate topics mock test using AI question generator"""
#     try:
#         session_id = request.session_id
        
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         if not request.selected_topics:
#             raise HTTPException(status_code=400, detail="No topics selected")
        
#         session_data = SESSION_STORE[session_id]
#         goal = session_data.get("goal", "Data Scientist")
#         target_level = session_data.get("target_level_name", "Moderate Level")
        
#         # Calculate questions per topic
#         total_questions = min(request.total_questions, 50)
#         questions_per_topic = max(3, total_questions // len(request.selected_topics))
        
#         # Get topic details
#         topics_response = await get_level_topics(session_id, target_level)
#         all_topics = {topic["id"]: topic for topic in topics_response["topics"]}
        
#         # Generate questions for selected topics
#         all_questions = []
#         topic_question_counts = {}
        
#         print(f"\n🚀 Generating topics mock test for {len(request.selected_topics)} topics...")
#         print(f"   Target level: {target_level}, Total questions: {total_questions}")
        
#         for topic_id in request.selected_topics:
#             topic = all_topics.get(topic_id)
#             if not topic:
#                 print(f"  ⚠ Topic not found: {topic_id}")
#                 continue
            
#             print(f"  📝 Generating {questions_per_topic} questions for: {topic['name']}")
            
#             # Build context for question generation
#             config = QuestionGenerationConfig()
#             context = {
#                 "topic_name": topic["name"],
#                 "topic_id": topic_id,
#                 "level": target_level,
#                 "total_questions": questions_per_topic,
#                 "assessment_type": AssessmentType.TOPICS,
#                 "goal": goal,
#                 "category": "topic",
#                 "subtopics": topic.get("subtopics", [])
#             }
            
#             # Generate questions using AI
#             topic_questions = await QuestionBuilder.build_question_set(config, context)
#             topic_question_counts[topic_id] = len(topic_questions)
            
#             # Add topic metadata to each question
#             for q in topic_questions:
#                 q['topic_id'] = topic_id
#                 q['topic_name'] = topic["name"]
#                 q['level'] = target_level
            
#             all_questions.extend(topic_questions)
        
#         # Ensure we have enough questions
#         if len(all_questions) < total_questions:
#             additional_needed = total_questions - len(all_questions)
#             for topic_id in request.selected_topics:
#                 if additional_needed <= 0:
#                     break
                    
#                 topic = all_topics.get(topic_id)
#                 if not topic:
#                     continue
                
#                 extra_questions = min(2, additional_needed)
                
#                 context = {
#                     "topic_name": topic["name"],
#                     "topic_id": topic_id,
#                     "level": target_level,
#                     "total_questions": extra_questions,
#                     "assessment_type": AssessmentType.TOPICS,
#                     "goal": goal
#                 }
                
#                 extra_topic_questions = await QuestionBuilder.build_question_set(config, context)
                
#                 for q in extra_topic_questions:
#                     q['topic_id'] = topic_id
#                     q['topic_name'] = topic["name"]
#                     q['level'] = target_level
                
#                 all_questions.extend(extra_topic_questions)
#                 additional_needed -= len(extra_topic_questions)
        
#         all_questions = all_questions[:total_questions]
#         random.shuffle(all_questions)
        
#         # Create test record
#         test_id = str(uuid4())
#         test_data = {
#             "test_id": test_id,
#             "session_id": session_id,
#             "questions": all_questions,
#             "total_questions": len(all_questions),
#             "test_type": AssessmentType.TOPICS.value,
#             "created_at": datetime.now().isoformat(),
#             "topics_covered": [all_topics[tid]["name"] for tid in request.selected_topics if tid in all_topics],
#             "topic_question_counts": topic_question_counts
#         }
        
#         MOCK_TEST_STORE[test_id] = test_data
        
#         print(f"✅ Topics mock test created: {len(all_questions)} total questions")
#         print(f"   Topics covered: {test_data['topics_covered']}\n")
        
#         return {
#             "test_id": test_id,
#             "questions": all_questions,
#             "total_questions": len(all_questions),
#             "topics_covered": test_data["topics_covered"],
#             "topic_question_counts": topic_question_counts
#         }
        
#     except Exception as e:
#         print(f"✗ Error creating topics mock test: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/api/submit-mock-test")
# async def submit_mock_test(submission: MockTestSubmission):
#     """Step 9: Evaluate mock test and generate comprehensive results"""
#     try:
#         test_id = submission.test_id
        
#         if test_id not in MOCK_TEST_STORE:
#             raise HTTPException(status_code=400, detail="Test not found")
        
#         test_data = MOCK_TEST_STORE[test_id]
#         questions = test_data["questions"]
#         test_type = test_data["test_type"]
        
#         # Evaluate answers
#         total_questions = len(questions)
#         correct_count = 0
#         detailed_results = {}
#         skill_results = {}
#         topic_results = {}
        
#         for question in questions:
#             q_id = question["id"]
#             user_answer = submission.answers.get(q_id)
#             correct_answer = question.get("correct_answer")
            
#             is_correct = user_answer == correct_answer
#             if is_correct:
#                 correct_count += 1
            
#             # Track results by skill/topic
#             if test_type == AssessmentType.SKILLS.value:
#                 skill_id = question.get("skill_id")
#                 skill_name = question.get("skill_name")
                
#                 if skill_id not in detailed_results:
#                     detailed_results[skill_id] = {
#                         "skill_name": skill_name,
#                         "total": 0,
#                         "correct": 0,
#                         "score": 0
#                     }
#                 detailed_results[skill_id]["total"] += 1
#                 if is_correct:
#                     detailed_results[skill_id]["correct"] += 1
                
#                 # Calculate skill score
#                 skill_score = (detailed_results[skill_id]["correct"] / detailed_results[skill_id]["total"] * 100) if detailed_results[skill_id]["total"] > 0 else 0
#                 detailed_results[skill_id]["score"] = round(skill_score, 2)
                
#                 # Add to skill results with level assessment
#                 skill_results[skill_id] = {
#                     "skill_name": skill_name,
#                     "score": skill_score,
#                     "correct_answers": detailed_results[skill_id]["correct"],
#                     "total_questions": detailed_results[skill_id]["total"],
#                     "level": "advanced" if skill_score >= 80 else "intermediate" if skill_score >= 60 else "beginner"
#                 }
#             else:
#                 topic_id = question.get("topic_id")
#                 topic_name = question.get("topic_name")
                
#                 if topic_id not in detailed_results:
#                     detailed_results[topic_id] = {
#                         "topic_name": topic_name,
#                         "total": 0,
#                         "correct": 0,
#                         "score": 0
#                     }
#                 detailed_results[topic_id]["total"] += 1
#                 if is_correct:
#                     detailed_results[topic_id]["correct"] += 1
                
#                 # Calculate topic score
#                 topic_score = (detailed_results[topic_id]["correct"] / detailed_results[topic_id]["total"] * 100) if detailed_results[topic_id]["total"] > 0 else 0
#                 detailed_results[topic_id]["score"] = round(topic_score, 2)
                
#                 # Add to topic results
#                 topic_results[topic_id] = {
#                     "topic_name": topic_name,
#                     "score": topic_score,
#                     "correct_answers": detailed_results[topic_id]["correct"],
#                     "total_questions": detailed_results[topic_id]["total"],
#                     "level": "excellent" if topic_score >= 85 else "good" if topic_score >= 70 else "moderate" if topic_score >= 50 else "needs_work"
#                 }
        
#         # Calculate overall score
#         overall_score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
#         # Generate recommendations based on test type
#         good_items = []
#         needs_improvement = []
        
#         for item_id, result in detailed_results.items():
#             item_score = result["score"]
#             item_name = result.get("skill_name") or result.get("topic_name")
            
#             if item_score >= 70:
#                 good_items.append(item_name)
#             else:
#                 needs_improvement.append(item_name)
        
#         # Determine readiness level and next steps
#         if overall_score >= 85:
#             readiness = "excellent"
#             next_steps = [
#                 "You're ready to advance to the target level",
#                 "Consider tackling more advanced challenges",
#                 "Focus on real-world project implementation"
#             ]
#         elif overall_score >= 70:
#             readiness = "good"
#             next_steps = [
#                 "Solid foundation established",
#                 "Focus on areas needing improvement", 
#                 "Practice with real-world projects",
#                 "Consider advanced learning resources"
#             ]
#         elif overall_score >= 50:
#             readiness = "moderate"
#             next_steps = [
#                 "More preparation needed",
#                 "Review weak areas thoroughly",
#                 "Take additional practice tests",
#                 "Focus on foundational concepts"
#             ]
#         else:
#             readiness = "needs_work"
#             next_steps = [
#                 "Focus on foundational learning first",
#                 "Review core concepts systematically", 
#                 "Seek additional resources or mentorship",
#                 "Build practical projects to reinforce learning"
#             ]
        
#         # Store results in session
#         session_id = test_data["session_id"]
#         if session_id in SESSION_STORE:
#             if test_type == AssessmentType.SKILLS.value:
#                 SESSION_STORE[session_id]["skills_assessment_results"] = {
#                     "score": overall_score,
#                     "good_skills": good_items,
#                     "needs_improvement_skills": needs_improvement,
#                     "skill_results": skill_results,
#                     "test_id": test_id,
#                     "timestamp": datetime.now().isoformat()
#                 }
#             else:
#                 SESSION_STORE[session_id]["topics_assessment_results"] = {
#                     "score": overall_score,
#                     "good_topics": good_items,
#                     "needs_improvement_topics": needs_improvement,
#                     "topic_results": topic_results,
#                     "test_id": test_id,
#                     "timestamp": datetime.now().isoformat()
#                 }
        
#         return {
#             "overall_score": round(overall_score, 2),
#             "overall_level": readiness,
#             "total_questions": total_questions,
#             "total_correct": correct_count,
#             "time_taken_seconds": submission.time_taken_seconds,
#             "time_taken_display": f"{submission.time_taken_seconds // 60}m {submission.time_taken_seconds % 60}s",
#             "good_skills" if test_type == AssessmentType.SKILLS.value else "good_topics": good_items,
#             "needs_improvement_skills" if test_type == AssessmentType.SKILLS.value else "needs_improvement_topics": needs_improvement,
#             "next_steps": next_steps,
#             "detailed_results": detailed_results,
#             "skill_results" if test_type == AssessmentType.SKILLS.value else "topic_results": skill_results if test_type == AssessmentType.SKILLS.value else topic_results
#         }
        
#     except Exception as e:
#         print(f"✗ Error submitting mock test: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/get-user-progress/{session_id}")
# async def get_user_progress(session_id: str):
#     """Step 10: Get comprehensive user progress and schedule future tests"""
#     try:
#         if session_id not in SESSION_STORE:
#             raise HTTPException(status_code=400, detail="Session not found")
        
#         session_data = SESSION_STORE[session_id]
        
#         # Get skill and topic stacks
#         skill_stack = SKILL_STACK_STORE.get(session_id, [])
#         topic_stack = TOPIC_STACK_STORE.get(session_id, [])
        
#         # Calculate next test schedule based on skill/topic stacks
#         next_tests = []
#         if skill_stack:
#             next_tests.append({
#                 "type": "skill_microtest",
#                 "items": skill_stack[:3],  # Next 3 skills to test
#                 "scheduled_date": (datetime.now() + timedelta(days=7)).isoformat(),
#                 "description": "Next skill assessment for learning stack"
#             })
        
#         if topic_stack:
#             next_tests.append({
#                 "type": "topic_microtest", 
#                 "items": topic_stack[:2],  # Next 2 topics to test
#                 "scheduled_date": (datetime.now() + timedelta(days=14)).isoformat(),
#                 "description": "Next topic assessment for learning stack"
#             })
        
#         progress_data = {
#             "goal": session_data.get("goal"),
#             "current_level": DATA_SCIENCE_ROADMAP["levels"][session_data["current_level"]]["name"],
#             "target_level": session_data.get("target_level_name"),
#             "assessment_score": session_data.get("assessment_score"),
#             "skill_stack": skill_stack,
#             "topic_stack": topic_stack,
#             "skill_stack_count": len(skill_stack),
#             "topic_stack_count": len(topic_stack),
#             "next_tests": next_tests,
#             "skills_assessment": session_data.get("skills_assessment_results"),
#             "topics_assessment": session_data.get("topics_assessment_results")
#         }
        
#         return progress_data
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Utility endpoints

# @app.get("/")
# async def root():
#     return {
#         "message": "Enhanced Skills Mock Test API with AI Question Generation",
#         "version": "4.0",
#         "features": [
#             "Dynamic AI-powered question generation using Llama 3.2 1B",
#             "Comprehensive skills and topics assessment workflow",
#             "Question independence and integrity",
#             "Skill stack management for future learning",
#             "Detailed progress tracking and recommendations"
#         ],
#         "workflow_steps": [
#             "1. Goal submission and initial assessment",
#             "2. Skills selection and comprehensive mock test generation", 
#             "3. AI-powered evaluation and current level determination",
#             "4. Target level selection (must be higher than current)",
#             "5. Topics selection for target level",
#             "6. Topic-focused mock test generation", 
#             "7. Comprehensive results with skill/topic breakdown",
#             "8. Learning stack management for remaining skills/topics",
#             "9. Progress tracking and future test scheduling"
#         ]
#     }

# @app.get("/supported-careers")
# async def get_supported_careers():
#     return {
#         "predefined_frameworks": ["Data Scientist"],
#         "custom_goals_supported": False,
#         "ai_question_generation": True,
#         "model": "llama3.2:1b",
#         "features": [
#             "Skills-based mock tests",
#             "Topic-based assessments", 
#             "Learning stack management",
#             "Progress tracking"
#         ]
#     }

# @app.get("/api/test-ollama")
# async def test_ollama():
#     """Test Ollama connection and model availability"""
#     try:
#         response = ollama.chat(
#             model='llama3.2:1b',
#             messages=[{'role': 'user', 'content': 'Say "Hello, I am working!"'}]
#         )
#         return {
#             "status": "success",
#             "model": "llama3.2:1b",
#             "response": response['message']['content']
#         }
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }

# @app.delete("/api/clear-session/{session_id}")
# async def clear_session(session_id: str):
#     """Clear session data"""
#     try:
#         QUESTION_STORE.pop(session_id, None)
#         SESSION_STORE.pop(session_id, None)
#         USER_SKILLS_STORE.pop(session_id, None)
#         SKILL_STACK_STORE.pop(session_id, None)
#         TOPIC_STACK_STORE.pop(session_id, None)
        
#         # Clear related tests
#         tests_to_remove = [
#             test_id for test_id, data in MOCK_TEST_STORE.items()
#             if data.get("session_id") == session_id
#         ]
#         for test_id in tests_to_remove:
#             MOCK_TEST_STORE.pop(test_id, None)
        
#         return {"status": "success", "message": f"Session {session_id} cleared"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/debug-session/{session_id}")
# async def debug_session(session_id: str):
#     """Debug endpoint to inspect session data"""
#     return {
#         "session_exists": session_id in SESSION_STORE,
#         "session_data": SESSION_STORE.get(session_id, {}),
#         "questions_count": len(QUESTION_STORE.get(session_id, [])),
#         "user_skills_exists": session_id in USER_SKILLS_STORE,
#         "skill_stack": SKILL_STACK_STORE.get(session_id, []),
#         "topic_stack": TOPIC_STACK_STORE.get(session_id, []),
#         "tests": [
#             {"test_id": tid, "type": data.get("test_type"), "questions": len(data.get("questions", []))}
#             for tid, data in MOCK_TEST_STORE.items()
#             if data.get("session_id") == session_id
#         ]
#     }

# if __name__ == "__main__":
#     import uvicorn
#     print("\n" + "="*60)
#     print("🚀 Enhanced Skills Mock Test API")
#     print("="*60)
#     print("✓ AI Question Generation: Enabled (Llama 3.2 1B)")
#     print("✓ Skills Assessment Workflow: Enabled")
#     print("✓ Topics Assessment Workflow: Enabled") 
#     print("✓ Learning Stack Management: Enabled")
#     print("✓ Progress Tracking: Enabled")
#     print("="*60 + "\n")
#     uvicorn.run(app, host="0.0.0.0", port=8000)





from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import random
import ollama
from uuid import uuid4
from datetime import datetime, timedelta
import re

app = FastAPI(title="Skills Assessment API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class SkillsMockTestRequest(BaseModel):
    session_id: str
    selected_skills: List[str]
    total_questions: int

class TopicsMockTestRequest(BaseModel):
    session_id: str
    selected_topics: List[str]
    total_questions: int

class MockTestSubmission(BaseModel):
    test_id: str
    answers: Dict[str, int]
    time_taken_seconds: int

# Enhanced Data Science Roadmap
DATA_SCIENCE_ROADMAP = {
    "skills": {
        "programming": {
            "Python": {
                "description": "Python programming for data analysis",
                "difficulty": "beginner",
                "category": "core"
            },
            "R": {
                "description": "Statistical programming with R", 
                "difficulty": "beginner",
                "category": "core"
            },
            "SQL": {
                "description": "Database querying and management",
                "difficulty": "beginner", 
                "category": "core"
            },
            "Git": {
                "description": "Version control and collaboration",
                "difficulty": "beginner",
                "category": "tools"
            }
        },
        "mathematics": {
            "Statistics": {
                "description": "Statistical analysis and inference",
                "difficulty": "beginner", 
                "category": "foundation"
            },
            "Linear Algebra": {
                "description": "Vectors, matrices and linear transformations",
                "difficulty": "intermediate",
                "category": "foundation"
            },
            "Calculus": {
                "description": "Differential and integral calculus", 
                "difficulty": "intermediate",
                "category": "foundation"
            },
            "Probability": {
                "description": "Probability theory and distributions",
                "difficulty": "intermediate",
                "category": "foundation"
            }
        },
        "machine_learning": {
            "Supervised Learning": {
                "description": "Classification and regression algorithms",
                "difficulty": "intermediate",
                "category": "ml"
            },
            "Unsupervised Learning": {
                "description": "Clustering and dimensionality reduction",
                "difficulty": "intermediate", 
                "category": "ml"
            },
            "Deep Learning": {
                "description": "Neural networks and deep architectures",
                "difficulty": "advanced",
                "category": "ml"
            },
            "Model Evaluation": {
                "description": "Performance metrics and validation",
                "difficulty": "intermediate",
                "category": "ml" 
            }
        },
        "data_processing": {
            "Data Cleaning": {
                "description": "Handling missing values and outliers",
                "difficulty": "beginner",
                "category": "processing"
            },
            "Feature Engineering": {
                "description": "Creating and selecting features", 
                "difficulty": "intermediate",
                "category": "processing"
            },
            "Data Visualization": {
                "description": "Creating insightful visualizations",
                "difficulty": "beginner",
                "category": "processing"
            },
            "ETL": {
                "description": "Extract, transform, load processes",
                "difficulty": "intermediate",
                "category": "processing"
            }
        }
    },
    "topics": {
        "Beginner Level": [
            {
                "id": "math_foundations",
                "name": "Mathematics for Data Science",
                "description": "Fundamental mathematical concepts for data analysis",
                "subtopics": [
                    "Probability Theory - Independent & dependent events",
                    "Descriptive Statistics - Central tendency, Dispersion", 
                    "Inferential Statistics - Hypothesis testing, Confidence intervals",
                    "Correlation & Covariance - Pearson correlation"
                ]
            },
            {
                "id": "python_ds",
                "name": "Python for Data Science", 
                "description": "Essential Python libraries and tools for data analysis",
                "subtopics": [
                    "Numpy - Arrays, indexing, Broadcasting",
                    "Pandas - Series & DataFrame, GroupBy, merges",
                    "Visualization - Matplotlib, Seaborn basics"
                ]
            }
        ],
        "Moderate Level": [
            {
                "id": "sql_databases",
                "name": "SQL & Databases",
                "description": "Database management and querying skills",
                "subtopics": [
                    "Queries - SELECT, WHERE, ORDER BY, GROUP BY",
                    "Joins - INNER, LEFT, RIGHT, FULL", 
                    "Subqueries & CTEs - Common table expressions",
                    "Window Functions - ROW_NUMBER, RANK, LAG"
                ]
            },
            {
                "id": "ml_basics",
                "name": "Machine Learning Basics",
                "description": "Fundamental machine learning algorithms",
                "subtopics": [
                    "Regression - Linear regression, Multiple regression",
                    "Classification - Logistic regression, k-NN, Decision Trees",
                    "Evaluation Metrics - Accuracy, Precision, Recall, F1"
                ]
            }
        ],
        "Advanced Level": [
            {
                "id": "advanced_ml",
                "name": "Advanced Machine Learning", 
                "description": "Complex machine learning algorithms and ensemble methods",
                "subtopics": [
                    "Ensembles - Random Forest, Gradient Boosting, XGBoost",
                    "SVM - Linear, Kernel methods",
                    "Clustering - K-Means, Hierarchical, DBSCAN",
                    "Dimensionality Reduction - PCA, t-SNE"
                ]
            }
        ],
        "Expert Level": [
            {
                "id": "ml_system_design",
                "name": "ML System Design",
                "description": "Designing and deploying machine learning systems at scale", 
                "subtopics": [
                    "System Architecture - Microservices, Data pipelines",
                    "Scalability - Distributed computing, Cloud infrastructure",
                    "Monitoring - Model performance tracking, Data drift detection"
                ]
            }
        ]
    }
}

# Storage
SESSION_STORE = {}
MOCK_TEST_STORE = {}

class AIQuestionGenerator:
    @staticmethod
    def generate_questions(context: Dict, num_questions: int = 5) -> List[Dict]:
        """Generate questions using Ollama"""
        try:
            subject = context.get('subject', 'Data Science')
            level = context.get('level', 'beginner')
            
            prompt = f"""Generate {num_questions} multiple-choice questions about {subject} at {level} level.
            Each question should have 4 options (A, B, C, D) and indicate the correct answer.
            Make questions practical and relevant to real-world applications.
            
            Format each question exactly like:
            Q1: [Question text]
            A. [Option A]
            B. [Option B] 
            C. [Option C]
            D. [Option D]
            Correct: [A/B/C/D]
            Difficulty: [easy/medium/hard]
            
            Generate questions now:"""
            
            response = ollama.chat(
                model='llama3.2:1b',
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            return AIQuestionGenerator._parse_questions(response['message']['content'], context)
            
        except Exception as e:
            print(f"AI generation failed: {e}")
            return AIQuestionGenerator._generate_fallback_questions(context, num_questions)
    
    @staticmethod
    def _parse_questions(text: str, context: Dict) -> List[Dict]:
        """Parse AI-generated questions"""
        questions = []
        lines = text.strip().split('\n')
        current_q = None
        
        for line in lines:
            line = line.strip()
            if re.match(r'^Q\d+:', line):
                if current_q and AIQuestionGenerator._is_complete_question(current_q):
                    questions.append(current_q)
                
                question_text = re.sub(r'^Q\d+:\s*', '', line)
                current_q = {
                    'id': str(uuid4()),
                    'text': question_text,
                    'options': [],
                    'category': context.get('category', 'General'),
                    'level': context.get('level', 'beginner'),
                    'difficulty': 'medium'
                }
            
            elif re.match(r'^[A-D]\.', line):
                if current_q:
                    option_text = re.sub(r'^[A-D]\.\s*', '', line)
                    current_q['options'].append(option_text)
            
            elif re.match(r'^Correct:', line):
                if current_q:
                    match = re.search(r'Correct:\s*([A-D])', line)
                    if match:
                        current_q['correct_letter'] = match.group(1).upper()
            
            elif re.match(r'^Difficulty:', line):
                if current_q:
                    match = re.search(r'Difficulty:\s*(easy|medium|hard)', line)
                    if match:
                        current_q['difficulty'] = match.group(1).lower()
        
        if current_q and AIQuestionGenerator._is_complete_question(current_q):
            questions.append(current_q)
        
        # Process questions
        for q in questions:
            correct_text = q['options'][ord(q['correct_letter']) - ord('A')]
            random.shuffle(q['options'])
            q['correct_answer'] = q['options'].index(correct_text)
            q['skill_name'] = context.get('skill_name')
            q['topic_name'] = context.get('topic_name')
        
        return questions
    
    @staticmethod
    def _is_complete_question(q: Dict) -> bool:
        return (q.get('text') and len(q.get('options', [])) == 4 and q.get('correct_letter'))
    
    @staticmethod
    def _generate_fallback_questions(context: Dict, num_questions: int) -> List[Dict]:
        """Generate fallback questions when AI fails"""
        subject = context.get('subject', 'Data Science')
        questions = []
        
        for i in range(num_questions):
            questions.append({
                'id': str(uuid4()),
                'text': f"What is a key concept in {subject}?",
                'options': [
                    "Understanding core fundamentals",
                    "Practical implementation", 
                    "Theoretical knowledge",
                    "Industry best practices"
                ],
                'correct_answer': random.randint(0, 3),
                'difficulty': random.choice(['easy', 'medium', 'hard']),
                'category': context.get('category', 'General'),
                'level': context.get('level', 'beginner'),
                'skill_name': context.get('skill_name'),
                'topic_name': context.get('topic_name')
            })
        
        return questions

# API Endpoints
@app.get("/api/get-skills/{session_id}")
async def get_skills(session_id: str):
    """STEP 1: Get available skills for selection"""
    try:
        skills_list = []
        for category, skills in DATA_SCIENCE_ROADMAP["skills"].items():
            for skill_name, skill_info in skills.items():
                skills_list.append({
                    "id": f"{category}_{skill_name}",
                    "name": skill_name,
                    "category": category.replace('_', ' ').title(),
                    "description": skill_info["description"],
                    "difficulty": skill_info["difficulty"]
                })
        
        return {"skills": skills_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-skills-mock-test")
async def generate_skills_mock_test(request: SkillsMockTestRequest):
    """STEP 1: Generate skills mock test"""
    try:
        all_questions = []
        
        for skill_id in request.selected_skills:
            category, skill_name = skill_id.split('_', 1)
            skill_info = DATA_SCIENCE_ROADMAP["skills"][category][skill_name]
            
            context = {
                "subject": skill_name,
                "skill_name": skill_name,
                "category": category,
                "level": skill_info["difficulty"]
            }
            
            questions = AIQuestionGenerator.generate_questions(context, 5)
            all_questions.extend(questions)
        
        # Ensure we don't exceed requested total
        all_questions = all_questions[:request.total_questions]
        random.shuffle(all_questions)
        
        test_id = str(uuid4())
        test_data = {
            "test_id": test_id,
            "session_id": request.session_id,
            "questions": all_questions,
            "total_questions": len(all_questions),
            "test_type": "skills",
            "created_at": datetime.now().isoformat()
        }
        
        MOCK_TEST_STORE[test_id] = test_data
        
        return {
            "test_id": test_id,
            "questions": all_questions,
            "total_questions": len(all_questions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get-level-topics/{session_id}")
async def get_level_topics(session_id: str, target_level: str):
    """STEP 3: Get topics for target level"""
    try:
        topics = DATA_SCIENCE_ROADMAP["topics"].get(target_level, [])
        return {"topics": topics, "target_level": target_level}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-topics-mock-test")
async def generate_topics_mock_test(request: TopicsMockTestRequest):
    """STEP 3: Generate topics mock test"""
    try:
        all_questions = []
        
        # Get all topics to find the selected ones
        all_topics = {}
        for level_topics in DATA_SCIENCE_ROADMAP["topics"].values():
            for topic in level_topics:
                all_topics[topic["id"]] = topic
        
        for topic_id in request.selected_topics:
            topic = all_topics.get(topic_id)
            if not topic:
                continue
            
            context = {
                "subject": topic["name"],
                "topic_name": topic["name"],
                "category": "topic",
                "level": "intermediate"
            }
            
            questions = AIQuestionGenerator.generate_questions(context, 5)
            all_questions.extend(questions)
        
        all_questions = all_questions[:request.total_questions]
        random.shuffle(all_questions)
        
        test_id = str(uuid4())
        test_data = {
            "test_id": test_id,
            "session_id": request.session_id,
            "questions": all_questions,
            "total_questions": len(all_questions),
            "test_type": "topics",
            "created_at": datetime.now().isoformat()
        }
        
        MOCK_TEST_STORE[test_id] = test_data
        
        return {
            "test_id": test_id,
            "questions": all_questions,
            "total_questions": len(all_questions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/submit-mock-test")
async def submit_mock_test(submission: MockTestSubmission):
    """STEP 4: Evaluate mock test and return results"""
    try:
        test_id = submission.test_id
        
        if test_id not in MOCK_TEST_STORE:
            raise HTTPException(status_code=400, detail="Test not found")
        
        test_data = MOCK_TEST_STORE[test_id]
        questions = test_data["questions"]
        test_type = test_data["test_type"]
        
        # Evaluate answers
        total_questions = len(questions)
        correct_count = 0
        skill_results = {}
        topic_results = {}
        
        for question in questions:
            q_id = question["id"]
            user_answer = submission.answers.get(q_id)
            correct_answer = question.get("correct_answer")
            
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1
            
            # Track results by skill/topic
            if test_type == "skills":
                skill_name = question.get("skill_name")
                if skill_name:
                    if skill_name not in skill_results:
                        skill_results[skill_name] = {"total": 0, "correct": 0}
                    skill_results[skill_name]["total"] += 1
                    if is_correct:
                        skill_results[skill_name]["correct"] += 1
            else:
                topic_name = question.get("topic_name")
                if topic_name:
                    if topic_name not in topic_results:
                        topic_results[topic_name] = {"total": 0, "correct": 0}
                    topic_results[topic_name]["total"] += 1
                    if is_correct:
                        topic_results[topic_name]["correct"] += 1
        
        # Calculate overall score
        overall_score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Generate recommendations
        good_items = []
        needs_improvement = []
        
        if test_type == "skills":
            for skill_name, result in skill_results.items():
                skill_score = (result["correct"] / result["total"] * 100)
                if skill_score >= 70:
                    good_items.append(skill_name)
                else:
                    needs_improvement.append(skill_name)
        else:
            for topic_name, result in topic_results.items():
                topic_score = (result["correct"] / result["total"] * 100)
                if topic_score >= 70:
                    good_items.append(topic_name)
                else:
                    needs_improvement.append(topic_name)
        
        # Determine readiness level
        if overall_score >= 85:
            readiness = "excellent"
            next_steps = ["You're ready to advance", "Focus on real-world projects"]
        elif overall_score >= 70:
            readiness = "good" 
            next_steps = ["Solid foundation", "Practice weak areas"]
        elif overall_score >= 50:
            readiness = "moderate"
            next_steps = ["More preparation needed", "Review fundamentals"]
        else:
            readiness = "needs_work"
            next_steps = ["Focus on foundational learning", "Seek additional resources"]
        
        return {
            "overall_score": round(overall_score, 2),
            "overall_level": readiness,
            "total_questions": total_questions,
            "total_correct": correct_count,
            "time_taken_seconds": submission.time_taken_seconds,
            "time_taken_display": f"{submission.time_taken_seconds // 60}m {submission.time_taken_seconds % 60}s",
            "good_skills" if test_type == "skills" else "good_topics": good_items,
            "needs_improvement_skills" if test_type == "skills" else "needs_improvement_topics": needs_improvement,
            "next_steps": next_steps,
            "skill_results" if test_type == "skills" else "topic_results": skill_results if test_type == "skills" else topic_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Skills Assessment API", "version": "2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)