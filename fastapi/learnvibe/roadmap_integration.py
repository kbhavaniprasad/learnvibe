
# import ollama
# import re
# import json
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional, Any
# import logging
# from enum import Enum
# import asyncio

# logger = logging.getLogger(__name__)

# class ResourceType(Enum):
#     YOUTUBE = "youtube"
#     DOCUMENTATION = "documentation"
#     ARTICLE = "article"
#     PRACTICE = "practice"
#     PROJECT = "project"
#     COMMUNITY = "community"
#     COURSE = "course"

# class RoadmapGenerator:
#     def __init__(self):
#         # Use available model - will auto-detect
#         self.model = None
#         self.daily_study_hours = 2
#         self.weekly_study_days = 5
        
#         # Verify model availability
#         self._verify_model()
    
#     def _verify_model(self):
#         """Verify the model is available and working"""
#         try:
#             models_response = ollama.list()
#             logger.info(f"Ollama models response: {models_response}")
            
#             # Handle different response structures
#             if 'models' in models_response:
#                 models_list = models_response['models']
#                 if models_list:
#                     # Get the first available model
#                     first_model = models_list[0]
#                     if 'name' in first_model:
#                         self.model = first_model['name']
#                     elif 'model' in first_model:
#                         self.model = first_model['model']
#                     else:
#                         # Try to find any model name in the first model
#                         model_name = self._extract_model_name(first_model)
#                         self.model = model_name
                    
#                     logger.info(f"Using model: {self.model}")
#                 else:
#                     logger.warning("No models found in Ollama. Please install a model first.")
#                     logger.info("Run: ollama pull llama3.1:8b")
#                     self.model = "llama3.1:8b"  # Default, will fail if not available
#             else:
#                 logger.warning("Unexpected Ollama response structure")
#                 self.model = "llama3.1:8b"  # Fallback
                
#         except Exception as e:
#             logger.error(f"Model verification failed: {str(e)}")
#             # Set a default model and hope it works
#             self.model = "llama3.1:8b"
#             logger.info(f"Using default model: {self.model}")

#     def _extract_model_name(self, model_data: Dict) -> str:
#         """Extract model name from various possible structures"""
#         # Try different possible keys
#         possible_keys = ['name', 'model', 'model_name', 'id']
#         for key in possible_keys:
#             if key in model_data:
#                 return model_data[key]
        
#         # If no key found, return a default
#         return "llama3.1:8b"

#     async def generate_personalized_roadmap(
#         self,
#         user_goal: str,
#         current_level: str,
#         target_level: str,
#         assessment_score: float,
#         weak_skills: List[str],
#         weak_topics: List[str],
#         strong_areas: List[str],
#         timeline_preference: str = "standard"
#     ) -> Dict:
#         """Generate truly personalized learning roadmap with unique daily tasks"""
        
#         logger.info(f"Starting roadmap generation for: {user_goal}")
        
#         try:
#             # Calculate timeline
#             base_weeks = self._calculate_base_timeline(assessment_score, timeline_preference)
            
#             # For faster testing, use fallback for now
#             if not self.model:
#                 logger.warning("No model available, using fallback roadmap")
#                 return self._generate_fallback_complete_roadmap(
#                     user_goal, current_level, target_level, assessment_score,
#                     weak_skills, weak_topics, strong_areas, timeline_preference
#                 )
            
#             # Try AI generation with timeout
#             try:
#                 roadmap_data = await asyncio.wait_for(
#                     self._generate_complete_roadmap(
#                         user_goal, current_level, target_level, assessment_score,
#                         weak_skills, weak_topics, strong_areas, base_weeks
#                     ),
#                     timeout=120  # 2 minute timeout for testing
#                 )
#                 logger.info(f"AI roadmap generation completed: {base_weeks} weeks")
#                 return roadmap_data
                
#             except asyncio.TimeoutError:
#                 logger.warning("AI generation timed out, using fallback roadmap")
#                 return self._generate_fallback_complete_roadmap(
#                     user_goal, current_level, target_level, assessment_score,
#                     weak_skills, weak_topics, strong_areas, timeline_preference
#                 )
#             except Exception as ai_error:
#                 logger.warning(f"AI generation failed: {str(ai_error)}, using fallback roadmap")
#                 return self._generate_fallback_complete_roadmap(
#                     user_goal, current_level, target_level, assessment_score,
#                     weak_skills, weak_topics, strong_areas, timeline_preference
#                 )
            
#         except Exception as e:
#             logger.error(f"Roadmap generation failed: {str(e)}")
#             # Return fallback roadmap
#             return self._generate_fallback_complete_roadmap(
#                 user_goal, current_level, target_level, assessment_score,
#                 weak_skills, weak_topics, strong_areas, timeline_preference
#             )
    
#     def _calculate_base_timeline(self, assessment_score: float, timeline_preference: str) -> int:
#         """Calculate realistic timeline in weeks"""
#         # Base calculation
#         if assessment_score >= 80:
#             base_weeks = 8
#         elif assessment_score >= 60:
#             base_weeks = 12
#         elif assessment_score >= 40:
#             base_weeks = 16
#         else:
#             base_weeks = 20
        
#         # Adjust by preference
#         if timeline_preference == "accelerated":
#             base_weeks = max(6, int(base_weeks * 0.7))
#         elif timeline_preference == "relaxed":
#             base_weeks = int(base_weeks * 1.3)
        
#         return base_weeks
    
#     async def _generate_complete_roadmap(
#         self,
#         user_goal: str,
#         current_level: str,
#         target_level: str,
#         assessment_score: float,
#         weak_skills: List[str],
#         weak_topics: List[str],
#         strong_areas: List[str],
#         base_weeks: int
#     ) -> Dict:
#         """Generate complete roadmap in one optimized call"""
        
#         prompt = self._build_complete_roadmap_prompt(
#             user_goal, current_level, target_level, assessment_score,
#             weak_skills, weak_topics, strong_areas, base_weeks
#         )
        
#         try:
#             logger.info(f"Generating complete roadmap for {user_goal} ({base_weeks} weeks)")
            
#             # Single API call for complete roadmap
#             response = ollama.chat(
#                 model=self.model,
#                 messages=[{"role": "user", "content": prompt}],
#                 options={
#                     "temperature": 0.7,
#                     "num_predict": 2000,  # Reduced for faster response
#                     "top_k": 40,
#                     "top_p": 0.8,
#                     "repeat_penalty": 1.1
#                 }
#             )
            
#             roadmap_content = response['message']['content'].strip()
#             logger.info(f"Complete roadmap generated: {len(roadmap_content)} chars")
            
#             # Parse the complete roadmap
#             roadmap_data = self._parse_complete_roadmap(
#                 roadmap_content, user_goal, current_level, target_level,
#                 assessment_score, weak_skills, weak_topics, strong_areas, base_weeks
#             )
            
#             return roadmap_data
            
#         except Exception as e:
#             logger.error(f"Complete roadmap generation failed: {str(e)}")
#             raise
    
#     def _build_complete_roadmap_prompt(
#         self,
#         user_goal: str,
#         current_level: str,
#         target_level: str,
#         assessment_score: float,
#         weak_skills: List[str],
#         weak_topics: List[str],
#         strong_areas: List[str],
#         total_weeks: int
#     ) -> str:
#         """Build prompt for generating complete roadmap"""
        
#         weak_areas_text = ", ".join(weak_skills + weak_topics) if (weak_skills or weak_topics) else "No specific weaknesses"
#         strong_areas_text = ", ".join(strong_areas) if strong_areas else "General foundational knowledge"
        
#         return f"""Create a {total_weeks}-week learning roadmap for {user_goal} from {current_level} to {target_level}.

# Weak Areas: {weak_areas_text}
# Strong Areas: {strong_areas_text}
# Study: {self.daily_study_hours} hours/day, {self.weekly_study_days} days/week

# Create {total_weeks} weeks with {self.weekly_study_days} days each. Each day has 3 unique tasks.

# OUTPUT FORMAT:

# WEEK 1: [Week Title]
# OVERVIEW: [Description]

# DAY 1: [Day Focus]
# TASKS:
# 1. [Task 1]
#    RESOURCES:
#    - YouTube: [Title] | [URL]
#    - Docs: [Title] | [URL]

# 2. [Task 2]
#    RESOURCES:
#    - Article: [Title] | [URL]
#    - Practice: [Title] | [URL]

# 3. [Task 3]
#    RESOURCES:
#    - Project: [Title] | [URL]
#    - Community: [Title] | [URL]

# Continue for all days and weeks. Make tasks unique and practical.

# Start:"""
    
#     def _parse_complete_roadmap(self, content: str, user_goal: str, current_level: str,
#                               target_level: str, assessment_score: float, 
#                               weak_skills: List[str], weak_topics: List[str],
#                               strong_areas: List[str], total_weeks: int) -> Dict:
#         """Parse complete roadmap content"""
        
#         weekly_schedule = []
        
#         # Try to parse AI-generated content
#         week_pattern = r'WEEK\s+(\d+):\s*(.+?)(?=WEEK\s+\d+:|$)'
#         week_matches = list(re.finditer(week_pattern, content, re.IGNORECASE | re.DOTALL))
        
#         for week_match in week_matches:
#             week_num = int(week_match.group(1))
#             week_content = week_match.group(2)
            
#             if week_num > total_weeks:
#                 break
                
#             week_data = self._parse_week_content(week_content, week_num, user_goal)
#             weekly_schedule.append(week_data)
        
#         # If AI didn't generate enough weeks, create fallback weeks
#         while len(weekly_schedule) < total_weeks:
#             week_num = len(weekly_schedule) + 1
#             week_data = self._generate_fallback_week(week_num, user_goal, weak_skills + weak_topics, strong_areas, total_weeks)
#             weekly_schedule.append(week_data)
        
#         # Ensure uniqueness across all weeks
#         weekly_schedule = self._ensure_cross_week_uniqueness(weekly_schedule, user_goal)
        
#         return self._build_complete_roadmap_structure(
#             weekly_schedule, user_goal, current_level, target_level,
#             assessment_score, weak_skills, weak_topics, strong_areas, total_weeks
#         )
    
#     def _parse_week_content(self, content: str, week_number: int, user_goal: str) -> Dict:
#         """Parse individual week content"""
        
#         week = {
#             "week_number": week_number,
#             "title": f"Week {week_number}: Personalized Learning",
#             "overview": f"Focused learning week for {user_goal} development",
#             "days": [],
#             "total_tasks": 0,
#             "total_resources": 0,
#             "ai_generated": True
#         }
        
#         # Extract week title
#         title_match = re.search(r'^([^\n]+)', content.strip())
#         if title_match and 'OVERVIEW' not in title_match.group(1):
#             week["title"] = title_match.group(1).strip()
        
#         # Extract overview
#         overview_match = re.search(r'OVERVIEW:\s*(.+?)(?=DAY\s+\d+:|$)', content, re.IGNORECASE | re.DOTALL)
#         if overview_match:
#             week["overview"] = overview_match.group(1).strip()[:300]
        
#         # Extract days
#         for day_num in range(1, self.weekly_study_days + 1):
#             day_pattern = rf'DAY\s+{day_num}:\s*(.+?)(?=DAY\s+{day_num + 1}:|WEEK\s+\d+:|$)'
#             day_match = re.search(day_pattern, content, re.IGNORECASE | re.DOTALL)
            
#             if day_match:
#                 day_content = day_match.group(1)
#                 day = self._parse_daily_content(day_content, day_num, week_number, user_goal)
#                 if day and day["tasks"]:
#                     week["days"].append(day)
#                     week["total_tasks"] += len(day["tasks"])
#                     week["total_resources"] += sum(len(task["resources"]) for task in day["tasks"])
#             else:
#                 # Generate fallback day
#                 day = self._generate_unique_day(day_num, week_number, user_goal, [], [])
#                 week["days"].append(day)
#                 week["total_tasks"] += len(day["tasks"])
#                 week["total_resources"] += day["total_resources"]
        
#         return week
    
#     def _parse_daily_content(self, content: str, day_number: int, week_number: int, user_goal: str) -> Dict:
#         """Parse daily content"""
        
#         day = {
#             "day_number": day_number,
#             "week_number": week_number,
#             "date": (datetime.now() + timedelta(weeks=week_number-1, days=day_number-1)).isoformat(),
#             "day_title": f"Day {day_number}: Learning Session",
#             "tasks": [],
#             "total_resources": 0,
#             "estimated_hours": self.daily_study_hours
#         }
        
#         # Extract day title from first line
#         lines = [line.strip() for line in content.split('\n') if line.strip()]
#         if lines and not lines[0].startswith('TASKS:'):
#             day["day_title"] = lines[0]
        
#         # Extract tasks
#         task_sections = re.split(r'\d+\.\s+', content)
#         for section in task_sections[1:]:  # Skip first empty split
#             if not section.strip():
#                 continue
                
#             # Extract task description (first line)
#             task_lines = [line.strip() for line in section.split('\n') if line.strip()]
#             if not task_lines:
#                 continue
                
#             task_title = task_lines[0]
            
#             # Extract resources
#             resources = []
#             for line in task_lines[1:]:
#                 if line.startswith('RESOURCES:') or any(x in line.upper() for x in ['YOUTUBE', 'DOCUMENTATION', 'ARTICLE', 'PRACTICE', 'PROJECT', 'COMMUNITY']):
#                     resource = self._parse_resource_line(line)
#                     if resource:
#                         resources.append(resource)
            
#             # Ensure minimum resources
#             if not resources:
#                 resources = self._generate_contextual_resources(task_title, user_goal)
            
