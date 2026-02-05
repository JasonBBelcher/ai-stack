"""
Clarification Engine - Interactive dialogue system for ambiguity resolution.

This component presents choices to users, handles their selections, and
manages the clarification dialogue flow.
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .ambiguity_detector import Ambiguity, AmbiguityType

logger = logging.getLogger(__name__)


class DialogueState(Enum):
    """States in the clarification dialogue"""
    INITIALIZING = "initializing"
    PRESENTING_CHOICES = "presenting_choices"
    WAITING_FOR_INPUT = "waiting_for_input"
    PROCESSING_INPUT = "processing_input"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Choice:
    """Represents a clarification choice"""
    id: str
    text: str
    description: str
    is_default: bool = False
    requires_input: bool = False


@dataclass
class ClarificationSession:
    """Represents an active clarification session"""
    session_id: str
    ambiguities: List[Ambiguity]
    current_index: int = 0
    state: DialogueState = DialogueState.INITIALIZING
    user_choices: Dict[str, Any] = None
    completed: bool = False
    
    def __post_init__(self):
        if self.user_choices is None:
            self.user_choices = {}


class ClarificationEngine:
    """Manages interactive clarification dialogues with users."""
    
    def __init__(self, verbosity: str = "normal"):
        """
        Initialize the clarification engine.
        
        Args:
            verbosity: Level of detail in clarifications ("minimal", "normal", "verbose")
        """
        self.verbosity = verbosity
        self.sessions: Dict[str, ClarificationSession] = {}
        self.session_counter = 0
    
    def start_session(self, ambiguities: List[Ambiguity]) -> ClarificationSession:
        """
        Start a new clarification session.
        
        Args:
            ambiguities: List of detected ambiguities
            
        Returns:
            New clarification session
        """
        self.session_counter += 1
        session_id = f"session_{self.session_counter}"
        
        session = ClarificationSession(
            session_id=session_id,
            ambiguities=ambiguities,
            state=DialogueState.INITIALIZING
        )
        
        self.sessions[session_id] = session
        logger.info(f"Started clarification session {session_id} with {len(ambiguities)} ambiguities")
        
        return session
    
    def generate_choices(self, ambiguity: Ambiguity) -> List[Choice]:
        """
        Generate clarification choices for an ambiguity.
        
        Args:
            ambiguity: The ambiguity to generate choices for
            
        Returns:
            List of clarification choices
        """
        choices = []
        
        if ambiguity.type == AmbiguityType.VAGUE_QUANTIFIER:
            choices = self._generate_quantifier_choices(ambiguity)
        elif ambiguity.type == AmbiguityType.UNDEFINED_TERM:
            choices = self._generate_term_choices(ambiguity)
        elif ambiguity.type == AmbiguityType.MISSING_CONTEXT:
            choices = self._generate_context_choices(ambiguity)
        elif ambiguity.type == AmbiguityType.AMBIGUOUS_REFERENCE:
            choices = self._generate_reference_choices(ambiguity)
        elif ambiguity.type == AmbiguityType.UNCLEAR_SCOPE:
            choices = self._generate_scope_choices(ambiguity)
        elif ambiguity.type == AmbiguityType.SUBJECTIVE_CRITERIA:
            choices = self._generate_criteria_choices(ambiguity)
        
        # Add a "skip" option
        choices.append(Choice(
            id="skip",
            text="Skip this ambiguity",
            description="Proceed without clarifying this point",
            is_default=True
        ))
        
        return choices
    
    def _generate_quantifier_choices(self, ambiguity: Ambiguity) -> List[Choice]:
        """Generate choices for vague quantifiers."""
        return [
            Choice(
                id="specify_number",
                text="Specify exact number",
                description=f"Replace '{ambiguity.text}' with a specific number",
                requires_input=True
            ),
            Choice(
                id="specify_range",
                text="Specify range",
                description=f"Replace '{ambiguity.text}' with a range (e.g., 3-5)",
                requires_input=True
            ),
            Choice(
                id="specify_percentage",
                text="Specify percentage",
                description=f"Replace '{ambiguity.text}' with a percentage",
                requires_input=True
            )
        ]
    
    def _generate_term_choices(self, ambiguity: Ambiguity) -> List[Choice]:
        """Generate choices for undefined terms."""
        term = ambiguity.text.lower()
        
        if term in ['better', 'improve', 'enhance']:
            return [
                Choice(
                    id="improve_performance",
                    text="Improve performance",
                    description="Focus on speed, efficiency, and resource usage"
                ),
                Choice(
                    id="improve_quality",
                    text="Improve code quality",
                    description="Focus on readability, maintainability, and structure"
                ),
                Choice(
                    id="improve_ux",
                    text="Improve user experience",
                    description="Focus on usability, interface, and user satisfaction"
                ),
                Choice(
                    id="improve_features",
                    text="Improve functionality",
                    description="Focus on features, capabilities, and completeness"
                ),
                Choice(
                    id="custom_improvement",
                    text="Specify custom improvement",
                    description="Define your own improvement criteria",
                    requires_input=True
                )
            ]
        elif term in ['faster', 'quicker', 'speed up', 'accelerate']:
            return [
                Choice(
                    id="optimize_algorithms",
                    text="Optimize algorithms",
                    description="Improve algorithmic complexity and efficiency"
                ),
                Choice(
                    id="add_caching",
                    text="Add caching",
                    description="Implement caching to reduce redundant computations"
                ),
                Choice(
                    id="reduce_network",
                    text="Reduce network calls",
                    description="Minimize network requests and data transfer"
                ),
                Choice(
                    id="parallelize",
                    text="Parallelize operations",
                    description="Use concurrent/parallel processing"
                )
            ]
        elif term in ['easier', 'simpler', 'streamline']:
            return [
                Choice(
                    id="simplify_api",
                    text="Simplify API/Interface",
                    description="Make the interface more intuitive and straightforward"
                ),
                Choice(
                    id="reduce_complexity",
                    text="Reduce complexity",
                    description="Simplify internal logic and architecture"
                ),
                Choice(
                    id="improve_docs",
                    text="Improve documentation",
                    description="Add better documentation and examples"
                ),
                Choice(
                    id="add_automation",
                    text="Add automation",
                    description="Automate repetitive tasks"
                )
            ]
        else:
            return [
                Choice(
                    id="define_criteria",
                    text="Define criteria",
                    description="Specify what you want to improve",
                    requires_input=True
                )
            ]
    
    def _generate_context_choices(self, ambiguity: Ambiguity) -> List[Choice]:
        """Generate choices for missing context."""
        return [
            Choice(
                id="specify_name",
                text="Specify exact name",
                description=f"Provide the exact name instead of '{ambiguity.text}'",
                requires_input=True
            ),
            Choice(
                id="specify_path",
                text="Specify file path",
                description="Provide the full file path",
                requires_input=True
            ),
            Choice(
                id="describe_component",
                text="Describe component",
                description="Describe the component you're referring to",
                requires_input=True
            )
        ]
    
    def _generate_reference_choices(self, ambiguity: Ambiguity) -> List[Choice]:
        """Generate choices for ambiguous references."""
        return [
            Choice(
                id="replace_with_name",
                text="Replace with specific name",
                description=f"Replace '{ambiguity.text}' with the actual name",
                requires_input=True
            ),
            Choice(
                id="clarify_context",
                text="Clarify context",
                description="Provide more context about what you're referring to",
                requires_input=True
            )
        ]
    
    def _generate_scope_choices(self, ambiguity: Ambiguity) -> List[Choice]:
        """Generate choices for unclear scope."""
        return [
            Choice(
                id="limit_specific",
                text="Limit to specific files",
                description="Specify which files to include",
                requires_input=True
            ),
            Choice(
                id="limit_modules",
                text="Limit to specific modules",
                description="Specify which modules to include",
                requires_input=True
            ),
            Choice(
                id="define_boundaries",
                text="Define boundaries",
                description="Specify what to include and exclude",
                requires_input=True
            )
        ]
    
    def _generate_criteria_choices(self, ambiguity: Ambiguity) -> List[Choice]:
        """Generate choices for subjective criteria."""
        return [
            Choice(
                id="define_objective",
                text="Define objective criteria",
                description="Specify measurable, objective criteria",
                requires_input=True
            ),
            Choice(
                id="provide_examples",
                text="Provide examples",
                description="Give examples of what you consider good/bad",
                requires_input=True
            ),
            Choice(
                id="specify_requirements",
                text="Specify requirements",
                description="List specific requirements",
                requires_input=True
            )
        ]
    
    def format_choices(self, choices: List[Choice], ambiguity: Ambiguity) -> str:
        """
        Format choices for presentation to the user.
        
        Args:
            choices: List of choices to format
            ambiguity: The ambiguity being clarified
            
        Returns:
            Formatted string with choices
        """
        lines = []
        
        # Header
        lines.append(f"\n{'=' * 60}")
        lines.append(f"Ambiguity Detected: {ambiguity.text}")
        lines.append(f"Type: {ambiguity.type.value}")
        lines.append(f"Confidence: {ambiguity.confidence:.2f}")
        lines.append(f"{'=' * 60}\n")
        
        # Suggestions
        if self.verbosity != "minimal":
            lines.append("Suggestions:")
            for i, suggestion in enumerate(ambiguity.suggestions[:3], 1):
                lines.append(f"  {i}. {suggestion}")
            lines.append("")
        
        # Choices
        lines.append("Please choose an option:")
        for i, choice in enumerate(choices, 1):
            marker = " (default)" if choice.is_default else ""
            input_marker = " [requires input]" if choice.requires_input else ""
            lines.append(f"  {i}. {choice.text}{marker}{input_marker}")
            if self.verbosity == "verbose":
                lines.append(f"     {choice.description}")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def process_choice(self, session: ClarificationSession, choice_id: str, 
                      user_input: Optional[str] = None) -> bool:
        """
        Process a user's choice in a clarification session.
        
        Args:
            session: The clarification session
            choice_id: The ID of the chosen option
            user_input: Optional user input for choices that require it
            
        Returns:
            True if the choice was processed successfully
        """
        ambiguity = session.ambiguities[session.current_index]
        
        # Store the choice
        session.user_choices[f"ambiguity_{session.current_index}"] = {
            "ambiguity_text": ambiguity.text,
            "choice_id": choice_id,
            "user_input": user_input
        }
        
        # Move to next ambiguity
        session.current_index += 1
        
        # Check if session is complete
        if session.current_index >= len(session.ambiguities):
            session.state = DialogueState.COMPLETED
            session.completed = True
            logger.info(f"Clarification session {session.session_id} completed")
        else:
            session.state = DialogueState.PRESENTING_CHOICES
        
        return True
    
    def get_next_ambiguity(self, session: ClarificationSession) -> Optional[Ambiguity]:
        """
        Get the next ambiguity to clarify in a session.
        
        Args:
            session: The clarification session
            
        Returns:
            Next ambiguity or None if session is complete
        """
        if session.current_index >= len(session.ambiguities):
            return None
        
        return session.ambiguities[session.current_index]
    
    def get_session_summary(self, session: ClarificationSession) -> Dict[str, Any]:
        """
        Get a summary of a clarification session.
        
        Args:
            session: The clarification session
            
        Returns:
            Dictionary with session summary
        """
        return {
            "session_id": session.session_id,
            "total_ambiguities": len(session.ambiguities),
            "clarified": session.current_index,
            "skipped": sum(1 for c in session.user_choices.values() if c.get("choice_id") == "skip"),
            "completed": session.completed,
            "state": session.state.value,
            "choices": session.user_choices
        }
    
    def apply_clarifications(self, original_request: str, 
                            session: ClarificationSession) -> str:
        """
        Apply clarifications to the original request.
        
        Args:
            original_request: The original user request
            session: The clarification session with user choices
            
        Returns:
            Clarified request string
        """
        clarified = original_request
        
        # Apply each clarification in order
        for i, ambiguity in enumerate(session.ambiguities):
            choice_key = f"ambiguity_{i}"
            if choice_key not in session.user_choices:
                continue
            
            choice_data = session.user_choices[choice_key]
            choice_id = choice_data["choice_id"]
            user_input = choice_data.get("user_input")
            
            # Skip if user chose to skip
            if choice_id == "skip":
                continue
            
            # Apply clarification based on choice
            if user_input:
                # Replace ambiguity text with user input
                clarified = clarified.replace(ambiguity.text, user_input, 1)
            elif choice_id.startswith("improve_"):
                # Add context to improvement terms
                improvement_type = choice_id.replace("improve_", "")
                context_map = {
                    "performance": " (performance: speed, efficiency)",
                    "quality": " (code quality: readability, maintainability)",
                    "ux": " (user experience: usability, interface)",
                    "features": " (functionality: features, capabilities)"
                }
                if improvement_type in context_map:
                    clarified = clarified.replace(ambiguity.text, 
                                                 f"{ambiguity.text}{context_map[improvement_type]}", 1)
        
        logger.info(f"Applied clarifications to request")
        return clarified
    
    def cancel_session(self, session: ClarificationSession):
        """
        Cancel a clarification session.
        
        Args:
            session: The session to cancel
        """
        session.state = DialogueState.CANCELLED
        session.completed = True
        logger.info(f"Clarification session {session.session_id} cancelled")