from typing import Dict, Any
from langchain.graphs import StateGraph
from langchain_core.messages import HumanMessage

from .agents import (
    market_data_agent,
    quant_agent, 
    fundamentals_agent,
    sentiment_agent,
    risk_management_agent,
    portfolio_management_agent
)

def create_workflow() -> StateGraph:
    """Create the agent workflow graph"""
    workflow = StateGraph()
    
    # Add nodes
    workflow.add_node("market_data", market_data_agent)
    workflow.add_node("quant", quant_agent)
    workflow.add_node("fundamentals", fundamentals_agent) 
    workflow.add_node("sentiment", sentiment_agent)
    workflow.add_node("risk", risk_management_agent)
    workflow.add_node("portfolio", portfolio_management_agent)

    # Define edges
    workflow.set_entry_point("market_data")
    workflow.add_edge("market_data", "quant")
    workflow.add_edge("market_data", "fundamentals")
    workflow.add_edge("market_data", "sentiment")
    workflow.add_edge("quant", "risk")
    workflow.add_edge("fundamentals", "risk") 
    workflow.add_edge("sentiment", "risk")
    workflow.add_edge("risk", "portfolio")
    workflow.add_edge("portfolio", "END")

    return workflow.compile()

def run_hedge_fund(
    ticker: str,
    start_date: str,
    end_date: str,
    portfolio: Dict[str, Any],
    show_reasoning: bool = False
) -> str:
    """Run the hedge fund workflow"""
    workflow = create_workflow()
    
    final_state = workflow.invoke({
        "messages": [
            HumanMessage(content="Make a trading decision based on the provided data.")
        ],
        "data": {
            "ticker": ticker,
            "portfolio": portfolio,
            "start_date": start_date,
            "end_date": end_date,
        },
        "metadata": {
            "show_reasoning": show_reasoning
        }
    })
    
    return final_state["messages"][-1].content