"""
Prompt loader utility for reading markdown prompt files.
Supports template variable substitution at runtime.
"""
from pathlib import Path
from typing import Optional


# Base path to prompts directory (relative to project root)
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(filename: str, **kwargs) -> str:
    """
    Load a markdown prompt file and substitute template variables.
    
    Args:
        filename: Name of the prompt file (e.g., 'supervisor_prompt.md')
        **kwargs: Template variables to substitute using str.format()
                  Example: load_prompt('supervisor.md', schema=schema_str)
    
    Returns:
        The prompt content with variables substituted
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = PROMPTS_DIR / filename
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    content = prompt_path.read_text(encoding="utf-8")
    
    # Substitute template variables if provided
    if kwargs:
        content = content.format(**kwargs)
    
    return content


def get_schema_string(db_path: str = "ecommerce.db") -> str:
    """
    Extract and format the database schema as a string for prompt injection.
    
    Args:
        db_path: Path to the SQLite database
        
    Returns:
        Formatted string describing all tables and their columns
    """
    from sqlalchemy import create_engine, inspect
    
    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    
    schema_parts = []
    
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        col_defs = [f"  - {col['name']} ({col['type']})" for col in columns]
        schema_parts.append(f"Table: {table_name}\n" + "\n".join(col_defs))
    
    return "\n\n".join(schema_parts)
