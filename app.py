import streamlit as st
import os
import uuid
from src.config import Config
from src.ingestion import IngestionManager
from src.extractor import PrescriptionExtractor
from src.vector_store import VectorStoreManager
from src.graph import RAGGraph
from src.memory import MemoryManager
from src.auth import AuthManager
from src.otc_manager import OTCManager
from src.utils import setup_logger

logger = setup_logger(__name__)

# Page Config
st.set_page_config(page_title="Medical Prescription RAG", layout="wide")

# Initialize Auth
if 'auth' not in st.session_state:
    st.session_state.auth = AuthManager()
if 'user' not in st.session_state:
    st.session_state.user = None

# --- Login / Register Page ---
# --- Login / Register Page ---
# --- Global Layout Setup ---
def setup_global_styles():
    st.markdown("""
        <style>
        /* --- Global Animations --- */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes border-glow {
            0% { border-color: rgba(128, 128, 128, 0.1); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            50% { border-color: rgba(255, 75, 75, 0.5); box-shadow: 0 4px 20px rgba(255, 75, 75, 0.2); }
            100% { border-color: rgba(128, 128, 128, 0.1); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        }

        @keyframes gradient-flow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        
        .animate-header {
            animation: fadeInUp 0.8s ease-out;
        }

        .floating-icon {
            display: inline-block;
            animation: float 3s ease-in-out infinite;
        }
        
        .gradient-text {
            background: linear-gradient(-45deg, #FF4B4B, #FF9051, #FF4B4B, #FF9051);
            background-size: 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-flow 2s ease infinite;
            display: inline-block;
        }

        /* --- Component Styling --- */
        
        /* Login Form Card */
        div[data-testid="stForm"] {
            background-color: var(--secondary-background-color);
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 2px solid transparent; 
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: border-glow 4s ease-in-out infinite;
        }
        div[data-testid="stForm"]:hover {
            transform: translateY(-5px) !important;
        }

        /* Buttons */
        .stButton button {
            background: linear-gradient(45deg, #FF4B4B, #FF9051) !important;
            border: none !important;
            color: white !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(255, 75, 75, 0.3) !important;
        }
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 15px rgba(255, 75, 75, 0.5) !important;
            background: linear-gradient(45deg, #FF9051, #FF4B4B) !important;
        }

        /* Metric Cards (e.g., File Upload Area) */
        div[data-testid="stFileUploader"] {
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px dashed rgba(128, 128, 128, 0.3);
            transition: all 0.3s ease;
            animation: fadeInUp 0.5s ease-out backwards;
        }
        div[data-testid="stFileUploader"]:hover {
            background-color: rgba(255, 75, 75, 0.05);
            border-color: #FF4B4B;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            border-radius: 0.5rem !important;
            transition: background-color 0.2s !important;
        }
        .streamlit-expanderHeader:hover {
            color: #FF4B4B !important;
            background-color: rgba(255, 75, 75, 0.05) !important;
        }
        
        /* Chat Messages */
        .stChatMessage {
            animation: fadeInUp 0.3s ease-out;
        }
        </style>
    """, unsafe_allow_html=True)

setup_global_styles()

