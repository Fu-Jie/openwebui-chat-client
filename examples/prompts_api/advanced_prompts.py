#!/usr/bin/env python3
"""
Advanced Prompts Integration Example for OpenWebUI Chat Client.

This example demonstrates:
- Creating interactive prompts with various input types
- Using prompts in chat conversations
- Advanced variable substitution
- Dynamic prompt generation
- Integration with chat context

Requirements:
- Environment variable: OUI_BASE_URL
- Environment variable: OUI_AUTH_TOKEN
- Environment variable: OUI_DEFAULT_MODEL

Usage:
    python examples/prompts_api/advanced_prompts.py
"""

import logging
import os
import json
from typing import Optional, Dict, Any, List

from openwebui_chat_client import OpenWebUIClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")
DEFAULT_MODEL = os.getenv("OUI_DEFAULT_MODEL", "gpt-4.1")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_interactive_prompts(client: OpenWebUIClient) -> List[Dict[str, Any]]:
    """Create a comprehensive set of interactive prompts."""
    logger.info("=== Creating Interactive Prompts ===")
    
    prompts_to_create = [
        {
            "command": "/article_writer",
            "title": "Professional Article Writer",
            "content": """Write a professional article with the following specifications:

**Title:** {{title | text:placeholder="Enter article title"}}
**Topic:** {{topic | text:placeholder="Main topic/subject"}}
**Target Audience:** {{audience | select:options=["General Public","Technical","Business","Academic"]:default="General Public"}}
**Article Length:** {{length | select:options=["Short (300-500 words)","Medium (500-1000 words)","Long (1000+ words)"]:default="Medium (500-1000 words)"}}
**Tone:** {{tone | select:options=["Professional","Casual","Academic","Conversational"]:default="Professional"}}
**Key Points:** {{key_points | textarea:placeholder="List the main points you want covered"}}
**Include Sources:** {{include_sources | checkbox:default=false}}
**Publication Date:** {{pub_date | date}}

Please write a comprehensive article covering these requirements."""
        },
        {
            "command": "/bug_reporter",
            "title": "Bug Report Generator",
            "content": """Create a detailed bug report with the following information:

**Bug Title:** {{bug_title | text:placeholder="Brief description of the bug"}}
**Priority:** {{priority | select:options=["Critical","High","Medium","Low"]:default="Medium"}}
**Severity:** {{severity | select:options=["Blocker","Major","Minor","Trivial"]:default="Major"}}
**Affected Component:** {{component | text:placeholder="Module/component affected"}}
**Browser/OS:** {{environment | text:placeholder="e.g., Chrome 120/Windows 11"}}
**Steps to Reproduce:**
{{steps | textarea:placeholder="1. Go to...\n2. Click on...\n3. Enter..."}}
**Expected Result:**
{{expected | textarea:placeholder="What should happen"}}
**Actual Result:**
{{actual | textarea:placeholder="What actually happened"}}
**Additional Notes:** {{notes | textarea:placeholder="Any additional information"}}
**Reproducibility:** {{reproducible | select:options=["Always","Sometimes","Rarely","Unable to Reproduce"]:default="Always"}}
**Reporter Email:** {{reporter_email | email:placeholder="your.email@company.com"}}

Generate a well-formatted bug report based on this information."""
        },
        {
            "command": "/meeting_planner",
            "title": "Meeting Agenda Planner",
            "content": """Plan a comprehensive meeting agenda:

**Meeting Title:** {{meeting_title | text:placeholder="Enter meeting name"}}
**Date:** {{meeting_date | date}}
**Start Time:** {{start_time | time:default="09:00"}}
**Duration:** {{duration | number:placeholder="Duration in minutes":default=60}}
**Meeting Type:** {{meeting_type | select:options=["Team Standup","Project Review","Client Meeting","All Hands","One-on-One","Board Meeting"]:default="Team Standup"}}
**Attendees:** {{attendees | textarea:placeholder="List attendees (one per line)"}}
**Main Objective:** {{objective | text:placeholder="Primary goal of this meeting"}}
**Discussion Topics:** {{topics | textarea:placeholder="List topics to be discussed"}}
**Decisions Needed:** {{decisions | textarea:placeholder="What decisions need to be made?"}}
**Pre-reading Required:** {{pre_reading | checkbox:default=false}}
**Location/Link:** {{location | url:placeholder="https://zoom.us/j/... or Conference Room A"}}

Create a structured meeting agenda with time allocations and clear action items."""
        },
        {
            "command": "/social_campaign",
            "title": "Social Media Campaign Creator",
            "content": """Design a social media campaign:

**Campaign Name:** {{campaign_name | text:placeholder="Enter campaign name"}}
**Platform:** {{platform | select:options=["Instagram","Twitter","LinkedIn","Facebook","TikTok","YouTube"]:default="Instagram"}}
**Campaign Goal:** {{goal | select:options=["Brand Awareness","Lead Generation","Sales","Engagement","Community Building"]:default="Brand Awareness"}}
**Target Audience:** {{target_audience | text:placeholder="Describe your target audience"}}
**Campaign Duration:** {{duration | range:min=1:max=30:default=7}} days
**Budget Range:** {{budget | select:options=["Under $1000","$1000-$5000","$5000-$10000","Over $10000"]:default="$1000-$5000"}}
**Key Message:** {{key_message | textarea:placeholder="Main message to communicate"}}
**Call to Action:** {{cta | text:placeholder="What action should users take?"}}
**Brand Color:** {{brand_color | color:default="#1da1f2"}}
**Include Hashtags:** {{include_hashtags | checkbox:default=true}}
**Content Types:** {{content_types | select:options=["Images","Videos","Stories","Reels","Carousels"]:default="Images"}}

Generate a comprehensive social media campaign strategy with content suggestions."""
        }
    ]
    
    created_prompts = []
    for prompt_data in prompts_to_create:
        logger.info(f"Creating prompt: {prompt_data['command']}")
        created_prompt = client.create_prompt(**prompt_data)
        if created_prompt:
            created_prompts.append(created_prompt)
            logger.info(f"✅ Created: {created_prompt['title']}")
        else:
            logger.error(f"❌ Failed to create: {prompt_data['command']}")
    
    return created_prompts


