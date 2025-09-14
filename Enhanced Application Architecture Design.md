## Enhanced Application Architecture Design

### 1. Data Structures for Custom Bots and User Configurations

To support custom bots and personalization, we will introduce new data structures, likely stored in Supabase, linked to the `user_id`.

**`custom_bots` table (in Supabase):**
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key to Supabase auth.users table)
- `name`: String (e.g., "My Marketing Bot")
- `description`: Text
- `emoji`: String (e.g., "💡")
- `category`: String (e.g., "My Custom Bots")
- `temperature`: Float (OpenAI API parameter)
- `system_prompt`: Text (The core instruction for the custom bot)
- `specialties`: JSONB (List of strings)
- `quick_actions`: JSONB (List of strings)
- `created_at`: Timestamp
- `updated_at`: Timestamp

**`chat_histories` table (in Supabase):**
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key)
- `agent_name`: String (Name of the bot, custom or predefined)
- `messages`: JSONB (List of message objects: `{'role': 'user'/'assistant', 'content': 'message', 'timestamp': '...'}`)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### 2. Mechanism for Custom Bots

Instead of directly modifying `BOT_PERSONALITIES`, we will:
- **Load `BOT_PERSONALITIES`**: Keep the existing `BOT_PERSONALITIES` dictionary for predefined agents.
- **Load Custom Bots**: Fetch custom bots from the `custom_bots` Supabase table for the authenticated user.
- **Combine Bots**: Create a combined dictionary or list of all available bots (predefined + custom) for display in the agent selector.
- **Dynamic `get_agent_prompt`**: The `get_agent_prompt` function will need to dynamically construct the system prompt based on whether the selected agent is predefined or a custom bot (using its `system_prompt` field).

### 3. OpenAI API Integration for Custom Bot Creation

- **Bot Creation Form**: A new Streamlit page/section will allow users to input details for their custom bot (name, description, emoji, system prompt, specialties, quick actions, temperature).
- **Save to Supabase**: Upon submission, this data will be saved to the `custom_bots` table in Supabase, linked to the current `user_id`.
- **No direct OpenAI API call for creation**: The custom bot creation process itself does not directly call the OpenAI API. Instead, it defines the *parameters* that will be used when the custom bot interacts with the OpenAI API.

### 4. Streamlit Multi-Page Structure

Streamlit applications can be structured into multiple pages by creating separate Python files in a `pages` directory. However, for simplicity and to keep the application within a single file as much as possible, we will implement a page navigation system within `ai_agent_toolkit.py` using Streamlit's `st.sidebar` and `st.radio` or `st.selectbox` to switch between different functional views (pages).

**Proposed Pages/Views:**
- **Home/Chat**: The existing chat interface.
- **Manage Custom Bots**: A new page where users can create, view, edit, and delete their custom AI bots.
- **User Profile/Settings**: A page for user-specific settings, potentially including API key management (if we allow users to bring their own keys) or other preferences.

**Navigation Flow:**
- The `main()` function will orchestrate which page function is called based on a `st.session_state.page` variable, which will be updated via sidebar navigation elements.

### 5. Personalization Areas

- **Custom Bots**: Users can define their own AI assistants.
- **Persistent Chat History**: Chat history will be loaded from and saved to Supabase, allowing conversations to persist across sessions and devices.
- **User-specific settings**: Future enhancements could include user-specific default models, temperatures, or other preferences stored in Supabase.

This design ensures that the core `ai_agent_toolkit.py` remains manageable while extending functionality and leveraging Supabase for persistent, personalized data storage.

