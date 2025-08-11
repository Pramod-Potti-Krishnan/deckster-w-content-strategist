#!/usr/bin/env python3
"""
Create sample checkpoint files for testing
==========================================

This script generates sample checkpoint files for the default scenario
to enable testing of the checkpoint system.

Usage:
    python3 create_sample_checkpoints.py
"""

import json
import os
from datetime import datetime
from pathlib import Path


def create_sample_checkpoints():
    """Create sample checkpoint files for the default scenario."""
    
    # Base directory for checkpoints
    checkpoint_dir = Path(__file__).parent / "checkpoints" / "default"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # Complete strawman data for AI in Healthcare presentation
    full_strawman = {
        "main_title": "AI in Healthcare: Transforming Patient Care",
        "overall_theme": "Professional and data-driven",
        "design_suggestions": "Modern professional design with blue and green medical tones",
        "target_audience": "Healthcare professionals at a medical conference",
        "presentation_duration": 20,  # Integer, not string
        "theme_style": "professional",
        "formality_level": "moderate_professional",
        "visual_complexity": "balanced",
        "slides": [
            {
                "slide_id": "slide_001",
                "slide_number": 1,
                "slide_type": "title_slide",
                "title": "AI in Healthcare: Transforming Patient Care",
                "narrative": "Opening slide to grab the audience's attention and introduce the core topic",
                "key_points": [
                    "Dr. Sarah Johnson, MD, PhD",
                    "International Medical Conference 2024",
                    "December 2024"
                ],
                "visuals_needed": "Abstract graphic combining neural network patterns with medical symbols like heartbeat line or DNA helix. Modern, clean design with blue and green color palette.",
                "structure_preference": "full_bleed_visual"
            },
            {
                "slide_id": "slide_002",
                "slide_number": 2,
                "slide_type": "section_divider",
                "title": "Agenda: Our Journey Today",
                "narrative": "Sets expectations and provides a clear roadmap for the presentation",
                "key_points": [
                    "The AI Revolution in Healthcare",
                    "Diagnostic Applications & Case Studies",
                    "Impact on Patient Outcomes",
                    "Challenges & Regulatory Considerations",
                    "The Future of AI in Medicine"
                ],
                "visuals_needed": None,
                "structure_preference": "two_column"
            },
            {
                "slide_id": "slide_003",
                "slide_number": 3,
                "slide_type": "content_heavy",
                "title": "The AI Revolution is Already Here",
                "narrative": "Establish context and importance of AI in current healthcare landscape",
                "key_points": [
                    "78% of healthcare organizations now use AI in some capacity (2024 study)",
                    "AI can process medical images 150x faster than human radiologists",
                    "Machine Learning, Deep Learning, and NLP are transforming diagnostics"
                ],
                "visuals_needed": "High-quality photograph of diverse healthcare professionals collaborating around a screen displaying data visualizations",
                "analytics_needed": "Bar chart showing AI adoption rates in healthcare over the last 5 years",
                "structure_preference": "single_focal"
            },
            {
                "slide_id": "slide_004",
                "slide_number": 4,
                "slide_type": "diagram_focused",
                "title": "How AI Augments Diagnostic Accuracy",
                "narrative": "Explain the fundamental mechanism of how AI assists in diagnostics",
                "key_points": [
                    "AI algorithms trained on millions of medical images",
                    "Pattern recognition beyond human visual capability",
                    "Real-time analysis of pathology slides and genomic data"
                ],
                "diagrams_needed": "Flowchart showing: Medical Data Input → AI Processing → Pattern Recognition → Clinical Insights → Physician Review → Enhanced Diagnosis",
                "structure_preference": "centered_visual"
            },
            {
                "slide_id": "slide_005",
                "slide_number": 5,
                "slide_type": "data_driven",
                "title": "Case Study: AI in Radiology - Stanford Medical Center",
                "narrative": "Provide concrete proof of AI's effectiveness in real-world radiology",
                "key_points": [
                    "Implementation of AI-powered chest X-ray analysis system",
                    "95% accuracy in detecting pneumonia (vs 92% for radiologists alone)",
                    "Reduced diagnosis time from 30 minutes to 3 minutes",
                    "Identified 14% more early-stage lung nodules"
                ],
                "analytics_needed": "Comparison chart showing accuracy rates and time savings",
                "visuals_needed": "Medical imaging examples showing AI-highlighted areas of concern",
                "structure_preference": "two_column"
            },
            {
                "slide_id": "slide_006",
                "slide_number": 6,
                "slide_type": "data_driven",
                "title": "Case Study: Predictive Analytics at Mount Sinai",
                "narrative": "Showcase AI application in patient outcome prediction",
                "key_points": [
                    "AI model predicts sepsis 6 hours before traditional methods",
                    "30% reduction in sepsis-related mortality",
                    "Saved average of $5,000 per patient in ICU costs",
                    "Model analyzes 50+ variables in real-time"
                ],
                "analytics_needed": "Line graph showing prediction timeline and intervention points",
                "structure_preference": "single_focal"
            },
            {
                "slide_id": "slide_007",
                "slide_number": 7,
                "slide_type": "mixed_content",
                "title": "Balancing Benefits and Challenges",
                "narrative": "Present balanced perspective on AI implementation",
                "key_points": [
                    "Benefits: Increased accuracy, early detection, workflow efficiency, 24/7 availability",
                    "Challenges: Data privacy concerns, algorithm bias, integration costs, regulatory compliance"
                ],
                "visuals_needed": "Balanced scale graphic showing benefits vs challenges",
                "structure_preference": "two_column"
            },
            {
                "slide_id": "slide_008",
                "slide_number": 8,
                "slide_type": "content_heavy",
                "title": "Regulatory Landscape & Data Privacy",
                "narrative": "Address regulatory considerations and data privacy in AI implementation",
                "key_points": [
                    "FDA has approved 500+ AI/ML medical devices as of 2024",
                    "HIPAA compliance requirements for AI systems",
                    "EU AI Act implications for healthcare",
                    "Patient consent and data governance frameworks",
                    "Algorithmic accountability and explainability requirements"
                ],
                "visuals_needed": "Infographic showing regulatory framework hierarchy",
                "structure_preference": "three_column"
            },
            {
                "slide_id": "slide_009",
                "slide_number": 9,
                "slide_type": "diagram_focused",
                "title": "The Future: AI as a Clinical Partner",
                "narrative": "Inspire audience with vision of AI-augmented healthcare",
                "key_points": [
                    "Personalized treatment plans based on genetic markers",
                    "AI-powered drug discovery reducing development time by 70%",
                    "Virtual health assistants for continuous patient monitoring",
                    "The concept of the 'augmented clinician'"
                ],
                "diagrams_needed": "Timeline showing AI healthcare milestones from 2024-2030",
                "structure_preference": "timeline"
            },
            {
                "slide_id": "slide_010",
                "slide_number": 10,
                "slide_type": "conclusion_slide",
                "title": "Key Takeaways & Next Steps",
                "narrative": "Reinforce core message and provide clear action items",
                "key_points": [
                    "AI is not replacing doctors, it's empowering them",
                    "Start small: Identify one diagnostic area for AI pilot",
                    "Invest in data infrastructure and staff training",
                    "Join the AI in Healthcare Professional Network"
                ],
                "visuals_needed": "Professional headshot with contact information overlay",
                "structure_preference": "split_layout"
            }
        ]
    }
    
    # Base context for all stages
    base_context = {
        "current_state": "",
        "conversation_history": [],
        "session_data": {},
        "user_intent": "BUILD_PRESENTATION"
    }
    
    # Stage 1: After PROVIDE_GREETING (ready for ASK_CLARIFYING_QUESTIONS)
    stage_1 = {
        "checkpoint_version": "1.0",
        "scenario": "default",
        "stage": "ASK_CLARIFYING_QUESTIONS",
        "timestamp": datetime.utcnow().isoformat(),
        "context": {
            **base_context,
            "current_state": "ASK_CLARIFYING_QUESTIONS",
            "conversation_history": [
                {"role": "assistant", "content": "Hello! I'm Deckster, your AI presentation assistant. I can help you create professional, engaging presentations on any topic.\n\nWhat presentation would you like to build today?"},
                {"role": "user", "content": "I need a presentation about AI in healthcare, focusing on diagnostic applications and patient outcomes."}
            ],
            "session_data": {
                "user_initial_request": "I need a presentation about AI in healthcare, focusing on diagnostic applications and patient outcomes."
            }
        },
        "stage_outputs": {
            "greeting": "Hello! I'm Deckster, your AI presentation assistant. I can help you create professional, engaging presentations on any topic.\n\nWhat presentation would you like to build today?"
        }
    }
    
    # Stage 2: After ASK_CLARIFYING_QUESTIONS (ready for CREATE_CONFIRMATION_PLAN)
    stage_2 = {
        "checkpoint_version": "1.0",
        "scenario": "default",
        "stage": "CREATE_CONFIRMATION_PLAN",
        "timestamp": datetime.utcnow().isoformat(),
        "context": {
            **base_context,
            "current_state": "CREATE_CONFIRMATION_PLAN",
            "conversation_history": stage_1["context"]["conversation_history"] + [
                {"role": "assistant", "content": "Great topic! To create the perfect presentation for you, I need to understand your needs better:\n• Who is the target audience?\n• What is the primary goal?\n• How long should the presentation be?\n• Any specific diagnostic applications or patient outcomes to emphasize?"},
                {"role": "user", "content": "The audience will be healthcare professionals at a medical conference. They have basic understanding of AI but want practical applications. The presentation should be about 20 minutes long. Focus on recent case studies and real-world implementations. Include both benefits and challenges."}
            ],
            "session_data": {
                "user_initial_request": "I need a presentation about AI in healthcare, focusing on diagnostic applications and patient outcomes.",
                "clarifying_answers": {
                    "raw_answers": "The audience will be healthcare professionals at a medical conference. They have basic understanding of AI but want practical applications. The presentation should be about 20 minutes long. Focus on recent case studies and real-world implementations. Include both benefits and challenges.",
                    "parsed": {
                        "audience": "Healthcare professionals at a medical conference",
                        "audience_knowledge": "Basic understanding of AI",
                        "duration": "20 minutes",
                        "focus_areas": ["Recent case studies", "Real-world implementations"],
                        "requirements": ["Include benefits", "Include challenges", "Practical applications"]
                    }
                }
            }
        },
        "stage_outputs": {
            "greeting": "Hello! I'm Deckster, your AI presentation assistant.",
            "questions": {
                "questions": [
                    "Who is the target audience?",
                    "What is the primary goal?",
                    "How long should the presentation be?",
                    "Any specific diagnostic applications or patient outcomes to emphasize?"
                ],
                "follow_up": None
            }
        }
    }
    
    # Stage 3: After CREATE_CONFIRMATION_PLAN (ready for GENERATE_STRAWMAN)
    stage_3 = {
        "checkpoint_version": "1.0",
        "scenario": "default",
        "stage": "GENERATE_STRAWMAN",
        "timestamp": datetime.utcnow().isoformat(),
        "context": {
            **base_context,
            "current_state": "GENERATE_STRAWMAN",
            "conversation_history": stage_2["context"]["conversation_history"] + [
                {"role": "assistant", "content": "Perfect! Based on your input, I'll create a 10-slide presentation.\n• Focus on practical AI applications in diagnostics and patient outcomes\n• Include real-world case studies from leading hospitals\n• Address both advantages and implementation challenges\n• Tailored for healthcare professionals with actionable insights\n\nDoes this structure work for you?"},
                {"role": "user", "content": "Yes, this looks good. Please proceed with creating the presentation."}
            ],
            "session_data": {
                **stage_2["context"]["session_data"],
                "confirmation_plan": {
                    "title": "AI in Healthcare: Transforming Patient Care",
                    "slide_count": 10,
                    "main_sections": [
                        "Introduction & Context",
                        "AI in Diagnostics",
                        "Real-world Case Studies",
                        "Patient Outcome Improvements",
                        "Challenges & Considerations",
                        "Future Outlook"
                    ],
                    "target_audience": "Healthcare professionals at medical conference",
                    "duration": "20 minutes",
                    "key_themes": ["Practical applications", "Evidence-based results", "Balanced perspective"]
                }
            }
        },
        "stage_outputs": {
            **stage_2["stage_outputs"],
            "plan": {
                "title": "AI in Healthcare: Transforming Patient Care",
                "slide_count": 10,
                "structure": "Introduction → Current State → Case Studies → Benefits/Challenges → Future",
                "confirmed": True
            }
        }
    }
    
    # Stage 4: After GENERATE_STRAWMAN (ready for REFINE_STRAWMAN)
    stage_4 = {
        "checkpoint_version": "1.0",
        "scenario": "default",
        "stage": "REFINE_STRAWMAN",
        "timestamp": datetime.utcnow().isoformat(),
        "context": {
            **base_context,
            "current_state": "REFINE_STRAWMAN",
            "conversation_history": stage_3["context"]["conversation_history"] + [
                {"role": "assistant", "content": "📊 Presentation ready: AI in Healthcare: Transforming Patient Care\n10 slides | 20 minutes\n\nI've created a comprehensive structure covering:\n• The current state of AI in healthcare\n• Detailed case studies from Stanford and Mount Sinai\n• Impact on diagnostic accuracy and patient outcomes\n• Regulatory and privacy considerations\n• Future opportunities\n\nWould you like to make any changes?"},
                {"role": "user", "content": "Can you add more details about regulatory considerations and data privacy in the implementation section?"}
            ],
            "session_data": {
                **stage_3["context"]["session_data"],
                "presentation_strawman": full_strawman
            }
        },
        "stage_outputs": {
            **stage_3["stage_outputs"],
            "strawman": full_strawman
        }
    }
    
    # Stage 5: After REFINE_STRAWMAN (ready for CONTENT_GENERATION)
    # Updated strawman with enhanced regulatory content
    refined_strawman = {**full_strawman}
    refined_strawman["slides"][7]["key_points"].extend([
        "Algorithmic accountability and explainability requirements",
        "Cross-border data transfer regulations"
    ])
    
    stage_5 = {
        "checkpoint_version": "1.0",
        "scenario": "default",
        "stage": "CONTENT_GENERATION",
        "timestamp": datetime.utcnow().isoformat(),
        "context": {
            **base_context,
            "current_state": "CONTENT_GENERATION",
            "conversation_history": stage_4["context"]["conversation_history"] + [
                {"role": "assistant", "content": "I've updated slide 8 with comprehensive regulatory and data privacy details:\n• Added FDA approval statistics\n• Included HIPAA compliance requirements\n• Added EU AI Act implications\n• Enhanced data governance framework details\n\nThe presentation now provides thorough coverage of regulatory considerations. Ready to generate the detailed content?"},
                {"role": "user", "content": "Looks good! Let's see the detailed content for each slide."}
            ],
            "session_data": {
                **stage_4["context"]["session_data"],
                "presentation_strawman": refined_strawman,
                "strawman_metadata": {
                    "main_title": refined_strawman["main_title"],
                    "total_slides": len(refined_strawman["slides"]),
                    "audience": refined_strawman["target_audience"],
                    "duration": refined_strawman["presentation_duration"]
                }
            }
        },
        "stage_outputs": {
            **stage_4["stage_outputs"],
            "refined_strawman": refined_strawman,
            "refinement_changes": [
                {
                    "slide_id": "slide_008",
                    "changes": ["Added algorithmic accountability requirements", "Added cross-border data regulations"]
                }
            ]
        }
    }
    
    # Save all checkpoint files
    checkpoints = [
        ("stage_2_clarifying.json", stage_1),
        ("stage_3_confirmation.json", stage_2),
        ("stage_4_strawman.json", stage_3),
        ("stage_5_refined.json", stage_4),
        ("stage_6_content_ready.json", stage_5)
    ]
    
    for filename, data in checkpoints:
        filepath = checkpoint_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Created checkpoint: {filepath}")
    
    print(f"\n📋 All sample checkpoints created in: {checkpoint_dir}")
    print("\nYou can now test with commands like:")
    print("  python3 test/test_director_e2e.py --scenario default --start-stage CONTENT_GENERATION --no-images")
    print("  python3 test/test_director_e2e.py --checkpoint-file test/checkpoints/default/stage_4_strawman.json")
    print("\nEach checkpoint contains:")
    print("  • Complete conversation history")
    print("  • Full strawman with all 10 slides")
    print("  • Session data and context")
    print("  • Outputs from all previous stages")


if __name__ == "__main__":
    create_sample_checkpoints()