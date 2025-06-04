"""
dbt-col: Automated dbt to OpenMetadata publisher

Publishes dbt artifacts to OpenMetadata after your dbt runs - no user intervention required.
Similar to elementary, this package includes both a dbt package and Python CLI tool.
"""

__version__ = "0.1.0"
__author__ = "dbt-col Team"

from .core import DbtColIngestion, run_dbt_ingestion_from_config
from .cli import main

__all__ = [
    "DbtColIngestion",
    "run_dbt_ingestion_from_config", 
    "main"
] 