def demonstrate_variable_parsing(client: OpenWebUIClient):
    """Demonstrate advanced variable parsing and type detection."""
    logger.info("\n=== Advanced Variable Parsing Demo ===")
    
    complex_content = """Create a project plan with these specifications:

**Project Info:**
- Name: {{project_name | text:placeholder="Enter project name"}}
- Manager: {{manager | text:placeholder="Project manager name"}}
- Start Date: {{start_date | date}}
- End Date: {{end_date | date}}
- Budget: ${{budget | number:min=1000:max=1000000:default=50000}}

**Team Configuration:**
- Team Size: {{team_size | range:min=1:max=20:default=5}} people
- Experience Level: {{experience | select:options=["Junior","Mid-level","Senior","Mixed"]:default="Mixed"}}
- Remote Work: {{remote_allowed | checkbox:default=true}}

**Requirements:**
- Technical Stack: {{tech_stack | textarea:placeholder="List technologies to be used"}}
- Key Features: {{features | textarea:placeholder="List main features"}}
- Success Metrics: {{metrics | textarea:placeholder="How will success be measured?"}}

**Communication:**
- Client Email: {{client_email | email:placeholder="client@company.com"}}
- Meeting Time: {{meeting_time | time:default="14:00"}}
- Project URL: {{project_url | url:placeholder="https://github.com/..."}}
- Location: {{location | map:default="37.7749,-122.4194"}}

**Preferences:**
- Priority Level: {{priority | select:options=["Low","Medium","High","Critical"]:default="Medium"}}
- Preferred Color Scheme: {{color_scheme | color:default="#007bff"}}
- Review Frequency: {{review_frequency | select:options=["Daily","Weekly","Bi-weekly","Monthly"]:default="Weekly"}}

Generate a detailed project plan based on these parameters."""
    
    # Extract and analyze variables
    variables = client.extract_variables(complex_content)
    logger.info(f"📝 Extracted {len(variables)} variables:")
    
    for var in sorted(variables):
        logger.info(f"  - {var}")
    
    # Create sample data that matches the variable types
    sample_data = {
        "project_name": "E-commerce Platform Redesign",
        "manager": "Sarah Johnson",
        "start_date": "2024-03-01", 
        "end_date": "2024-06-30",
        "budget": 75000,
        "team_size": 8,
        "experience": "Mixed",
        "remote_allowed": "Yes",
        "tech_stack": "React, Node.js, PostgreSQL, AWS",
        "features": "User authentication, Product catalog, Shopping cart, Payment integration",
        "metrics": "User engagement, Conversion rate, Page load time, Customer satisfaction",
        "client_email": "john.doe@acmecorp.com",
        "meeting_time": "15:30",
        "project_url": "https://github.com/acme/ecommerce-redesign",
        "location": "San Francisco, CA",
        "priority": "High",
        "color_scheme": "#28a745",
        "review_frequency": "Weekly"
    }
    
    # Substitute with system variables included
    system_vars = client.get_system_variables()
    enhanced_content = f"Generated on {{{{CURRENT_DATE}}}} by {{{{USER_NAME}}}}\n\n{complex_content}"
    
    # Add mock user name since it's not available in system vars by default
    system_vars["USER_NAME"] = "AI Assistant"
    
    final_content = client.substitute_variables(enhanced_content, sample_data, system_vars)
    
    logger.info("\n📋 Generated project plan:")
    logger.info("=" * 60)
    logger.info(final_content)
    logger.info("=" * 60)


