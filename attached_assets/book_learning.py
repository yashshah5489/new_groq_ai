import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from vector_store.chromadb_store import ChromaVectorStore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
os.makedirs("logs", exist_ok=True)
load_dotenv()

def insert_book_learnings():
    """
    Insert learnings from top self-help finance books into the ChromaDB collection.
    """
    book_learnings = [
        "The Intelligent Investor by Benjamin Graham: A foundational guide to value investing and long-term wealth creation.",
        "Rich Dad Poor Dad by Robert Kiyosaki: Challenges conventional wisdom about money and wealth.",
        "Think and Grow Rich by Napoleon Hill: Focuses on the mindset needed for financial success.",
        "The Psychology of Money by Morgan Housel: Explores how emotions influence financial decisions.",
        "The Simple Path to Wealth by JL Collins: Offers accessible advice on investing and financial independence.",
        "I Will Teach You To Be Rich by Ramit Sethi: Practical advice on managing finances for young professionals.",
        "Your Money or Your Life by Vicki Robin and Joe Dominguez: Helps readers align their spending with their values.",
        "The Millionaire Next Door by Thomas J. Stanley and William D. Danko: Reveals surprising secrets of America's wealthy.",
        "A Random Walk Down Wall Street by Burton G. Malkiel: A comprehensive guide to investing and market analysis.",
        "The Total Money Makeover by Dave Ramsey: A step-by-step plan for debt elimination and wealth building.",
        "Get Good with Money by Tiffany Aliche: Practical steps to financial wellness with worksheets.",
        "Broke Millennial Takes On Investing by Erin Lowry: A beginner's guide to investing for young adults.",
        "Wealth Warrior by Linda Garcia: Empowers communities of color to start investing.",
        "Finance for the People by Paco de Leon: Focuses on holistic financial wellness.",
        "Financially Lit!: The Modern Latina's Guide by Jannese Torres: Tailored financial advice for Latinas.",
        "The Compound Effect by Darren Hardy: Shows how small changes can lead to significant financial gains.",
        "The Algebra of Wealth by David M. Rubenstein: Offers insights into achieving financial security.",
        "Four Thousand Weeks by Oliver Burkeman: Helps with time management and prioritization.",
        "Retire Before Mom & Dad by Rob Berger: Strategies for early retirement.",
        "How I Invest My Money by Joshua Brown and Brian Portnoy: Insights from financial experts on investment strategies.",
        "Enough: True Measures of Money, Business, and Life by John C. Bogle: Reflects on what truly matters in financial success.",
        "Simple Money, Rich Life by Bob Lotich: Achieving financial freedom with a focus on impact.",
        "Becoming Your Own Banker by Nelson Nash: Introduces the infinite banking concept.",
        "Small Time Operator by Bernard B. Kamoroff: Practical advice for small business owners.",
        "Never Split the Difference by Chris Voss: Helps with negotiation skills."
    ]
    
    # Initialize the self-help book vector store using the same persist_directory ("chroma_db")
    vector_store = ChromaVectorStore(collection_name="self_help_books", persist_directory="chroma_db")
    ids = [f"book_learning_{i+1}" for i in range(len(book_learnings))]
    metadatas = [{"source": "self_help_finance_books"} for _ in book_learnings]
    
    try:
        vector_store.add_documents(ids, book_learnings, metadatas)
        logger.info("Self-help finance book learnings inserted successfully.")
    except Exception as e:
        logger.error(f"Error inserting book learnings: {e}")

if __name__ == "__main__":
    insert_book_learnings()
