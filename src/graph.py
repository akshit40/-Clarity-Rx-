from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import Config
from src.vector_store import VectorStoreManager
from src.memory import MemoryManager
from src.utils import setup_logger, remove_stopwords

logger = setup_logger(__name__)

class GraphState(TypedDict):
    question: str
    prescription_id: Optional[str]  # None for Global, ID for Local
    session_id: str
    language: str  # Language for response
    context: List[str]
    answer: str

class RAGGraph:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.memory = MemoryManager()
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=Config.GEMINI_MODEL_NAME,
                google_api_key=Config.GOOGLE_API_KEY
            )
            logger.info("RAGGraph LLM initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize RAGGraph LLM: {e}")
            self.llm = None

    def retrieve(self, state: GraphState):
        """
        Retrieve relevant chunks from Pinecone.
        """
        logger.info("Node: Retrieve")
        question = state["question"]
        prescription_id = state.get("prescription_id")

        try:
            results = self.vector_store.search(question, prescription_id=prescription_id)
            context = [match.metadata["text"] for match in results if match.metadata.get("text")]
        except Exception as e:
            logger.error(f"Retrieve node failed: {e}")
            context = []

        return {"context": context}

    def generate(self, state: GraphState):
        """
        Generate answer using Gemini.
        """
        logger.info("Node: Generate")

        if not self.llm:
            return {"answer": "AI model not available. Please check your GOOGLE_API_KEY."}

        question = state["question"]
        context = state["context"]
        language = state.get("language", "English")

        context_str = "\n\n".join(context) if context else "No prescription context available."

        # Fetch History
        try:
            history = self.memory.get_history(state["session_id"], limit=5)
            history_str = "\n".join([
                f"{msg['role'].capitalize()}: {remove_stopwords(msg['content'])}"
                for msg in history
            ])
        except Exception as e:
            logger.error(f"Failed to fetch history: {e}")
            history_str = ""

        prompt = f"""
        You are a helpful medical assistant. Answer the user's question based on the provided context and chat history.
        
        IMPORTANT INSTRUCTIONS:
        1. Answer in the following language: {language}
        2. If the user asks about a medicine ("What is this for?"), provide TWO things:
           a) The specific instructions from the prescription (dosage, timing).
           b) General medical knowledge about what the medicine is commonly used for (e.g., "Paracetamol is commonly used for fever and pain relief").
        
        Context from Prescriptions:
        {context_str}
        
        Chat History:
        {history_str}
        
        User Question: {question}
        
        Answer:
        """

        try:
            response = self.llm.invoke(prompt)
            answer = response.content

            # Save to memory
            self.memory.add_message(state["session_id"], "user", question)
            self.memory.add_message(state["session_id"], "ai", answer)

            return {"answer": answer}
        except Exception as e:
            logger.error(f"Generate node failed: {e}")
            return {"answer": f"Failed to generate response: {str(e)}"}

    def build_graph(self):
        """
        Builds the LangGraph workflow.
        """
        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("generate", self.generate)

        # Define edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()