#             task = {
#                 "title": task_title,
#                 "description": f"Practical learning activity for {user_goal}",
#                 "resources": resources,
#                 "type": self._determine_task_type(task_title),
#                 "priority": "medium",
#                 "completed": False,
#                 "ai_generated": True
#             }
            
#             day["tasks"].append(task)
#             day["total_resources"] += len(resources)
        
#         # Ensure minimum tasks
#         if len(day["tasks"]) < 3:
#             additional_tasks = self._generate_unique_tasks(day_number, week_number, user_goal)
#             day["tasks"].extend(additional_tasks[:3 - len(day["tasks"])])
#             day["total_resources"] = sum(len(task["resources"]) for task in day["tasks"])
        
#         return day

#     def _ensure_cross_week_uniqueness(self, weekly_schedule: List[Dict], user_goal: str) -> List[Dict]:
#         """Ensure task uniqueness across all weeks"""
        
#         all_task_titles = set()
        
#         for week in weekly_schedule:
#             for day in week["days"]:
#                 unique_tasks = []
#                 for task in day["tasks"]:
#                     task_title = task["title"].lower().strip()
                    
#                     if task_title not in all_task_titles:
#                         all_task_titles.add(task_title)
#                         unique_tasks.append(task)
#                     else:
#                         # Replace duplicate task
#                         new_task = self._create_unique_task(all_task_titles, user_goal, day["day_number"])
#                         unique_tasks.append(new_task)
#                         all_task_titles.add(new_task["title"].lower().strip())
                
#                 day["tasks"] = unique_tasks
#                 week["total_tasks"] = len(unique_tasks)
        
#         return weekly_schedule

#     def _build_complete_roadmap_structure(self, weekly_schedule: List[Dict], user_goal: str,
#                                         current_level: str, target_level: str, assessment_score: float,
#                                         weak_skills: List[str], weak_topics: List[str],
#                                         strong_areas: List[str], total_weeks: int) -> Dict:
#         """Build complete roadmap structure"""
        
#         start_date = datetime.now()
#         total_days = total_weeks * self.weekly_study_days
        
#         roadmap = {
#             "goal": user_goal,
#             "current_level": current_level,
#             "target_level": target_level,
#             "total_weeks": total_weeks,
#             "total_days": total_days,
#             "total_hours": total_days * self.daily_study_hours,
#             "daily_study_hours": self.daily_study_hours,
#             "weekly_study_days": self.weekly_study_days,
#             "start_date": start_date.isoformat(),
#             "estimated_end_date": (start_date + timedelta(weeks=total_weeks)).isoformat(),
#             "assessment_summary": {
#                 "proficiency_level": self._get_proficiency_level(current_level),
#                 "readiness_score": int(assessment_score),
#                 "learning_style_recommendation": f"AI-personalized daily learning for {user_goal}",
#                 "key_strengths": strong_areas if strong_areas else ["Adaptive learning capacity"],
#                 "priority_gaps": weak_skills + weak_topics if (weak_skills or weak_topics) else []
#             },
#             "weekly_schedule": weekly_schedule,
#             "success_metrics": [
#                 f"Complete {total_weeks} weeks of personalized learning",
#                 f"Achieve {target_level} proficiency in {user_goal}",
#                 f"Master {len(weak_skills + weak_topics)} identified weak areas",
#                 "Build portfolio of practical projects"
#             ],
#             "study_plan": {
#                 "weekly_hours": self.daily_study_hours * self.weekly_study_days,
#                 "daily_hours": self.daily_study_hours,
#                 "study_days_per_week": self.weekly_study_days,
#                 "rest_days_per_week": 7 - self.weekly_study_days,
#                 "learning_approach": f"AI-customized progression for {user_goal}"
#             },
#             "resource_statistics": self._calculate_resource_stats(weekly_schedule),
#             "ai_generated": any(week.get('ai_generated', False) for week in weekly_schedule),
#             "personalization_factors": {
#                 "weak_areas_addressed": weak_skills + weak_topics,
#                 "strengths_leveraged": strong_areas,
#                 "total_weeks": total_weeks
#             },
#             "generated_at": datetime.now().isoformat()
#         }
        
#         return roadmap

#     def _generate_fallback_complete_roadmap(self, user_goal: str, current_level: str,
#                                           target_level: str, assessment_score: float,
#                                           weak_skills: List[str], weak_topics: List[str],
#                                           strong_areas: List[str], timeline_preference: str) -> Dict:
#         """Generate complete fallback roadmap when AI fails"""
        
#         base_weeks = self._calculate_base_timeline(assessment_score, timeline_preference)
#         weekly_schedule = []
        
#         for week_num in range(1, base_weeks + 1):
#             week_data = self._generate_fallback_week(week_num, user_goal, weak_skills + weak_topics, strong_areas, base_weeks)
#             weekly_schedule.append(week_data)
        
#         return self._build_complete_roadmap_structure(
#             weekly_schedule, user_goal, current_level, target_level,
#             assessment_score, weak_skills, weak_topics, strong_areas, base_weeks
#         )

#     def _generate_unique_day(self, day_number: int, week_number: int, user_goal: str, 
#                            weak_areas: List[str], strong_areas: List[str]) -> Dict:
#         """Generate a unique day with non-repetitive tasks"""
        
#         day_focuses = [
#             "Fundamental Concepts & Theory",
#             "Practical Skill Building", 
#             "Advanced Techniques & Problem Solving",
#             "Project Implementation",
#             "Review & Integration"
#         ]
        
#         focus_index = (day_number - 1) % len(day_focuses)
#         focus = day_focuses[focus_index]
        
#         day = {
#             "day_number": day_number,
#             "week_number": week_number,
#             "date": (datetime.now() + timedelta(weeks=week_number-1, days=day_number-1)).isoformat(),
#             "day_title": f"Day {day_number}: {focus}",
#             "tasks": self._generate_unique_tasks(day_number, week_number, user_goal),
#             "total_resources": 0,
#             "estimated_hours": self.daily_study_hours
#         }
        
#         day["total_resources"] = sum(len(task["resources"]) for task in day["tasks"])
#         return day

#     def _generate_unique_tasks(self, day_number: int, week_number: int, user_goal: str) -> List[Dict]:
#         """Generate unique tasks for a specific day"""
        
#         task_templates = [
#             {
#                 "type": "learning",
#                 "templates": [
#                     f"Study core concepts of {user_goal} fundamentals",
#                     f"Learn advanced techniques for {user_goal}",
#                     f"Understand theoretical principles behind {user_goal}",
#                     f"Explore different approaches to {user_goal} problems"
#                 ]
#             },
#             {
#                 "type": "practice", 
#                 "templates": [
#                     f"Hands-on exercises for {user_goal} skills",
#                     f"Solve practical problems in {user_goal}",
#                     f"Complete coding challenges for {user_goal}",
#                     f"Practice real-world {user_goal} scenarios"
#                 ]
#             },
#             {
#                 "type": "project",
#                 "templates": [
#                     f"Build a mini-project demonstrating {user_goal} concepts",
#                     f"Implement a practical {user_goal} application",
#                     f"Create a portfolio piece for {user_goal}",
#                     f"Develop a complete solution using {user_goal} skills"
#                 ]
#             }
#         ]
        
#         tasks = []
#         for i, template_group in enumerate(task_templates):
#             template_index = (day_number + week_number + i) % len(template_group["templates"])
#             task_title = template_group["templates"][template_index]
            
#             tasks.append({
#                 "title": task_title,
#                 "description": f"Day {day_number} focused activity for {user_goal} development",
#                 "resources": self._generate_contextual_resources(task_title, user_goal),
#                 "type": template_group["type"],
#                 "priority": "high" if template_group["type"] == "project" else "medium",
#                 "completed": False,
#                 "ai_generated": False
#             })
        
#         return tasks

#     def _create_unique_task(self, existing_titles: set, user_goal: str, day_number: int) -> Dict:
#         """Create a unique task that doesn't repeat existing titles"""
        
#         unique_tasks = [
#             f"Advanced practical exercise for {user_goal} day {day_number}",
#             f"Comprehensive skill drill for {user_goal} concepts",
#             f"Real-world implementation challenge for {user_goal}",
#             f"Expert-level practice session for {user_goal}",
#             f"Complex problem-solving activity for {user_goal}",
#             f"Integrated project work for {user_goal} development"
#         ]
        
#         for task_title in unique_tasks:
#             if task_title.lower() not in existing_titles:
#                 return {
#                     "title": task_title,
#                     "description": f"Unique learning activity tailored for day {day_number}",
#                     "resources": self._generate_contextual_resources(task_title, user_goal),
#                     "type": "practice",
#                     "priority": "medium",
#                     "completed": False,
#                     "ai_generated": False
#                 }
        
#         # Fallback
#         return {
#             "title": f"Specialized {user_goal} learning activity day {day_number}",
#             "description": f"Custom learning task for comprehensive skill development",
#             "resources": self._generate_contextual_resources(user_goal, user_goal),
#             "type": "learning",
#             "priority": "medium",
#             "completed": False,
#             "ai_generated": False
#         }

#     def _parse_resource_line(self, resource_line: str) -> Optional[Dict]:
#         """Parse resource line"""
#         if '|' in resource_line:
#             parts = resource_line.split('|', 1)
#             type_part = parts[0].strip()
#             url_part = parts[1].strip()
            
#             url_match = re.search(r'(https?://[^\s]+)', url_part)
#             if url_match:
#                 url = url_match.group(1)
#                 title = url_part.replace(url, '').strip() or type_part
                
#                 resource_type = self._infer_resource_type(type_part)
                
#                 return {
#                     "title": title[:100],
#                     "url": url,
#                     "type": resource_type.value,
#                     "platform": self._get_platform_name(resource_type)
#                 }
        
#         return None

#     def _infer_resource_type(self, type_hint: str) -> ResourceType:
#         """Infer resource type"""
#         hint_lower = type_hint.lower()
#         if 'youtube' in hint_lower:
#             return ResourceType.YOUTUBE
#         elif 'documentation' in hint_lower or 'docs' in hint_lower:
#             return ResourceType.DOCUMENTATION
#         elif 'practice' in hint_lower or 'exercise' in hint_lower:
#             return ResourceType.PRACTICE
#         elif 'project' in hint_lower:
#             return ResourceType.PROJECT
#         elif 'community' in hint_lower:
#             return ResourceType.COMMUNITY
#         else:
#             return ResourceType.ARTICLE

#     def _get_platform_name(self, resource_type: ResourceType) -> str:
#         """Get platform name"""
#         names = {
#             ResourceType.YOUTUBE: "YouTube",
#             ResourceType.DOCUMENTATION: "Official Docs",
#             ResourceType.ARTICLE: "Tutorial",
#             ResourceType.PRACTICE: "Practice Platform",
#             ResourceType.PROJECT: "Project Guide",
#             ResourceType.COMMUNITY: "Community",
#             ResourceType.COURSE: "Learning Platform"
#         }
#         return names.get(resource_type, "Learning Resource")

#     def _generate_contextual_resources(self, topic: str, user_goal: str) -> List[Dict]:
#         """Generate contextual resources"""
#         topic_encoded = topic.replace(' ', '+')
        
#         return [
#             {
#                 "title": f"Video Tutorials: {topic}",
#                 "url": f"https://www.youtube.com/results?search_query={topic_encoded}+tutorial",
#                 "type": ResourceType.YOUTUBE.value,
#                 "platform": "YouTube"
#             },
#             {
#                 "title": f"Official Documentation: {topic}",
#                 "url": f"https://www.google.com/search?q={topic_encoded}+documentation",
#                 "type": ResourceType.DOCUMENTATION.value,
#                 "platform": "Official Docs"
#             }
#         ]

#     def _generate_fallback_week(self, week_number: int, user_goal: str, weak_areas: List[str], 
#                               strong_areas: List[str], total_weeks: int) -> Dict:
#         """Generate fallback week when AI fails"""
#         logger.info(f"Generating fallback week {week_number}")
        
#         week = {
#             "week_number": week_number,
#             "title": f"Week {week_number}: Progressive {user_goal} Learning",
#             "overview": f"Structured learning week focusing on {user_goal} skill development",
#             "days": [],
#             "total_tasks": 0,
#             "total_resources": 0,
#             "ai_generated": False
#         }
        
#         for day_num in range(1, self.weekly_study_days + 1):
#             day = self._generate_unique_day(day_num, week_number, user_goal, weak_areas, strong_areas)
#             week["days"].append(day)
#             week["total_tasks"] += len(day["tasks"])
#             week["total_resources"] += day["total_resources"]
        
#         return week

#     def _calculate_resource_stats(self, weeks: List[Dict]) -> Dict[str, Any]:
#         """Calculate resource statistics"""
#         total_resources = 0
        
#         for week in weeks:
#             total_resources += week.get('total_resources', 0)
        
#         return {
#             "total_resources": total_resources,
#             "average_resources_per_day": total_resources / (len(weeks) * self.weekly_study_days) if weeks else 0
#         }

#     def _determine_task_type(self, title: str) -> str:
#         """Determine task type from title"""
#         title_lower = title.lower()
#         if any(word in title_lower for word in ['project', 'build', 'create', 'develop', 'implement']):
#             return "project"
#         elif any(word in title_lower for word in ['practice', 'exercise', 'solve', 'challenge']):
#             return "practice"
#         elif any(word in title_lower for word in ['review', 'revise', 'recap']):
#             return "review"
#         else:
#             return "learning"

#     def _get_proficiency_level(self, current_level: str) -> str:
#         """Map current level to proficiency"""
#         level_lower = current_level.lower()
#         if "beginner" in level_lower:
#             return "Developing"
#         elif "intermediate" in level_lower:
#             return "Proficient"
#         elif "advanced" in level_lower:
#             return "Advanced"
#         else:
#             return "Developing"

