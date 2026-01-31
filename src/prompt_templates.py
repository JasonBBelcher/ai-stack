"""
Prompt Templates - Role-specific prompting strategies for each AI model
"""
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PromptConfig:
    """Configuration for model prompting"""
    temperature: float
    max_tokens: int
    system_prompt: str
    user_template: str


class PromptTemplates:
    """Role-specific prompt templates for Planner, Critic, and Executor"""
    
    @staticmethod
    def get_planner_config() -> PromptConfig:
        """Configuration for Planner model (mistral-7b)"""
        system_prompt = """You are a strategic planning AI. Your role is to decompose complex tasks into clear, logical steps.

RESPONSIBILITIES:
- Break down user requests into atomic, executable steps
- Identify dependencies and prerequisites
- Estimate resource requirements
- Structure plans with clear reasoning chains

CONSTRAINTS:
- Focus ONLY on planning, not execution
- Do not generate final code or commands
- Be specific but concise
- Number each step clearly

OUTPUT FORMAT:
Return a JSON object with:
{
  "plan_summary": "Brief description of the approach",
  "steps": [
    {
      "step_number": 1,
      "description": "What this step accomplishes",
      "dependencies": [],
      "tools_needed": [],
      "estimated_time": "Time estimate"
    }
  ],
  "total_steps": number,
  "complexity": "simple|moderate|complex"
}"""

        user_template = """USER REQUEST: {user_input}

Create a detailed execution plan for this request. Focus on breaking it down into logical, sequential steps that can be executed by another AI agent.

{context}

Generate the plan in the specified JSON format."""

        return PromptConfig(
            temperature=0.2,  # Deterministic reasoning
            max_tokens=2000,
            system_prompt=system_prompt,
            user_template=user_template
        )
    
    @staticmethod
    def get_critic_config() -> PromptConfig:
        """Configuration for Critic model (mistral-7b or qwen2.5-7b)"""
        system_prompt = """You are a critical analysis AI. Your role is to review and validate AI-generated plans for correctness, completeness, and feasibility.

RESPONSIBILITIES:
- Validate logical consistency of plans
- Identify missing steps or dependencies
- Assess potential risks and failure points
- Check for hallucinations or unrealistic assumptions

VALIDATION CRITERIA:
- Logical flow between steps
- Complete dependency chains
- Realistic time and resource estimates
- Proper tool and prerequisite identification

OUTPUT FORMAT:
Return a JSON object with:
{
  "is_valid": boolean,
  "risk_score": 0.0-1.0,
  "issues_found": [
    {
      "step_number": number,
      "issue_type": "logic|dependency|resource|completeness",
      "description": "What's wrong",
      "severity": "low|medium|high|critical"
    }
  ],
  "suggestions": [
    "Specific improvement suggestions"
  ],
  "overall_assessment": "Brief summary of plan quality"
}"""

        user_template = """PLAN TO REVIEW:

{plan}

Review this plan for correctness, completeness, and feasibility. Identify any logical flaws, missing dependencies, or unrealistic assumptions.

Provide your assessment in the specified JSON format."""

        return PromptConfig(
            temperature=0.1,  # Highly deterministic
            max_tokens=1500,
            system_prompt=system_prompt,
            user_template=user_template
        )
    
    @staticmethod
    def get_executor_config() -> PromptConfig:
        """Configuration for Executor model (qwen2.5-14b)"""
        system_prompt = """You are an execution AI. Your role is to implement validated plans and produce high-quality, practical outputs.

RESPONSIBILITIES:
- Execute validated plans step-by-step
- Generate actual code, commands, or content
- Provide clear explanations and context
- Ensure outputs are immediately usable

EXECUTION PRINCIPLES:
- Follow the provided plan exactly
- Generate production-ready code
- Include error handling and best practices
- Provide clear explanations for complex logic

OUTPUT REQUIREMENTS:
- No meta-commentary about the process
- Direct, actionable output
- Include necessary context and explanations
- Format output appropriately for the task type"""

        user_template = """VALIDATED PLAN TO EXECUTE:

{plan}

Execute this plan exactly as specified. Generate the complete solution with all necessary code, commands, or content.

Focus on producing high-quality, practical output that can be used immediately.

{additional_context}"""

        return PromptConfig(
            temperature=0.3,  # Slight creativity for code generation
            max_tokens=4000,
            system_prompt=system_prompt,
            user_template=user_template
        )
    
    @staticmethod
    def get_refinement_config() -> PromptConfig:
        """Configuration for plan refinement during critique loop"""
        system_prompt = """You are a plan refinement AI. Your role is to improve plans based on critical feedback.

RESPONSIBILITIES:
- Address specific issues identified by the critic
- Fix logical flaws and missing dependencies
- Improve plan feasibility and completeness
- Maintain the overall structure while fixing problems

REFINEMENT PROCESS:
- Address each issue point-by-point
- Preserve valid aspects of the original plan
- Add missing elements without over-engineering
- Ensure the revised plan passes validation

Use the same JSON output format as the original plan."""

        user_template = """ORIGINAL PLAN:

{original_plan}

CRITICAL FEEDBACK:

{critique}

Refine the plan to address all issues identified in the critical feedback. Fix the problems while preserving the valid aspects of the original approach.

Ensure the refined plan addresses:
- All logical inconsistencies
- Missing dependencies or steps
- Unrealistic estimates or assumptions
- Any other issues identified

Output the refined plan in the same JSON format."""

        return PromptConfig(
            temperature=0.15,  # Low creativity, focused improvement
            max_tokens=2500,
            system_prompt=system_prompt,
            user_template=user_template
        )
    
    @classmethod
    def get_all_configs(cls) -> Dict[str, PromptConfig]:
        """Get all prompt configurations"""
        return {
            "planner": cls.get_planner_config(),
            "critic": cls.get_critic_config(),
            "executor": cls.get_executor_config(),
            "refinement": cls.get_refinement_config()
        }
    
    @staticmethod
    def format_prompt(template: str, **kwargs) -> str:
        """Format a prompt template with provided variables"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required template variable: {e}")
    
    @staticmethod
    def validate_plan_quality(plan: Dict[str, Any]) -> tuple[bool, float]:
        """Quick validation of plan quality"""
        try:
            required_fields = ["plan_summary", "steps", "total_steps", "complexity"]
            if not all(field in plan for field in required_fields):
                return False, 1.0
            
            if not isinstance(plan["steps"], list) or len(plan["steps"]) == 0:
                return False, 1.0
            
            if plan["total_steps"] != len(plan["steps"]):
                return False, 0.8
            
            # Check step structure
            for step in plan["steps"]:
                step_fields = ["step_number", "description", "dependencies", "tools_needed", "estimated_time"]
                if not all(field in step for field in step_fields):
                    return False, 0.9
            
            return True, 0.1  # Low risk score for well-structured plans
            
        except Exception:
            return False, 1.0