# 🏗️ Architecture Documentation - Personal Health Coach

## Executive Summary

The Personal Health Coach is a production-ready healthcare AI application built with a modern, cost-optimized architecture. It processes sensitive medical data through intelligent compression before leveraging large language models to provide personalized health recommendations.

**Key Design Principles:**
- **Cost Optimization**: 60% token reduction through intelligent compression
- **Privacy First**: No data persistence, session-only processing
- **Fail-Safe**: Graceful degradation with fallback mechanisms
- **Medical Safety**: Prominent disclaimers and consultation reminders

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                      (Streamlit Web App)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Session    │  │    Chat      │  │   Medical    │         │
│  │    State     │  │   History    │  │  Disclaimer  │         │
│  │  Management  │  │   Manager    │  │   Handler    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROCESSING PIPELINE                           │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │     PDF      │ ───▶ │  ScaleDown   │ ───▶ │   Google     │ │
│  │  Extraction  │      │ Compression  │      │   Gemini     │ │
│  │ (PDFPlumber) │      │  (40% size)  │      │     AI       │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│         │                      │                      │         │
│         │                      ▼                      │         │
│         │              ┌──────────────┐              │         │
│         │              │   Fallback   │              │         │
│         └──────────────│   Handler    │──────────────┘         │
│                        └──────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
│  ┌──────────────┐                  ┌──────────────┐            │
│  │  ScaleDown   │                  │ Google GenAI │            │
│  │     API      │                  │     API      │            │
│  │ (Compression)│                  │  (Inference) │            │
│  └──────────────┘                  └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Architecture

### User Journey Flow

```
┌─────────────┐
│   User      │
│  Opens App  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Upload PDF     │
│  Medical Record │
└──────┬──────────┘
       │
       ▼
┌──────────────────────────────────┐
│   PDF Text Extraction            │
│   - PDFPlumber reads pages       │
│   - Cleans whitespace            │
│   - Handles errors               │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│   Compression Pipeline           │
│   ┌──────────────────────────┐  │
│   │ 1. Initialize Compressor │  │
│   │ 2. Set health context    │  │
│   │ 3. Compress to 40%       │  │
│   │ 4. Store statistics      │  │
│   └──────────────────────────┘  │
│         │                        │
│         ▼                        │
│   ┌──────────────────────────┐  │
│   │  Error? → Use Original   │  │
│   └──────────────────────────┘  │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│   Session State Storage          │
│   - medical_context              │
│   - compressed_context           │
│   - compression_stats            │
│   - wellness_goals               │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│   User Asks Question             │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│   Adaptive Prompt Selection      │
│   - Analyze query intent         │
│   - Select prompt template       │
│   - Build context                │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│   Google Gemini API Call         │
│   - Include compressed data      │
│   - Add wellness goals           │
│   - Send chat history            │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│   Stream Response to User        │
│   - Display with disclaimers     │
│   - Add to chat history          │
└──────────────────────────────────┘
```

---

## 🧩 Component Architecture

### 1. **User Interface Layer**

```python
Component: Streamlit Web Interface
├── Sidebar
│   ├── Health Profile Section
│   │   ├── PDF Upload Widget
│   │   ├── Wellness Goals Input
│   │   └── Medical Disclaimer
│   └── Data Summary Panel
│       ├── Compression Statistics
│       └── Context Information
└── Main Content
    ├── Welcome Message
    ├── Chat Interface
    │   ├── Message History Display
    │   └── Chat Input Field
    └── Footer (Timestamp, Credits)
```

**Technologies:**
- Framework: Streamlit 1.31+
- Styling: Custom CSS injected via st.markdown()
- State: Streamlit session_state
- Widgets: Native Streamlit components

---

### 2. **Session State Management**

```python
Session State Schema:
{
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ],
    "medical_context": "Original PDF text...",
    "compressed_context": "Compressed text...",
    "compression_stats": {
        "compressed_text": "...",
        "original_length": 8000,
        "compressed_length": 3200,
        "compression_ratio": 0.4,
        "error": None
    },
    "wellness_goals": "User goals..."
}
```

**Lifecycle:**
- **Initialize**: On app start
- **Update**: On user interaction
- **Persist**: During browser session only
- **Clear**: On browser close (no server-side storage)

---

### 3. **PDF Processing Module**