# --- Login / Register Page ---
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='animate-header' style='text-align: center; margin-bottom: 2rem;'><span class='floating-icon'>🩺</span> <span class='gradient-text'>Medi-Buddy Login</span></h1>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", key="login_user", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
                
                st.markdown("") # Spacer
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        success, msg = st.session_state.auth.login_user(username, password)
                        if success:
                            st.session_state.user = username
                            st.toast(f"Welcome back, {username}!")
                            st.rerun()
                        else:
                            st.error(msg)
                            
        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username", key="reg_user", placeholder="johndoe")    
                new_pass = st.text_input("Choose Password", type="password", key="reg_pass", placeholder="Minimum 6 characters")
                
                st.markdown("") # Spacer
                submit_reg = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit_reg:
                    if new_user and new_pass:
                        success, msg = st.session_state.auth.register_user(new_user, new_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
                    else:
                        st.error("All fields are required")

        # Animated Footer Badge
        st.markdown("""
            <div style='text-align: center; margin-top: 3rem; animation: fadeInUp 1s ease-out 0.5s backwards;'>
                <div style='display: inline-flex; align-items: center; gap: 1rem; background: rgba(255, 255, 255, 0.05); padding: 0.5rem 1.5rem; border-radius: 50px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(5px);'>
                    <span>✨ AI Assistant</span>
                    <span style='opacity: 0.2'>|</span>
                    <span>🔒 Secure</span>
                </div>
                <p style='margin-top: 1rem; font-size: 0.8em; opacity: 0.5;'>
                    Clarity Rx helps you understand prescriptions. <br> Always consult a doctor.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.stop() # Stop execution if not logged in

# --- Main App (Only accessible after login) ---

# Initialize Managers
if 'extractor' not in st.session_state:
    st.session_state.extractor = PrescriptionExtractor()
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStoreManager()
if 'rag_graph' not in st.session_state:
    st.session_state.rag_graph = RAGGraph().build_graph()
if 'memory' not in st.session_state:
    st.session_state.memory = MemoryManager()
elif not hasattr(st.session_state.memory, 'get_otc_result'):
    # Reload memory manager if it's an old instance without the new methods
    st.session_state.memory = MemoryManager()
if 'otc_manager' not in st.session_state:
    st.session_state.otc_manager = OTCManager()

# Self-healing: Check if OTCManager has the new data format (dict)
# If the first item is a string, it means we have the old instance. Reload it.
try:
    if st.session_state.otc_manager.get_otc_list() and isinstance(st.session_state.otc_manager.get_otc_list()[0], str):
        logger.info("Detecting legacy OTCManager instance. Re-initializing...")
        from src.otc_manager import OTCManager # Re-import to ensure fresh class
        st.session_state.otc_manager = OTCManager()
except Exception as e:
    logger.error(f"Error checking OTCManager state: {e}")
    st.session_state.otc_manager = OTCManager() # Safety fallback

# Session State for Chat
if 'uploaded_files_map' not in st.session_state:
    st.session_state.uploaded_files_map = {} # ID -> Filename

# Sidebar
with st.sidebar:
    st.write(f"Logged in as: **{st.session_state.user}**")
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()
       
    # Navigation
    if "navigation" not in st.session_state:
        st.session_state.navigation = "Home"
        
    def switch_to_otc():
        st.session_state.navigation = "OTC List"
        
    page = st.radio("Menu", ["Home", "OTC List"], key="navigation")

    if page == "Home":
        st.title("Prescription RAG")
        
        # File Upload
        uploaded_file = st.file_uploader("Upload Prescription (PDF/Image)", type=['pdf', 'png', 'jpg', 'jpeg'])
        
        if uploaded_file:
            # Check if this file has already been uploaded by this user
            existing_p_id = st.session_state.memory.get_prescription_by_filename(st.session_state.user, uploaded_file.name)
            
            if existing_p_id:
                if st.session_state.get('current_view') != existing_p_id:
                    st.info(f"File '{uploaded_file.name}' already uploaded. Switching to existing chat.")
                    st.session_state.current_view = existing_p_id
                    st.rerun()
                # If already viewing this file, do nothing (prevent infinite loop)
            else:
                file_id = str(uuid.uuid4())
                # Save file temporarily
                from src.utils import ensure_directory
                ensure_directory(Config.INPUT_DIR)
                
                file_path = os.path.join(Config.INPUT_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process only if not already in session map (double check)
                if file_path not in st.session_state.uploaded_files_map.values():
                    with st.spinner("Processing Prescription..."):
                        # 1. Extract Data
                        data = st.session_state.extractor.extract_data(file_path)
                        
                        if data:
                            st.success("Extraction Complete!")
                            
                            # 2. Vectorize
                            # Create chunks from the extracted JSON/Text
                            # Format the medicine details nicely for the LLM context
                            med_details = []
                            for med in data.get('medicines', []):
                                timing = med.get('timing', {})
                                timing_str = f"Morning: {timing.get('morning')}, Afternoon: {timing.get('afternoon')}, Night: {timing.get('night')}, Instruction: {timing.get('instruction')}"
                                med_details.append(f"- {med.get('name')} (Qty: {med.get('quantity')}): {timing_str}, Freq: {med.get('frequency')}, Duration: {med.get('duration')}")
                            
                            meds_str = "\n".join(med_details)
                            text_content = f"Date: {data.get('date')}\n\nMedicines:\n{meds_str}\n\nNotes: {data.get('notes')}"
                            
                            # Store in Pinecone
                            metadata = {"filename": uploaded_file.name}
                            st.session_state.vector_store.add_prescription(file_id, [text_content], metadata)
                            
                            st.session_state.uploaded_files_map[file_id] = uploaded_file.name
                            
                            # Initialize session for this upload immediately with a descriptive title
                            # Generate Title from Medicines
                            med_names = [m.get('name', 'Unknown') for m in data.get('medicines', [])]
                            if med_names:
                                title = f"Prescription: {', '.join(med_names[:2])}" # First 2 meds
                                if len(med_names) > 2:
                                    title += "..."
                            else:
                                title = f"Prescription {uploaded_file.name}"
                            
                            # Pass filename to store it for future checks
                            # Also pass meds_str as details
                            st.session_state.memory.get_or_create_session(st.session_state.user, file_id, title=title, filename=uploaded_file.name, details=meds_str)
                            
                            st.success("Indexed in Vector DB!")
                            # Auto-switch to this new chat
                            st.session_state.current_view = file_id
                            st.rerun()
                        else:
                            st.error("Failed to extract data.")

        st.divider()
        
        # --- Chat History Sidebar ---
        st.subheader("Your Chats")
        
        # 2. Fetch User's Prescriptions from DB
        user_prescriptions = st.session_state.memory.get_user_prescriptions(st.session_state.user)
        
        if not user_prescriptions:
            st.info("No prescription chats yet.")
        
        for p_data in user_prescriptions:
            p_id = p_data['id']
            p_title = p_data['title']
            
            if st.button(f"📄 {p_title}", key=p_id, use_container_width=True):
                st.session_state.current_view = p_id
                st.rerun()

# Main Area Logic based on Page
if page == "OTC List":
    st.markdown("<h1 class='animate-header'><span class='gradient-text'>Allowed OTC Medicines</span></h1>", unsafe_allow_html=True)
    st.info("These medicines are generally considered safe for over-the-counter purchase. However, always consult a doctor if you are unsure.")
    
    # Search functionality
    search_query = st.text_input("🔍 Search OTC Medicines", placeholder="Type medicine name, brand, or use...")
    
    try:
        if search_query:
            # Search using Pinecone Vector DB
            with st.spinner("Searching Vector Database..."):
                results = st.session_state.otc_manager.search_otc_db(search_query)
                if results:
                    st.dataframe(results, use_container_width=True)
                else:
                    st.warning("No matches found in database.")
        else:
            # Display Full List (from Manager Source)
            raw_list = st.session_state.otc_manager.get_otc_list()
            # Convert dict list to DataFrame friendly format
            display_list = []
            for item in raw_list:
                display_list.append({
                    "Medicine Name": item['medicine_name'],
                    "Type": item['metadata'].get('type', 'General')
                })
            st.dataframe(display_list, use_container_width=True, column_config={
                "Medicine Name": st.column_config.TextColumn("Medicine Name", width="medium"),
                "Type": st.column_config.TextColumn("Category", width="medium"),
            })
            
    except Exception as e:
        st.error(f"Error fetching OTC data: {e}")

elif page == "Home":
    # Determine Active View
    if 'current_view' not in st.session_state:
        st.session_state.current_view = None
    
    if st.session_state.current_view is None:
        st.markdown("<h1 class='animate-header' style='text-align: center;'><span class='floating-icon'>💊</span> <span class='gradient-text'>Welcome to Prescription RAG</span></h1>", unsafe_allow_html=True)
        st.info("Please upload a prescription or select a chat from the sidebar to begin.")
    else:
        # Fetch user prescriptions again to get title (optimization: could pass from sidebar but this is safer)
        user_prescriptions = st.session_state.memory.get_user_prescriptions(st.session_state.user)
        selected_prescription_id = st.session_state.current_view
        # Fetch title for header
        current_title = next((p['title'] for p in user_prescriptions if p['id'] == selected_prescription_id), "Unknown Prescription")
        
        st.session_state.session_id = st.session_state.memory.get_or_create_session(st.session_state.user, selected_prescription_id)
        header_text = f"Chat: {current_title}"
        
        # Fetch details (medicine summary)
        details_text = st.session_state.memory.get_session_details(st.session_state.session_id)

        # Chat Interface
        st.header(header_text)
        if details_text:
            with st.expander("💊 Medicine Details", expanded=True):
                st.markdown(details_text)

        # OTC Check (Moved to Top)
        if st.session_state.get('current_view'):
            # Use a container to separate it visually
            with st.container():
                # Checkbox to trigger check - Use dynamic key to reset per session
                if st.checkbox("Check for OTC Medicines", key=f"otc_check_{st.session_state.session_id}"):
                     # Get details for the current view
                    active_p_id = st.session_state.current_view
                    
                    # details_text is already fetched above
                    if details_text:
                        # Use a unique key for caching based on prescription ID
                        cache_key = f"otc_{active_p_id}"
                        
                        if cache_key not in st.session_state:
                            # 1. Try to fetch from DB first
                            db_result = st.session_state.memory.get_otc_result(st.session_state.session_id)
                            
                            if db_result:
                                st.session_state[cache_key] = db_result
                            else:
                                # 2. If not in DB, run LLM check
                                with st.spinner("Checking OTC status..."):
                                    result = st.session_state.otc_manager.check_medicines_with_llm([details_text])
                                    st.session_state[cache_key] = result
                                    
                                    # 3. Save to DB if successful
                                    if "error" not in result:
                                        st.session_state.memory.save_otc_result(st.session_state.session_id, result)
                        
                        otc_result = st.session_state[cache_key]
                        
                        if "error" in otc_result:
                            st.error(f"Error: {otc_result['error']}")
                            st.button("View Allowed OTC List", key="btn_error_otc", on_click=switch_to_otc)
                        else:
                            # Display results nicely
                            with st.expander("OTC Analysis Results", expanded=True):
                                otc_meds = otc_result.get("otc_medicines", [])
                                consult_meds = otc_result.get("consult_medicines", [])
                                
                                if otc_meds and consult_meds:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.success("**✅ Safe to Buy**")
                                        for item in otc_meds:
                                            st.write(f"- **{item['name']}**: {item['reason']}")
                                    with col2:
                                        st.warning("**⚠️ Consult Doctor and proceed accordingly**")
                                        for item in consult_meds:
                                            st.write(f"- **{item['name']}**: {item['reason']}")
                                elif otc_meds:
                                    st.success("**✅ Safe to Buy**")
                                    for item in otc_meds:
                                        st.write(f"- **{item['name']}**: {item['reason']}")
                                elif consult_meds:
                                    st.warning("**⚠️ Consult Doctor and proceed accordingly**")
                                    for item in consult_meds:
                                        st.write(f"- **{item['name']}**: {item['reason']}")
                                else:
                                    st.info("No medicines found to analyze.")
                                st.button("View Allowed OTC List", key="btn_view_otc_list", on_click=switch_to_otc)
                    else:
                        st.info("No medicine details available to check.")

        # Display History
        # Always fetch fresh history for the CURRENT session_id
        history = st.session_state.memory.get_history(st.session_state.session_id)
        st.session_state.messages = [{"role": msg['role'], "content": msg['content']} for msg in history]
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # User Input
        if prompt := st.chat_input("Ask about prescriptions..."):
            # Add user message to state
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Run Graph
            with st.spinner("Thinking..."):
                inputs = {
                    "question": prompt,
                    "prescription_id": selected_prescription_id,
                    "session_id": st.session_state.session_id,
                    "language": "English",  # FIX: added missing language field
                    "context": [],
                    "answer": ""
                }
                
                result = st.session_state.rag_graph.invoke(inputs)
                answer = result["answer"]
                
                # Add AI message to state
                st.session_state.messages.append({"role": "ai", "content": answer})
                with st.chat_message("ai"):
                    st.markdown(answer)
                
                # Rerun to update history and keep OTC check at the bottom
                st.rerun()