# # Global instance
# roadmap_generator = RoadmapGenerator()













# import ollama
# import re
# import json
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional, Any
# import logging
# from enum import Enum
# import asyncio
# import hashlib
# import uuid

# logger = logging.getLogger(__name__)

# class ResourceType(Enum):
#     YOUTUBE = "youtube"
#     DOCUMENTATION = "documentation"
#     ARTICLE = "article"
#     PRACTICE = "practice"
#     PROJECT = "project"
#     COMMUNITY = "community"
#     COURSE = "course"

# class RoadmapGenerator:
#     def __init__(self):
#         self.model = "llama3.1:8b"  # Default model
#         self.daily_study_hours = 2
#         self.weekly_study_days = 5
#         self._verify_model()
        
#         # Learning progression framework
#         self.learning_stages = {
#             "beginner": {
#                 "duration_ratio": 0.4,
#                 "focus_areas": ["foundations", "basic_skills", "simple_projects"],
#                 "outcomes": ["core_concepts", "basic_competency", "simple_applications"]
#             },
#             "intermediate": {
#                 "duration_ratio": 0.35,
#                 "focus_areas": ["advanced_concepts", "complex_projects", "integration"],
#                 "outcomes": ["proficient_skills", "complex_projects", "tool_mastery"]
#             },
#             "advanced": {
#                 "duration_ratio": 0.25,
#                 "focus_areas": ["expert_techniques", "optimization", "leadership"],
#                 "outcomes": ["mastery", "innovation", "mentorship"]
#             }
#         }

#     def _verify_model(self):
#         """Verify the model is available"""
#         try:
#             models = ollama.list()
#             if models.get('models'):
#                 available_models = [model.get('name', '').split(':')[0] for model in models['models']]
#                 if 'llama3.1' in available_models:
#                     self.model = "llama3.1:8b"
#                 elif 'mistral' in available_models:
#                     self.model = "mistral:7b"
#                 logger.info(f"Using model: {self.model}")
#         except Exception as e:
#             logger.warning(f"Model verification failed: {e}")

#     def _create_roadmap_prompt(self, user_data: Dict) -> str:
#         """Create a structured prompt for AI roadmap generation"""
        
#         prompt = f"""
#         Create a comprehensive, progressive learning roadmap for the following goal:

#         LEARNING OBJECTIVE:
#         - Goal: {user_data['user_goal']}
#         - Current Level: {user_data['current_level']}
#         - Target Level: {user_data['target_level']}
#         - Timeline: {user_data['total_weeks']} weeks
#         - Daily Study: {self.daily_study_hours} hours
#         - Weekly Study: {self.weekly_study_days} days

#         ASSESSMENT DATA:
#         - Score: {user_data['assessment_score']}/100
#         - Weak Areas: {', '.join(user_data['weak_areas'])}
#         - Strong Areas: {', '.join(user_data['strong_areas'])}

#         ROADMAP STRUCTURE REQUIREMENTS:

#         1. PROGRESSIVE LEARNING PATH:
#            - Weeks 1-{max(3, int(user_data['total_weeks'] * 0.3))}: Foundational concepts and basic skills
#            - Weeks {max(4, int(user_data['total_weeks'] * 0.3)+1)}-{int(user_data['total_weeks'] * 0.7)}: Intermediate skills and projects
#            - Weeks {int(user_data['total_weeks'] * 0.7)+1}-{user_data['total_weeks']}: Advanced topics and mastery

#         2. WEEKLY STRUCTURE:
#            Each week must have:
#            - Clear weekly objective
#            - 5 days of structured learning
#            - 3 unique, non-repetitive tasks per day
#            - Progressive difficulty throughout the week
#            - Practical application tasks

#         3. TASK GUIDELINES:
#            - Tasks must be specific, actionable, and measurable
#            - No repetition across weeks
#            - Include variety:理论学习, practical exercises, projects
#            - Progress from simple to complex
#            - Include weak area reinforcement

#         4. OUTPUT FORMAT:
#            Return ONLY valid JSON with this exact structure:
#            {{
#              "roadmap": {{
#                "goal": "{user_data['user_goal']}",
#                "current_level": "{user_data['current_level']}",
#                "target_level": "{user_data['target_level']}",
#                "total_weeks": {user_data['total_weeks']},
#                "weekly_schedule": [
#                  {{
#                    "week_number": 1,
#                    "title": "Week 1: [Specific Focus Area]",
#                    "overview": "Clear weekly objective",
#                    "learning_phase": "foundational|intermediate|advanced",
#                    "days": [
#                      {{
#                        "day_number": 1,
#                        "day_title": "Day 1: [Specific Daily Focus]",
#                        "tasks": [
#                          {{
#                            "title": "Unique, specific task title",
#                            "description": "Detailed task description with clear objectives",
#                            "type": "learning|practice|project",
#                            "priority": "high|medium|low",
#                            "estimated_hours": 2,
#                            "resources": [
#                              {{
#                                "title": "Relevant resource name",
#                                "type": "youtube|documentation|article|practice|project",
#                                "url": "Search query or resource link"
#                              }}
#                            ]
#                          }}
#                        ]
#                      }}
#                    ]
#                  }}
#                ]
#              }}
#            }}

#         IMPORTANT: Ensure all tasks are unique, progressively challenging, and directly aligned with the learning goal. Avoid generic tasks - be specific to {user_data['user_goal']}.
#         """

#         return prompt

#     def _calculate_adaptive_timeline(self, assessment_score: float, timeline_preference: str, 
#                                    current_level: str, target_level: str) -> int:
#         """Calculate adaptive timeline based on multiple factors"""
        
#         # Base timeline from assessment
#         if assessment_score >= 80:
#             base_weeks = 8
#         elif assessment_score >= 60:
#             base_weeks = 12
#         elif assessment_score >= 40:
#             base_weeks = 16
#         else:
#             base_weeks = 20

#         # Adjust for level progression
#         level_adjustment = {
#             "beginner-beginner": 0.8,
#             "beginner-intermediate": 1.0,
#             "beginner-advanced": 1.5,
#             "intermediate-intermediate": 0.7,
#             "intermediate-advanced": 1.0,
#             "advanced-advanced": 0.6
#         }
        
#         level_key = f"{current_level.split()[0].lower()}-{target_level.split()[0].lower()}"
#         adjustment = level_adjustment.get(level_key, 1.0)
#         base_weeks = int(base_weeks * adjustment)

#         # Timeline preference
#         if timeline_preference == "accelerated":
#             base_weeks = max(6, int(base_weeks * 0.7))
#         elif timeline_preference == "relaxed":
#             base_weeks = int(base_weeks * 1.3)

#         return max(4, min(base_weeks, 52))  # 4 weeks to 1 year limit

#     async def generate_ai_enhanced_roadmap(
#         self,
#         user_goal: str,
#         current_level: str,
#         target_level: str,
#         assessment_score: float,
#         weak_skills: List[str],
#         weak_topics: List[str],
#         strong_areas: List[str],
#         timeline_preference: str = "standard"
#     ) -> Dict:
#         """Generate AI-enhanced adaptive roadmap"""
        
#         logger.info(f"Generating AI-enhanced roadmap for: {user_goal}")

#         # Calculate adaptive timeline
#         total_weeks = self._calculate_adaptive_timeline(
#             assessment_score, timeline_preference, current_level, target_level
#         )

#         # Prepare user data for prompt
#         user_data = {
#             "user_goal": user_goal,
#             "current_level": current_level,
#             "target_level": target_level,
#             "assessment_score": assessment_score,
#             "weak_areas": weak_skills + weak_topics,
#             "strong_areas": strong_areas,
#             "total_weeks": total_weeks
#         }

#         try:
#             # Generate roadmap using AI
#             prompt = self._create_roadmap_prompt(user_data)
#             response = await self._get_ai_response(prompt)
#             roadmap_data = self._parse_ai_response(response, user_data)
            
#             # Enhance with additional metadata
#             enhanced_roadmap = self._enhance_roadmap_metadata(roadmap_data, user_data)
#             logger.info(f"Successfully generated AI-enhanced roadmap: {total_weeks} weeks")
            
#             return enhanced_roadmap

#         except Exception as e:
#             logger.error(f"AI roadmap generation failed: {e}")
#             return self._generate_structured_fallback(user_data)

#     async def _get_ai_response(self, prompt: str) -> str:
#         """Get response from AI model with error handling"""
#         try:
#             response = ollama.generate(model=self.model, prompt=prompt)
#             return response.get('response', '')
#         except Exception as e:
#             logger.error(f"AI request failed: {e}")
#             return ""

#     def _parse_ai_response(self, response: str, user_data: Dict) -> Dict:
#         """Parse AI response and extract roadmap data"""
#         try:
#             # Extract JSON from response
#             json_match = re.search(r'\{.*\}', response, re.DOTALL)
#             if json_match:
#                 roadmap_json = json_match.group()
#                 roadmap_data = json.loads(roadmap_json)
#                 return roadmap_data.get('roadmap', {})
#             else:
#                 raise ValueError("No valid JSON found in AI response")
#         except (json.JSONDecodeError, ValueError) as e:
#             logger.warning(f"AI response parsing failed: {e}")
#             return self._generate_structured_fallback(user_data)

#     def _enhance_roadmap_metadata(self, roadmap_data: Dict, user_data: Dict) -> Dict:
#         """Add comprehensive metadata to roadmap"""
        
#         start_date = datetime.now()
#         total_days = user_data['total_weeks'] * self.weekly_study_days
        
#         enhanced_roadmap = {
#             **roadmap_data,
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "version": "ai_enhanced_2.0",
#                 "total_hours": total_days * self.daily_study_hours,
#                 "daily_study_hours": self.daily_study_hours,
#                 "weekly_study_days": self.weekly_study_days,
#                 "start_date": start_date.isoformat(),
#                 "estimated_end_date": (start_date + timedelta(weeks=user_data['total_weeks'])).isoformat(),
#                 "ai_generated": True,
#                 "personalization_factors": {
#                     "weak_areas_addressed": user_data['weak_areas'],
#                     "strong_areas_leveraged": user_data['strong_areas'],
#                     "assessment_informed": user_data['assessment_score'] > 0,
#                     "timeline_optimized": True
#                 }
#             },
#             "success_metrics": self._generate_success_metrics(user_data),
#             "study_recommendations": self._generate_study_recommendations(user_data),
#             "progress_tracking": {
#                 "weekly_checkpoints": self._generate_weekly_checkpoints(user_data['total_weeks']),
#                 "milestones": self._generate_learning_milestones(user_data)
#             }
#         }
        
#         # Calculate resource statistics
#         enhanced_roadmap["resource_statistics"] = self._calculate_enhanced_stats(enhanced_roadmap)
        
#         return enhanced_roadmap

#     def _generate_structured_fallback(self, user_data: Dict) -> Dict:
#         """Generate structured fallback roadmap when AI fails"""
        
#         total_weeks = user_data['total_weeks']
#         weekly_schedule = []
        
#         # Define progressive learning phases
#         phases = [
#             (1, int(total_weeks * 0.3), "foundational", "Foundations & Basics"),
#             (int(total_weeks * 0.3) + 1, int(total_weeks * 0.7), "intermediate", "Skills & Projects"),
#             (int(total_weeks * 0.7) + 1, total_weeks, "advanced", "Mastery & Optimization")
#         ]
        
#         for week_num in range(1, total_weeks + 1):
#             # Determine current phase
#             current_phase = next((phase for start, end, phase_name, desc in phases 
#                                 if start <= week_num <= end), "foundational")
            
#             week_data = self._create_progressive_week(week_num, user_data, current_phase)
#             weekly_schedule.append(week_data)
        
#         return {
#             "goal": user_data['user_goal'],
#             "current_level": user_data['current_level'],
#             "target_level": user_data['target_level'],
#             "total_weeks": total_weeks,
#             "weekly_schedule": weekly_schedule,
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "version": "structured_fallback_2.0",
#                 "ai_generated": False,
#                 "fallback_used": True
#             }
#         }

#     def _create_progressive_week(self, week_num: int, user_data: Dict, phase: str) -> Dict:
#         """Create a progressive learning week"""
        
#         phase_focus = {
#             "foundational": f"Master {user_data['user_goal']} Fundamentals",
#             "intermediate": f"Develop {user_data['user_goal']} Practical Skills", 
#             "advanced": f"Achieve {user_data['user_goal']} Mastery"
#         }
        
#         week = {
#             "week_number": week_num,
#             "title": f"Week {week_num}: {phase_focus.get(phase, 'Progressive Learning')}",
#             "overview": self._generate_week_overview(week_num, user_data, phase),
#             "learning_phase": phase,
#             "days": []
#         }
        
#         # Create unique days with progressive tasks
#         for day_num in range(1, self.weekly_study_days + 1):
#             day_data = self._create_progressive_day(day_num, week_num, user_data, phase)
#             week["days"].append(day_data)
        
#         return week

#     def _create_progressive_day(self, day_num: int, week_num: int, user_data: Dict, phase: str) -> Dict:
#         """Create a progressive learning day"""
        
#         day_focus = {
#             1: "Core Concepts & Theory",
#             2: "Practical Application", 
#             3: "Skill Development",
#             4: "Project Work & Integration",
#             5: "Review & Reinforcement"
#         }
        
#         return {
#             "day_number": day_num,
#             "day_title": f"Day {day_num}: {day_focus.get(day_num, 'Structured Learning')}",
#             "tasks": self._generate_progressive_tasks(day_num, week_num, user_data, phase),
#             "estimated_hours": self.daily_study_hours
#         }