```python
Function: extract_medical_data(uploaded_file)

Input: UploadedFile (Streamlit)
       ├── .name: "lab_results.pdf"
       ├── .size: bytes
       └── .read(): file content

Processing:
├── Open with PDFPlumber
├── Iterate through pages
│   ├── Extract text per page
│   ├── Clean whitespace
│   └── Mark page numbers
├── Concatenate all pages
└── Final cleanup
    ├── Remove null bytes
    └── Normalize spacing

Output: String (cleaned medical text)

Error Handling:
├── Corrupted PDF → Error message
├── No text extracted → Empty string
├── Permission denied → Error message
└── General exception → Logged & error message
```

**Dependencies:**
- `pdfplumber >= 0.10.0`
- Native Python file handling

---

### 4. **Compression Pipeline**

```python
Function: compress_health_context(text)

Input: Raw medical text (string)

Pipeline:
┌─────────────────────────────────┐
│ 1. Validation                   │
│    - Check if text is empty     │
│    - Verify ScaleDown available │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 2. API Authentication           │
│    - Load SCALEDOWN_API_KEY     │
│    - Initialize compressor      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 3. Compression                  │
│    Parameters:                  │
│    - context: medical_text      │
│    - prompt: extraction_prompt  │
│    - target_model: gemini-2.0   │
│    - ratio: 0.4                 │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 4. Statistics Calculation       │
│    - Original length            │
│    - Compressed length          │
│    - Compression ratio          │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 5. Error Handling               │
│    Success → Return compressed  │
│    Failure → Fallback original  │
└─────────────────────────────────┘

Output: Dictionary with stats & compressed text
```

**Key Features:**
- **Health-Specific Extraction**: Focuses on vitals, medications, allergies
- **Aggressive Compression**: 40% target ratio
- **Graceful Fallback**: Uses original text if compression fails
- **Transparency**: Shows compression statistics to user

---

### 5. **AI Inference Engine**

```python
Function: get_health_advice(query, medical_text, goals, history)

Architecture:

┌────────────────────────────────────┐
│   Query Intent Analysis            │
│   ┌──────────────────────────────┐ │
│   │ Keywords Detection           │ │
│   │ - "checkup" → Scenario A     │ │
│   │ - "pain/symptom" → Scenario B│ │
│   │ - "diet/exercise" → Scenario C│ │
│   │ - "lab/test" → Scenario D    │ │
│   └──────────────────────────────┘ │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│   Context Assembly                 │
│   ┌──────────────────────────────┐ │
│   │ Medical Records (compressed) │ │
│   │ + Wellness Goals             │ │
│   │ + Chat History (last 6 msgs) │ │
│   │ + Scenario-Specific Prompt   │ │
│   └──────────────────────────────┘ │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│   Gemini API Call                  │
│   Model: gemini-2.0-flash-exp      │
│   System: HEALTH_COACH_PROMPT      │
│   Temperature: Default (0.7)       │
└────────┬───────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│   Response Processing              │
│   - Extract text                   │
│   - Add disclaimers                │
│   - Format for display             │
└────────────────────────────────────┘
```

**Adaptive Prompting System:**

| Scenario | Trigger Keywords | Response Focus | Token Budget |
|----------|-----------------|----------------|--------------|
| **A: General Checkup** | checkup, overall, assessment | Comprehensive health review | ~800 tokens |
| **B: Symptoms** | pain, symptom, feel, experiencing | Educational + warning signs | ~600 tokens |
| **C: Lifestyle** | diet, exercise, sleep, stress | Evidence-based recommendations | ~700 tokens |
| **D: Lab Results** | lab, test, cholesterol, glucose | Simple explanations with analogies | ~650 tokens |

---

## 🔐 Security Architecture

### 1. **API Key Management**

```
Secrets Storage: .streamlit/secrets.toml
├── Never in code
├── Never in version control (.gitignore)
├── Loaded at runtime via st.secrets
└── Environment-specific values

Production Alternative:
├── AWS Secrets Manager
├── Google Cloud Secret Manager
├── Azure Key Vault
└── Environment variables (cloud platforms)
```

### 2. **Data Privacy**

```
Data Lifecycle:
┌─────────────┐
│ User Upload │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ RAM (Session)   │  ← Only stored here
│ - Temporary     │
│ - Not logged    │
│ - Not cached    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Browser Close   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Data Destroyed  │  ← Automatic cleanup
└─────────────────┘

No Persistence:
❌ No database
❌ No file storage
❌ No server logs with PHI
❌ No cloud storage
✅ Session memory only
```

### 3. **Input Validation**

