import os
import re
from app.db import get_db_connection

def split_sql_statements(content):
    """
    Splits SQL script into distinct executable statements,
    handling DELIMITER $$ blocks for triggers and stored procedures.
    """
    statements = []
    current_stmt = []
    delimiter = ";"
    
    lines = content.splitlines()
    for line in lines:
        stripped = line.strip()
        
        # Check for DELIMITER command
        if stripped.upper().startswith("DELIMITER"):
            parts = stripped.split()
            if len(parts) >= 2:
                delimiter = parts[1]
            continue
            
        # Ignore full-line comments and blank lines
        if not stripped or stripped.startswith("--"):
            continue
            
        current_stmt.append(line)
        
        # Check if line ends with current delimiter
        if stripped.endswith(delimiter):
            stmt_text = "\n".join(current_stmt).strip()
            if stmt_text.endswith(delimiter):
                stmt_text = stmt_text[:-len(delimiter)].strip()
            if stmt_text:
                statements.append(stmt_text)
            current_stmt = []
            
    # Trailing statement if any
    if current_stmt:
        remaining = "\n".join(current_stmt).strip()
        if remaining:
            statements.append(remaining)
            
    return statements

def run_script(file_path):
    print(f"Loading script: {file_path}")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    statements = split_sql_statements(content)
    print(f"Found {len(statements)} executable statements.")
    
    conn = get_db_connection()
    success_count = 0
    try:
        with conn.cursor() as cursor:
            for i, stmt in enumerate(statements, 1):
                clean = stmt.strip()
                # Skip SELECT * queries at the bottom of base script
                if clean.upper().startswith("SELECT * FROM"):
                    continue
                try:
                    cursor.execute(clean)
                    success_count += 1
                except Exception as e:
                    print(f"Warning on statement {i}: {e}\nSnippet: {clean[:100]}...\n")
        print(f"Successfully executed {success_count} statements from {file_path}")
        return True
    finally:
        conn.close()

def initialize_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    scripts = [
        os.path.join(base_dir, "Club_Management_System_BASE.sql"),
        os.path.join(base_dir, "triggers.sql"),
        os.path.join(base_dir, "cursor.sql")
    ]
    
    for s in scripts:
        run_script(s)

if __name__ == "__main__":
    initialize_database()
