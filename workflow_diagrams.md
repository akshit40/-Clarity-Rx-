# Clarity Rx: Detailed Workflow Diagrams

## 1. High-Level System Overview

```mermaid
flowchart TB
    subgraph User["👤 User"]
        A[Upload Prescription]
        B[Ask Question]
        C[Check OTC Safety]
    end
    
    subgraph Frontend["🖥️ Streamlit Frontend"]
        D[app.py]
    end
    
    subgraph Backend["⚙️ Backend Services"]
        E[AuthManager]
        F[PrescriptionExtractor]
        G[RAGGraph]
        H[OTCManager]
        I[MemoryManager]
        J[VectorStoreManager]
    end
    
    subgraph External["☁️ External Services"]
        K[(MongoDB)]
        L[(Pinecone)]
        M[Google Gemini]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    D --> F
    D --> G
    D --> H
    E --> K
    F --> M
    G --> J
    G --> M
    G --> I
    H --> J
    H --> M
    I --> K
    J --> L
```

---

## 2. Authentication Flow

```mermaid
flowchart TD
    A[User Opens App] --> B{Logged In?}
    B -->|No| C[Show Login Page]
    C --> D{Login or Register?}
    
    D -->|Login| E[Enter Credentials]
    E --> F[AuthManager.login_user]
    F --> G[Query MongoDB]
    G --> H{User Exists?}
    H -->|No| I[Show Error]
    H -->|Yes| J[Verify bcrypt Hash]
    J --> K{Password Match?}
    K -->|No| I
    K -->|Yes| L[Set Session State]
    L --> M[Redirect to Home]
    
    D -->|Register| N[Enter New Credentials]
    N --> O[AuthManager.register_user]
    O --> P[Hash Password with bcrypt]
    P --> Q[Store in MongoDB]
    Q --> R[Show Success Message]
    R --> C
    
    B -->|Yes| M
    I --> C
```

---

## 3. Prescription Upload & Processing

```mermaid
flowchart TD
    A[User Uploads File] --> B{File Type?}
    B -->|PDF| C[pypdf Extract Pages]
    B -->|Image| D[PIL Load Image]
    
    C --> E[PrescriptionExtractor]
    D --> E
    
    E --> F[Send to Gemini Vision]
    F --> G[Extract Structured JSON]
    
    G --> H{Extraction Success?}
    H -->|No| I[Show Error]
    H -->|Yes| J[Parse Medicine Details]
    
    J --> K[Format Text Content]
    K --> L[Generate Embeddings]
    L --> M[Store in Pinecone]
    
    M --> N[Create Session in MongoDB]
    N --> O[Update UI with Details]
    O --> P[Ready for Chat]
    
    subgraph Extracted["📋 Extracted Data"]
        Q[Date]
        R[Medicines List]
        S[Dosage & Timing]
        T[Notes]
    end
    
    G --> Q
    G --> R
    G --> S
    G --> T
```

---

## 4. RAG Chat Pipeline (LangGraph)

```mermaid
flowchart TD
    A[User Asks Question] --> B[RAGGraph.invoke]
    
    B --> C[State Initialization]
    C --> D["question, prescription_id, session_id"]
    
    D --> E[Retrieve Node]
    E --> F[VectorStoreManager.search]
    F --> G[Query Pinecone]
    G --> H[Get Top-K Chunks]
    H --> I[Return Context Documents]
    
    I --> J[Generate Node]
    J --> K[Build Prompt]
    
    subgraph Prompt["📝 Prompt Construction"]
        L[System Instructions]
        M[Retrieved Context]
        N[Chat History]
        O[User Question]
    end
    
    K --> L
    K --> M
    K --> N
    K --> O
    
    L --> P[Send to Gemini LLM]
    M --> P
    N --> P
    O --> P
    
    P --> Q[Generate Answer]
    Q --> R[Save to Memory]
    R --> S[MemoryManager.add_to_history]
    S --> T[Store in MongoDB]
    T --> U[Return Answer to UI]
```

---

## 5. OTC Safety Verification (Hybrid RAG)

