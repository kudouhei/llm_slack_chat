# llm_slack_chat
A chat bot that lets you chat with LLMs from Slack

### uv

```bash
uv venv .venv  # 创建虚拟环境
uv sync  # 安装依赖
uv run python run.py  # 运行程序
```

### quick start

**Slack app setup**

1. Create a new Slack app
2. Add scopes in `OAuth & Permissions`:
   - `app_mentions:read`
   - `chat:write`
   - `channels:history`
3. Enable **Socket Mode** and get the App-Level Token
4. Set up `app_mention` events in **Event Subscriptions**
5. Invite the bot to a channel

Example:
```
display_information:
  name: Chat Bot
  description: A chat bot
features:
  app_home:
    home_tab_enabled: false
    messages_tab_enabled: true
    messages_tab_read_only_enabled: false
  bot_user:
    display_name: Chat Bot
    always_online: true
  slash_commands:
    - command: /help
      description: Show help
      usage_hint: ""
      should_escape: false
oauth_config:
  scopes:
    bot:
      - app_mentions:read
      - channels:history
      - chat:write
      - chat:write.customize
      - chat:write.public
      - commands
      - files:write
      - groups:history
      - im:history
      - users:read
settings:
  event_subscriptions:
    bot_events:
      - app_mention
      - message.im
  interactivity:
    is_enabled: true
  org_deploy_enabled: false
  socket_mode_enabled: true
  token_rotation_enabled: false
```


**Environment Setup**

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

**Run the bot**

```bash
# start ollama
ollama serve

# start the bot
uv run python run.py
```

**Basic Commands**

```
@bot Hello                        # Default (Ollama)
@bot /help                        # Show help
@bot /clear                       # Clear history
```
