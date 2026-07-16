import re

class SQLValidator:
    UNSAFE_KEYWORDS = [
        r"\binsert\b",
        r"\bupdate\b",
        r"\bdelete\b",
        r"\bdrop\b",
        r"\balter\b",
        r"\bcreate\b",
        r"\btruncate\b",
        r"\bexec\b",
        r"\bgrant\b",
        r"\brevoke\b",
        r"\bmerge\b",
        r"\bcopy\b"
    ]

    @classmethod
    def validate_safety(cls, sql: str) -> bool:
        sql_clean = sql.lower().strip()
        
        # 1. Enforce SELECT queries only
        if not sql_clean.startswith("select"):
            return False

        # 2. Reject unsafe DDL/DML keywords
        for kw in cls.UNSAFE_KEYWORDS:
            if re.search(kw, sql_clean):
                return False

        # 3. Prevent multiple statements (semi-colon injection check)
        # Allow trailing semicolon but reject nested semicolons
        if ";" in sql_clean:
            if sql_clean.count(";") > 1 or (sql_clean.count(";") == 1 and not sql_clean.endswith(";")):
                return False

        # 4. Block dangerous system functions or comments injection
        dangerous_patterns = [
            r"xp_cmdshell", # SQL Server execution
            r"pg_sleep", # Postgres time injection
            r"sleep\(", # MySQL time injection
            r"--", # Comments injection block
            r"/\*" # Block block comments
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, sql_clean):
                return False

        return True