#     def _generate_progressive_tasks(self, day_num: int, week_num: int, user_data: Dict, phase: str) -> List[Dict]:
#         """Generate progressive, non-repetitive tasks"""
        
#         task_templates = {
#             "foundational": [
#                 {
#                     "type": "learning",
#                     "template": "Study {topic} fundamental concepts: {specific_aspect}",
#                     "priority": "high"
#                 },
#                 {
#                     "type": "practice", 
#                     "template": "Practice basic {topic} skills through {exercise_type}",
#                     "priority": "medium"
#                 },
#                 {
#                     "type": "project",
#                     "template": "Build simple {topic} application demonstrating {concept}",
#                     "priority": "low"
#                 }
#             ],
#             "intermediate": [
#                 {
#                     "type": "learning",
#                     "template": "Master advanced {topic} techniques: {advanced_concept}",
#                     "priority": "medium"
#                 },
#                 {
#                     "type": "practice",
#                     "template": "Solve complex {topic} problems using {methodology}",
#                     "priority": "high"
#                 },
#                 {
#                     "type": "project",
#                     "template": "Develop intermediate {topic} project with {features}",
#                     "priority": "high"
#                 }
#             ],
#             "advanced": [
#                 {
#                     "type": "learning", 
#                     "template": "Research cutting-edge {topic} methodologies: {innovation}",
#                     "priority": "medium"
#                 },
#                 {
#                     "type": "practice",
#                     "template": "Optimize {topic} performance through {optimization_technique}",
#                     "priority": "high"
#                 },
#                 {
#                     "type": "project",
#                     "template": "Architect complex {topic} system implementing {architecture}",
#                     "priority": "high"
#                 }
#             ]
#         }
        
#         templates = task_templates.get(phase, task_templates["foundational"])
#         tasks = []
        
#         for i, template in enumerate(templates):
#             task_id = f"week{week_num}_day{day_num}_task{i+1}"
#             task_title = self._generate_unique_task_title(template, user_data, week_num, day_num)
            
#             tasks.append({
#                 "title": task_title,
#                 "description": self._enhance_task_description(task_title, user_data, phase),
#                 "type": template["type"],
#                 "priority": template["priority"],
#                 "estimated_hours": self.daily_study_hours / len(templates),
#                 "resources": self._generate_contextual_resources(task_title, user_data, phase),
#                 "task_id": task_id
#             })
        
#         return tasks

#     def _generate_unique_task_title(self, template: Dict, user_data: Dict, week_num: int, day_num: int) -> str:
#         """Generate unique task title using multiple factors"""
        
#         topic = user_data['user_goal']
#         aspects = {
#             "specific_aspect": ["core principles", "fundamental theories", "basic components", "essential elements"],
#             "exercise_type": ["hands-on exercises", "practical drills", "skill challenges", "application practice"],
#             "concept": ["core functionality", "basic operations", "simple workflows", "foundational patterns"],
#             "advanced_concept": ["complex patterns", "advanced methodologies", "sophisticated techniques", "expert approaches"],
#             "methodology": ["systematic approaches", "structured methods", "proven techniques", "best practices"],
#             "features": ["multiple components", "integrated systems", "complex functionality", "advanced capabilities"],
#             "innovation": ["emerging trends", "innovative approaches", "cutting-edge methods", "advanced paradigms"],
#             "optimization_technique": ["performance tuning", "efficiency improvements", "scalability enhancements", "optimization strategies"],
#             "architecture": ["scalable design", "robust architecture", "enterprise patterns", "production-ready structure"]
#         }
        
#         template_text = template["template"]
#         for key, options in aspects.items():
#             if f"{{{key}}}" in template_text:
#                 chosen_option = options[(week_num + day_num) % len(options)]
#                 template_text = template_text.replace(f"{{{key}}}", chosen_option)
        
#         return template_text.format(topic=topic)

#     def _enhance_task_description(self, task_title: str, user_data: Dict, phase: str) -> str:
#         """Create detailed task description"""
        
#         descriptions = {
#             "foundational": "Build solid understanding of core concepts through structured learning and practice.",
#             "intermediate": "Develop practical skills and apply knowledge to real-world scenarios and projects.", 
#             "advanced": "Master complex topics and optimize solutions for professional-level applications."
#         }
        
#         base_desc = descriptions.get(phase, "Structured learning activity for skill development.")
#         return f"{task_title}. {base_desc} Focus on progressive mastery and practical application."

#     def _generate_contextual_resources(self, task_title: str, user_data: Dict, phase: str) -> List[Dict]:
#         """Generate contextual learning resources"""
        
#         topic_encoded = task_title.replace(' ', '+')
#         resources = []
        
#         # Base resources for all phases
#         base_resources = [
#             {
#                 "title": f"Comprehensive Tutorial: {task_title}",
#                 "type": ResourceType.YOUTUBE.value,
#                 "url": f"https://youtube.com/results?search_query={topic_encoded}+tutorial+guide"
#             },
#             {
#                 "title": f"Official Documentation: {task_title}",
#                 "type": ResourceType.DOCUMENTATION.value, 
#                 "url": f"https://google.com/search?q={topic_encoded}+official+documentation"
#             }
#         ]
        
#         resources.extend(base_resources)
        
#         # Phase-specific additional resources
#         if phase == "foundational":
#             resources.append({
#                 "title": f"Beginner Exercises: {task_title}",
#                 "type": ResourceType.PRACTICE.value,
#                 "url": f"https://google.com/search?q={topic_encoded}+beginner+exercises+practice"
#             })
#         elif phase == "intermediate":
#             resources.append({
#                 "title": f"Project Guide: {task_title}",
#                 "type": ResourceType.PROJECT.value,
#                 "url": f"https://google.com/search?q={topic_encoded}+project+guide+tutorial"
#             })
#         else:  # advanced
#             resources.append({
#                 "title": f"Advanced Techniques: {task_title}",
#                 "type": ResourceType.ARTICLE.value,
#                 "url": f"https://google.com/search?q={topic_encoded}+advanced+techniques+best+practices"
#             })
        
#         return resources

#     def _generate_week_overview(self, week_num: int, user_data: Dict, phase: str) -> str:
#         """Generate contextual week overview"""
        
#         overviews = {
#             "foundational": f"Week {week_num}: Establish strong foundation in {user_data['user_goal']} core concepts and basic principles.",
#             "intermediate": f"Week {week_num}: Develop practical {user_data['user_goal']} skills through hands-on projects and complex problem-solving.",
#             "advanced": f"Week {week_num}: Master advanced {user_data['user_goal']} techniques and optimize solutions for professional applications."
#         }
        
#         return overviews.get(phase, f"Week {week_num}: Progressive learning and skill development in {user_data['user_goal']}.")

#     def _generate_success_metrics(self, user_data: Dict) -> List[str]:
#         """Generate success metrics for the roadmap"""
#         return [
#             f"Complete {user_data['total_weeks']} weeks of structured learning",
#             f"Achieve {user_data['target_level']} proficiency in {user_data['user_goal']}",
#             f"Master {len(user_data['weak_areas'])} identified weak areas",
#             "Build comprehensive project portfolio demonstrating skills",
#             "Develop ability to solve complex problems independently"
#         ]

#     def _generate_study_recommendations(self, user_data: Dict) -> Dict:
#         """Generate study recommendations"""
#         return {
#             "weekly_commitment": f"{self.weekly_study_days} days × {self.daily_study_hours} hours",
#             "learning_approach": "Progressive skill development with practical application",
#             "review_strategy": "Weekly review sessions and project-based assessment",
#             "resource_utilization": "Combine tutorials, documentation, and hands-on practice"
#         }

#     def _generate_weekly_checkpoints(self, total_weeks: int) -> List[Dict]:
#         """Generate weekly progress checkpoints"""
#         checkpoints = []
#         for week in range(1, total_weeks + 1):
#             checkpoints.append({
#                 "week": week,
#                 "checkpoint": f"Week {week} progress review and skill assessment",
#                 "assessment_focus": "Concept mastery and practical application"
#             })
#         return checkpoints

#     def _generate_learning_milestones(self, user_data: Dict) -> List[Dict]:
#         """Generate key learning milestones"""
#         total_weeks = user_data['total_weeks']
#         return [
#             {
#                 "milestone": "Foundation Complete",
#                 "week": max(1, int(total_weeks * 0.25)),
#                 "description": f"Mastered basic {user_data['user_goal']} concepts and principles"
#             },
#             {
#                 "milestone": "Intermediate Proficiency", 
#                 "week": max(2, int(total_weeks * 0.5)),
#                 "description": f"Developed practical {user_data['user_goal']} skills and project capabilities"
#             },
#             {
#                 "milestone": "Advanced Mastery",
#                 "week": max(3, int(total_weeks * 0.75)),
#                 "description": f"Achieved expert-level {user_data['user_goal']} proficiency and optimization skills"
#             },
#             {
#                 "milestone": "Goal Achievement",
#                 "week": total_weeks,
#                 "description": f"Completed {user_data['target_level']} level in {user_data['user_goal']}"
#             }
#         ]

#     def _calculate_enhanced_stats(self, roadmap: Dict) -> Dict[str, Any]:
#         """Calculate enhanced resource statistics"""
#         total_tasks = 0
#         total_resources = 0
        
#         for week in roadmap.get('weekly_schedule', []):
#             for day in week.get('days', []):
#                 total_tasks += len(day.get('tasks', []))
#                 for task in day.get('tasks', []):
#                     total_resources += len(task.get('resources', []))
        
#         total_days = len(roadmap.get('weekly_schedule', [])) * self.weekly_study_days
        
#         return {
#             "total_tasks": total_tasks,
#             "total_resources": total_resources,
#             "average_tasks_per_day": total_tasks / total_days if total_days > 0 else 0,
#             "average_resources_per_task": total_resources / total_tasks if total_tasks > 0 else 0,
#             "total_learning_hours": total_days * self.daily_study_hours
#         }

# # Global instance
# roadmap_generator = RoadmapGenerator()











# import ollama
# import re
# import json
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional, Any
# import logging
# from enum import Enum
# import asyncio
# import hashlib
# import uuid

# logger = logging.getLogger(__name__)

# class ResourceType(Enum):
#     YOUTUBE = "youtube"
#     DOCUMENTATION = "documentation"
#     ARTICLE = "article"
#     PRACTICE = "practice"
#     PROJECT = "project"
#     COMMUNITY = "community"
#     COURSE = "course"

# class RoadmapGenerator:
#     def __init__(self):
#         self.model = "llama3.1:8b"  # Default model
#         self.daily_study_hours = 2
#         self.weekly_study_days = 5
#         self._verify_model()
        
#         # Enhanced learning progression framework
#         self.learning_stages = {
#             "beginner": {
#                 "duration_ratio": 0.4,
#                 "focus_areas": ["foundations", "basic_skills", "simple_projects"],
#                 "outcomes": ["core_concepts", "basic_competency", "simple_applications"]
#             },
#             "intermediate": {
#                 "duration_ratio": 0.35,
#                 "focus_areas": ["advanced_concepts", "complex_projects", "integration"],
#                 "outcomes": ["proficient_skills", "complex_projects", "tool_mastery"]
#             },
#             "advanced": {
#                 "duration_ratio": 0.25,
#                 "focus_areas": ["expert_techniques", "optimization", "leadership"],
#                 "outcomes": ["mastery", "innovation", "mentorship"]
#             }
#         }

#         # Task uniqueness tracking
#         self.generated_tasks = set()

#     def _verify_model(self):
#         """Verify the model is available"""
#         try:
#             models = ollama.list()
#             if models.get('models'):
#                 available_models = [model.get('name', '').split(':')[0] for model in models['models']]
#                 if 'llama3.1' in available_models:
#                     self.model = "llama3.1:8b"
#                 elif 'mistral' in available_models:
#                     self.model = "mistral:7b"
#                 logger.info(f"Using model: {self.model}")
#         except Exception as e:
#             logger.warning(f"Model verification failed: {e}")

#     def _create_roadmap_prompt(self, user_data: Dict) -> str:
#         """Create a structured prompt for AI roadmap generation with uniqueness enforcement"""
        
#         prompt = f"""
#         Create a comprehensive, progressive learning roadmap for the following goal:

#         LEARNING OBJECTIVE:
#         - Goal: {user_data['user_goal']}
#         - Current Level: {user_data['current_level']}
#         - Target Level: {user_data['target_level']}
#         - Timeline: {user_data['total_weeks']} weeks
#         - Daily Study: {self.daily_study_hours} hours
#         - Weekly Study: {self.weekly_study_days} days

#         ASSESSMENT DATA:
#         - Score: {user_data['assessment_score']}/100
#         - Weak Areas: {', '.join(user_data['weak_areas'])}
#         - Strong Areas: {', '.join(user_data['strong_areas'])}

#         CRITICAL REQUIREMENTS FOR UNIQUE TASKS:

#         1. ABSOLUTELY NO REPETITIVE TASKS across weeks or days
#         2. Each task must be completely unique in content and focus
#         3. Progressively build skills from basic to advanced
#         4. Focus on weak areas: {', '.join(user_data['weak_areas'])}
#         5. Leverage strong areas: {', '.join(user_data['strong_areas'])}

#         ROADMAP STRUCTURE:

#         1. PROGRESSIVE LEARNING PATH:
#            - Weeks 1-{max(3, int(user_data['total_weeks'] * 0.3))}: Foundational concepts and basic skills
#            - Weeks {max(4, int(user_data['total_weeks'] * 0.3)+1)}-{int(user_data['total_weeks'] * 0.7)}: Intermediate skills and projects
#            - Weeks {int(user_data['total_weeks'] * 0.7)+1}-{user_data['total_weeks']}: Advanced topics and mastery

