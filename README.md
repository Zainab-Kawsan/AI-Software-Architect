🚀 AI Software Architect
An AI-powered Streamlit app that generates complete software architecture blueprints from a plain-English app idea — including tech stack recommendations, database schema, API endpoints, folder structure, a development roadmap, starter backend code, and an interactive system diagram.

✨ Features

- Architecture Blueprint — generates a full, structured blueprint across 7 sections using a senior architect system prompt
- System Diagram Generator — AI draws a Mermaid.js architecture diagram with subgraph layers (Client, Backend, Services, Database, External)
- Diagram Editor — edit Mermaid code manually, re-render live, or give natural-language instructions to the AI to modify the diagram
- Iterative Refinement Chat — chat with the AI to refine specific sections, swap tech choices, or ask architecture questions without regenerating from scratch
- Save History — every generation is saved to a local history.json file with full chat history and diagram; reload any past entry from the sidebar
- Download Project — export your blueprint as .txt, .pdf (styled with ReportLab), or .mmd (Mermaid source)
- Application Type Selector — tailor output to Web App, Mobile App, AI SaaS, or E-commerce


📁 Project Structure
ai-software-architect/
│
├── app.py                  # Main Streamlit app, all UI tabs and routing
├── llm.py                  # Architecture generation via LangChain + Groq
├── prompt.py               # System prompt for the architect LLM
├── diagram.py              # Mermaid generation, syntax fixing, HTML renderer
├── diagram_prompt.py       # System prompt for diagram generation
├── chat_refine.py          # Iterative refinement chat logic
├── downloader.py           # .txt and .pdf export generation
├── history.py              # Load, save, delete, clear history.json
│
├── history.json            # Auto-created; stores all past blueprints
├── requirements.txt
├── .env                    # Your API keys (never commit this)
└── README.md

🛠️ Tech Stack
LayerTechnologyUIStreamlitLLM OrchestrationLangChainLLM ProviderGroq (Llama 3.3 70B)Diagram RenderingMermaid.js v10PDF GenerationReportLabHistory StorageLocal JSON fileEnvironmentPython 3.10+

⚙️ Setup
1. Clone the repository
bashgit clone https://github.com/your-username/ai-software-architect.git
cd ai-software-architect
2. Create a virtual environment
bashpython -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate


3. Install dependencies
bashpip install -r requirements.txt
4. Set up your environment variables
Create a .env file in the project root:
envGROQ_API_KEY=your_groq_api_key_here
Get your free Groq API key at console.groq.com.
5. Run the app
bashstreamlit run app.py

📦 Requirements
streamlit
langchain
langchain-groq
python-dotenv
reportlab
Install all at once:
pip install streamlit langchain langchain-groq python-dotenv reportlab

🖥️ How to Use
Generate a Blueprint

Select your Application Type from the sidebar (Web App, Mobile App, AI SaaS, E-commerce)
Type your app idea in the text area — be as descriptive as you like
Click ⚡ Generate Architecture
The blueprint appears in the 📋 Architecture Blueprint tab across 7 sections

Generate a System Diagram

Switch to the 🗺️ System Diagram tab
Click 🗺️ Generate Diagram
The AI draws a layered Mermaid flowchart (Client → Backend → Services → Database → External)
Edit the Mermaid code directly in the right panel and click ▶ Re-render
Or type a natural-language instruction (e.g. "Add a Redis cache layer") and click Apply AI Edit
Download the diagram as .mmd or save the edited version back to history

Refine with AI Chat

Switch to the 💬 Refine with AI tab
Use the suggestion chips or type your own message:

"Switch the database to PostgreSQL"
"Add real-time notifications with WebSockets"
"Why REST instead of GraphQL?"
"Make it more scalable for 1M users"


If the AI returns an updated blueprint, click ✅ Apply as new blueprint to replace the current one
The diagram is automatically marked stale when you apply an update — regenerate it in the Diagram tab

Download Your Blueprint
In the 📋 Architecture Blueprint tab, scroll to 📥 Download Project:

⬇️ .txt — plain text with metadata header, all markdown stripped
⬇️ .pdf — styled PDF with section headings, code blocks, and bullet formatting
⬇️ .mmd — raw Mermaid diagram source (from the Diagram tab)

History:
- Every generation is auto-saved to history.json
- Past entries appear in the sidebar with timestamp and app type
- Click Load to restore a full entry including blueprint, diagram, and chat history
- Click Delete to remove a single entry, or 🗑 Clear all to wipe everything
