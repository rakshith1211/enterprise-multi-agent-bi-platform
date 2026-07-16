from typing import List, Dict, Any

class SQLOptimizer:
    @staticmethod
    def prune_joins(required_tables: List[str], joins: List[str]) -> List[str]:
        """
        Eliminates joins that do not reference any of the required tables.
        """
        if len(required_tables) <= 1:
            return [] # No joins required if only 1 table is queried
            
        pruned = []
        for join in joins:
            # Simple check: does the join string reference any of our required tables?
            # E.g. JOIN sales ON sales.user_id = users.id
            if any(t in join for t in required_tables):
                pruned.append(join)
        return pruned

    @staticmethod
    def parameterize_filters(filters: List[Dict[str, Any]]) -> tuple[List[str], Dict[str, Any]]:
        """
        Converts filters into parameterized clauses (e.g. column = :param_0) 
        and returns parameter binding dict.
        """
        clauses = []
        params = {}
        
        for idx, f in enumerate(filters):
            col = f["column"]
            op = f["operator"]
            val = f["value"]
            
            if op == "SQL_EXPR":
                # Raw SQL expressions (like time intelligence date_sub) cannot be parameterized easily
                clauses.append(val)
            else:
                param_name = f"param_{idx}"
                clauses.append(f"{col} {op} :{param_name}")
                params[param_name] = val
                
        return clauses, params
