"""
Test configuration for cascade components.

This configuration uses smaller, faster models for testing.
"""

from enum import Enum

# Test mode configuration
TEST_MODE = True


class TaskPriority(Enum):
    """Priority of a task"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Model mappings for testing (use smaller models)
TEST_MODEL_CAPABILITIES = {
    'coding': {
        'simple': 'mistral:latest',      # 4.4 GB - fastest
        'moderate': 'qwen2.5:7b',         # 4.7 GB - smaller than 14B
        'complex': 'llama3.1:8b'          # 4.9 GB - reasonable for complex
    },
    'writing': {
        'simple': 'mistral:latest',
        'moderate': 'qwen2.5:7b',
        'complex': 'llama3.1:8b'
    },
    'analysis': {
        'simple': 'mistral:latest',
        'moderate': 'qwen2.5:7b',
        'complex': 'llama3.1:8b'
    },
    'research': {
        'simple': 'mistral:latest',
        'moderate': 'qwen2.5:7b',
        'complex': 'llama3.1:8b'
    }
}

# Model optimizations for testing
TEST_MODEL_OPTIMIZATIONS = {
    'mistral:latest': {
        'max_tokens': 1024,      # Reduced for speed
        'temperature': 0.7,
        'style': 'concise',
        'avoid': ['complex reasoning', 'multi-step logic']
    },
    'qwen2.5:7b': {
        'max_tokens': 2048,      # Reduced from 4096
        'temperature': 0.7,
        'style': 'balanced',
        'avoid': ['overly complex']
    },
    'llama3.1:8b': {
        'max_tokens': 2048,      # Reduced from 4096
        'temperature': 0.7,
        'style': 'detailed',
        'avoid': ['overly complex', 'ambiguous']
    }
}

# Timeout settings for testing (shorter timeouts)
TEST_TIMEOUTS = {
    'model_call': 30,           # Reduced from 60s
    'validation': 30,           # Reduced from 60s
    'health_check': 5           # Reduced from 10s
}

# Performance thresholds for testing
TEST_PERFORMANCE_THRESHOLD = 1.5  # 1.5x slower than expected (reduced from 2.0)

# Subtask templates for testing (fewer steps)
TEST_SUBTASK_TEMPLATES = {
    'coding': [
        {
            'description': 'Analyze requirements',
            'priority': TaskPriority.CRITICAL,
            'estimated_time': 0.5,  # Reduced from 2.0
            'output_format': 'notes'
        },
        {
            'description': 'Implement core functionality',
            'priority': TaskPriority.HIGH,
            'estimated_time': 1.0,  # Reduced from 4.0
            'output_format': 'code'
        },
        {
            'description': 'Test and verify',
            'priority': TaskPriority.MEDIUM,
            'estimated_time': 0.5,  # Reduced from 2.0
            'output_format': 'test results'
        }
    ],
    'writing': [
        {
            'description': 'Outline content',
            'priority': TaskPriority.CRITICAL,
            'estimated_time': 0.5,
            'output_format': 'outline'
        },
        {
            'description': 'Draft content',
            'priority': TaskPriority.HIGH,
            'estimated_time': 1.0,
            'output_format': 'text'
        },
        {
            'description': 'Review and finalize',
            'priority': TaskPriority.MEDIUM,
            'estimated_time': 0.5,
            'output_format': 'final text'
        }
    ],
    'analysis': [
        {
            'description': 'Load and explore data',
            'priority': TaskPriority.CRITICAL,
            'estimated_time': 0.5,
            'output_format': 'data summary'
        },
        {
            'description': 'Analyze patterns',
            'priority': TaskPriority.HIGH,
            'estimated_time': 1.0,
            'output_format': 'analysis results'
        },
        {
            'description': 'Document findings',
            'priority': TaskPriority.MEDIUM,
            'estimated_time': 0.5,
            'output_format': 'report'
        }
    ],
    'research': [
        {
            'description': 'Define research question',
            'priority': TaskPriority.CRITICAL,
            'estimated_time': 0.5,
            'output_format': 'research plan'
        },
        {
            'description': 'Gather information',
            'priority': TaskPriority.HIGH,
            'estimated_time': 1.0,
            'output_format': 'notes'
        },
        {
            'description': 'Summarize findings',
            'priority': TaskPriority.MEDIUM,
            'estimated_time': 0.5,
            'output_format': 'summary'
        }
    ]
}


def get_test_model(task_type: str, complexity: str) -> str:
    """Get the appropriate test model for a task type and complexity."""
    return TEST_MODEL_CAPABILITIES.get(task_type, {}).get(complexity, 'mistral:latest')


def get_test_model_optimizations(model: str) -> dict:
    """Get test model optimizations."""
    return TEST_MODEL_OPTIMIZATIONS.get(model, TEST_MODEL_OPTIMIZATIONS['mistral:latest'])


def get_test_subtask_template(task_type: str) -> list:
    """Get test subtask template for a task type."""
    return TEST_SUBTASK_TEMPLATES.get(task_type, TEST_SUBTASK_TEMPLATES['coding'])


def is_test_mode() -> bool:
    """Check if running in test mode."""
    return TEST_MODE