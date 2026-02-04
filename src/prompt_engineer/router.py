"""
Intent Router - Classify user intents and route to appropriate prompt templates.
"""

import re
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents"""
    DEBUG = "debug"
    GENERATE = "generate"
    EXPLAIN = "explain"
    GENERAL = "general"


class IntentRouter:
    """Rule-based intent classifier for routing user requests."""
    
    def __init__(self):
        """Initialize the intent router with keyword patterns."""
        self.debug_keywords = [
            # Error-related
            r'\b(error|exception|bug|issue|problem|fail|crash|broken)\b',
            r'\b(stack trace|traceback|error message)\b',
            r'\b(debug|debugging|fix|repair|resolve)\b',
            r'\b(not working|doesn\'t work|won\'t work)\b',
            r'\b(wrong|incorrect|unexpected|unexpectedly)\b',
            # Specific error patterns
            r'\b(NameError|TypeError|ValueError|AttributeError|KeyError|IndexError|ImportError)\b',
            r'\b(NullPointerException|NullReference|undefined|null)\b',
        ]
        
        self.generate_keywords = [
            # Creation-related
            r'\b(create|write|generate|implement|build|develop|make)\b',
            r'\b(add|new|addition)\b',
            r'\b(function|class|method|module|package)\b',
            r'\b(code|script|program|application)\b',
            r'\b(feature|functionality|capability)\b',
            r'\b(api|endpoint|route|handler)\b',
            r'\b(database|model|schema|migration)\b',
            r'\b(test|unit test|integration test)\b',
        ]
        
        self.explain_keywords = [
            # Understanding-related
            r'\b(explain|explain to me|what is|how does|how do)\b',
            r'\b(understand|understanding|clarify)\b',
            r'\b(what does|what\'s the|what are)\b',
            r'\b(why|why does|why is)\b',
            r'\b(how|how to|how can)\b',
            r'\b(describe|describe the|overview|summary)\b',
            r'\b(documentation|docs|readme)\b',
            r'\b(purpose|function|role|responsibility)\b',
        ]
        
        # Compile regex patterns
        self.debug_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.debug_keywords]
        self.generate_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.generate_keywords]
        self.explain_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.explain_keywords]
    
    def classify(self, user_input: str) -> IntentType:
        """
        Classify the user's intent based on keywords and patterns.
        
        Args:
            user_input: The user's request string
            
        Returns:
            IntentType enum value
        """
        if not user_input:
            return IntentType.GENERAL
        
        # Count matches for each intent type
        debug_score = sum(1 for pattern in self.debug_patterns if pattern.search(user_input))
        generate_score = sum(1 for pattern in self.generate_patterns if pattern.search(user_input))
        explain_score = sum(1 for pattern in self.explain_patterns if pattern.search(user_input))
        
        # Determine intent based on highest score
        scores = {
            IntentType.DEBUG: debug_score,
            IntentType.GENERATE: generate_score,
            IntentType.EXPLAIN: explain_score,
            IntentType.GENERAL: 0
        }
        
        # Find the intent with the highest score
        max_score = max(scores.values())
        
        if max_score == 0:
            return IntentType.GENERAL
        
        # Get all intents with the max score
        top_intents = [intent for intent, score in scores.items() if score == max_score]
        
        # If there's a tie, prefer DEBUG > GENERATE > EXPLAIN > GENERAL
        if IntentType.DEBUG in top_intents:
            return IntentType.DEBUG
        elif IntentType.GENERATE in top_intents:
            return IntentType.GENERATE
        elif IntentType.EXPLAIN in top_intents:
            return IntentType.EXPLAIN
        else:
            return IntentType.GENERAL
    
    def get_intent_info(self, user_input: str) -> Dict[str, Any]:
        """
        Get detailed information about the classified intent.
        
        Args:
            user_input: The user's request string
            
        Returns:
            Dictionary with intent information
        """
        intent = self.classify(user_input)
        
        return {
            "intent": intent.value,
            "confidence": self._calculate_confidence(user_input, intent),
            "matched_keywords": self._get_matched_keywords(user_input, intent),
            "suggested_template": self._get_suggested_template(intent)
        }
    
    def _calculate_confidence(self, user_input: str, intent: IntentType) -> float:
        """
        Calculate confidence score for the classified intent.
        
        Args:
            user_input: The user's request string
            intent: The classified intent
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if intent == IntentType.GENERAL:
            return 0.5
        
        # Get the appropriate patterns
        if intent == IntentType.DEBUG:
            patterns = self.debug_patterns
        elif intent == IntentType.GENERATE:
            patterns = self.generate_patterns
        elif intent == IntentType.EXPLAIN:
            patterns = self.explain_patterns
        else:
            return 0.5
        
        # Count matches
        matches = sum(1 for pattern in patterns if pattern.search(user_input))
        
        # Calculate confidence based on number of matches
        # More matches = higher confidence
        confidence = min(0.5 + (matches * 0.15), 1.0)
        
        return confidence
    
    def _get_matched_keywords(self, user_input: str, intent: IntentType) -> list:
        """
        Get the keywords that matched for the classified intent.
        
        Args:
            user_input: The user's request string
            intent: The classified intent
            
        Returns:
            List of matched keywords
        """
        if intent == IntentType.GENERAL:
            return []
        
        # Get the appropriate patterns
        if intent == IntentType.DEBUG:
            patterns = self.debug_keywords
        elif intent == IntentType.GENERATE:
            patterns = self.generate_keywords
        elif intent == IntentType.EXPLAIN:
            patterns = self.explain_keywords
        else:
            return []
        
        # Find matched keywords
        matched = []
        for pattern in patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                # Extract the keyword from the pattern
                keyword_match = re.search(r'\(([^)]+)\)', pattern)
                if keyword_match:
                    keywords = keyword_match.group(1).split('|')
                    for keyword in keywords:
                        if keyword.lower() in user_input.lower():
                            matched.append(keyword)
        
        return matched
    
    def _get_suggested_template(self, intent: IntentType) -> str:
        """
        Get the suggested prompt template for the intent.
        
        Args:
            intent: The classified intent
            
        Returns:
            Template name string
        """
        template_map = {
            IntentType.DEBUG: "debug",
            IntentType.GENERATE: "generate",
            IntentType.EXPLAIN: "explain",
            IntentType.GENERAL: "executor"
        }
        
        return template_map.get(intent, "executor")