#         2. WEEKLY STRUCTURE:
#            Each week must have:
#            - Clear weekly objective
#            - 5 days of structured learning
#            - 3 unique, non-repetitive tasks per day
#            - Progressive difficulty throughout the week
#            - Practical application tasks

#         3. TASK UNIQUENESS ENFORCEMENT:
#            - NO repeated task titles or concepts across entire roadmap
#            - Each task must build upon previous learning
#            - Include specific weak area reinforcement: {', '.join(user_data['weak_areas'])}
#            - Tasks should be specific to {user_data['user_goal']}
#            - Use different learning modalities each day

#         4. TASK VARIETY PATTERNS:
#            Day 1: Theory & Concepts
#            Day 2: Practical Implementation  
#            Day 3: Problem Solving
#            Day 4: Project Work
#            Day 5: Review & Integration

#         5. OUTPUT FORMAT:
#            Return ONLY valid JSON with this exact structure:
#            {{
#              "roadmap": {{
#                "goal": "{user_data['user_goal']}",
#                "current_level": "{user_data['current_level']}",
#                "target_level": "{user_data['target_level']}",
#                "total_weeks": {user_data['total_weeks']},
#                "total_days": {user_data['total_weeks'] * self.weekly_study_days},
#                "total_hours": {user_data['total_weeks'] * self.weekly_study_days * self.daily_study_hours},
#                "weekly_schedule": [
#                  {{
#                    "week_number": 1,
#                    "title": "Week 1: [Specific Unique Focus Area]",
#                    "overview": "Clear weekly objective focusing on unique aspects",
#                    "learning_phase": "foundational|intermediate|advanced",
#                    "total_tasks": 15,
#                    "days": [
#                      {{
#                        "day_number": 1,
#                        "day_title": "Day 1: [Unique Daily Focus]",
#                        "date": "2024-01-01",
#                        "tasks": [
#                          {{
#                            "title": "UNIQUE: Specific task title that hasn't appeared before",
#                            "description": "Detailed task description with clear objectives and unique approach",
#                            "type": "learning|practice|project|review",
#                            "priority": "high|medium|low",
#                            "estimated_hours": {self.daily_study_hours / 3},
#                            "ai_generated": true,
#                            "unique_id": "hash_value",
#                            "resources": [
#                              {{
#                                "title": "Relevant resource name",
#                                "type": "youtube|documentation|article|practice|project",
#                                "url": "Search query or resource link",
#                                "platform": "YouTube|Official Docs|Blog|Practice Platform"
#                              }}
#                            ]
#                          }}
#                        ]
#                      }}
#                    ]
#                  }}
#                ]
#              }}
#            }}

#         IMPORTANT: 
#         - Generate completely unique tasks for each day across all weeks
#         - Focus on weak areas: {', '.join(user_data['weak_areas'])}
#         - Ensure progressive skill building
#         - Avoid generic tasks - be extremely specific to {user_data['user_goal']}
#         - Include practical applications and projects
#         - No task repetition allowed
#         """

#         return prompt

#     def _calculate_adaptive_timeline(self, assessment_score: float, timeline_preference: str, 
#                                    current_level: str, target_level: str) -> int:
#         """Calculate adaptive timeline based on multiple factors"""
        
#         # Base timeline from assessment
#         if assessment_score >= 80:
#             base_weeks = 8
#         elif assessment_score >= 60:
#             base_weeks = 12
#         elif assessment_score >= 40:
#             base_weeks = 16
#         else:
#             base_weeks = 20

#         # Adjust for level progression
#         level_adjustment = {
#             "beginner-beginner": 0.8,
#             "beginner-intermediate": 1.0,
#             "beginner-advanced": 1.5,
#             "intermediate-intermediate": 0.7,
#             "intermediate-advanced": 1.0,
#             "advanced-advanced": 0.6
#         }
        
#         level_key = f"{current_level.split()[0].lower()}-{target_level.split()[0].lower()}"
#         adjustment = level_adjustment.get(level_key, 1.0)
#         base_weeks = int(base_weeks * adjustment)

#         # Timeline preference
#         if timeline_preference == "accelerated":
#             base_weeks = max(6, int(base_weeks * 0.7))
#         elif timeline_preference == "relaxed":
#             base_weeks = int(base_weeks * 1.3)

#         return max(4, min(base_weeks, 52))  # 4 weeks to 1 year limit

#     async def generate_ai_enhanced_roadmap(
#         self,
#         user_goal: str,
#         current_level: str,
#         target_level: str,
#         assessment_score: float,
#         weak_skills: List[str],
#         weak_topics: List[str],
#         strong_areas: List[str],
#         timeline_preference: str = "standard"
#     ) -> Dict:
#         """Generate AI-enhanced adaptive roadmap with guaranteed unique tasks"""
        
#         logger.info(f"Generating AI-enhanced roadmap for: {user_goal}")
        
#         # Reset task tracking for new generation
#         self.generated_tasks = set()

#         # Calculate adaptive timeline
#         total_weeks = self._calculate_adaptive_timeline(
#             assessment_score, timeline_preference, current_level, target_level
#         )

#         # Prepare user data for prompt
#         user_data = {
#             "user_goal": user_goal,
#             "current_level": current_level,
#             "target_level": target_level,
#             "assessment_score": assessment_score,
#             "weak_areas": weak_skills + weak_topics,
#             "strong_areas": strong_areas,
#             "total_weeks": total_weeks
#         }

#         try:
#             # Generate roadmap using AI
#             prompt = self._create_roadmap_prompt(user_data)
#             response = await self._get_ai_response(prompt)
#             roadmap_data = self._parse_ai_response(response, user_data)
            
#             # Post-process to ensure uniqueness
#             roadmap_data = self._ensure_task_uniqueness(roadmap_data)
            
#             # Enhance with additional metadata
#             enhanced_roadmap = self._enhance_roadmap_metadata(roadmap_data, user_data)
            
#             # Calculate uniqueness metrics
#             uniqueness_metrics = self._calculate_uniqueness_metrics(enhanced_roadmap)
#             enhanced_roadmap["uniqueness_metrics"] = uniqueness_metrics
            
#             logger.info(f"Successfully generated AI-enhanced roadmap: {total_weeks} weeks, {uniqueness_metrics['unique_tasks']} unique tasks")
            
#             return enhanced_roadmap

#         except Exception as e:
#             logger.error(f"AI roadmap generation failed: {e}")
#             return self._generate_structured_fallback(user_data)

#     async def _get_ai_response(self, prompt: str) -> str:
#         """Get response from AI model with error handling"""
#         try:
#             response = ollama.generate(model=self.model, prompt=prompt)
#             return response.get('response', '')
#         except Exception as e:
#             logger.error(f"AI request failed: {e}")
#             return ""

#     def _parse_ai_response(self, response: str, user_data: Dict) -> Dict:
#         """Parse AI response and extract roadmap data"""
#         try:
#             # Extract JSON from response
#             json_match = re.search(r'\{.*\}', response, re.DOTALL)
#             if json_match:
#                 roadmap_json = json_match.group()
#                 roadmap_data = json.loads(roadmap_json)
#                 roadmap_data = roadmap_data.get('roadmap', {})
                
#                 # Add unique IDs to tasks
#                 roadmap_data = self._add_unique_task_ids(roadmap_data)
#                 return roadmap_data
#             else:
#                 raise ValueError("No valid JSON found in AI response")
#         except (json.JSONDecodeError, ValueError) as e:
#             logger.warning(f"AI response parsing failed: {e}")
#             return self._generate_structured_fallback(user_data)

#     def _add_unique_task_ids(self, roadmap_data: Dict) -> Dict:
#         """Add unique IDs to all tasks"""
#         for week in roadmap_data.get('weekly_schedule', []):
#             for day in week.get('days', []):
#                 for task in day.get('tasks', []):
#                     task_hash = hashlib.md5(task['title'].encode()).hexdigest()[:8]
#                     task['unique_id'] = f"task_{task_hash}"
#                     task['ai_generated'] = True
#         return roadmap_data

#     def _ensure_task_uniqueness(self, roadmap_data: Dict) -> Dict:
#         """Ensure all tasks are unique across the entire roadmap"""
#         seen_tasks = set()
#         unique_roadmap = {"weekly_schedule": []}
        
#         for week in roadmap_data.get('weekly_schedule', []):
#             unique_week = week.copy()
#             unique_week['days'] = []
            
#             for day in week.get('days', []):
#                 unique_day = day.copy()
#                 unique_day['tasks'] = []
                
#                 for task in day.get('tasks', []):
#                     task_key = task['title'].lower().strip()
                    
#                     # If task is unique, add it
#                     if task_key not in seen_tasks:
#                         seen_tasks.add(task_key)
#                         unique_day['tasks'].append(task)
#                     else:
#                         # Generate replacement for duplicate task
#                         replacement = self._generate_unique_replacement_task(
#                             task, seen_tasks, week['week_number'], day['day_number']
#                         )
#                         if replacement:
#                             unique_day['tasks'].append(replacement)
                
#                 unique_week['days'].append(unique_day)
            
#             unique_roadmap['weekly_schedule'].append(unique_week)
        
#         return {**roadmap_data, **unique_roadmap}

#     def _generate_unique_replacement_task(self, original_task: Dict, seen_tasks: set, week: int, day: int) -> Optional[Dict]:
#         """Generate a unique replacement task"""
#         base_title = original_task['title']
#         for i in range(5):  # Try 5 different variations
#             variation = f"{base_title} - Variation {i+1} for Week {week} Day {day}"
#             if variation.lower() not in seen_tasks:
#                 seen_tasks.add(variation.lower())
#                 new_task = original_task.copy()
#                 new_task['title'] = variation
#                 new_task['unique_id'] = f"task_{hashlib.md5(variation.encode()).hexdigest()[:8]}"
#                 new_task['ai_generated'] = True
#                 return new_task
#         return None

#     def _calculate_uniqueness_metrics(self, roadmap: Dict) -> Dict[str, Any]:
#         """Calculate task uniqueness metrics"""
#         all_tasks = []
#         task_titles = set()
#         duplicate_count = 0
        
#         for week in roadmap.get('weekly_schedule', []):
#             for day in week.get('days', []):
#                 for task in day.get('tasks', []):
#                     all_tasks.append(task)
#                     title_lower = task['title'].lower().strip()
#                     if title_lower in task_titles:
#                         duplicate_count += 1
#                     else:
#                         task_titles.add(title_lower)
        
#         return {
#             "total_tasks": len(all_tasks),
#             "unique_tasks": len(task_titles),
#             "duplicate_count": duplicate_count,
#             "uniqueness_percentage": (len(task_titles) / len(all_tasks) * 100) if all_tasks else 100
#         }

#     def _enhance_roadmap_metadata(self, roadmap_data: Dict, user_data: Dict) -> Dict:
#         """Add comprehensive metadata to roadmap"""
        
#         start_date = datetime.now()
#         total_days = user_data['total_weeks'] * self.weekly_study_days
        
#         enhanced_roadmap = {
#             **roadmap_data,
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "version": "ai_enhanced_3.0",
#                 "total_hours": total_days * self.daily_study_hours,
#                 "daily_study_hours": self.daily_study_hours,
#                 "weekly_study_days": self.weekly_study_days,
#                 "start_date": start_date.isoformat(),
#                 "estimated_end_date": (start_date + timedelta(weeks=user_data['total_weeks'])).isoformat(),
#                 "ai_generated": True,
#                 "personalization_factors": {
#                     "weak_areas_addressed": user_data['weak_areas'],
#                     "strong_areas_leveraged": user_data['strong_areas'],
#                     "assessment_informed": user_data['assessment_score'] > 0,
#                     "timeline_optimized": True
#                 }
#             },
#             "success_metrics": self._generate_success_metrics(user_data),
#             "study_recommendations": self._generate_study_recommendations(user_data),
#             "progress_tracking": {
#                 "weekly_checkpoints": self._generate_weekly_checkpoints(user_data['total_weeks']),
#                 "milestones": self._generate_learning_milestones(user_data)
#             }
#         }
        
#         # Calculate resource statistics
#         enhanced_roadmap["resource_statistics"] = self._calculate_enhanced_stats(enhanced_roadmap)
        
#         return enhanced_roadmap

#     def _generate_structured_fallback(self, user_data: Dict) -> Dict:
#         """Generate structured fallback roadmap when AI fails"""
        
#         total_weeks = user_data['total_weeks']
#         weekly_schedule = []
        
#         # Reset task tracking
#         self.generated_tasks = set()
        
#         # Define progressive learning phases
#         phases = [
#             (1, int(total_weeks * 0.3), "foundational", "Foundations & Basics"),
#             (int(total_weeks * 0.3) + 1, int(total_weeks * 0.7), "intermediate", "Skills & Projects"),
#             (int(total_weeks * 0.7) + 1, total_weeks, "advanced", "Mastery & Optimization")
#         ]
        
#         for week_num in range(1, total_weeks + 1):
#             # Determine current phase
#             current_phase = next((phase_name for start, end, phase_name, desc in phases 
#                                 if start <= week_num <= end), "foundational")
            
#             week_data = self._create_progressive_week(week_num, user_data, current_phase)
#             weekly_schedule.append(week_data)
        
#         roadmap_data = {
#             "goal": user_data['user_goal'],
#             "current_level": user_data['current_level'],
#             "target_level": user_data['target_level'],
#             "total_weeks": total_weeks,
#             "total_days": total_weeks * self.weekly_study_days,
#             "total_hours": total_weeks * self.weekly_study_days * self.daily_study_hours,
#             "weekly_schedule": weekly_schedule,
#             "metadata": {
#                 "generated_at": datetime.now().isoformat(),
#                 "version": "structured_fallback_3.0",
#                 "ai_generated": False,
#                 "fallback_used": True
#             }
#         }
        