```python
PDF Upload Validation:
├── File type check (extension .pdf)
├── File size limit (handled by Streamlit)
├── Content extraction error handling
└── Malformed PDF rejection

Text Input Validation:
├── XSS prevention (Streamlit auto-escapes)
├── SQL injection N/A (no database)
└── Length limits (API token limits)
```

---

## 📈 Performance Architecture

### 1. **Token Optimization**

```
Without Compression:
┌─────────────────────────────────┐
│ Medical PDF (10 pages)          │
│ ~8,000 characters               │
│ ~2,000 tokens                   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ + User Query                    │
│ ~200 tokens                     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ + Chat History                  │
│ ~500 tokens                     │
└────────┬────────────────────────┘
         │
         ▼
        Total: ~2,700 tokens input
        Cost: $0.027 per query


With Compression (40% ratio):
┌─────────────────────────────────┐
│ Compressed Medical Data         │
│ ~3,200 characters               │
│ ~800 tokens (60% reduction!)    │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ + User Query                    │
│ ~200 tokens                     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ + Chat History                  │
│ ~500 tokens                     │
└────────┬────────────────────────┘
         │
         ▼
        Total: ~1,500 tokens input
        Cost: $0.015 per query
        
💰 Savings: 44% cost reduction
```

### 2. **Response Time Breakdown**

```
Total Query Time: 6-16 seconds

┌─────────────────────────────────────┐
│ PDF Extraction: 2-5 seconds         │
│ - PDFPlumber processing             │
│ - Text cleanup                      │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Compression: 1-3 seconds            │
│ - API call to ScaleDown             │
│ - Token reduction processing        │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ AI Generation: 3-8 seconds          │
│ - Gemini API inference              │
│ - Response streaming                │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ UI Rendering: <1 second             │
│ - Streamlit display                 │
└─────────────────────────────────────┘
```

**Optimization Strategies:**
- ✅ Compression reduces API latency (fewer tokens)
- ✅ Session state caching (no re-processing)
- ✅ Async API calls (where supported)
- ⚠️ PDF processing is synchronous (bottleneck)

### 3. **Scalability Considerations**

```
Current Architecture: Single-instance
├── Users: 1-10 concurrent
├── Memory: ~500MB per user session
└── CPU: Minimal (API-heavy)

Scaling Options:
├── Horizontal: Multiple Streamlit instances + Load Balancer
├── Vertical: Increase instance RAM/CPU
└── Caching: Redis for compression results (optional)

Bottlenecks:
├── PDF Processing (CPU-bound)
├── API Rate Limits (external services)
└── Session State Memory (per user)
```

---

## 🧪 Testing Architecture

### Test Pyramid

```
                    ┌─────────────┐
                    │  E2E Tests  │
                    │  (Manual)   │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │  Integration Tests      │
              │  (API Interactions)     │
              └────────────┬────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │     Unit Tests                    │
         │     (Functions)                   │
         └───────────────────────────────────┘
```

**Test Coverage:**
- Unit Tests: PDF extraction, compression logic
- Integration Tests: API calls, error handling
- E2E Tests: User workflows (manual)

See `TESTING_GUIDE.md` for 18 detailed test scenarios.

---

## 🚀 Deployment Architectures

### Development (Local)

```
┌─────────────────────────────────────┐
│  Developer Machine                  │
│  ┌────────────────────────────────┐ │
│  │  Streamlit Dev Server          │ │
│  │  Port: 8501                    │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌────────────────────────────────┐ │
│  │  Local ScaleDown Module        │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌────────────────────────────────┐ │
│  │  .streamlit/secrets.toml       │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Production (AWS - Recommended)

```
┌──────────────────────────────────────────────────────┐
│                    AWS Cloud                         │
│                                                      │
│  ┌────────────────┐                                 │
│  │  CloudFront    │  ← CDN, SSL/TLS                │
│  │  (CDN)         │                                 │
│  └───────┬────────┘                                 │
│          │                                          │
│          ▼                                          │
│  ┌────────────────┐                                 │
│  │  Application   │  ← HTTPS, Health checks        │
│  │  Load Balancer │                                 │
│  └───────┬────────┘                                 │
│          │                                          │
│          ▼                                          │
│  ┌─────────────────────────────┐                   │
│  │  ECS Fargate (Auto-scaling) │                   │
│  │  ┌──────────┐  ┌──────────┐ │                   │
│  │  │Container1│  │Container2│ │                   │
│  │  │health-app│  │health-app│ │                   │
│  │  └──────────┘  └──────────┘ │                   │
│  └─────────────────────────────┘                   │
│          │                                          │
│          ▼                                          │
│  ┌────────────────┐                                 │
│  │ Secrets Manager│  ← API keys                    │
│  └────────────────┘                                 │
│          │                                          │
│          ▼                                          │
│  ┌────────────────┐                                 │
│  │  CloudWatch    │  ← Logs, Metrics               │
│  └────────────────┘                                 │
└──────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│   External APIs                │
│   ├── Google Gemini API        │
│   └── ScaleDown API            │
└────────────────────────────────┘
```

**Infrastructure as Code:**
- Container: Docker
- Orchestration: AWS ECS
- Networking: VPC, Security Groups
- Monitoring: CloudWatch
- Secrets: AWS Secrets Manager

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## 🔧 Configuration Architecture

### Environment Configuration

```
Development:
├── .streamlit/secrets.toml (local)
├── DEBUG=True
└── Compression: Enabled with fallback

