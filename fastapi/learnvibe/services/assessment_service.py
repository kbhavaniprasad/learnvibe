import json
import random
from typing import List, Dict, Any
from models.schemas import Question, AssessmentResult, CareerLevel

class AssessmentService:
    def __init__(self, llm_service):
        self.llm_service = llm_service
        
        # Enhanced question templates specifically for Data Science
        self.data_science_question_bank = {
            "foundational_concepts": [
                {
                    "template": "What is the primary purpose of {concept} in data science?",
                    "concepts": ["data normalization", "feature engineering", "cross-validation", "regularization", "dimensionality reduction"],
                    "options_template": [
                        "To {wrong_purpose1}",
                        "To {correct_purpose}",
                        "To {wrong_purpose2}",
                        "To {wrong_purpose3}"
                    ],
                    "correct_purposes": {
                        "data normalization": "scale features to a common range and improve model performance",
                        "feature engineering": "create new input features from existing ones to improve model accuracy",
                        "cross-validation": "assess how model results will generalize to an independent dataset",
                        "regularization": "prevent overfitting by adding penalty terms to the model",
                        "dimensionality reduction": "reduce number of input variables while preserving important information"
                    },
                    "wrong_purposes": [
                        "increase computational complexity unnecessarily",
                        "make data visualization more colorful",
                        "automatically clean missing values from datasets",
                        "convert data into binary format only",
                        "speed up data collection processes",
                        "simplify database management systems"
                    ],
                    "difficulty": "easy",
                    "skill_name": "Data Science Fundamentals",
                    "topic_name": "Core Concepts"
                }
            ],
            "technical_knowledge": [
                {
                    "template": "Which of the following is the best approach for {scenario}?",
                    "scenarios": [
                        "handling missing values in a dataset with 5% missing data",
                        "dealing with highly imbalanced classification data",
                        "selecting features for a high-dimensional dataset",
                        "evaluating regression model performance",
                        "tuning hyperparameters for a machine learning model"
                    ],
                    "options_sets": [
                        [
                            "Remove all rows with missing values",
                            "Use mean/median imputation for numerical features",
                            "Fill with zeros",
                            "Ignore the missing values"
                        ],
                        [
                            "Use accuracy as the main metric",
                            "Apply class weighting or resampling techniques",
                            "Remove samples from the majority class",
                            "Focus only on the majority class"
                        ],
                        [
                            "Use all features without selection",
                            "Apply PCA for dimensionality reduction",
                            "Use recursive feature elimination",
                            "Select features randomly"
                        ],
                        [
                            "R-squared score alone",
                            "Mean Absolute Error and R-squared together",
                            "Only visual inspection of plots",
                            "Training accuracy only"
                        ],
                        [
                            "Use default parameters always",
                            "Manual trial and error",
                            "Grid search or random search with cross-validation",
                            "Copy parameters from another project"
                        ]
                    ],
                    "correct_answers": [1, 1, 2, 1, 2],
                    "difficulty": "medium",
                    "skill_name": "Technical Implementation",
                    "topic_name": "Best Practices"
                }
            ],
            "machine_learning": [
                {
                    "template": "In the context of {algorithm}, what is the role of {component}?",
                    "algorithms": [
                        {"name": "decision trees", "component": "the Gini impurity", "correct": "measures node purity for classification splits", "wrong": ["prunes the tree automatically", "handles missing values", "speeds up prediction time"]},
                        {"name": "neural networks", "component": "the activation function", "correct": "introduces non-linearity to the model", "wrong": ["stores model parameters", "optimizes learning rate", "normalizes input data"]},
                        {"name": "k-means clustering", "component": "the centroid", "correct": "represents the center point of a cluster", "wrong": ["measures cluster quality", "determines the number of clusters", "handles categorical data"]},
                        {"name": "linear regression", "component": "the coefficient", "correct": "represents the relationship between feature and target", "wrong": ["regularizes the model", "handles outliers", "scales the features"]}
                    ],
                    "difficulty": "medium",
                    "skill_name": "Machine Learning",
                    "topic_name": "Algorithm Understanding"
                }
            ],
            "statistics_probability": [
                {
                    "template": "When analyzing {scenario}, which statistical concept is most relevant?",
                    "scenarios": [
                        "the relationship between two continuous variables",
                        "whether a new marketing strategy increased conversion rates",
                        "the distribution of customer purchase amounts",
                        "predicting customer churn probability"
                    ],
                    "options_sets": [
                        ["Correlation analysis", "Cluster analysis", "Time series decomposition", "Principal component analysis"],
                        ["Hypothesis testing", "Descriptive statistics", "Association rules", "Dimensionality reduction"],
                        ["Probability distributions", "Classification metrics", "Feature importance", "Cross-validation"],
                        ["Logistic regression", "K-means clustering", "Linear regression", "Association mining"]
                    ],
                    "correct_answers": [0, 0, 0, 0],
                    "difficulty": "hard",
                    "skill_name": "Statistics & Probability",
                    "topic_name": "Statistical Thinking"
                }
            ],
            "programming_tools": [
                {
                    "template": "Which {tool_type} would be most appropriate for {task}?",
                    "tool_types": ["Python library", "data structure", "SQL operation", "visualization tool"],
                    "tasks": [
                        "manipulating and analyzing structured data",
                        "storing key-value pairs with fast lookup",
                        "combining data from multiple tables",
                        "creating interactive dashboards"
                    ],
                    "options_sets": [
                        ["Pandas", "NumPy", "Scikit-learn", "Matplotlib"],
                        ["Dictionary", "List", "Set", "Tuple"],
                        ["JOIN", "WHERE", "GROUP BY", "ORDER BY"],
                        ["Plotly", "Seaborn", "Matplotlib", "Pandas plotting"]
                    ],
                    "correct_answers": [0, 0, 0, 0],
                    "difficulty": "easy",
                    "skill_name": "Programming & Tools",
                    "topic_name": "Technical Skills"
                }
            ]
        }
    
    def generate_custom_levels(self, goal: str) -> List[str]:
        """Generate custom career levels for a given goal"""
        # For data science roles, use specific progression
        goal_lower = goal.lower()
        if any(term in goal_lower for term in ['data scientist', 'data analyst', 'machine learning', 'ai']):
            return ["Junior Data Scientist", "Data Scientist", "Senior Data Scientist", "Principal Data Scientist"]
        elif any(term in goal_lower for term in ['data engineer', 'ml engineer']):
            return ["Junior Data Engineer", "Data Engineer", "Senior Data Engineer", "Lead Data Engineer"]
        else:
            # Generic progression for other roles
            return [f"Junior {goal}", goal, f"Senior {goal}", f"Principal {goal}"]
    
    def generate_assessment_questions(self, goal: str, levels: List[str]) -> List[Question]:
        """Generate 10-12 effective assessment questions for a career goal"""
        num_questions = random.randint(10, 12)  # Generate 10-12 questions
        questions = []
        
        # Determine question distribution based on career focus
        goal_lower = goal.lower()
        
        if any(term in goal_lower for term in ['data scientist', 'data analyst', 'machine learning', 'ai']):
            questions = self._generate_data_science_questions(num_questions)
        else:
            questions = self._generate_general_tech_questions(goal, num_questions)
        
        # Shuffle questions and assign IDs
        random.shuffle(questions)
        for i, question in enumerate(questions):
            question.id = i + 1
        
        return questions
    
    def _generate_data_science_questions(self, num_questions: int) -> List[Question]:
        """Generate data science specific questions"""
        questions = []
        categories = list(self.data_science_question_bank.keys())
        
        # Ensure good distribution across categories
        questions_per_category = max(2, num_questions // len(categories))
        
        for category in categories:
            category_questions = self._generate_questions_from_category(
                category, questions_per_category
            )
            questions.extend(category_questions)
        
        # If we need more questions, add from random categories
        while len(questions) < num_questions:
            random_category = random.choice(categories)
            extra_question = self._generate_questions_from_category(random_category, 1)
            if extra_question:
                questions.extend(extra_question)
        
        return questions[:num_questions]
    
    def _generate_questions_from_category(self, category: str, count: int) -> List[Question]:
        """Generate questions from a specific category"""
        questions = []
        category_data = self.data_science_question_bank[category]
        
        for question_template in category_data:
            for _ in range(count):
                try:
                    if category == "foundational_concepts":
                        question = self._create_foundational_question(question_template)
                    elif category == "technical_knowledge":
                        question = self._create_technical_question(question_template)
                    elif category == "machine_learning":
                        question = self._create_ml_question(question_template)
                    elif category == "statistics_probability":
                        question = self._create_stats_question(question_template)
                    elif category == "programming_tools":
                        question = self._create_tools_question(question_template)
                    
                    if question:
                        questions.append(question)
                        
                except Exception as e:
                    print(f"Error generating question: {e}")
                    continue
        
        return questions[:count]
    
    def _create_foundational_question(self, template_data: Dict) -> Question:
        """Create foundational concept question"""
        concept = random.choice(template_data["concepts"])
        correct_purpose = template_data["correct_purposes"][concept]
        
        # Select wrong purposes
        wrong_purposes = random.sample(template_data["wrong_purposes"], 3)
        
        # Create options
        options = []
        for option_template in template_data["options_template"]:
            if "correct_purpose" in option_template:
                options.append(option_template.format(correct_purpose=correct_purpose))
            else:
                wrong_purpose = wrong_purposes.pop()
                options.append(option_template.format(wrong_purpose1=wrong_purpose))
        
        # Shuffle options but remember correct answer position
        correct_answer = options.index(f"To {correct_purpose}")
        random.shuffle(options)
        correct_answer = options.index(f"To {correct_purpose}")
        
        return Question(
            id=0,  # Will be reassigned later
            text=template_data["template"].format(concept=concept),
            options=options,
            correct_answer=correct_answer,
            difficulty=template_data["difficulty"],
            skill_name=template_data["skill_name"],
            topic_name=template_data["topic_name"]
        )
    
    def _create_technical_question(self, template_data: Dict) -> Question:
        """Create technical implementation question"""
        scenario_idx = random.randint(0, len(template_data["scenarios"]) - 1)
        scenario = template_data["scenarios"][scenario_idx]
        options = template_data["options_sets"][scenario_idx]
        correct_answer = template_data["correct_answers"][scenario_idx]
        
        return Question(
            id=0,
            text=template_data["template"].format(scenario=scenario),
            options=options,
            correct_answer=correct_answer,
            difficulty=template_data["difficulty"],
            skill_name=template_data["skill_name"],
            topic_name=template_data["topic_name"]
        )
    
    def _create_ml_question(self, template_data: Dict) -> Question:
        """Create machine learning algorithm question"""
        algorithm_data = random.choice(template_data["algorithms"])
        
        options = [algorithm_data["correct"]] + algorithm_data["wrong"]
        random.shuffle(options)
        correct_answer = options.index(algorithm_data["correct"])
        
        return Question(
            id=0,
            text=template_data["template"].format(
                algorithm=algorithm_data["name"],
                component=algorithm_data["component"]
            ),
            options=options,
            correct_answer=correct_answer,
            difficulty=template_data["difficulty"],
            skill_name=template_data["skill_name"],
            topic_name=template_data["topic_name"]
        )
    
    def _create_stats_question(self, template_data: Dict) -> Question:
        """Create statistics and probability question"""
        scenario_idx = random.randint(0, len(template_data["scenarios"]) - 1)
        scenario = template_data["scenarios"][scenario_idx]
        options = template_data["options_sets"][scenario_idx]
        correct_answer = template_data["correct_answers"][scenario_idx]
        
        return Question(
            id=0,
            text=template_data["template"].format(scenario=scenario),
            options=options,
            correct_answer=correct_answer,
            difficulty=template_data["difficulty"],
            skill_name=template_data["skill_name"],
            topic_name=template_data["topic_name"]
        )
    
    def _create_tools_question(self, template_data: Dict) -> Question:
        """Create programming tools question"""
        task_idx = random.randint(0, len(template_data["tasks"]) - 1)
        task = template_data["tasks"][task_idx]
        tool_type = template_data["tool_types"][task_idx % len(template_data["tool_types"])]
        options = template_data["options_sets"][task_idx]
        correct_answer = template_data["correct_answers"][task_idx]
        
        return Question(
            id=0,
            text=template_data["template"].format(
                tool_type=tool_type,
                task=task
            ),
            options=options,
            correct_answer=correct_answer,
            difficulty=template_data["difficulty"],
            skill_name=template_data["skill_name"],
            topic_name=template_data["topic_name"]
        )
    
    def _generate_general_tech_questions(self, goal: str, num_questions: int) -> List[Question]:
        """Generate general technology questions for non-data science roles"""
        # Common tech questions that apply to most technical roles
        general_questions = [
            {
                "text": "What is the main advantage of using version control systems like Git?",
                "options": [
                    "Tracking changes and enabling collaboration",
                    "Automatically debugging code",
                    "Compiling code faster",
                    "Designing user interfaces"
                ],
                "correct_answer": 0,
                "difficulty": "easy",
                "skill_name": "Software Development",
                "topic_name": "Version Control"
            },
            {
                "text": "Which principle suggests that a class should have only one reason to change?",
                "options": [
                    "Single Responsibility Principle",
                    "Open-Closed Principle",
                    "Liskov Substitution Principle",
                    "Interface Segregation Principle"
                ],
                "correct_answer": 0,
                "difficulty": "medium",
                "skill_name": "Software Design",
                "topic_name": "SOLID Principles"
            },
            {
                "text": "What is the time complexity of accessing an element in a hash table?",
                "options": [
                    "O(1) on average",
                    "O(log n)",
                    "O(n)",
                    "O(n log n)"
                ],
                "correct_answer": 0,
                "difficulty": "medium",
                "skill_name": "Computer Science",
                "topic_name": "Data Structures"
            },
            {
                "text": "In database design, what is the purpose of normalization?",
                "options": [
                    "Reduce data redundancy and improve integrity",
                    "Speed up query performance",
                    "Increase storage capacity",
                    "Simplify backup processes"
                ],
                "correct_answer": 0,
                "difficulty": "medium",
                "skill_name": "Database Management",
                "topic_name": "Database Design"
            }
        ]
        
        questions = []
        for i, q_data in enumerate(general_questions[:num_questions]):
            questions.append(Question(
                id=i + 1,
                text=q_data["text"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                difficulty=q_data["difficulty"],
                skill_name=q_data["skill_name"],
                topic_name=q_data["topic_name"]
            ))
        
        return questions
    
    def evaluate_answers(self, goal: str, questions: List[Dict], user_answers: List[int]) -> AssessmentResult:
        """Evaluate user answers and generate results"""
        if len(user_answers) != len(questions):
            raise ValueError("Number of answers doesn't match number of questions")
        
        # Calculate score
        correct_count = 0
        for i, answer in enumerate(user_answers):
            if answer == questions[i]["correct_answer"]:
                correct_count += 1
        
        score = (correct_count / len(questions)) * 100
        
        # Determine level based on score and custom levels
        assigned_level = self._assign_level(goal, score, questions)
        
        # Generate detailed feedback
        feedback = self._generate_detailed_feedback(score, correct_count, len(questions), assigned_level, questions, user_answers)
        
        # Identify improvement areas
        improvement_areas = self._identify_improvement_areas(questions, user_answers)
        
        return AssessmentResult(
            score=round(score, 1),
            correct_answers=correct_count,
            total_questions=len(questions),
            assigned_level=assigned_level,
            feedback=feedback,
            improvement_areas=improvement_areas
        )
    
    def _assign_level(self, goal: str, score: float, questions: List[Dict]) -> str:
        """Assign career level based on score and question difficulty"""
        # Analyze question difficulty distribution
        difficulty_scores = {"easy": 0, "medium": 0, "hard": 0}
        for q in questions:
            difficulty_scores[q.get("difficulty", "medium")] += 1
        
        # Adjust level thresholds based on question difficulty
        hard_question_ratio = difficulty_scores["hard"] / len(questions)
        
        if score >= 90 - (hard_question_ratio * 20):
            return f"Expert {goal}"
        elif score >= 75 - (hard_question_ratio * 15):
            return f"Senior {goal}"
        elif score >= 60 - (hard_question_ratio * 10):
            return goal
        elif score >= 40:
            return f"Junior {goal}"
        else:
            return f"Entry {goal}"
    
    def _generate_detailed_feedback(self, score: float, correct: int, total: int, level: str, 
                                  questions: List[Dict], user_answers: List[int]) -> str:
        """Generate personalized feedback based on score and performance patterns"""
        
        # Analyze performance by skill area
        skill_performance = {}
        for i, question in enumerate(questions):
            skill = question.get("skill_name", "General")
            is_correct = user_answers[i] == question["correct_answer"]
            if skill not in skill_performance:
                skill_performance[skill] = {"correct": 0, "total": 0}
            skill_performance[skill]["total"] += 1
            if is_correct:
                skill_performance[skill]["correct"] += 1
        
        # Find strongest and weakest areas
        skill_accuracy = {skill: (data["correct"] / data["total"]) * 100 
                         for skill, data in skill_performance.items()}
        strongest_area = max(skill_accuracy.items(), key=lambda x: x[1])
        weakest_area = min(skill_accuracy.items(), key=lambda x: x[1])
        
        if score >= 90:
            return (f"Exceptional performance! Your {score}% score demonstrates expert-level proficiency "
                   f"across all assessed areas. You're well-prepared for {level} roles. "
                   f"Your strongest area is {strongest_area[0]} ({strongest_area[1]:.0f}% accuracy).")
        
        elif score >= 75:
            return (f"Strong performance! Your {score}% score indicates you're ready for {level} positions. "
                   f"You show particular strength in {strongest_area[0]} ({strongest_area[1]:.0f}% accuracy). "
                   f"Consider deepening your knowledge in {weakest_area[0]} to reach the next level.")
        
        elif score >= 60:
            return (f"Solid foundation! Your {score}% score places you at {level} level. "
                   f"You have good understanding of core concepts but should focus on improving "
                   f"your skills in {weakest_area[0]} (currently {weakest_area[1]:.0f}% accuracy).")
        
        elif score >= 40:
            return (f"Developing skills! Your {score}% score suggests you're at {level} level. "
                   f"Focus on building foundational knowledge, particularly in {weakest_area[0]} "
                   f"where you scored {weakest_area[1]:.0f}%. Practice and hands-on projects will help.")
        
        else:
            return (f"Beginning your journey! Your {score}% score indicates you're starting your {level} path. "
                   f"This is a great starting point - focus on core fundamentals and consider structured "
                   f"learning in {weakest_area[0]} to build your foundation.")
    
    def _identify_improvement_areas(self, questions: List[Dict], user_answers: List[int]) -> List[str]:
        """Identify specific areas for improvement based on incorrect answers"""
        incorrect_skills = {}
        incorrect_topics = {}
        
        for i, answer in enumerate(user_answers):
            if answer != questions[i]["correct_answer"]:
                skill = questions[i].get("skill_name", "General Knowledge")
                topic = questions[i].get("topic_name", "Fundamentals")
                
                incorrect_skills[skill] = incorrect_skills.get(skill, 0) + 1
                incorrect_topics[topic] = incorrect_topics.get(topic, 0) + 1
        
        # Return top 3 improvement areas combining skills and topics
        sorted_skills = sorted(incorrect_skills.items(), key=lambda x: x[1], reverse=True)
        sorted_topics = sorted(incorrect_topics.items(), key=lambda x: x[1], reverse=True)
        
        improvement_areas = []
        
        # Add top skills needing improvement
        for skill, count in sorted_skills[:2]:
            improvement_areas.append(f"Advanced {skill} concepts")
        
        # Add specific topics needing work
        for topic, count in sorted_topics[:1]:
            improvement_areas.append(f"{topic} fundamentals")
        
        return improvement_areas[:3]