#         # Calculate uniqueness metrics for fallback
#         roadmap_data["uniqueness_metrics"] = self._calculate_uniqueness_metrics(roadmap_data)
        
#         return roadmap_data

#     def _create_progressive_week(self, week_num: int, user_data: Dict, phase: str) -> Dict:
#         """Create a progressive learning week with guaranteed unique tasks"""
        
#         phase_focus = {
#             "foundational": f"Master {user_data['user_goal']} Fundamentals",
#             "intermediate": f"Develop {user_data['user_goal']} Practical Skills", 
#             "advanced": f"Achieve {user_data['user_goal']} Mastery"
#         }
        
#         week = {
#             "week_number": week_num,
#             "title": f"Week {week_num}: {phase_focus.get(phase, 'Progressive Learning')}",
#             "overview": self._generate_week_overview(week_num, user_data, phase),
#             "learning_phase": phase,
#             "days": []
#         }
        
#         # Create unique days with progressive tasks
#         for day_num in range(1, self.weekly_study_days + 1):
#             day_data = self._create_progressive_day(day_num, week_num, user_data, phase)
#             week["days"].append(day_data)
        
#         # Calculate week statistics
#         week["total_tasks"] = sum(len(day.get("tasks", [])) for day in week["days"])
        
#         return week

#     def _create_progressive_day(self, day_num: int, week_num: int, user_data: Dict, phase: str) -> Dict:
#         """Create a progressive learning day with unique tasks"""
        
#         day_focus = {
#             1: "Core Concepts & Theory",
#             2: "Practical Application", 
#             3: "Skill Development",
#             4: "Project Work & Integration",
#             5: "Review & Reinforcement"
#         }
        
#         # Calculate date
#         start_date = datetime.now()
#         day_offset = (week_num - 1) * self.weekly_study_days + (day_num - 1)
#         day_date = start_date + timedelta(days=day_offset)
        
#         return {
#             "day_number": day_num,
#             "day_title": f"Day {day_num}: {day_focus.get(day_num, 'Structured Learning')}",
#             "date": day_date.strftime("%Y-%m-%d"),
#             "tasks": self._generate_progressive_tasks(day_num, week_num, user_data, phase),
#             "estimated_hours": self.daily_study_hours
#         }

#     def _generate_progressive_tasks(self, day_num: int, week_num: int, user_data: Dict, phase: str) -> List[Dict]:
#         """Generate progressive, non-repetitive tasks"""
        
#         task_templates = self._get_task_templates(phase, day_num)
#         tasks = []
        
#         for i, template in enumerate(task_templates):
#             task_title = self._generate_unique_task_title(template, user_data, week_num, day_num, i)
            
#             # Ensure uniqueness
#             task_key = task_title.lower().strip()
#             if task_key in self.generated_tasks:
#                 # Generate alternative if duplicate
#                 for attempt in range(3):
#                     alternative_title = f"{task_title} - Week {week_num} Day {day_num}"
#                     if alternative_title.lower() not in self.generated_tasks:
#                         task_title = alternative_title
#                         break
            
#             self.generated_tasks.add(task_title.lower().strip())
            
#             task_id = f"week{week_num}_day{day_num}_task{i+1}"
#             task_hash = hashlib.md5(task_title.encode()).hexdigest()[:8]
            
#             tasks.append({
#                 "title": task_title,
#                 "description": self._enhance_task_description(task_title, user_data, phase, week_num, day_num),
#                 "type": template["type"],
#                 "priority": template["priority"],
#                 "estimated_hours": self.daily_study_hours / len(task_templates),
#                 "ai_generated": True,
#                 "unique_id": f"task_{task_hash}",
#                 "resources": self._generate_contextual_resources(task_title, user_data, phase),
#                 "task_id": task_id
#             })
        
#         return tasks

#     def _get_task_templates(self, phase: str, day_num: int) -> List[Dict]:
#         """Get task templates based on phase and day number"""
        
#         foundational_templates = [
#             {
#                 "type": "learning",
#                 "template": "Study {topic} fundamental concepts: {specific_aspect}",
#                 "priority": "high"
#             },
#             {
#                 "type": "practice", 
#                 "template": "Practice basic {topic} skills through {exercise_type}",
#                 "priority": "medium"
#             },
#             {
#                 "type": "project",
#                 "template": "Build simple {topic} application demonstrating {concept}",
#                 "priority": "low"
#             }
#         ]
        
#         intermediate_templates = [
#             {
#                 "type": "learning",
#                 "template": "Master advanced {topic} techniques: {advanced_concept}",
#                 "priority": "medium"
#             },
#             {
#                 "type": "practice",
#                 "template": "Solve complex {topic} problems using {methodology}",
#                 "priority": "high"
#             },
#             {
#                 "type": "project",
#                 "template": "Develop intermediate {topic} project with {features}",
#                 "priority": "high"
#             }
#         ]
        
#         advanced_templates = [
#             {
#                 "type": "learning", 
#                 "template": "Research cutting-edge {topic} methodologies: {innovation}",
#                 "priority": "medium"
#             },
#             {
#                 "type": "practice",
#                 "template": "Optimize {topic} performance through {optimization_technique}",
#                 "priority": "high"
#             },
#             {
#                 "type": "project",
#                 "template": "Architect complex {topic} system implementing {architecture}",
#                 "priority": "high"
#             }
#         ]
        
#         # Select templates based on phase
#         if phase == "foundational":
#             return foundational_templates
#         elif phase == "intermediate":
#             return intermediate_templates
#         else:
#             return advanced_templates

#     def _generate_unique_task_title(self, template: Dict, user_data: Dict, week_num: int, day_num: int, task_index: int) -> str:
#         """Generate unique task title using multiple factors"""
        
#         topic = user_data['user_goal']
#         weak_areas = user_data['weak_areas']
#         strong_areas = user_data['strong_areas']
        
#         # Enhanced aspect variations with weak/strong area integration
#         aspects = {
#             "specific_aspect": [
#                 "core principles and fundamentals",
#                 "basic components and architecture", 
#                 "essential elements and workflows",
#                 "fundamental theories and concepts",
#                 "key building blocks and patterns",
#                 *[f"{area} fundamentals" for area in weak_areas[:2]]
#             ],
#             "exercise_type": [
#                 "hands-on practical exercises",
#                 "skill-building drills and challenges", 
#                 "real-world application practice",
#                 "interactive learning activities",
#                 "problem-solving scenarios",
#                 *[f"{area} practice exercises" for area in weak_areas[:2]]
#             ],
#             "concept": [
#                 "core functionality and operations",
#                 "basic workflows and processes",
#                 "simple patterns and structures",
#                 "foundational algorithms and methods",
#                 "elementary applications and use cases",
#                 *[f"{area} core concepts" for area in strong_areas[:2]]
#             ],
#             "advanced_concept": [
#                 "complex patterns and architectures",
#                 "advanced methodologies and techniques", 
#                 "sophisticated algorithms and optimizations",
#                 "expert-level approaches and strategies",
#                 "enterprise-grade solutions and designs",
#                 *[f"advanced {area} techniques" for area in weak_areas[:2]]
#             ],
#             "methodology": [
#                 "systematic problem-solving approaches",
#                 "structured development methodologies", 
#                 "proven implementation techniques",
#                 "best practices and industry standards",
#                 "agile development processes",
#                 *[f"{area} specific methodologies" for area in strong_areas[:2]]
#             ],
#             "features": [
#                 "multiple integrated components",
#                 "complex functionality and capabilities",
#                 "advanced system features", 
#                 "comprehensive application modules",
#                 "enterprise-level functionality",
#                 *[f"{area} integration features" for area in weak_areas[:2]]
#             ],
#             "innovation": [
#                 "emerging trends and technologies",
#                 "innovative approaches and paradigms", 
#                 "cutting-edge methods and tools",
#                 "advanced optimization techniques",
#                 "next-generation solutions",
#                 *[f"{area} innovation areas" for area in strong_areas[:2]]
#             ],
#             "optimization_technique": [
#                 "performance tuning and optimization",
#                 "efficiency improvements and scaling", 
#                 "resource optimization strategies",
#                 "speed and performance enhancements",
#                 "production-ready optimizations",
#                 *[f"{area} optimization methods" for area in weak_areas[:2]]
#             ],
#             "architecture": [
#                 "scalable system design and architecture",
#                 "robust enterprise architecture patterns", 
#                 "production-ready system structures",
#                 "maintainable code architecture",
#                 "cloud-native design patterns",
#                 *[f"{area} architecture patterns" for area in strong_areas[:2]]
#             ]
#         }
        
#         template_text = template["template"]
#         for key, options in aspects.items():
#             if f"{{{key}}}" in template_text:
#                 # Use week, day, and task index to select different options
#                 option_index = (week_num + day_num + task_index) % len(options)
#                 chosen_option = options[option_index]
#                 template_text = template_text.replace(f"{{{key}}}", chosen_option)
        
#         return template_text.format(topic=topic)

#     def _enhance_task_description(self, task_title: str, user_data: Dict, phase: str, week_num: int, day_num: int) -> str:
#         """Create detailed task description"""
        
#         phase_descriptions = {
#             "foundational": "Build solid understanding of core concepts through structured learning and hands-on practice.",
#             "intermediate": "Develop practical skills and apply knowledge to real-world scenarios and complex projects.", 
#             "advanced": "Master complex topics and optimize solutions for professional-level applications and system design."
#         }
        
#         base_desc = phase_descriptions.get(phase, "Structured learning activity for progressive skill development.")
        
#         # Add weak area focus if applicable
#         weak_area_focus = ""
#         if user_data['weak_areas']:
#             weak_focus = user_data['weak_areas'][(week_num + day_num) % len(user_data['weak_areas'])]
#             weak_area_focus = f" Special focus on improving {weak_focus} skills."
        
#         return f"{task_title}. {base_desc}{weak_area_focus} Focus on progressive mastery and practical application in Week {week_num}."

#     def _generate_contextual_resources(self, task_title: str, user_data: Dict, phase: str) -> List[Dict]:
#         """Generate contextual learning resources"""
        
#         topic_encoded = task_title.replace(' ', '+')
#         resources = []
        
#         # Base resources for all phases
#         base_resources = [
#             {
#                 "title": f"Comprehensive Tutorial: {task_title}",
#                 "type": ResourceType.YOUTUBE.value,
#                 "url": f"https://youtube.com/results?search_query={topic_encoded}+tutorial+guide",
#                 "platform": "YouTube"
#             },
#             {
#                 "title": f"Official Documentation: {task_title}",
#                 "type": ResourceType.DOCUMENTATION.value, 
#                 "url": f"https://google.com/search?q={topic_encoded}+official+documentation",
#                 "platform": "Official Docs"
#             }
#         ]
        
#         resources.extend(base_resources)
        
#         # Phase-specific additional resources
#         if phase == "foundational":
#             resources.append({
#                 "title": f"Beginner Exercises: {task_title}",
#                 "type": ResourceType.PRACTICE.value,
#                 "url": f"https://google.com/search?q={topic_encoded}+beginner+exercises+practice",
#                 "platform": "Practice Platform"
#             })
#         elif phase == "intermediate":
#             resources.append({
#                 "title": f"Project Guide: {task_title}",
#                 "type": ResourceType.PROJECT.value,
#                 "url": f"https://google.com/search?q={topic_encoded}+project+guide+tutorial",
#                 "platform": "Project Guides"
#             })
#         else:  # advanced
#             resources.append({
#                 "title": f"Advanced Techniques: {task_title}",
#                 "type": ResourceType.ARTICLE.value,
#                 "url": f"https://google.com/search?q={topic_encoded}+advanced+techniques+best+practices",
#                 "platform": "Technical Blogs"
#             })
        
#         return resources

#     def _generate_week_overview(self, week_num: int, user_data: Dict, phase: str) -> str:
#         """Generate contextual week overview"""
        
#         weak_focus = user_data['weak_areas'][week_num % len(user_data['weak_areas'])] if user_data['weak_areas'] else "key concepts"
        
#         overviews = {
#             "foundational": f"Week {week_num}: Establish strong foundation in {user_data['user_goal']} core concepts with focus on {weak_focus}.",
#             "intermediate": f"Week {week_num}: Develop practical {user_data['user_goal']} skills through hands-on projects and complex problem-solving, emphasizing {weak_focus}.",
#             "advanced": f"Week {week_num}: Master advanced {user_data['user_goal']} techniques and optimize solutions, with deep dive into {weak_focus}."
#         }
        
#         return overviews.get(phase, f"Week {week_num}: Progressive learning and skill development in {user_data['user_goal']} with focus on {weak_focus}.")

#     def _generate_success_metrics(self, user_data: Dict) -> List[str]:
#         """Generate success metrics for the roadmap"""
#         return [
#             f"Complete {user_data['total_weeks']} weeks of structured learning",
#             f"Achieve {user_data['target_level']} proficiency in {user_data['user_goal']}",
#             f"Master {len(user_data['weak_areas'])} identified weak areas",
#             "Build comprehensive project portfolio demonstrating skills",
#             "Develop ability to solve complex problems independently"
#         ]

#     def _generate_study_recommendations(self, user_data: Dict) -> Dict:
#         """Generate study recommendations"""
#         return {
#             "weekly_commitment": f"{self.weekly_study_days} days × {self.daily_study_hours} hours",
#             "learning_approach": "Progressive skill development with practical application",
#             "review_strategy": "Weekly review sessions and project-based assessment",
#             "resource_utilization": "Combine tutorials, documentation, and hands-on practice"
#         }