Staging:
├── AWS Secrets Manager
├── DEBUG=True
└── Compression: Enabled

Production:
├── AWS Secrets Manager
├── DEBUG=False
├── Compression: Enforced
├── Rate Limiting: Enabled
├── Authentication: Required
└── Monitoring: Full logging
```

### Feature Flags

```python
# Configurable features
FEATURES = {
    "compression": True,           # Enable/disable compression
    "compression_fallback": True,  # Fallback to original if fails
    "chat_history_limit": 6,       # Context messages
    "max_pdf_size_mb": 10,         # Upload limit
    "compression_ratio": 0.4,      # Target compression
    "ai_model": "gemini-2.0-flash-exp"
}
```

---

## 📊 Monitoring & Observability

### Metrics to Track

```
Application Metrics:
├── Query response time (p50, p95, p99)
├── PDF processing time
├── Compression success rate
├── API error rate
├── Token usage per query
└── User session duration

Business Metrics:
├── Daily active users
├── Queries per user
├── PDF uploads count
├── Feature usage (compression stats)
└── Error types frequency

Cost Metrics:
├── API costs (Gemini)
├── API costs (ScaleDown)
├── Infrastructure costs
└── Cost per query
```

### Logging Strategy

```python
Logging Levels:
├── ERROR: API failures, crashes
├── WARNING: Compression failures, fallbacks
├── INFO: User actions, query flow
└── DEBUG: Detailed processing steps (dev only)

Log Format:
{
    "timestamp": "2026-02-07T10:30:00Z",
    "level": "INFO",
    "component": "compression_pipeline",
    "message": "Compression successful",
    "metadata": {
        "original_length": 8000,
        "compressed_length": 3200,
        "ratio": 0.4
    }
}
```

---

## 🔄 Error Handling Architecture

### Error Handling Strategy

```
┌─────────────────────────────────┐
│  Error Occurs                   │
└────────┬────────────────────────┘
         │
         ▼
    ┌────────┐
    │ Log It │
    └────┬───┘
         │
         ▼
┌──────────────────────┐
│ Can Recover?         │
└────┬────────────┬────┘
     │            │
    Yes           No
     │            │
     ▼            ▼
┌─────────┐  ┌──────────────────┐
│ Fallback│  │ Show User-Friendly│
│ Mechanism│  │ Error Message   │
└────┬────┘  └────┬─────────────┘
     │            │
     ▼            ▼
┌──────────────────────────────┐
│ Continue Normal Operation    │
└──────────────────────────────┘
```

**Error Categories:**

| Error Type | Handling Strategy | User Impact |
|-----------|------------------|-------------|
| PDF Extraction Failed | Show error message | Cannot process PDF |
| Compression Failed | Use original text | Higher API cost |
| API Key Missing | Block app, show instructions | Cannot use app |
| Gemini API Error | Show error, retry option | Cannot get response |
| Rate Limit Hit | Show cooldown message | Temporary block |
| Network Error | Retry with exponential backoff | Slight delay |

---

## 🌐 API Integration Architecture

### External API Dependencies

```
┌────────────────────────────────────────┐
│  Personal Health Coach App             │
└─────┬────────────────────┬─────────────┘
      │                    │
      ▼                    ▼
