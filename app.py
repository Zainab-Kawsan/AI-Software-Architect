import json
import streamlit as st
import streamlit.components.v1 as components

from llm import generate_architecture
from history import load_history, save_to_history, delete_entry, clear_history
from downloader import generate_txt, generate_pdf
from diagram import generate_mermaid, mermaid_to_html, ai_edit_diagram
from chat_refine import refine_architecture

st.set_page_config(page_title="AI Software Architect", page_icon="🚀", layout="wide")
st.title("🚀 AI Software Architect")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Architecture Settings")
    app_type = st.selectbox(
        "Application Type",
        ["Web App", "Mobile App", "AI SaaS", "E-commerce"],
    )

    st.divider()
    st.header("🕓 History")
    history = load_history()

    if not history:
        st.caption("No history yet.")
    else:
        if st.button("🗑 Clear all", use_container_width=True):
            clear_history()
            st.rerun()
        for entry in history:
            with st.expander(f"**{entry['app_type']}** · {entry['timestamp']}"):
                st.caption(entry["idea"])
                if st.button("Load", key=f"load_{entry['id']}"):
                    st.session_state["loaded_idea"] = entry["full_idea"]
                    st.session_state["loaded_response"] = entry["response"]
                    st.session_state["loaded_app_type"] = entry["app_type"]
                    st.session_state["loaded_mermaid"] = entry.get("mermaid", "")
                    st.session_state["chat_history"] = entry.get("chat_history", [])
                    st.session_state["loaded_full_idea"] = entry["full_idea"]
                    st.rerun()
                if st.button("Delete", key=f"del_{entry['id']}"):
                    delete_entry(entry["id"])
                    st.rerun()

# ── Input ──────────────────────────────────────────────────────────────────────
st.markdown("Generate software architecture using AI.")

default_idea = st.session_state.pop("loaded_idea", "")
user_input = st.text_area(
    "Describe your app idea",
    value=default_idea,
    height=200,
    placeholder="Example: I want a food delivery app...",
)

if st.button("⚡ Generate Architecture"):
    if not user_input.strip():
        st.warning("Please enter an app idea.")
    else:
        with st.spinner("Generating architecture..."):
            response = generate_architecture(user_input, app_type)
        st.session_state["loaded_response"] = response
        st.session_state["loaded_app_type"] = app_type
        st.session_state["loaded_full_idea"] = user_input
        st.session_state["loaded_mermaid"] = ""
        st.session_state["chat_history"] = []  # reset chat on new generation
        save_to_history(user_input, app_type, response)
        st.rerun()

