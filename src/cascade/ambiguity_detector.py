"""
Ambiguity Detector - Identifies ambiguous requests and generates interpretations.

This component analyzes user requests to detect undefined terms, vague language,
and generates multiple possible interpretations with confidence scores.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AmbiguityType(Enum):
    """Types of ambiguities that can be detected"""
    VAGUE_QUANTIFIER = "vague_quantifier"  # "some", "a few", "many"
    UNDEFINED_TERM = "undefined_term"  # "better", "faster", "improve"
    MISSING_CONTEXT = "missing_context"  # "the file", "that function"
    AMBIGUOUS_REFERENCE = "ambiguous_reference"  # "it", "they", "this"
    UNCLEAR_SCOPE = "unclear_scope"  # "the whole project", "everything"
    SUBJECTIVE_CRITERIA = "subjective_criteria"  # "good", "bad", "nice"


@dataclass
class Ambiguity:
    """Represents a detected ambiguity"""
    type: AmbiguityType
    text: str
    position: int
    confidence: float
    interpretations: List[str]
    suggestions: List[str]


class AmbiguityDetector:
    """Detects ambiguities in user requests and generates interpretations."""
    
    def __init__(self):
        """Initialize the ambiguity detector with patterns and rules."""
        # Vague quantifiers
        self.vague_quantifiers = [
            r'\b(some|a few|several|many|lots of|a lot|plenty)\b',
            r'\b(a bit|a little|somewhat|rather|quite)\b',
        ]
        
        # Undefined terms (subjective or context-dependent)
        self.undefined_terms = [
            r'\b(better|improve|enhance|optimize|boost)\b',
            r'\b(faster|quicker|speed up|accelerate)\b',
            r'\b(easier|simpler|streamline)\b',
            r'\b(cleaner|tidier|organize)\b',
            r'\b(more efficient|efficient|effective)\b',
            r'\b(user-friendly|intuitive|usable)\b',
            r'\b(modern|up-to-date|current)\b',
            r'\b(professional|polished|refined)\b',
        ]
        
        # Missing context indicators
        self.missing_context_patterns = [
            r'\b(the file|the function|the class|the module)\b(?!\s+\w+)',
            r'\b(that|this|it|they|them)\s+(one|thing|stuff)\b',
        ]
        
        # Ambiguous references
        self.ambiguous_references = [
            r'\b(it|they|them|this|that)\s+(?!(?:is|are|was|were|will|would|should|could|can|may|might))',
        ]
        
        # Unclear scope
        self.unclear_scope_patterns = [
            r'\b(the whole|entire|all|everything)\b',
            r'\b(completely|totally|fully|thoroughly)\b',
        ]
        
        # Subjective criteria
        self.subjective_criteria = [
            r'\b(good|bad|nice|great|awesome|terrible|awful)\b',
            r'\b(best|worst|perfect|ideal)\b',
        ]
        
        # Compile regex patterns
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile all regex patterns for efficiency."""
        self.vague_quantifier_patterns = [re.compile(p, re.IGNORECASE) for p in self.vague_quantifiers]
        self.undefined_term_patterns = [re.compile(p, re.IGNORECASE) for p in self.undefined_terms]
        self.missing_context_patterns_compiled = [re.compile(p, re.IGNORECASE) for p in self.missing_context_patterns]
        self.ambiguous_reference_patterns = [re.compile(p, re.IGNORECASE) for p in self.ambiguous_references]
        self.unclear_scope_patterns_compiled = [re.compile(p, re.IGNORECASE) for p in self.unclear_scope_patterns]
        self.subjective_criteria_patterns = [re.compile(p, re.IGNORECASE) for p in self.subjective_criteria]
    
    def detect(self, user_input: str) -> List[Ambiguity]:
        """
        Detect ambiguities in the user's request.
        
        Args:
            user_input: The user's request string
            
        Returns:
            List of detected ambiguities
        """
        ambiguities = []
        
        # Detect vague quantifiers
        ambiguities.extend(self._detect_vague_quantifiers(user_input))
        
        # Detect undefined terms
        ambiguities.extend(self._detect_undefined_terms(user_input))
        
        # Detect missing context
        ambiguities.extend(self._detect_missing_context(user_input))
        
        # Detect ambiguous references
        ambiguities.extend(self._detect_ambiguous_references(user_input))
        
        # Detect unclear scope
        ambiguities.extend(self._detect_unclear_scope(user_input))
        
        # Detect subjective criteria
        ambiguities.extend(self._detect_subjective_criteria(user_input))
        
        # Sort by confidence (highest first)
        ambiguities.sort(key=lambda a: a.confidence, reverse=True)
        
        logger.info(f"Detected {len(ambiguities)} ambiguities in request")
        return ambiguities
    
    def _detect_vague_quantifiers(self, text: str) -> List[Ambiguity]:
        """Detect vague quantifiers in the text."""
        ambiguities = []
        
        for pattern in self.vague_quantifier_patterns:
            for match in pattern.finditer(text):
                ambiguity = Ambiguity(
                    type=AmbiguityType.VAGUE_QUANTIFIER,
                    text=match.group(),
                    position=match.start(),
                    confidence=0.7,
                    interpretations=self._generate_quantifier_interpretations(match.group()),
                    suggestions=self._generate_quantifier_suggestions(match.group())
                )
                ambiguities.append(ambiguity)
        
        return ambiguities
    
    def _detect_undefined_terms(self, text: str) -> List[Ambiguity]:
        """Detect undefined terms in the text."""
        ambiguities = []
        
        for pattern in self.undefined_term_patterns:
            for match in pattern.finditer(text):
                ambiguity = Ambiguity(
                    type=AmbiguityType.UNDEFINED_TERM,
                    text=match.group(),
                    position=match.start(),
                    confidence=0.8,
                    interpretations=self._generate_term_interpretations(match.group()),
                    suggestions=self._generate_term_suggestions(match.group())
                )
                ambiguities.append(ambiguity)
        
        return ambiguities
    
    def _detect_missing_context(self, text: str) -> List[Ambiguity]:
        """Detect missing context in the text."""
        ambiguities = []
        
        for pattern in self.missing_context_patterns_compiled:
            for match in pattern.finditer(text):
                ambiguity = Ambiguity(
                    type=AmbiguityType.MISSING_CONTEXT,
                    text=match.group(),
                    position=match.start(),
                    confidence=0.9,
                    interpretations=self._generate_context_interpretations(match.group()),
                    suggestions=self._generate_context_suggestions(match.group())
                )
                ambiguities.append(ambiguity)
        
        return ambiguities
    
    def _detect_ambiguous_references(self, text: str) -> List[Ambiguity]:
        """Detect ambiguous references in the text."""
        ambiguities = []
        
        for pattern in self.ambiguous_reference_patterns:
            for match in pattern.finditer(text):
                ambiguity = Ambiguity(
                    type=AmbiguityType.AMBIGUOUS_REFERENCE,
                    text=match.group(),
                    position=match.start(),
                    confidence=0.85,
                    interpretations=self._generate_reference_interpretations(match.group()),
                    suggestions=self._generate_reference_suggestions(match.group())
                )
                ambiguities.append(ambiguity)
        
        return ambiguities
    
    def _detect_unclear_scope(self, text: str) -> List[Ambiguity]:
        """Detect unclear scope in the text."""
        ambiguities = []
        
        for pattern in self.unclear_scope_patterns_compiled:
            for match in pattern.finditer(text):
                ambiguity = Ambiguity(
                    type=AmbiguityType.UNCLEAR_SCOPE,
                    text=match.group(),
                    position=match.start(),
                    confidence=0.75,
                    interpretations=self._generate_scope_interpretations(match.group()),
                    suggestions=self._generate_scope_suggestions(match.group())
                )
                ambiguities.append(ambiguity)
        
        return ambiguities
    
    def _detect_subjective_criteria(self, text: str) -> List[Ambiguity]:
        """Detect subjective criteria in the text."""
        ambiguities = []
        
        for pattern in self.subjective_criteria_patterns:
            for match in pattern.finditer(text):
                ambiguity = Ambiguity(
                    type=AmbiguityType.SUBJECTIVE_CRITERIA,
                    text=match.group(),
                    position=match.start(),
                    confidence=0.65,
                    interpretations=self._generate_criteria_interpretations(match.group()),
                    suggestions=self._generate_criteria_suggestions(match.group())
                )
                ambiguities.append(ambiguity)
        
        return ambiguities
    
    def _generate_quantifier_interpretations(self, text: str) -> List[str]:
        """Generate interpretations for vague quantifiers."""
        return [
            f"Specify exact number (e.g., '3 items', '5 functions')",
            f"Specify range (e.g., '3-5 items', '5-10 functions')",
            f"Specify percentage (e.g., '50% of items', 'all functions')"
        ]
    
    def _generate_quantifier_suggestions(self, text: str) -> List[str]:
        """Generate suggestions for vague quantifiers."""
        return [
            "Be more specific about quantity",
            "Use exact numbers or ranges",
            "Define what 'some' means in your context"
        ]
    
    def _generate_term_interpretations(self, text: str) -> List[str]:
        """Generate interpretations for undefined terms."""
        term = text.lower()
        
        if term in ['better', 'improve', 'enhance']:
            return [
                "Improve performance (speed, efficiency)",
                "Improve code quality (readability, maintainability)",
                "Improve user experience (usability, interface)",
                "Improve functionality (features, capabilities)"
            ]
        elif term in ['faster', 'quicker', 'speed up', 'accelerate']:
            return [
                "Reduce execution time",
                "Optimize algorithms",
                "Improve caching",
                "Reduce network calls"
            ]
        elif term in ['easier', 'simpler', 'streamline']:
            return [
                "Simplify API/Interface",
                "Reduce complexity",
                "Improve documentation",
                "Add automation"
            ]
        else:
            return [
                "Define specific improvement criteria",
                "Specify what aspect to improve",
                "Provide measurable goals"
            ]
    
    def _generate_term_suggestions(self, text: str) -> List[str]:
        """Generate suggestions for undefined terms."""
        return [
            "Specify what you want to improve",
            "Define measurable criteria",
            "Provide context or examples"
        ]
    
    def _generate_context_interpretations(self, text: str) -> List[str]:
        """Generate interpretations for missing context."""
        return [
            "Specify the exact file/function/class name",
            "Provide the file path",
            "Describe the component you're referring to"
        ]
    
    def _generate_context_suggestions(self, text: str) -> List[str]:
        """Generate suggestions for missing context."""
        return [
            "Use specific names instead of 'the file'",
            "Provide file paths or module names",
            "Reference specific components by name"
        ]
    
    def _generate_reference_interpretations(self, text: str) -> List[str]:
        """Generate interpretations for ambiguous references."""
        return [
            "Replace with the specific item name",
            "Clarify what 'it' refers to",
            "Use the actual noun instead of pronoun"
        ]
    
    def _generate_reference_suggestions(self, text: str) -> List[str]:
        """Generate suggestions for ambiguous references."""
        return [
            "Be explicit about what you're referring to",
            "Use specific names instead of pronouns",
            "Provide more context"
        ]
    
    def _generate_scope_interpretations(self, text: str) -> List[str]:
        """Generate interpretations for unclear scope."""
        return [
            "Limit to specific files/modules",
            "Define boundaries clearly",
            "Specify what to include/exclude"
        ]
    
    def _generate_scope_suggestions(self, text: str) -> List[str]:
        """Generate suggestions for unclear scope."""
        return [
            "Be specific about what to change",
            "Define the scope clearly",
            "List specific files or components"
        ]
    
    def _generate_criteria_interpretations(self, text: str) -> List[str]:
        """Generate interpretations for subjective criteria."""
        return [
            "Define objective criteria",
            "Provide measurable goals",
            "Specify what 'good' means in your context"
        ]
    
    def _generate_criteria_suggestions(self, text: str) -> List[str]:
        """Generate suggestions for subjective criteria."""
        return [
            "Use objective, measurable criteria",
            "Define specific requirements",
            "Provide examples of desired outcome"
        ]
    
    def get_ambiguity_summary(self, ambiguities: List[Ambiguity]) -> Dict[str, Any]:
        """
        Get a summary of detected ambiguities.
        
        Args:
            ambiguities: List of detected ambiguities
            
        Returns:
            Dictionary with ambiguity summary
        """
        if not ambiguities:
            return {
                "has_ambiguities": False,
                "count": 0,
                "types": [],
                "high_confidence": 0
            }
        
        # Count by type
        type_counts = {}
        for ambiguity in ambiguities:
            type_name = ambiguity.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Count high confidence ambiguities
        high_confidence = sum(1 for a in ambiguities if a.confidence >= 0.8)
        
        return {
            "has_ambiguities": True,
            "count": len(ambiguities),
            "types": list(type_counts.keys()),
            "type_counts": type_counts,
            "high_confidence": high_confidence,
            "average_confidence": sum(a.confidence for a in ambiguities) / len(ambiguities)
        }