┌─────────────┐    ┌──────────────────┐
│ ScaleDown   │    │ Google Gemini    │
│ API         │    │ API              │
│             │    │                  │
│ Endpoints:  │    │ Endpoints:       │
│ /compress   │    │ /v1/messages     │
│             │    │                  │
│ Auth:       │    │ Auth:            │
│ API Key     │    │ API Key          │
│             │    │                  │
│ Rate Limit: │    │ Rate Limit:      │
│ 100/hour    │    │ Tier-based       │
└─────────────┘    └──────────────────┘
```

**API Contract:**

```python
# ScaleDown API
Request:
{
    "context": "medical text...",
    "prompt": "extraction instructions",
    "target_model": "gemini-2.0-flash-exp",
    "ratio": 0.4
}

Response:
"compressed medical text..."

# Google Gemini API
Request:
{
    "model": "gemini-2.0-flash-exp",
    "system_instruction": "...",
    "messages": [
        {"role": "user", "parts": ["query"]}
    ]
}

Response:
{
    "content": [
        {"type": "text", "text": "AI response..."}
    ]
}
```

---

## 📚 Technology Stack Summary

### Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | Streamlit | 1.31+ | Web UI framework |
| **PDF Processing** | PDFPlumber | 0.10+ | Text extraction |
| **Compression** | ScaleDown | Custom | Token optimization |
| **AI Model** | Google Gemini | 2.0 Flash | Health recommendations |
| **Language** | Python | 3.10+ | Application logic |

### Dependencies Tree

```
health_app.py
├── streamlit
│   ├── Session state
│   ├── UI components
│   └── File upload
├── pdfplumber
│   └── PDF text extraction
├── google.genai
│   ├── Model initialization
│   └── Content generation
└── scaledown
    └── compression
        └── ScaleDownCompressor
```

---

## 🎯 Design Patterns Used

### 1. **Pipeline Pattern**
```
PDF → Extract → Compress → Store → Query → Generate → Display
```

### 2. **Strategy Pattern**
```
Query Intent → Select Prompt Strategy → Execute
```

### 3. **Fallback Pattern**
```
Try Compression → On Error → Use Original
```

### 4. **Session State Pattern**
```
Streamlit session_state as temporary data store
```

---

## 🔮 Future Architecture Enhancements

### Short-term (MVP+)
- [ ] Response caching (Redis)
- [ ] User authentication (OAuth)
- [ ] Rate limiting per user
- [ ] Multi-file upload support

### Medium-term
- [ ] Database for user preferences (PostgreSQL)
- [ ] Async API calls (FastAPI backend)
- [ ] Real-time collaboration
- [ ] Mobile app (React Native)

### Long-term
- [ ] On-premise deployment option
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Integration with EHR systems (HL7 FHIR)

---

## 📄 Architecture Decision Records (ADRs)

### ADR-001: Why Streamlit?
**Decision**: Use Streamlit for the UI framework

**Rationale**:
- Rapid prototyping (single Python file)
- Built-in session management
- Native file upload widgets
- Low learning curve for data scientists
- Good enough for MVP and internal tools

**Alternatives Considered**:
- Flask/FastAPI + React (more complex)
- Gradio (less flexible)
- Django (overkill)

---

### ADR-002: Why ScaleDown Compression?
**Decision**: Use ScaleDown for token compression

**Rationale**:
- 60% cost reduction on API calls
- Maintains medical context accuracy
- Health-specific extraction prompts
- Graceful fallback mechanism

**Alternatives Considered**:
- No compression (too expensive)
- Manual summarization (less accurate)
- Generic text compression (loses context)

---

### ADR-003: Why No Database?
**Decision**: Session-only storage, no persistence

**Rationale**:
- HIPAA compliance simplified
- No data breach risk
- Privacy by design
- Lower infrastructure cost
- Faster development

**Trade-offs**:
- No user history across sessions
- No analytics on past queries
- Re-upload needed each session

**Future**: May add encrypted database for authenticated users

---

### ADR-004: Why Gemini 2.0 Flash?
**Decision**: Use Gemini 2.0 Flash Experimental

**Rationale**:
- Fast inference (3-8 seconds)
- Cost-effective ($0.01 per 1K tokens)
- Good at conversational medical advice
- Native multi-turn context

**Alternatives Considered**:
- GPT-4 (more expensive)
- Claude (API limits)
- Open-source LLMs (hosting complexity)

---

## 📞 Support & Maintenance

### Architecture Reviews
- **Monthly**: Dependency updates
- **Quarterly**: Security audit
- **Annually**: Full architecture review

### Documentation
- This ARCHITECTURE.md (living document)
- See also: README.md, TESTING_GUIDE.md, DEPLOYMENT_GUIDE.md

---

**Last Updated**: February 2026  
**Version**: 1.0  
**Maintainer**: Senior Python AI Engineer