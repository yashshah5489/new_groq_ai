import logging
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from .llm_wrapper import GroqLLM

logger = logging.getLogger(__name__)

def create_portfolio_chain(temperature=0.7, max_tokens=1024):
    """
    Creates a LangChain chain for portfolio management advice.
    """
    # Configure memory with an explicit input key so that only "user_input" is recorded as the user's message.
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="user_input",  # Explicitly define the user input key
        return_messages=True
    )
    
    prompt_template = """
    You are a portfolio management advisor.
    Analyze the following portfolio details along with the provided additional context and conversation history,
    and generate recommendations for making the portfolio more defensive.
    
    Portfolio Details:
    {portfolio_details}
    
    Additional Context:
    {context}
    
    Conversation History:
    {chat_history}
    
    User Query:
    {user_input}
    
    Provide your advice in the following sections:
    1. Portfolio Overview
    2. Risk Analysis
    3. Strategic Recommendations
    4. Next Steps
    """
    
    prompt = PromptTemplate(
        input_variables=["portfolio_details", "context", "chat_history", "user_input"],
        template=prompt_template
    )
    
    llm = GroqLLM(temperature=temperature, max_tokens=max_tokens)
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    return chain

def get_portfolio_advice(portfolio_details: str, context: str, user_input: str,
                         temperature=0.7, max_tokens=1024) -> str:
    """
    Generates portfolio management advice based on the provided portfolio details, context, and user query.
    """
    logger.info("Generating portfolio management advice")
    try:
        chain = create_portfolio_chain(temperature=temperature, max_tokens=max_tokens)
        # Retrieve any existing conversation history from memory
        chat_history = chain.memory.load_memory_variables({}).get("chat_history", "")
        # Prepare all required inputs as a dictionary
        inputs = {
            "portfolio_details": portfolio_details,
            "context": context,
            "chat_history": chat_history,
            "user_input": user_input
        }
        # Call the chain with the dictionary of inputs
        result = chain(inputs)
        return result
    except Exception as e:
        logger.error(f"Error generating portfolio advice: {str(e)}", exc_info=True)
        return "Sorry, I encountered an error while generating portfolio advice. Please try again."