def demonstrate_dynamic_prompt_creation(client: OpenWebUIClient):
    """Demonstrate creating prompts dynamically based on context."""
    logger.info("\n=== Dynamic Prompt Creation Demo ===")
    
    # Simulate different use cases that would need different prompts
    use_cases = [
        {
            "context": "software_development",
            "user_role": "developer",
            "task": "code_review"
        },
        {
            "context": "marketing",
            "user_role": "marketer", 
            "task": "campaign_analysis"
        },
        {
            "context": "education",
            "user_role": "teacher",
            "task": "lesson_planning"
        }
    ]
    
    for use_case in use_cases:
        logger.info(f"Creating dynamic prompt for {use_case['context']} - {use_case['task']}")
        
        # Generate prompt content based on context
        if use_case["context"] == "software_development":
            content = f"""Perform a thorough code review for {{{{language}}}} code:

**Code to Review:**
{{{{code | textarea:placeholder="Paste the code here"}}}}

**Review Focus:**
{{{{focus | select:options=["Security","Performance","Maintainability","All"]:default="All"}}}}

**Severity Filter:**
{{{{severity | select:options=["All Issues","Critical Only","Major+","Minor+"]:default="All Issues"}}}}

**Include Suggestions:** {{{{include_suggestions | checkbox:default=true}}}}

Provide detailed feedback with improvement recommendations."""

        elif use_case["context"] == "marketing":
            content = f"""Analyze marketing campaign performance:

**Campaign Name:** {{{{campaign_name | text:placeholder="Enter campaign name"}}}}
**Platform:** {{{{platform | select:options=["Google Ads","Facebook","Instagram","LinkedIn","Email"]:default="Google Ads"}}}}
**Date Range:** 
- Start: {{{{start_date | date}}}}
- End: {{{{end_date | date}}}}

**Key Metrics:**
- Impressions: {{{{impressions | number:placeholder="Total impressions"}}}}
- Clicks: {{{{clicks | number:placeholder="Total clicks"}}}}
- Conversions: {{{{conversions | number:placeholder="Total conversions"}}}}
- Budget Spent: ${{{{budget_spent | number:placeholder="Amount spent"}}}}

**Campaign Goal:** {{{{goal | select:options=["Awareness","Traffic","Leads","Sales"]:default="Traffic"}}}}

Provide comprehensive analysis with actionable insights."""

        else:  # education
            content = f"""Create a detailed lesson plan:

**Subject:** {{{{subject | text:placeholder="e.g., Mathematics, History"}}}}
**Grade Level:** {{{{grade | select:options=["Elementary","Middle School","High School","College"]:default="High School"}}}}
**Duration:** {{{{duration | number:placeholder="Minutes":default=50}}}} minutes
**Topic:** {{{{topic | text:placeholder="Specific lesson topic"}}}}

**Learning Objectives:** {{{{objectives | textarea:placeholder="What students will learn"}}}}
**Prerequisites:** {{{{prerequisites | text:placeholder="Required prior knowledge"}}}}
**Materials Needed:** {{{{materials | textarea:placeholder="List required materials"}}}}

**Teaching Method:** {{{{method | select:options=["Lecture","Discussion","Hands-on","Mixed"]:default="Mixed"}}}}
**Assessment Type:** {{{{assessment | select:options=["Quiz","Project","Discussion","Homework"]:default="Quiz"}}}}

Design an engaging lesson plan with activities and assessment."""
        
        # Create the dynamic prompt
        command = f"/{use_case['context']}_{use_case['task']}"
        title = f"{use_case['context'].title()} {use_case['task'].replace('_', ' ').title()}"
        
        created_prompt = client.create_prompt(command, title, content)
        
        if created_prompt:
            logger.info(f"✅ Created dynamic prompt: {created_prompt['command']}")
        else:
            logger.error(f"❌ Failed to create dynamic prompt: {command}")


