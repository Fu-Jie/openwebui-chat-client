#!/usr/bin/env python3
"""
Test data generation utilities for OpenWebUI Chat Client examples.

This module provides utilities for generating test data, sample content,
and configuration data used across different examples.

Features provided:
- Sample conversation data
- Test questions and prompts
- Knowledge base content
- Model configuration data

Usage:
    from utils.test_data import TestDataGenerator
    
    generator = TestDataGenerator()
    questions = generator.get_sample_questions()
    kb_content = generator.get_knowledge_base_content()
"""

import random
from typing import List, Dict, Any, Tuple
from datetime import datetime


class TestDataGenerator:
    """Generator for various types of test data."""
    
    def __init__(self):
        """Initialize the test data generator."""
        self.random = random.Random(42)  # Fixed seed for reproducible results
    
    def get_sample_questions(self, category: str = "general") -> List[str]:
        """
        Get sample questions for testing chat functionality.
        
        Args:
            category: Category of questions ('general', 'technical', 'creative', 'science')
            
        Returns:
            List of sample questions
        """
        questions = {
            "general": [
                "What is the capital of France?",
                "How are you today?",
                "What's the weather like?",
                "Tell me a joke",
                "What is the meaning of life?",
                "How do I make coffee?",
                "What time is it?",
                "What's your favorite color?",
            ],
            "technical": [
                "What is machine learning?",
                "Explain the concept of recursion in programming",
                "What is the difference between HTTP and HTTPS?",
                "How does a computer processor work?",
                "What is cloud computing?",
                "Explain the MVC architecture pattern",
                "What is the difference between SQL and NoSQL databases?",
                "How does blockchain technology work?",
            ],
            "creative": [
                "Write a short poem about spring",
                "Create a story about a robot and a cat",
                "Design a fictional character",
                "What would you do if you could time travel?",
                "Describe a perfect day",
                "Create a recipe for happiness",
                "Write a haiku about technology",
                "Imagine a world without gravity",
            ],
            "science": [
                "What is photosynthesis?",
                "Explain the theory of relativity in simple terms",
                "How do vaccines work?",
                "What causes earthquakes?",
                "Explain the process of evolution",
                "What is DNA and how does it work?",
                "How do solar panels generate electricity?",
                "What is the greenhouse effect?",
            ]
        }
        
        return questions.get(category, questions["general"])
    
    def get_sample_prompts(self) -> Dict[str, str]:
        """
        Get sample system prompts for model configuration.
        
        Returns:
            Dictionary of prompt names to prompt content
        """
        return {
            "helpful_assistant": "You are a helpful assistant that provides accurate and concise information.",
            "creative_writer": "You are a creative writing assistant that helps users craft engaging stories and content.",
            "technical_expert": "You are a technical expert who explains complex concepts in simple, understandable terms.",
            "teacher": "You are a patient teacher who helps students learn by breaking down complex topics into manageable pieces.",
            "researcher": "You are a research assistant who provides well-sourced, factual information.",
            "coding_mentor": "You are a coding mentor who helps developers learn programming concepts and debug code.",
            "translator": "You are a professional translator who provides accurate translations between languages.",
            "analyst": "You are a data analyst who helps interpret data and provides insights based on evidence.",
        }
    
    def get_knowledge_base_content(self) -> Dict[str, str]:
        """
        Get sample content for knowledge base examples.
        
        Returns:
            Dictionary mapping document names to content
        """
        return {
            "project_apollo.txt": """
Project Apollo was a spaceflight program conducted by NASA between 1961 and 1972. 
The primary objective was to land humans on the Moon and bring them back safely to Earth.

Key Missions:
- Apollo 7: First crewed Apollo mission (1968)
- Apollo 8: First crewed mission to orbit the Moon (1968)
- Apollo 11: First Moon landing with Neil Armstrong and Buzz Aldrin (1969)
- Apollo 17: Final Apollo mission (1972)

The program employed over 400,000 people and cost approximately $25 billion 
(equivalent to over $150 billion in 2020 dollars).
            """.strip(),
            
            "machine_learning_basics.txt": """
Machine Learning (ML) is a subset of artificial intelligence that enables 
computers to learn and make decisions from data without being explicitly programmed.

Types of Machine Learning:
1. Supervised Learning: Uses labeled data to train models
2. Unsupervised Learning: Finds patterns in unlabeled data
3. Reinforcement Learning: Learns through trial and error

Common Algorithms:
- Linear Regression
- Decision Trees
- Neural Networks
- Support Vector Machines
- K-Means Clustering

Applications include image recognition, natural language processing, 
recommendation systems, and autonomous vehicles.
            """.strip(),
            
            "quantum_computing.txt": """
Quantum computing is a type of computation that harnesses quantum mechanical 
phenomena such as superposition and entanglement to process information.

Key Concepts:
- Qubits: Basic units of quantum information
- Superposition: Ability to exist in multiple states simultaneously
- Entanglement: Quantum correlation between particles
- Quantum Gates: Operations performed on qubits

Advantages:
- Exponential speedup for certain problems
- Potential to solve currently intractable problems
- Applications in cryptography, optimization, and simulation

Current challenges include maintaining quantum coherence and error correction.
            """.strip(),
            
            "climate_change.txt": """
Climate change refers to long-term changes in global or regional climate patterns, 
primarily attributed to increased atmospheric carbon dioxide from fossil fuel use.

Key Indicators:
- Rising global temperatures
- Melting ice caps and glaciers
- Rising sea levels
- Changes in precipitation patterns
- Ocean acidification

Major Causes:
- Greenhouse gas emissions (CO2, methane, nitrous oxide)
- Deforestation
- Industrial processes
- Transportation
- Agriculture

Mitigation strategies include renewable energy adoption, energy efficiency, 
carbon capture, and sustainable practices.
            """.strip(),
        }
    
    def get_sample_tags(self) -> List[str]:
        """
        Get sample tags for chat organization.
        
        Returns:
            List of sample tags
        """
        return [
            "urgent", "follow-up", "research", "brainstorming", "technical",
            "creative", "planning", "meeting", "documentation", "bug-fix",
            "feature-request", "question", "tutorial", "example", "test",
            "work", "personal", "learning", "ai", "programming", "science",
            "business", "education", "health", "technology", "review"
        ]
    
    def get_sample_folders(self) -> List[str]:
        """
        Get sample folder names for chat organization.
        
        Returns:
            List of sample folder names
        """
        return [
            "Work Projects", "Personal", "Research", "Learning", "Technical Support",
            "Creative Writing", "Meeting Notes", "Ideas", "Documentation", "Tutorials",
            "Code Review", "Bug Reports", "Feature Requests", "Questions", "Archive"
        ]
    
    def get_sample_model_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get sample model configurations for testing.
        
        Returns:
            Dictionary of model configurations
        """
        return {
            "conservative_model": {
                "temperature": 0.3,
                "top_p": 0.8,
                "max_tokens": 1000,
                "description": "Conservative model with low creativity, good for factual responses"
            },
            "balanced_model": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000,
                "description": "Balanced model suitable for most general-purpose tasks"
            },
            "creative_model": {
                "temperature": 0.9,
                "top_p": 0.95,
                "max_tokens": 3000,
                "description": "Creative model with high variability, good for creative writing"
            },
            "precise_model": {
                "temperature": 0.1,
                "top_p": 0.7,
                "max_tokens": 1500,
                "description": "Very precise model for technical and analytical tasks"
            }
        }
    
    def get_conversation_starters(self) -> List[Tuple[str, str]]:
        """
        Get conversation starters with expected response types.
        
        Returns:
            List of tuples (question, expected_response_type)
        """
        return [
            ("Hello, how can you help me today?", "greeting_and_capabilities"),
            ("What's the latest news about AI?", "informational"),
            ("Can you write me a short story?", "creative"),
            ("Explain quantum physics in simple terms", "educational"),
            ("Help me debug this Python code", "technical_assistance"),
            ("What are some good restaurants nearby?", "local_information"),
            ("How do I stay motivated?", "advice"),
            ("What's the weather forecast?", "data_request"),
        ]
    
    def get_sample_rag_questions(self) -> Dict[str, List[str]]:
        """
        Get sample questions for RAG (Retrieval Augmented Generation) testing.
        
        Returns:
            Dictionary mapping document topics to relevant questions
        """
        return {
            "project_apollo": [
                "What was the primary objective of Project Apollo?",
                "Which Apollo mission first landed on the Moon?",
                "How much did the Apollo program cost?",
                "Who were the astronauts on Apollo 11?",
                "When did the Apollo program end?",
            ],
            "machine_learning": [
                "What are the main types of machine learning?",
                "List some common machine learning algorithms",
                "What is supervised learning?",
                "What are some applications of machine learning?",
                "What is the difference between supervised and unsupervised learning?",
            ],
            "quantum_computing": [
                "What is a qubit?",
                "What is quantum superposition?",
                "What are the advantages of quantum computing?",
                "What are quantum gates?",
                "What are the current challenges in quantum computing?",
            ],
            "climate_change": [
                "What are the key indicators of climate change?",
                "What are the major causes of climate change?",
                "What is ocean acidification?",
                "What are some mitigation strategies for climate change?",
                "How do greenhouse gases contribute to climate change?",
            ],
        }
    
    def generate_random_chat_title(self) -> str:
        """
        Generate a random chat title for testing.
        
        Returns:
            Random chat title
        """
        adjectives = ["Quick", "Deep", "Important", "Urgent", "Creative", "Technical", "Simple", "Complex"]
        nouns = ["Discussion", "Meeting", "Analysis", "Review", "Planning", "Brainstorming", "Question", "Research"]
        topics = ["AI", "Code", "Project", "Ideas", "Data", "Design", "Strategy", "Solutions"]
        
        # Different title patterns
        patterns = [
            f"{self.random.choice(adjectives)} {self.random.choice(nouns)}",
            f"{self.random.choice(topics)} {self.random.choice(nouns)}",
            f"{self.random.choice(adjectives)} {self.random.choice(topics)} {self.random.choice(nouns)}",
            f"{self.random.choice(nouns)} - {self.random.choice(topics)}",
        ]
        
        title = self.random.choice(patterns)
        
        # Add timestamp for uniqueness if needed
        if self.random.random() < 0.3:  # 30% chance to add timestamp
            timestamp = datetime.now().strftime("%Y%m%d")
            title += f" ({timestamp})"
        
        return title
    
    def get_test_images_data(self) -> Dict[str, str]:
        """
        Get test data for image generation.
        
        Returns:
            Dictionary mapping image descriptions to filenames
        """
        return {
            "sample_chart": "Sample Chart Data",
            "test_diagram": "Test System Diagram", 
            "logo_mockup": "Company Logo Mockup",
            "flowchart": "Process Flowchart",
            "screenshot": "UI Screenshot Example",
            "graph": "Data Visualization Graph",
            "infographic": "Information Graphic",
            "presentation": "Slide Presentation"
        }
    
    def get_sample_tools_config(self) -> List[Dict[str, Any]]:
        """
        Get sample tool configurations for testing tool integration.
        
        Returns:
            List of tool configuration dictionaries
        """
        return [
            {
                "id": "web_search",
                "name": "Web Search",
                "description": "Search the web for current information",
                "parameters": {"query": "string", "max_results": "integer"}
            },
            {
                "id": "calculator",
                "name": "Calculator", 
                "description": "Perform mathematical calculations",
                "parameters": {"expression": "string"}
            },
            {
                "id": "weather",
                "name": "Weather Service",
                "description": "Get weather information for a location",
                "parameters": {"location": "string", "units": "string"}
            },
            {
                "id": "translator",
                "name": "Language Translator",
                "description": "Translate text between languages",
                "parameters": {"text": "string", "source_lang": "string", "target_lang": "string"}
            },
            {
                "id": "code_executor",
                "name": "Code Executor",
                "description": "Execute code snippets safely",
                "parameters": {"code": "string", "language": "string"}
            }
        ]


if __name__ == "__main__":
    # Example usage
    generator = TestDataGenerator()
    
    print("Sample Questions (Technical):")
    for q in generator.get_sample_questions("technical")[:3]:
        print(f"  - {q}")
    
    print("\nSample Chat Title:")
    print(f"  - {generator.generate_random_chat_title()}")
    
    print("\nKnowledge Base Content Keys:")
    for key in generator.get_knowledge_base_content().keys():
        print(f"  - {key}")
        
    print("\nSample RAG Questions for Apollo:")
    for q in generator.get_sample_rag_questions()["project_apollo"][:2]:
        print(f"  - {q}")