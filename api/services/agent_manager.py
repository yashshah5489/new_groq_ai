from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from .groq_client import get_groq_llm
from .rag_utils import get_rag_context
import logging

logger = logging.getLogger(__name__)

def get_agent_advice(query_type, context="", user_input="", portfolio_details="", domain_details=""):
    """Get advice from the appropriate agent based on query type"""
    try:
        llm = get_groq_llm()

        if query_type == "generic":
            template = """
            You are a helpful financial advisor. Use the following context and user query to provide detailed financial advice.

            Context:
            {context}

            User Query:
            {user_input}

            Please provide a clear, well-structured response that incorporates both general financial principles and any relevant current information from the context.
            """

            prompt = PromptTemplate(template=template, input_variables=["context", "user_input"])
            chain = LLMChain(llm=llm, prompt=prompt)

            return chain.run(context=context, user_input=user_input)

        elif query_type == "portfolio":
            template = """
            You are a portfolio analysis expert. Analyze the following portfolio and provide recommendations based on the user's query.

            Portfolio Details:
            {portfolio_details}

            Context:
            {context}

            User Query:
            {user_input}

            Provide a detailed analysis including risk assessment, diversification suggestions, and specific recommendations.
            """

            prompt = PromptTemplate(
                template=template,
                input_variables=["portfolio_details", "context", "user_input"]
            )
            chain = LLMChain(llm=llm, prompt=prompt)

            return chain.run(
                portfolio_details=portfolio_details,
                context=context,
                user_input=user_input
            )

        elif query_type == "domain":
            template = """
            You are a domain-specific financial advisor. Use the following domain information and context to provide targeted advice.

            Domain Details:
            {domain_details}

            Context:
            {context}

            User Query:
            {user_input}

            Provide specific recommendations and insights relevant to this domain.
            """

            prompt = PromptTemplate(
                template=template,
                input_variables=["domain_details", "context", "user_input"]
            )
            chain = LLMChain(llm=llm, prompt=prompt)

            return chain.run(
                domain_details=domain_details,
                context=context,
                user_input=user_input
            )

        else:
            raise ValueError(f"Invalid query type: {query_type}")

    except Exception as e:
        logger.error(f"Error generating {query_type} advice: {str(e)}")
        raise RuntimeError(f"Failed to generate advice: {str(e)}")