```mermaid
flowchart TD
    A[User Clicks OTC Check] --> B[Get Medicine Details]
    B --> C[OTCManager.check_medicines_with_llm]
    
    C --> D[For Each Medicine]
    D --> E[Vector Search in Pinecone]
    
    subgraph VectorSearch["🔍 Semantic Search"]
        F[Query: Medicine Name]
        G[Namespace: otc_medicines]
        H[Top-K: 3]
        I[Threshold: 0.7]
    end
    
    E --> F
    F --> G
    G --> H
    H --> I
    
    I --> J{Candidates Found?}
    
    J -->|No| K["Mark as 'Consult Doctor'"]
    J -->|Yes| L[LLM Verification]
    
    L --> M[Build Verification Prompt]
    M --> N["Is Medicine == Candidate?"]
    N --> O[Send to Gemini]
    
    O --> P[Parse JSON Response]
    P --> Q{is_otc: true?}
    
    Q -->|Yes| R["Add to 'Safe to Buy'"]
    Q -->|No| K
    
    R --> S[Aggregate Results]
    K --> S
    
    S --> T[Save to MongoDB]
    T --> U[Display in UI]
    
    subgraph Results["📊 Final Output"]
        V["✅ OTC Medicines"]
        W["⚠️ Consult Medicines"]
    end
    
    U --> V
    U --> W
```

---

## 6. OTC Database Initialization (Startup)

```mermaid
flowchart TD
    A[App Startup] --> B[Initialize OTCManager]
    B --> C[Load OTC_LIST_DATA]
    C --> D[src/otc_data.py]
    
    D --> E[_initialize_otc_db]
    
    E --> F[For Each Medicine Entry]
    
    subgraph DataFormat["📦 Data Structure"]
        G["medicine_name: 'Paracetamol...'"]
        H["metadata: {type: 'Pain Relief'}"]
    end
    
    F --> G
    F --> H
    
    G --> I[Extract Texts List]
    H --> J[Extract Metadata List]
    
    I --> K[VectorStoreManager.add_texts]
    J --> K
    
    K --> L[Generate Embeddings]
    L --> M[Batch Upsert to Pinecone]
    M --> N[Namespace: otc_medicines]
    
    N --> O[Log: OTC List Ingested]
    O --> P[Ready for Searches]
```

---

## 7. Complete User Journey

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant Auth as AuthManager
    participant Ext as Extractor
    participant Vec as VectorStore
    participant RAG as RAGGraph
    participant OTC as OTCManager
    participant Mem as MemoryManager
    participant DB as MongoDB
    participant PC as Pinecone
    participant LLM as Gemini LLM
    
    User->>UI: Open App
    UI->>Auth: Check Session
    Auth->>DB: Verify User
    DB-->>Auth: User Data
    Auth-->>UI: Authenticated
    
    User->>UI: Upload Prescription
    UI->>Ext: Process File
    Ext->>LLM: Extract with Vision
    LLM-->>Ext: Structured JSON
    Ext->>Vec: Store Vectors
    Vec->>PC: Upsert Embeddings
    Ext->>Mem: Create Session
    Mem->>DB: Store Metadata
    UI-->>User: Show Medicine Details
    
    User->>UI: Ask Question
    UI->>RAG: Invoke Pipeline
    RAG->>Vec: Semantic Search
    Vec->>PC: Query Vectors
    PC-->>Vec: Context Chunks
    RAG->>LLM: Generate Answer
    LLM-->>RAG: Response
    RAG->>Mem: Save History
    Mem->>DB: Store Message
    UI-->>User: Display Answer
    
    User->>UI: Check OTC
    UI->>OTC: Verify Medicines
    OTC->>Vec: Search Candidates
    Vec->>PC: Semantic Match
    PC-->>Vec: Top-3 Candidates
    OTC->>LLM: Verify Match
    LLM-->>OTC: JSON Result
    OTC->>Mem: Cache Result
    Mem->>DB: Store OTC Result
    UI-->>User: Show Safe/Consult Lists
```

---

## 8. Data Flow Summary

| Step | Component | Input | Output | Storage |
|------|-----------|-------|--------|---------|
| 1 | AuthManager | Username/Password | Session Token | MongoDB |
| 2 | Extractor | PDF/Image | Structured JSON | - |
| 3 | VectorStore | Text Chunks | Embeddings | Pinecone |
| 4 | MemoryManager | Session Data | Persisted History | MongoDB |
| 5 | RAGGraph | User Query | AI Answer | - |
| 6 | OTCManager | Medicine List | Safety Classification | MongoDB (cached) |
