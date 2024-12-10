from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json

from src.agents import (
    market_data_agent,
    quant_agent,
    fundamentals_agent,
    AgentState
)

class AgentOrchestrator:
    def __init__(self, show_reasoning: bool = True):
        self.llm = ChatOpenAI(model="gpt-4")
        self.show_reasoning = show_reasoning
        
        # Define agent mapping
        self.agents = {
            "market_data": market_data_agent,
            "technical": quant_agent,
            "fundamental": fundamentals_agent
        }
        
        # Define agent capabilities
        self.agent_capabilities = {
            "market_data": "Fetches market data, financial statements, and company information",
            "technical": "Analyzes price patterns, momentum, and technical indicators",
            "fundamental": "Analyzes financial ratios, company health, and valuation metrics"
        }
    
    def _parse_prompt(self, prompt: str) -> Dict:
        """Parse user prompt to determine required agents and data"""
        template = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an AI assistant that helps determine which financial analysis agents to use.
            Available agents and their capabilities:
            - market_data: Fetches market data, financial statements, and company information
            - technical: Analyzes price patterns, momentum, and technical indicators
            - fundamental: Analyzes financial ratios, company health, and valuation metrics
            
            Based on the user's question, determine:
            1. Which agents should be used (list of agent names)
            2. What ticker symbol to analyze (if mentioned)
            3. What specific aspects to focus on
            
            Respond in JSON format with these fields:
            {
                "agents": ["agent1", "agent2"],
                "ticker": "TICKER",
                "focus_areas": ["area1", "area2"]
            }"""),
            HumanMessage(content=prompt)
        ])
        
        response = self.llm.invoke(template)
        return json.loads(response.content)
    
    def _format_agent_response(self, agent_name: str, response: Dict) -> str:
        """Format agent response for human readability"""
        if "signal" in response:
            return f"""
{agent_name.upper()} ANALYSIS:
Signal: {response['signal'].upper()}
Confidence: {response['confidence']*100:.0f}%
Reasoning:
{json.dumps(response['reasoning'], indent=2)}
"""
        return f"\n{agent_name.upper()} DATA:\n{json.dumps(response, indent=2)}"
    
    def process_prompt(self, prompt: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """Process a natural language prompt and return analysis"""
        try:
            # Parse the prompt
            parsed = self._parse_prompt(prompt)
            ticker = parsed["ticker"]
            required_agents = parsed["agents"]
            
            # Initialize state
            state = AgentState(
                messages=[],
                data={
                    "ticker": ticker,
                    "start_date": start_date,
                    "end_date": end_date
                },
                metadata={"show_reasoning": self.show_reasoning}
            )
            
            # Always run market_data_agent first if we need data
            if "market_data" not in required_agents and (
                "technical" in required_agents or "fundamental" in required_agents
            ):
                required_agents.insert(0, "market_data")
            
            responses = []
            
            # Run required agents in sequence
            for agent_name in required_agents:
                if agent_name in self.agents:
                    agent_func = self.agents[agent_name]
                    try:
                        result = agent_func(state)
                        state = result  # Update state for next agent
                        
                        # Format response
                        if agent_name != "market_data" or self.show_reasoning:
                            if len(result["messages"]) > 0:
                                last_message = result["messages"][-1]
                                response_content = json.loads(last_message.content.replace("'", '"'))
                                responses.append(self._format_agent_response(agent_name, response_content))
                    except Exception as e:
                        responses.append(f"\n{agent_name.upper()} ERROR: {str(e)}")
            
            # Generate summary using GPT-4
            summary_template = ChatPromptTemplate.from_messages([
                SystemMessage(content="""You are a financial advisor summarizing multiple analyses.
                Provide a clear, concise summary of the findings and a recommended action if applicable.
                Be specific about the reasons behind the recommendation."""),
                HumanMessage(content=f"Here are the analyses for {ticker}:\n{''.join(responses)}")
            ])
            
            summary = self.llm.invoke(summary_template)
            
            # Combine all responses with summary
            return f"""
ANALYSIS FOR {ticker}
{'='*50}
{''.join(responses)}
{'='*50}
SUMMARY:
{summary.content}
"""
        except Exception as e:
            return f"Error processing prompt: {str(e)}"

def analyze_prompt(prompt: str, start_date: Optional[str] = None, end_date: Optional[str] = None, show_reasoning: bool = True) -> str:
    """Convenience function to analyze a prompt"""
    orchestrator = AgentOrchestrator(show_reasoning=show_reasoning)
    return orchestrator.process_prompt(prompt, start_date, end_date)

if __name__ == "__main__":
    # Example usage
    prompt = "What's your technical and fundamental analysis of PETR4? Focus on momentum and valuation."
    print(analyze_prompt(prompt)) 