#     def _generate_weekly_checkpoints(self, total_weeks: int) -> List[Dict]:
#         """Generate weekly progress checkpoints"""
#         checkpoints = []
#         for week in range(1, total_weeks + 1):
#             checkpoints.append({
#                 "week": week,
#                 "checkpoint": f"Week {week} progress review and skill assessment",
#                 "assessment_focus": "Concept mastery and practical application"
#             })
#         return checkpoints

#     def _generate_learning_milestones(self, user_data: Dict) -> List[Dict]:
#         """Generate key learning milestones"""
#         total_weeks = user_data['total_weeks']
#         return [
#             {
#                 "milestone": "Foundation Complete",
#                 "week": max(1, int(total_weeks * 0.25)),
#                 "description": f"Mastered basic {user_data['user_goal']} concepts and principles"
#             },
#             {
#                 "milestone": "Intermediate Proficiency", 
#                 "week": max(2, int(total_weeks * 0.5)),
#                 "description": f"Developed practical {user_data['user_goal']} skills and project capabilities"
#             },
#             {
#                 "milestone": "Advanced Mastery",
#                 "week": max(3, int(total_weeks * 0.75)),
#                 "description": f"Achieved expert-level {user_data['user_goal']} proficiency and optimization skills"
#             },
#             {
#                 "milestone": "Goal Achievement",
#                 "week": total_weeks,
#                 "description": f"Completed {user_data['target_level']} level in {user_data['user_goal']}"
#             }
#         ]

#     def _calculate_enhanced_stats(self, roadmap: Dict) -> Dict[str, Any]:
#         """Calculate enhanced resource statistics"""
#         total_tasks = 0
#         total_resources = 0
        
#         for week in roadmap.get('weekly_schedule', []):
#             for day in week.get('days', []):
#                 total_tasks += len(day.get('tasks', []))
#                 for task in day.get('tasks', []):
#                     total_resources += len(task.get('resources', []))
        
#         total_days = len(roadmap.get('weekly_schedule', [])) * self.weekly_study_days
        
#         return {
#             "total_tasks": total_tasks,
#             "total_resources": total_resources,
#             "average_tasks_per_day": total_tasks / total_days if total_days > 0 else 0,
#             "average_resources_per_task": total_resources / total_tasks if total_tasks > 0 else 0,
#             "total_learning_hours": total_days * self.daily_study_hours
#         }

# # Global instance
# roadmap_generator = RoadmapGenerator()







#new one
import ollama
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from enum import Enum
import asyncio
import hashlib
import random
import time

logger = logging.getLogger(__name__)

class ResourceType(Enum):
    YOUTUBE = "youtube"
    DOCUMENTATION = "documentation"
    ARTICLE = "article"
    PRACTICE = "practice"
    PROJECT = "project"
    COMMUNITY = "community"
    COURSE = "course"

