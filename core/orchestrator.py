# core/orchestrator.py
from typing import List, Dict
from agents.tools_wrapper import ALL_TOOLS

def run_analysis_pipeline(df, target_column: str) -> List[Dict]:
    """
    Запускает все аналитические инструменты и возвращает список результатов.
    """
    from agents.tools_wrapper import set_current_data
    set_current_data(df, target_column)

    results = []
    for tool in ALL_TOOLS:
        print(f"🔧 Запуск: {tool.name}")
        try:
            result = tool._run()
            results.append(result)
        except Exception as e:
            results.append({
                "tool_name": tool.name,
                "status": "error",
                "summary": "",
                "details": {},
                "error_message": str(e)
            })
    return results