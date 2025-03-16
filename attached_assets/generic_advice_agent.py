from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from .llm_wrapper import GroqLLM
import logging

logger = logging.getLogger(__name__)

def create_generic_advice_chain(temperature=0.7, max_tokens=1024):
    """
    Creates a LangChain chain for generic financial advice.
    
    Args:
        temperature: Temperature parameter for generation (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        LLMChain: The configured chain
    """
    # Specify input_key so that the memory tracks only the 'user_input'
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        input_key="user_input", 
        return_messages=True
    )
    prompt_template = """
    You are a financial advisor specializing in general advice.
    Using the context below (including latest news and insights from key finance books),
    analyze the user's financial situation and provide comprehensive, actionable advice.
    
    Context:
    {context}
    
    Conversation History:
    {chat_history}
    
    User Query:
    {user_input}
    
    Provide clear, general recommendations that are personalized to the user's specific situation.
    Include both short-term actions and long-term strategies.
    Be specific with your advice but avoid recommending particular financial products or services.
    
    Format your response with clear sections and bullet points where appropriate.
    End with a summary of the key action items the user should consider.
    """
    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "user_input"],
        template=prompt_template
    )
    llm = GroqLLM(temperature=temperature, max_tokens=max_tokens)
    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)
    return chain

def get_generic_advice(context: str, user_input: str, temperature=0.7, max_tokens=1024):
    """
    Generates generic financial advice based on user input and context.
    
    Args:
        context: Additional context information
        user_input: The user's query
        temperature: Temperature parameter for generation (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        str: The generated advice
    """
    logger.info("Generating generic financial advice")
    try:
        chain = create_generic_advice_chain(temperature=temperature, max_tokens=max_tokens)
        chat_history = chain.memory.load_memory_variables({}).get("chat_history", "")
        return chain.run(context=context, chat_history=chat_history, user_input=user_input)
    except Exception as e:
        logger.error(f"Error generating generic advice: {str(e)}", exc_info=True)
        return "Sorry, I encountered an error while generating advice. Please try again or refine your query."