class RoadmapGenerator:
    def __init__(self):
        self.model = "llama3.1:8b"  # Using faster model
        self.daily_study_hours = 2
        self.weekly_study_days = 5
        self._verify_model()
        
        # Cache for common patterns to avoid regeneration
        self.task_patterns_cache = {}
        self.week_templates_cache = {}

    def _verify_model(self):
        """Verify the model is available"""
        try:
            models = ollama.list()
            if models.get('models'):
                available_models = [model.get('name', '').split(':')[0] for model in models['models']]
                if 'llama3.1' in available_models:
                    self.model = "llama3.1:8b"
                elif 'mistral' in available_models:
                    self.model = "mistral:7b"  # Faster alternative
                elif 'qwen' in available_models:
                    self.model = "qwen:7b"  # Even faster
                logger.info(f"Using model: {self.model}")
        except Exception as e:
            logger.warning(f"Model verification failed: {e}")

    def _calculate_adaptive_timeline(self, assessment_score: float, timeline_preference: str, 
                               learning_stack_size: int) -> int:
        """Calculate adaptive timeline with optimized defaults"""
        
        # Ensure minimum learning stack size
        if learning_stack_size < 3:
            learning_stack_size = 8
        
        # Optimized base calculation
        base_weeks = max(6, min(int(learning_stack_size * 1.5), 26))  # Added int() conversion
        
        # Adjust based on assessment score
        if assessment_score >= 80:
            base_weeks = int(base_weeks * 0.6)  # More aggressive reduction
        elif assessment_score >= 60:
            base_weeks = int(base_weeks * 0.8)
        elif assessment_score < 40:
            base_weeks = int(base_weeks * 1.1)  # Less extension
        
        # Apply timeline preference
        if timeline_preference == "accelerated":
            base_weeks = max(4, int(base_weeks * 0.6))
        elif timeline_preference == "relaxed":
            base_weeks = int(base_weeks * 1.2)

        final_weeks = max(4, min(base_weeks, 26))  # Cap at 26 weeks max
        logger.info(f"Optimized timeline: {final_weeks} weeks for {learning_stack_size} items")
        return final_weeks

    async def generate_ai_enhanced_roadmap(
        self,
        user_goal: str,
        current_level: str,
        target_level: str,
        assessment_score: float,
        weak_skills: List[str],
        weak_topics: List[str],
        strong_areas: List[str],
        timeline_preference: str = "standard"
    ) -> Dict:
        """Generate optimized AI-driven roadmap"""
        
        logger.info(f"🚀 OPTIMIZED ROADMAP GENERATION START")
        logger.info(f"Goal: {user_goal}, Level: {current_level} → {target_level}")
        
        start_time = time.time()
        
        # Validate learning stack
        if not weak_skills and not weak_topics:
            raise ValueError("Learning stack is empty. Cannot generate roadmap without areas to learn.")
        
        # Combine and optimize learning stack
        learning_stack = self._optimize_learning_stack(weak_skills + weak_topics, user_goal)
        
        # Calculate timeline
        total_weeks = self._calculate_adaptive_timeline(
            assessment_score, timeline_preference, len(learning_stack)
        )
        
        user_data = {
            "user_goal": user_goal,
            "current_level": current_level,
            "target_level": target_level,
            "assessment_score": assessment_score,
            "learning_stack": learning_stack,
            "weak_skills": weak_skills,
            "weak_topics": weak_topics,
            "strong_areas": strong_areas,
            "total_weeks": total_weeks
        }

        try:
            # Generate phases first with specific learning items
            phases = await self._generate_optimized_phases(user_data)
            
            # Generate weekly schedule with specific skill assignments
            weekly_schedule = []
            for week_num in range(1, total_weeks + 1):
                week_data = await self._generate_skill_based_week(week_num, user_data, phases)
                weekly_schedule.append(week_data)
            
            roadmap_data = self._build_roadmap_structure(user_data, weekly_schedule, phases)
            
            # Calculate metrics
            uniqueness_metrics = self._calculate_uniqueness_metrics(roadmap_data)
            roadmap_data["uniqueness_metrics"] = uniqueness_metrics
            
            generation_time = time.time() - start_time
            logger.info(f"✅ OPTIMIZED Roadmap Complete: {total_weeks} weeks, {generation_time:.1f}s, "
                       f"{uniqueness_metrics['unique_tasks']} unique tasks")
            
            return roadmap_data

        except Exception as e:
            logger.error(f"❌ Roadmap generation failed: {e}")
            # Fast fallback
            return self._generate_fast_fallback(user_data)

    def _optimize_learning_stack(self, learning_stack: List[str], goal: str) -> List[str]:
        """Optimize and expand learning stack efficiently"""
        if len(learning_stack) >= 8:
            return learning_stack[:15]  # Limit to prevent overload
        
        # Fast expansion based on goal
        expanded = learning_stack.copy()
        goal_lower = goal.lower()
        
        if any(x in goal_lower for x in ['data', 'analyst', 'scientist']):
            additional = [
                "Python Programming", "Statistics", "Data Visualization",
                "SQL Databases", "Data Cleaning", "Machine Learning",
                "Data Analysis", "Data Storytelling"
            ]
        elif any(x in goal_lower for x in ['web', 'developer', 'frontend']):
            additional = [
                "HTML/CSS", "JavaScript", "React/Vue", "Responsive Design",
                "API Integration", "Version Control", "Web Performance"
            ]
        else:
            additional = [
                "Core Fundamentals", "Practical Applications", 
                "Project Development", "Problem Solving"
            ]
        
        for item in additional:
            if item not in expanded and len(expanded) < 12:
                expanded.append(item)
        
        return expanded

    async def _generate_optimized_phases(self, user_data: Dict) -> List[Dict]:
        """Generate phases with specific learning item assignments"""
        total_weeks = user_data['total_weeks']
        learning_stack = user_data['learning_stack']
        
        # Determine phase structure based on weeks
        if total_weeks <= 8:
            phase_config = [("Foundation", 0.4), ("Application", 0.6)]
        elif total_weeks <= 16:
            phase_config = [("Foundation", 0.3), ("Core Skills", 0.4), ("Advanced", 0.3)]
        else:
            phase_config = [("Foundation", 0.25), ("Core Skills", 0.35), 
                        ("Advanced", 0.25), ("Mastery", 0.15)]
        
        phases = []
        current_week = 1
        
        # Distribute learning items across phases
        phase_assignments = self._assign_learning_items_to_phases(learning_stack, len(phase_config))
        
        for phase_idx, (phase_name, percentage) in enumerate(phase_config):
            duration = max(2, int(total_weeks * percentage))  # Ensure integer
            
            # Get specific learning items for this phase
            phase_items = phase_assignments[phase_idx]
            
            phases.append({
                "name": f"{phase_name} Phase",
                "description": f"Build {phase_name.lower()} knowledge and skills",
                "start_week": current_week,
                "end_week": current_week + duration - 1,
                "duration": duration,
                "focus_areas": phase_items,
                "assigned_skills": phase_items  # Store assigned skills for week generation
            })
            
            current_week += duration
        
        return phases

    def _assign_learning_items_to_phases(self, learning_stack: List[str], num_phases: int) -> List[List[str]]:
        """Assign specific learning items to each phase"""
        phase_assignments = [[] for _ in range(num_phases)]
        
        # Distribute items evenly across phases
        for i, item in enumerate(learning_stack):
            phase_idx = i % num_phases
            phase_assignments[phase_idx].append(item)
        
        return phase_assignments

    async def _generate_skill_based_week(self, week_num: int, user_data: Dict, phases: List[Dict]) -> Dict:
        """Generate week content based on specific skills from learning stack"""
        current_phase = self._get_current_phase(week_num, phases)
        
        # Get specific skills for this week from the phase assignments
        week_skills = self._get_specific_week_skills(week_num, current_phase, user_data['learning_stack'])
        
        # Generate week structure
        week_data = {
            "week_number": week_num,
            "title": f"Week {week_num}: {current_phase['name']} - {', '.join(week_skills[:2])}",
            "overview": f"Focus on {', '.join(week_skills)} and related concepts",
            "objectives": [
                f"Master {week_skills[0]}" if week_skills else "Master key concepts",
                f"Apply {week_skills[1]}" if len(week_skills) > 1 else "Apply skills in practice",
                f"Build projects using {week_skills[2]}" if len(week_skills) > 2 else "Build practical projects"
            ],
            "learning_phase": current_phase["name"],
            "assigned_skills": week_skills,  # Track which skills are assigned to this week
            "days": []
        }
        
        # Generate days with skill-specific tasks
        for day_num in range(1, self.weekly_study_days + 1):
            day_data = await self._generate_skill_based_day(day_num, week_num, user_data, week_skills)
            week_data["days"].append(day_data)
        
        week_data["total_tasks"] = sum(len(day.get("tasks", [])) for day in week_data["days"])
        return week_data

    def _get_specific_week_skills(self, week_num: int, current_phase: Dict, learning_stack: List[str]) -> List[str]:
        """Get specific skills for this week from phase assignments"""
        phase_skills = current_phase.get("assigned_skills", [])
        if not phase_skills:
            # Fallback to learning stack distribution
            start_idx = ((week_num - current_phase["start_week"]) * 2) % len(learning_stack)
            return learning_stack[start_idx:start_idx + 3]
        
        # Distribute phase skills across weeks in the phase
        phase_week_count = current_phase["end_week"] - current_phase["start_week"] + 1
        skills_per_week = max(1, len(phase_skills) // phase_week_count)
        
        week_idx_in_phase = week_num - current_phase["start_week"]
        start_idx = week_idx_in_phase * skills_per_week
        end_idx = start_idx + skills_per_week
        
        # For the last week, include remaining skills
        if week_idx_in_phase == phase_week_count - 1:
            return phase_skills[start_idx:]
        
        return phase_skills[start_idx:end_idx]

    async def _generate_skill_based_day(self, day_num: int, week_num: int, user_data: Dict, 
                                      week_skills: List[str]) -> Dict:
        """Generate day with tasks specific to the week's skills"""
        day_themes = ["Theory & Concepts", "Hands-on Practice", "Project Work", 
                     "Problem Solving", "Review & Integration"]
        
        day_theme = day_themes[(day_num - 1) % len(day_themes)]
        
        start_date = datetime.now()
        day_offset = (week_num - 1) * self.weekly_study_days + (day_num - 1)
        day_date = start_date + timedelta(days=day_offset)
        
        # Generate skill-specific tasks
        tasks = await self._generate_skill_specific_tasks(day_num, week_num, week_skills, day_theme)
        
        return {
            "day_number": day_num,
            "day_title": f"Day {day_num}: {day_theme}",
            "date": day_date.strftime("%Y-%m-%d"),
            "theme": day_theme,
            "tasks": tasks,
            "estimated_hours": self.daily_study_hours,
            "focused_skills": week_skills  # Track which skills this day focuses on
        }

    async def _generate_skill_specific_tasks(self, day_num: int, week_num: int, 
                                           week_skills: List[str], day_theme: str) -> List[Dict]:
        """Generate tasks specifically tied to the week's assigned skills"""
        tasks = []
        
        for i in range(3):  # 3 tasks per day
            # Assign specific skill to this task
            if week_skills:
                skill_index = (day_num + i - 1) % len(week_skills)
                assigned_skill = week_skills[skill_index]
            else:
                assigned_skill = "core concepts"
            
            # Generate task based on the specific skill and day theme
            task = self._create_skill_specific_task(
                task_num=i+1,
                skill=assigned_skill,
                day_theme=day_theme,
                week_num=week_num,
                day_num=day_num
            )
            tasks.append(task)
        
        return tasks

    def _create_skill_specific_task(self, task_num: int, skill: str, day_theme: str,
                                  week_num: int, day_num: int) -> Dict:
        """Create task specifically for a given skill"""
        # Different task templates based on theme and skill
        if "Theory" in day_theme:
            templates = [
                f"Study {skill} fundamentals and core concepts",
                f"Research {skill} theoretical foundations", 
                f"Understand {skill} principles and methodologies",
                f"Learn {skill} concepts through documentation",
                f"Explore {skill} theoretical frameworks"
            ]
        elif "Practice" in day_theme:
            templates = [
                f"Complete {skill} hands-on exercises",
                f"Solve {skill} coding challenges",
                f"Practice {skill} implementation techniques",
                f"Work on {skill} practical examples",
                f"Build {skill} mini-applications"
            ]
        elif "Project" in day_theme:
            templates = [
                f"Build {skill} mini-project",
                f"Create {skill} application prototype",
                f"Develop {skill} project component",
                f"Implement {skill} in a practical project",
                f"Design {skill} project solution"
            ]
        elif "Problem" in day_theme:
            templates = [
                f"Solve {skill} related problems",
                f"Debug {skill} implementation issues",
                f"Optimize {skill} performance",
                f"Troubleshoot {skill} challenges",
                f"Analyze {skill} case studies"
            ]
        else:  # Review & Integration
            templates = [
                f"Review {skill} concepts and applications",
                f"Integrate {skill} with previous learnings",
                f"Create {skill} summary and cheat sheet",
                f"Test {skill} knowledge with quizzes",
                f"Apply {skill} in comprehensive exercises"
            ]
        
        # Select template and create unique task
        template_idx = (week_num + day_num + task_num) % len(templates)
        task_title = templates[template_idx]
        
        # Add context to make it more unique
        contexts = [
            "with detailed examples",
            "through step-by-step approach", 
            "using real-world scenarios",
            "focusing on practical applications",
            "with comprehensive coverage",
            "including best practices",
            "with performance considerations",
            "through interactive learning"
        ]
        
        context_idx = (week_num * day_num * task_num) % len(contexts)
        full_title = f"{task_title} {contexts[context_idx]}"
        
        task_id = f"week{week_num}_day{day_num}_task{task_num}"
        
        return {
            "id": task_num,
            "title": full_title,
            "description": f"Focus on {skill} development. {full_title}.",
            "skill": skill,  # Track which skill this task addresses
            "type": self._get_task_type_from_theme(day_theme),
            "priority": "high" if task_num == 1 else "medium",
            "estimated_hours": round(self.daily_study_hours / 3, 1),
            "ai_generated": True,
            "unique_id": hashlib.md5(f"{task_id}_{skill}_{datetime.now().timestamp()}".encode()).hexdigest()[:8],
            "task_id": task_id,
            "resources": self._generate_skill_specific_resources(skill, day_theme)
        }

    def _get_task_type_from_theme(self, day_theme: str) -> str:
        """Map day theme to task type"""
        if "Theory" in day_theme:
            return "learning"
        elif "Practice" in day_theme:
            return "practice" 
        elif "Project" in day_theme:
            return "project"
        elif "Problem" in day_theme:
            return "problem_solving"
        else:
            return "review"

    def _generate_skill_specific_resources(self, skill: str, day_theme: str) -> List[Dict]:
        """Generate resources specific to the skill and theme"""
        skill_encoded = skill.replace(' ', '+')
        theme_encoded = day_theme.replace(' ', '+')
        
        resources = [
            {
                "title": f"Video: {skill} {day_theme} Tutorial",
                "type": ResourceType.YOUTUBE.value,
                "url": f"https://youtube.com/results?search_query={skill_encoded}+{theme_encoded}+tutorial",
                "platform": "YouTube",
                "skill_specific": True
            },
            {
                "title": f"Docs: {skill} Official Documentation",
                "type": ResourceType.DOCUMENTATION.value,
                "url": f"https://google.com/search?q={skill_encoded}+official+documentation",
                "platform": "Official Docs",
                "skill_specific": True
            }
        ]
        
        # Add theme-specific resources
        if "Practice" in day_theme or "Problem" in day_theme:
            resources.append({
                "title": f"Practice: {skill} Exercises and Challenges",
                "type": ResourceType.PRACTICE.value,
                "url": f"https://google.com/search?q={skill_encoded}+practice+exercises+{theme_encoded}",
                "platform": "Practice Platforms",
                "skill_specific": True
            })
        elif "Project" in day_theme:
            resources.append({
                "title": f"Project: {skill} Project Ideas and Tutorials",
                "type": ResourceType.PROJECT.value,
                "url": f"https://google.com/search?q={skill_encoded}+project+ideas+{theme_encoded}",
                "platform": "Project Resources",
                "skill_specific": True
            })
        
        return resources

    def _build_roadmap_structure(self, user_data: Dict, weekly_schedule: List[Dict], phases: List[Dict]) -> Dict:
        """Build final roadmap structure"""
        return {
            "goal": user_data['user_goal'],
            "current_level": user_data['current_level'],
            "target_level": user_data['target_level'],
            "total_weeks": user_data['total_weeks'],
            "total_days": user_data['total_weeks'] * self.weekly_study_days,
            "total_hours": user_data['total_weeks'] * self.weekly_study_days * self.daily_study_hours,
            "learning_stack": user_data['learning_stack'],
            "learning_stack_size": len(user_data['learning_stack']),
            "weekly_schedule": weekly_schedule,
            "phases": phases,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "skill_based_3.0",
                "ai_generated": True,
                "generation_time_optimized": True,
                "skill_based_tasks": True,  # New flag indicating skill-based task generation
                "daily_study_hours": self.daily_study_hours,
                "weekly_study_days": self.weekly_study_days
            }
        }

    def _get_current_phase(self, week_num: int, phases: List[Dict]) -> Dict:
        """Get phase for current week"""
        for phase in phases:
            if phase["start_week"] <= week_num <= phase["end_week"]:
                return phase
        return phases[0]

    def _calculate_uniqueness_metrics(self, roadmap: Dict) -> Dict[str, Any]:
        """Calculate task uniqueness metrics with skill coverage"""
        all_titles = set()
        total_tasks = 0
        skill_coverage = {}
        
        for week in roadmap.get('weekly_schedule', []):
            for day in week.get('days', []):
                for task in day.get('tasks', []):
                    total_tasks += 1
                    all_titles.add(task['title'].lower().strip())
                    
                    # Track skill coverage
                    skill = task.get('skill', 'unknown')
                    if skill not in skill_coverage:
                        skill_coverage[skill] = 0
                    skill_coverage[skill] += 1
        
        unique_tasks = len(all_titles)
        uniqueness_percentage = (unique_tasks / total_tasks * 100) if total_tasks > 0 else 100
        
        # Calculate skill distribution
        learning_stack = roadmap.get('learning_stack', [])
        covered_skills = len([skill for skill in learning_stack if skill in skill_coverage])
        skill_coverage_percentage = (covered_skills / len(learning_stack) * 100) if learning_stack else 100
        
        return {
            "total_tasks": total_tasks,
            "unique_tasks": unique_tasks,
            "duplicate_count": total_tasks - unique_tasks,
            "uniqueness_percentage": round(uniqueness_percentage, 2),
            "skill_coverage": {
                "total_skills": len(learning_stack),
                "covered_skills": covered_skills,
                "coverage_percentage": round(skill_coverage_percentage, 2),
                "skill_distribution": skill_coverage
            }
        }

    def _generate_fast_fallback(self, user_data: Dict) -> Dict:
        """Generate fast fallback roadmap with skill-based tasks"""
        logger.warning("Using fast fallback roadmap generation")
        
        total_weeks = user_data['total_weeks']
        learning_stack = user_data['learning_stack']
        
        # Simple phase generation with skill assignment
        foundation_duration = max(2, total_weeks // 3)
        core_duration = total_weeks - foundation_duration
        
        # Distribute skills across phases
        foundation_skills = learning_stack[:len(learning_stack)//2]
        core_skills = learning_stack[len(learning_stack)//2:]
        
        phases = [
            {
                "name": "Foundation Phase",
                "description": "Build fundamental knowledge",
                "start_week": 1,
                "end_week": foundation_duration,
                "duration": foundation_duration,
                "focus_areas": foundation_skills,
                "assigned_skills": foundation_skills
            },
            {
                "name": "Core Phase", 
                "description": "Develop core skills",
                "start_week": foundation_duration + 1,
                "end_week": total_weeks,
                "duration": core_duration,
                "focus_areas": core_skills,
                "assigned_skills": core_skills
            }
        ]
        
        weekly_schedule = []
        for week_num in range(1, total_weeks + 1):
            current_phase = self._get_current_phase(week_num, phases)
            week_skills = self._get_specific_week_skills(week_num, current_phase, learning_stack)
            week_data = self._create_skill_based_fallback_week(week_num, phases, week_skills)
            weekly_schedule.append(week_data)
        
        return self._build_roadmap_structure(user_data, weekly_schedule, phases)

    def _create_skill_based_fallback_week(self, week_num: int, phases: List[Dict], week_skills: List[str]) -> Dict:
        """Create fallback week data with skill-based tasks"""
        current_phase = self._get_current_phase(week_num, phases)
        
        return {
            "week_number": week_num,
            "title": f"Week {week_num}: {current_phase['name']} - {', '.join(week_skills[:2])}",
            "overview": f"Learn and practice {', '.join(week_skills)}",
            "objectives": [f"Master {skill}" for skill in week_skills[:3]],
            "learning_phase": current_phase["name"],
            "assigned_skills": week_skills,
            "days": self._create_skill_based_fallback_days(week_num, week_skills),
            "total_tasks": 15  # 3 tasks/day * 5 days
        }

    def _create_skill_based_fallback_days(self, week_num: int, week_skills: List[str]) -> List[Dict]:
        """Create fallback days with skill-specific tasks"""
        days = []
        day_themes = ["Theory & Concepts", "Hands-on Practice", "Project Work", 
                     "Problem Solving", "Review & Integration"]
        
        for day_num in range(1, 6):
            tasks = []
            day_theme = day_themes[day_num - 1]
            
            for task_num in range(1, 4):
                # Assign specific skill to task
                skill_index = (day_num + task_num - 2) % len(week_skills) if week_skills else 0
                skill = week_skills[skill_index] if week_skills else "core concepts"
                
                # Create skill-specific task
                task_title = self._create_fallback_task_title(skill, day_theme, week_num, day_num, task_num)
                
                tasks.append({
                    "id": task_num,
                    "title": task_title,
                    "description": f"Learn and practice {skill} through {day_theme.lower()}",
                    "skill": skill,
                    "type": self._get_task_type_from_theme(day_theme),
                    "priority": "high" if task_num == 1 else "medium",
                    "estimated_hours": 0.7,
                    "ai_generated": False,
                    "unique_id": hashlib.md5(f"fallback_{week_num}_{day_num}_{task_num}_{skill}".encode()).hexdigest()[:8],
                    "task_id": f"week{week_num}_day{day_num}_task{task_num}",
                    "resources": self._generate_skill_specific_resources(skill, day_theme)
                })
            
            days.append({
                "day_number": day_num,
                "day_title": f"Day {day_num}: {day_theme}",
                "date": (datetime.now() + timedelta(days=(week_num-1)*5 + (day_num-1))).strftime("%Y-%m-%d"),
                "theme": day_theme,
                "tasks": tasks,
                "focused_skills": week_skills,
                "estimated_hours": self.daily_study_hours
            })
        
        return days

    def _create_fallback_task_title(self, skill: str, day_theme: str, week_num: int, day_num: int, task_num: int) -> str:
        """Create fallback task title based on skill and theme"""
        base_templates = {
            "Theory & Concepts": [
                f"Study {skill} fundamentals",
                f"Learn {skill} concepts", 
                f"Understand {skill} principles"
            ],
            "Hands-on Practice": [
                f"Practice {skill} implementation",
                f"Complete {skill} exercises",
                f"Work on {skill} examples"
            ],
            "Project Work": [
                f"Build {skill} project",
                f"Create {skill} application",
                f"Develop {skill} prototype"
            ],
            "Problem Solving": [
                f"Solve {skill} problems",
                f"Debug {skill} issues",
                f"Optimize {skill} code"
            ],
            "Review & Integration": [
                f"Review {skill} knowledge",
                f"Integrate {skill} skills",
                f"Apply {skill} comprehensively"
            ]
        }
        
        templates = base_templates.get(day_theme, [f"Work on {skill}"])
        template_idx = (week_num + day_num + task_num) % len(templates)
        
        return f"{templates[template_idx]} - Week {week_num} Day {day_num}"

# Global instance
roadmap_generator = RoadmapGenerator()