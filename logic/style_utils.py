def load_css():
    return """
    <style>
    .message-board {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid #888;
        padding: 1rem;
        border-radius: 10px;
        max-height: 400px;
        overflow-y: auto;
        font-family: sans-serif;
    }
    .message {
        margin-bottom: 1.2rem;
    }
    .header {
        font-weight: bold;
        margin-bottom: 0.25rem;
    }
    .toxic {
        background-color: #111;
        padding: 0.5rem;
        color: #ff4b4b;
        border-radius: 4px;
        font-style: italic;
    }
    .clean {
        background-color: #222;
        padding: 0.5rem;
        color: #ddd;
        border-radius: 4px;
    }
    .confidence {
        font-size: 0.75rem;
        color: #aaa;
    }
    </style>
    """

def render_message_html(msg):
    emoji = "🔴" if msg["is_toxic"] else "🟢"
    time = msg["timestamp"]
    user = "Anonymous"
    conf = msg.get("confidence", 0.0)

    if msg["is_toxic"]:
        content = (
            '<div class="toxic">‼️ Muted by Moderator<br>'
            '<code>***************</code></div>'
        )
        conf_text = f'<div class="confidence">Confidence: {conf:.2f}% toxic</div>'
    else:
        content = f'<div class="clean">{msg["message"]}</div>'
        conf_text = f'<div class="confidence">Confidence: {100 - conf:.2f}% clean</div>'

    return (
        f'<div class="message">'
        f'<div class="header">{emoji} {user} • <i>{time}</i></div>'
        f'{content}'
        f'{conf_text}'
        f'</div>'
    )
