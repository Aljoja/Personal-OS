"""Predefined learning challenges for skill development"""

from typing import List, Dict

class ChallengeLibrary:
    """Library of predefined challenges for learning"""
    
    def __init__(self):
        self.challenges = self._initialize_challenges()
    
    def _initialize_challenges(self) -> Dict[str, List[Dict]]:
        """Initialize challenge library organized by skill area"""
        
        return {
            'python': [
                {
                    'title': 'CLI Todo App',
                    'description': '''Build a command-line todo application that can:
- Add tasks
- List all tasks
- Mark tasks as done
- Delete tasks
- Save/load from file

This teaches: functions, data structures (lists/dicts), file I/O, user input''',
                    'difficulty': 'beginner',
                    'estimated_hours': 3,
                    'skills_taught': ['functions', 'lists', 'dictionaries', 'file I/O', 'user input'],
                    'prerequisites': ['basic Python syntax'],
                    'unlocks': ['data_validator', 'web_scraper']
                },
                {
                    'title': 'Web Scraper with Error Handling',
                    'description': '''Build a web scraper that:
- Fetches data from a website (e.g., news headlines)
- Parses HTML
- Handles errors gracefully
- Saves data to CSV

This teaches: HTTP requests, HTML parsing, exception handling, data processing''',
                    'difficulty': 'beginner',
                    'estimated_hours': 4,
                    'skills_taught': ['requests', 'BeautifulSoup', 'exception handling', 'CSV'],
                    'prerequisites': ['functions', 'dictionaries'],
                    'unlocks': ['async_scraper', 'data_pipeline']
                },
                {
                    'title': 'Data Validator with Decorators',
                    'description': '''Create a validation system using decorators:
- Validate function inputs
- Type checking
- Range validation
- Custom validators

This teaches: decorators, function composition, design patterns''',
                    'difficulty': 'intermediate',
                    'estimated_hours': 4,
                    'skills_taught': ['decorators', 'type hints', 'validation', 'design patterns'],
                    'prerequisites': ['functions', 'CLI todo app completed'],
                    'unlocks': ['api_builder', 'testing_framework']
                },
                {
                    'title': 'Simple REST API',
                    'description': '''Build a REST API with Flask/FastAPI:
- CRUD endpoints
- JSON responses
- Error handling
- Basic authentication

This teaches: web frameworks, REST principles, API design''',
                    'difficulty': 'intermediate',
                    'estimated_hours': 5,
                    'skills_taught': ['Flask/FastAPI', 'REST', 'HTTP', 'JSON', 'authentication'],
                    'prerequisites': ['decorators', 'dictionaries'],
                    'unlocks': ['full_web_app', 'microservices']
                }
            ],
            
            'data_analysis': [
                {
                    'title': 'Kaggle Dataset Analysis',
                    'description': '''Pick a Kaggle dataset and:
- Load and explore data
- Clean and preprocess
- Create visualizations
- Find insights
- Write summary report

This teaches: pandas, data cleaning, visualization, analysis''',
                    'difficulty': 'beginner',
                    'estimated_hours': 5,
                    'skills_taught': ['pandas', 'matplotlib', 'data cleaning', 'EDA'],
                    'prerequisites': ['basic Python'],
                    'unlocks': ['automated_reports', 'time_series']
                },
                {
                    'title': 'Automated Report Generator',
                    'description': '''Build a system that:
- Loads data from CSV
- Performs analysis
- Generates visualizations
- Creates PDF/HTML report
- Runs on schedule

This teaches: automation, reporting, data pipelines''',
                    'difficulty': 'intermediate',
                    'estimated_hours': 6,
                    'skills_taught': ['automation', 'pandas', 'reporting', 'scheduling'],
                    'prerequisites': ['Kaggle analysis completed'],
                    'unlocks': ['dashboard', 'etl_pipeline']
                },
                {
                    'title': 'Time Series Analysis',
                    'description': '''Analyze time series data:
- Load temporal data
- Identify trends and seasonality
- Create forecasts
- Visualize patterns

This teaches: time series, forecasting, statistical analysis''',
                    'difficulty': 'intermediate',
                    'estimated_hours': 6,
                    'skills_taught': ['time series', 'forecasting', 'statistics', 'pandas'],
                    'prerequisites': ['pandas basics'],
                    'unlocks': ['predictive_maintenance', 'financial_analysis']
                }
            ],
            
            'machine_learning': [
                {
                    'title': 'Linear Regression from Scratch',
                    'description': '''Implement linear regression without scikit-learn:
- Gradient descent algorithm
- Cost function
- Training loop
- Predictions
- Visualization

This teaches: ML fundamentals, optimization, NumPy''',
                    'difficulty': 'beginner',
                    'estimated_hours': 6,
                    'skills_taught': ['gradient descent', 'NumPy', 'optimization', 'ML basics'],
                    'prerequisites': ['basic math', 'NumPy basics'],
                    'unlocks': ['logistic_regression', 'neural_network']
                },
                {
                    'title': 'Neural Network from Scratch',
                    'description': '''Build a neural network without frameworks:
- Forward propagation
- Backpropagation
- Training on simple dataset
- Activation functions

This teaches: deep learning fundamentals, calculus application''',
                    'difficulty': 'advanced',
                    'estimated_hours': 10,
                    'skills_taught': ['neural networks', 'backpropagation', 'deep learning'],
                    'prerequisites': ['linear regression from scratch', 'calculus'],
                    'unlocks': ['cnn', 'rnn', 'transformer']
                },
                {
                    'title': 'Housing Price Predictor',
                    'description': '''Build ML pipeline with scikit-learn:
- Feature engineering
- Model selection
- Cross-validation
- Hyperparameter tuning
- Deployment

This teaches: practical ML, scikit-learn, pipelines''',
                    'difficulty': 'intermediate',
                    'estimated_hours': 8,
                    'skills_taught': ['scikit-learn', 'feature engineering', 'model selection'],
                    'prerequisites': ['pandas', 'basic ML concepts'],
                    'unlocks': ['classification', 'ensemble_methods']
                }
            ],
            
            'digitalization': [
                {
                    'title': 'IoT Data Pipeline',
                    'description': '''Build IoT data processing:
- Simulate sensor data
- Real-time processing
- Store in database
- Create dashboard

This teaches: IoT, real-time systems, databases''',
                    'difficulty': 'intermediate',
                    'estimated_hours': 8,
                    'skills_taught': ['IoT', 'real-time processing', 'databases', 'MQTT'],
                    'prerequisites': ['Python basics', 'API experience'],
                    'unlocks': ['manufacturing_dashboard', 'predictive_maintenance']
                },
                {
                    'title': 'Manufacturing Dashboard',
                    'description': '''Create a dashboard for factory metrics:
- Real-time KPI visualization
- Historical trends
- Alerts/notifications
- Performance analytics

This teaches: dashboards, data viz, real-time systems''',
                    'difficulty': 'advanced',
                    'estimated_hours': 10,
                    'skills_taught': ['Plotly/Dash', 'real-time viz', 'KPIs', 'databases'],
                    'prerequisites': ['data analysis', 'web basics'],
                    'unlocks': ['full_mes_system']
                }
            ]
        }
    
    def get_challenges_for_skill(self, skill_category: str, difficulty: str = None) -> List[Dict]:
        """Get challenges for a skill category, optionally filtered by difficulty"""
        challenges = self.challenges.get(skill_category.lower(), [])
        
        if difficulty:
            challenges = [c for c in challenges if c['difficulty'] == difficulty.lower()]
        
        return challenges
    
    def get_all_challenges(self) -> Dict[str, List[Dict]]:
        """Get all challenges organized by category"""
        return self.challenges
    
    def search_challenges(self, keyword: str) -> List[Dict]:
        """Search challenges by keyword"""
        results = []
        keyword_lower = keyword.lower()
        
        for category, challenges in self.challenges.items():
            for challenge in challenges:
                if (keyword_lower in challenge['title'].lower() or
                    keyword_lower in challenge['description'].lower() or
                    keyword_lower in ' '.join(challenge['skills_taught']).lower()):
                    results.append({**challenge, 'category': category})
        
        return results