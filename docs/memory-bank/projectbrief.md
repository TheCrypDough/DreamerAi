# DreamerAI Project Brief (V2.0 - Post-V1 Launch / Planning V1.1+)
Project Title: DreamerAI
Version/Status: V1.0 Launched. Planning/Developing V1.1 Enhancements & V2.0 Core Features.
1. Mission & Vision
Mission: To forge a bulletproof, AAA-grade desktop application, DreamerAI, serving as the foundation of the "Money Tree DreamMaker Suite." DreamerAI will leverage a sophisticated team of specialized AI agents to empower users of all skill levels (beginner to absolute expert) to transform their ideas into high-quality software, websites, components, games, and more, seamlessly integrating education and development.
Vision: To create the premiere Gen AI Ecosystem ("We Build The Future"), revolutionizing software creation by making advanced AI development accessible, intuitive, and efficient for the masses. DreamerAI aims to be a "doing" and "teaching" titan, fostering a community where users learn, build, share, and ultimately bring their most ambitious digital dreams to life ("Beyond your wildest dreams.").
2. Problem Statement
Traditional software development presents significant barriers: steep learning curves, complex toolchains, time-consuming coding, difficulty translating ideas into technical plans, inadequate documentation, security oversights, and a disconnect between building and learning. Existing AI code generation tools often lack depth, context-awareness, customizability, integrated learning, or a holistic workflow encompassing the entire development lifecycle (planning, coding, testing, security, documentation, deployment prep). This prevents many potential creators from realizing their visions and hinders the productivity of experienced developers.
3. Solution Overview: The Dream Team & Dreamer Desktop
DreamerAI addresses these challenges through a novel approach centered around:
The Dream Team: A coordinated team of 28+ specialized AI agents (See agent_description.md), each expert in a specific domain (e.g., Jeff for chat, Arch for planning, Nexus for coding management, Lewis for administration, Spark for education, Billy for AI distillation). They work collaboratively within defined workflows to execute the user's project from concept to completion.
The Dreamer Desktop: An intuitive, panelized Electron/React/MUI desktop application serving as the user's primary interface. It features customizable panels for Chat, Project Management, Code Editing ("Dreamcoder"), System Monitoring ("Dream Theatre"), Education ("Spark"), Tools, Marketplace, User Files ("User Thoughts"), Terminal, Browser, and more, facilitating a seamless workflow.
Structured Workflow + Flexible Modes: A core workflow guides projects through Input Refinement (Promptimizer), User Interaction/Refinement (Jeff/Sophia/Spark), Planning (Arch/Lewis), Building ( Nexus/Coders/MCPs ), QA (Bastion/Daedalus/Herc), Documentation (Scribe), and Deployment Prep (Nike). Users can engage via different modes ("6-Step", "Dynamic", "Automagic") tailored to their needs.
Hybrid & Custom AI: Leverages a configurable mix of local (Ollama) and cloud LLMs (OpenRouter), integrating advanced Retrieval-Augmented Generation (RAG via ChromaDB/SentenceTransformers). Includes the "DreamBuilder" engine (Billy the Distiller) for users and the system to create highly specialized, fine-tuned AI agents and models.
Integrated Education ("Spark"): A central "Ignite Your Mind" engine providing context-aware tutorials, explanations, tips, and resources directly within the workflow, adapting to the user's specified skill level.
Robust Foundations: Built on modern tech (Python/FastAPI backend, PostgreSQL DB, Electron/React/MUI frontend), emphasizing security (Firebase Auth, JWT sessions, encryption, scans), scalability (DB migration, containerization via Docker/Compose), maintainability (DI framework), and quality (automated testing, QA agents).
4. Target Audience
Beginners: Zero coding experience, seeking a guided, "nurturing" path to create their first app or website, supported by Spark's integrated learning.
Intermediate Developers: Looking to accelerate their workflow, learn new technologies, and build more complex projects faster.
Expert Professionals & Businesses: Requiring a powerful, flexible, customizable tool for rapid prototyping, component generation, complex system architecture, automated testing/docs, and potentially creating specialized AI agents/tools for internal use ("Build Anything", "Any Stack").
5. Core Features & Pillars (V1 -> V2+ Vision)
Agent-Driven Development: The 28-agent Dream Team executing the full project lifecycle.
Dreamer Desktop UI: Customizable, panelized interface with integrated Chat, Project Manager, Code Editor (Dreamcoder), Browser, Terminal, Dream Theatre, User Thoughts/Notepad, Spark Education Panel, Marketplace, Tools Explorer, Settings.
Hybrid LLM Backend: Configurable local (Ollama) and cloud (OpenRouter) models with Redis caching.
ChromaDB/ST RAG System: Providing deep contextual knowledge for agents.
Spark Education Engine: Integrated, context-aware, adaptive learning (tutorials, hover tips, code explanations).
DreamBuilder (Billy/Smith): V1 Placeholders -> V2+ Functional user/system generation of custom AI agents/models and Modern Context Protocols (MCPs). Includes standalone UI concepts.
Project Management: V1 Basic -> V2+ Advanced Subproject handling, visualization (TreeView), file management, Recycle Bin.
Version Control: V1 Local Git + GitHub Repo Create/Push (backend) + UI -> V2+ Branching, Merging, Full workflow integration.
Template Marketplace: V1 Template sharing -> V2+ Workflow/Agent config sharing.
User Authentication: V1 Firebase Google Sign-In -> V2+ More providers, robust session management.
Cloud Sync/Backup: V1 Metadata sync (Firestore) -> V2+ Full project file sync/backup (S3), Restore functionality.
Workflow Modes: V1 Standard Sim -> V2+ Functional 6-Step, Dynamic, Automagic modes.
Security: V1 Basics (Auth, Encryption Utils, Scans) -> V2+ RBAC, Full Secret Management, Hardening.
Resilience: V1 Basic -> V2+ Retries (Tenacity), Circuit Breakers.
Quality Assurance: V1 Placeholders -> V2+ Functional QA agent loop (Herc/Bastion tests).
Documentation: V1 Basic README -> V2+ Full User Guides, API Docs, Code Comments (Scribe).
Packaging/Deployment: V1 Basic Notes/Zip -> V2+ Build Scripts, Installer options, Deployment Instructions (Nike).
6. Key Technical Concepts
Architecture: Agent-based, Service-Oriented (evolving towards potential Microservices V3+), Event-Driven elements (V2+), Desktop Application with API backend.
Stack: Electron/React/MUI (FE), Python/FastAPI (BE), PostgreSQL (DB), Redis (Cache), Firebase Auth, Docker/Compose (Dev Env).
AI: Hybrid LLMs, RAG (ChromaDB/ST), Fine-tuning/Distillation (Transformers/Datasets).
Design Patterns: Dependency Injection, Singleton, Factory, Observer (Event Manager), Repository (DB), Task Queue (V2+), Circuit Breaker (V2+).
7. Scope
V1.0 (Launched): Focused on establishing the core architecture, agent placeholders, essential UI panels (Chat, PM, Settings), functional V1/V2 logic for core flow (Jeff, Arch, Nexus->Specialists V2 Gen, Scribe/Nike V2 basic output), basic RAG, Hybrid LLM, Firebase Auth, SQLite DB V1, Basic VC backend/UI, Template Marketplace V1, basic Subprojects, UI Polish (Themes, i18n, A11y, Tutorial). PostgreSQL + V1 Sync/DI/Auth hardening planned immediately post-launch.
V1.1 / V2.0+ (Current Dev Cycle): Implementing planned Post-V1.0 features: PostgreSQL Migration & Refactor, Robust AuthN/AuthZ, Cloud Sync V2 UI, Agent DI, Functional V2 agents (QA, Research, Maintenance, Upgrade, Suggestion, Education), Advanced Subproject UI, Task Breakdown, functional QA loop, refining workflows, enhancing UX, implementing core vision elements (e.g., basic SnapApp, "Build Anything" component gen).
Long-Term (V3+): Full DreamBuilder capability, advanced collaboration, self-learning/optimization, full multi-stack support, IDE extensions, ecosystem apps (BizNestAI, Aittorney), potential microservices.
8. Ecosystem Vision
DreamerAI is the cornerstone of the planned "Money Tree DreamMaker Suite". Learnings and capabilities developed within DreamerAI, potentially including agents generated by DreamBuilder, will be leveraged to create sister applications like:
BizNestAI: A comprehensive AI assistant for business planning, strategy, market analysis, financial modeling, and operational management.
Aittorney: An AI-powered legal assistant for document analysis, research, drafting, and compliance checks (acknowledging high complexity/risk).
An external Community Hub website (beyond the in-app Marketplace) is also planned for forums, resources, and broader engagement.
9. Guiding Principles/Philosophy
Solve User Pain: Address the frustrations and inefficiencies of traditional development.
Empower All Users: Bridge the gap between beginner aspiration and expert execution.
Integrate Learning: Make education a seamless part of the creation process ("Education First").
Uncompromising Quality: Strive for "AAA-Grade" in both the tool and its output ("No half-assed work").
Nurturing & Engaging UX: Create a "fun, addictive, supportive" user experience.
Build for Scale: Architect for future growth and potentially millions of users.
Embody Passion: Reflect Anthony's dedication and personal vision ("heart and soul").
ACI > Prompting: Prioritize clear, robust Agent-Computer Interfaces (Tool/API design) for reliable agent function.