# ── Output tabs ────────────────────────────────────────────────────────────────
if "loaded_response" in st.session_state:
    response = st.session_state["loaded_response"]
    current_type = st.session_state.get("loaded_app_type", app_type)
    current_idea = st.session_state.get("loaded_full_idea", user_input)
    current_mermaid = st.session_state.get("loaded_mermaid", "")

    # Initialise chat history list if missing
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    tab1, tab2, tab3 = st.tabs(
        ["📋 Architecture Blueprint", "🗺️ System Diagram", "💬 Refine with AI"]
    )

    # ── Tab 1: Blueprint ───────────────────────────────────────────────────────
    with tab1:
        st.markdown(response)
        st.divider()
        st.subheader("📥 Download Project")
        col1, col2, col3 = st.columns(3)
        filename_base = f"architecture_{current_type.lower().replace(' ', '_')}"

        with col1:
            st.download_button(
                label="⬇️ Download .txt",
                data=generate_txt(current_idea, current_type, response),
                file_name=f"{filename_base}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                label="⬇️ Download .pdf",
                data=generate_pdf(current_idea, current_type, response),
                file_name=f"{filename_base}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with col3:
            st.button(
                "⬇️ Download .zip",
                disabled=True,
                help="Coming soon — scaffolded project files",
                use_container_width=True,
            )

    # ── Tab 2: Diagram ─────────────────────────────────────────────────────────
    with tab2:
        st.markdown("AI-generated system architecture diagram based on your blueprint.")

        gen_col, _ = st.columns([2, 5])
        with gen_col:
            generate_diagram = st.button(
                "🗺️ Generate Diagram",
                use_container_width=True,
                disabled=bool(current_mermaid),
            )

        if generate_diagram:
            with st.spinner("Drawing your system diagram..."):
                mermaid_code = generate_mermaid(current_idea, current_type, response)
            st.session_state["loaded_mermaid"] = mermaid_code
            st.session_state["edited_mermaid"] = mermaid_code

            history_list = load_history()
            for entry in history_list:
                if (
                    entry.get("full_idea") == current_idea
                    and entry.get("app_type") == current_type
                ):
                    entry["mermaid"] = mermaid_code
                    break
            with open("history.json", "w") as f:
                json.dump(history_list, f, indent=2)
            st.rerun()

        if current_mermaid:
            if "edited_mermaid" not in st.session_state:
                st.session_state["edited_mermaid"] = current_mermaid

            diagram_col, editor_col = st.columns([3, 2])

            with editor_col:
                st.markdown("**✏️ Edit Mermaid Code**")
                edited = st.text_area(
                    label="mermaid_editor",
                    value=st.session_state["edited_mermaid"],
                    height=420,
                    label_visibility="collapsed",
                    key="mermaid_editor_area",
                )
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("▶ Re-render", use_container_width=True):
                        st.session_state["edited_mermaid"] = edited
                        st.rerun()
                with btn_col2:
                    if st.button("↺ Reset", use_container_width=True):
                        st.session_state["edited_mermaid"] = current_mermaid
                        st.rerun()

                st.divider()
                st.markdown("**🤖 Ask AI to edit**")
                ai_instruction = st.text_input(
                    label="ai_instruction",
                    placeholder='e.g. "Add a Redis cache layer"',
                    label_visibility="collapsed",
                )
                if st.button("Apply AI Edit", use_container_width=True):
                    if ai_instruction.strip():
                        with st.spinner("Applying edit..."):
                            updated = ai_edit_diagram(
                                st.session_state["edited_mermaid"],
                                ai_instruction,
                            )
                        st.session_state["edited_mermaid"] = updated
                        st.rerun()
                    else:
                        st.warning("Enter an instruction first.")

            with diagram_col:
                components.html(
                    mermaid_to_html(st.session_state["edited_mermaid"]),
                    height=500,
                    scrolling=True,
                )
                st.divider()
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button(
                        label="⬇️ Download .mmd",
                        data=st.session_state["edited_mermaid"].encode("utf-8"),
                        file_name=f"{filename_base}_diagram.mmd",
                        mime="text/plain",
                        use_container_width=True,
                    )
                with dl_col2:
                    if st.button("💾 Save to History", use_container_width=True):
                        history_list = load_history()
                        for entry in history_list:
                            if (
                                entry.get("full_idea") == current_idea
                                and entry.get("app_type") == current_type
                            ):
                                entry["mermaid"] = st.session_state["edited_mermaid"]
                                break
                        with open("history.json", "w") as f:
                            json.dump(history_list, f, indent=2)
                        st.session_state["loaded_mermaid"] = st.session_state[
                            "edited_mermaid"
                        ]
                        st.success("Saved!")

        elif not generate_diagram:
            st.info(
                "Click **Generate Diagram** to create a visual system map from your blueprint."
            )

    # ── Tab 3: Refine with AI ──────────────────────────────────────────────────
    with tab3:
        st.markdown(
            "Chat with the AI to refine, extend, or question your architecture."
        )

        chat_history: list[dict] = st.session_state["chat_history"]

        # ── Render chat history ────────────────────────────────────────────────
        for turn in chat_history:
            with st.chat_message(turn["role"]):
                if turn.get("is_blueprint"):
                    # Collapsed expander so it doesn't flood the chat
                    with st.expander(
                        "📋 Updated Blueprint — click to expand", expanded=False
                    ):
                        st.markdown(turn["content"])
                    if turn.get("applied"):
                        st.success("✅ Applied to blueprint")
                else:
                    st.markdown(turn["content"])

        # ── Suggestion chips (only shown when chat is empty) ───────────────────
        if not chat_history:
            st.markdown("**Try asking:**")
            suggestions = [
                "Switch the database to PostgreSQL",
                "Add a Redis cache layer",
                "Why REST instead of GraphQL?",
                "Make it more scalable for 1M users",
                "Add real-time notifications with WebSockets",
                "Explain the folder structure in more detail",
            ]
            cols = st.columns(3)
            for i, suggestion in enumerate(suggestions):
                with cols[i % 3]:
                    if st.button(suggestion, key=f"chip_{i}", use_container_width=True):
                        st.session_state["prefill_message"] = suggestion
                        st.rerun()

        # ── Chat input ─────────────────────────────────────────────────────────
        prefill = st.session_state.pop("prefill_message", "")
        user_message = st.chat_input(
            placeholder="e.g. Switch the database to PostgreSQL...",
        )

        # Accept from either chat input or chip prefill
        final_message = user_message or prefill

        if final_message:
            # Show user message immediately
            with st.chat_message("user"):
                st.markdown(final_message)

            # Call the refinement LLM
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    ai_response, is_blueprint = refine_architecture(
                        original_blueprint=response,
                        app_type=current_type,
                        user_idea=current_idea,
                        chat_history=chat_history,
                        new_message=final_message,
                    )

                if is_blueprint:
                    with st.expander(
                        "📋 Updated Blueprint — click to expand", expanded=True
                    ):
                        st.markdown(ai_response)

                    apply_col, _ = st.columns([2, 5])
                    with apply_col:
                        apply_key = f"apply_{len(chat_history)}"
                        if st.button(
                            "✅ Apply as new blueprint",
                            key=apply_key,
                            use_container_width=True,
                        ):
                            # Replace the live blueprint
                            st.session_state["loaded_response"] = ai_response
                            st.session_state["loaded_mermaid"] = (
                                ""  # diagram is now stale
                            )
                            st.session_state["edited_mermaid"] = ""

                            # Mark last turn as applied
                            if chat_history and chat_history[-1].get("is_blueprint"):
                                chat_history[-1]["applied"] = True

                            # Persist to history
                            history_list = load_history()
                            for entry in history_list:
                                if (
                                    entry.get("full_idea") == current_idea
                                    and entry.get("app_type") == current_type
                                ):
                                    entry["response"] = ai_response
                                    entry["mermaid"] = ""
                                    entry["chat_history"] = chat_history
                                    break
                            with open("history.json", "w") as f:
                                json.dump(history_list, f, indent=2)

                            st.success(
                                "Blueprint updated! Diagram has been reset — regenerate it in the Diagram tab."
                            )
                            st.rerun()
                else:
                    st.markdown(ai_response)

            # Append both turns to history
            chat_history.append({"role": "user", "content": final_message})
            chat_history.append(
                {
                    "role": "assistant",
                    "content": ai_response,
                    "is_blueprint": is_blueprint,
                    "applied": False,
                }
            )
            st.session_state["chat_history"] = chat_history

            # Persist chat history to history.json
            history_list = load_history()
            for entry in history_list:
                if (
                    entry.get("full_idea") == current_idea
                    and entry.get("app_type") == current_type
                ):
                    entry["chat_history"] = chat_history
                    break
            with open("history.json", "w") as f:
                json.dump(history_list, f, indent=2)

        # ── Clear chat ─────────────────────────────────────────────────────────
        if chat_history:
            st.divider()
            if st.button("🗑 Clear chat", use_container_width=False):
                st.session_state["chat_history"] = []
                history_list = load_history()
                for entry in history_list:
                    if (
                        entry.get("full_idea") == current_idea
                        and entry.get("app_type") == current_type
                    ):
                        entry["chat_history"] = []
                        break
                with open("history.json", "w") as f:
                    json.dump(history_list, f, indent=2)
                st.rerun()