def simulate_chat_with_prompts(client: OpenWebUIClient):
    """Simulate using prompts in actual chat conversations."""
    logger.info("\n=== Chat Integration Simulation ===")
    
    # First, ensure we have a working prompt
    test_prompt = client.get_prompt_by_command("/article_writer")
    if not test_prompt:
        logger.info("Creating test prompt for chat simulation...")
        test_prompt = client.create_prompt(
            command="/quick_summary",
            title="Quick Summary Generator",
            content="Please provide a quick summary of: {{text}}"
        )
    
    if test_prompt:
        logger.info(f"Using prompt: {test_prompt['title']}")
        
        # Simulate different ways to use prompts in chat
        sample_texts = [
            "Artificial Intelligence is transforming industries across the globe...",
            "Climate change represents one of the most pressing challenges of our time...",
            "The future of remote work depends on several key technological advances..."
        ]
        
        for i, sample_text in enumerate(sample_texts, 1):
            logger.info(f"\n--- Chat Simulation {i} ---")
            
            # Extract variables from prompt content
            variables = client.extract_variables(test_prompt['content'])
            logger.info(f"Prompt variables: {variables}")
            
            # Prepare variable substitution
            variable_values = {"text": sample_text}
            system_vars = client.get_system_variables()
            
            # Generate the final prompt for chat
            final_prompt = client.substitute_variables(
                test_prompt['content'], 
                variable_values, 
                system_vars
            )
            
            logger.info(f"Final prompt for AI: {final_prompt[:100]}...")
            
            # Simulate chat interaction (without actually making API call)
            logger.info("🤖 [Simulated AI Response]")
            logger.info("   This would be the AI's response to the processed prompt...")
    
    else:
        logger.error("❌ No test prompt available for chat simulation")


