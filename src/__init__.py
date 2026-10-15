"""
Paquete src para el Asistente Inteligente H-E-B México.
"""

from src.data_loader import load_data, get_dataset_stats
from src.context_builder import build_json_context
from src.llm_router import fetch_openrouter
from src.evaluation import get_benchmark_questions

__all__ = [
    "load_data",
    "get_dataset_stats",
    "build_json_context",
    "fetch_openrouter",
    "get_benchmark_questions"
]