def demonstrate_prompt_templates(client: OpenWebUIClient):
    """Demonstrate creating reusable prompt templates."""
    logger.info("\n=== Prompt Templates Demo ===")
    
    # Create templates for common patterns
    templates = [
        {
            "name": "analysis_template",
            "pattern": """Analyze the following {{item_type}}:

**Item:** {{item_name}}
**Context:** {{context}}
**Analysis Type:** {{analysis_type | select:options=["SWOT","Competitive","Technical","Financial"]}}
**Depth:** {{depth | select:options=["High-level","Detailed","Comprehensive"]}}
**Focus Areas:** {{focus_areas | textarea:placeholder="Specific areas to focus on"}}

Provide {{analysis_type}} analysis with actionable insights."""
        },
        {
            "name": "comparison_template", 
            "pattern": """Compare the following items:

**Item A:** {{item_a | text:placeholder="First item to compare"}}
**Item B:** {{item_b | text:placeholder="Second item to compare"}}
**Comparison Criteria:** {{criteria | textarea:placeholder="What aspects to compare"}}
**Output Format:** {{format | select:options=["Table","Pros/Cons","Detailed","Summary"]}}
**Decision Context:** {{context | text:placeholder="Why is this comparison needed?"}}

Provide comprehensive comparison to help with decision making."""
        },
        {
            "name": "planning_template",
            "pattern": """Create a plan for {{plan_type}}:

**Objective:** {{objective | text:placeholder="What you want to achieve"}}
**Timeline:** {{timeline | select:options=["1 Week","1 Month","3 Months","6 Months","1 Year"]}}
**Resources Available:** {{resources | textarea:placeholder="Budget, team, tools, etc."}}
**Constraints:** {{constraints | textarea:placeholder="Limitations or restrictions"}}
**Success Metrics:** {{metrics | textarea:placeholder="How will success be measured?"}}
**Risk Tolerance:** {{risk | select:options=["Conservative","Moderate","Aggressive"]}}

Develop a detailed, actionable plan with milestones and deliverables."""
        }
    ]
    
    created_templates = []
    for template in templates:
        logger.info(f"Creating template: {template['name']}")
        
        # Create specific prompts based on templates
        specific_prompts = [
            {
                "command": f"/{template['name']}_business",
                "title": f"Business {template['name'].replace('_', ' ').title()}",
                "content": template['pattern']
            },
            {
                "command": f"/{template['name']}_tech",
                "title": f"Technical {template['name'].replace('_', ' ').title()}",  
                "content": template['pattern']
            }
        ]
        
        for prompt_data in specific_prompts:
            created_prompt = client.create_prompt(**prompt_data)
            if created_prompt:
                created_templates.append(created_prompt)
                logger.info(f"✅ Created: {created_prompt['command']}")
    
    logger.info(f"Created {len(created_templates)} template-based prompts")


def cleanup_advanced_prompts(client: OpenWebUIClient):
    """Clean up all prompts created in this demo."""
    logger.info("\n=== Cleanup Advanced Prompts ===")
    
    # Get all prompts and identify demo prompts
    all_prompts = client.get_prompts()
    if not all_prompts:
        logger.info("No prompts found to clean up")
        return
    
    demo_patterns = [
        "/article_writer", "/bug_reporter", "/meeting_planner", "/social_campaign",
        "/quick_summary", "/software_development_", "/marketing_", "/education_",
        "/analysis_template_", "/comparison_template_", "/planning_template_"
    ]
    
    commands_to_delete = []
    for prompt in all_prompts:
        command = prompt.get('command', '')
        for pattern in demo_patterns:
            if pattern in command:
                commands_to_delete.append(command)
                break
    
    if commands_to_delete:
        logger.info(f"Cleaning up {len(commands_to_delete)} demo prompts...")
        cleanup_results = client.batch_delete_prompts(commands_to_delete, continue_on_error=True)
        logger.info(f"🧹 Cleanup completed: {len(cleanup_results['success'])} deleted, {len(cleanup_results['failed'])} failed")
    else:
        logger.info("No demo prompts found to clean up")


def main():
    """Main function demonstrating advanced prompts functionality."""
    # Validate environment variables
    if not AUTH_TOKEN:
        logger.error("❌ OUI_AUTH_TOKEN environment variable not set")
        logger.info("Please set your OpenWebUI API token:")
        logger.info("export OUI_AUTH_TOKEN='your_api_token_here'")
        return
    
    # Initialize client
    try:
        client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, DEFAULT_MODEL)
        logger.info("✅ Client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Client initialization failed: {e}")
        return
    
    try:
        # Run advanced demonstrations
        created_prompts = create_interactive_prompts(client)
        demonstrate_variable_parsing(client)
        demonstrate_dynamic_prompt_creation(client) 
        simulate_chat_with_prompts(client)
        demonstrate_prompt_templates(client)
        
        logger.info(f"\n🎉 Advanced prompts demonstration completed!")
        logger.info(f"Created {len(created_prompts)} interactive prompts ready for use.")
        
        # Optional cleanup
        response = input("\nDo you want to clean up demo prompts? (y/N): ")
        if response.lower() == 'y':
            cleanup_advanced_prompts(client)
        
    except Exception as e:
        logger.error(f"❌ Advanced demo failed: {e}")
        raise


if __name__ == "__main__":
    main()