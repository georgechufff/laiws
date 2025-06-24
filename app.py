import gradio as gr
import os
import torch
from text_extractor import TextExtractor 
from typing import Optional
from prompts import TRANSLATION_PROMPT, INTRODUCTION_PROMPT
from configs import sync_openai_api, qdrant_client, embeddings
from qdrant_client import models
import shutil

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

if not qdrant_client.collection_exists(collection_name='laiws'):
    from db_creating import operation_info
    print(operation_info)


css = """
:root {
    --button-width: 200px;
}
.dark-theme {
    background-color: #1a1a1a;
    color: #f0f0f0;
}
.dark-theme .chatbot {
    height: 75vh !important;
    min-height: 600px !important;
    border: 1px solid #444;
    border-radius: 8px;
    background-color: #252525;
    margin-bottom: 15px;
}
.dark-theme .input-box {
    border: 1px solid #444 !important;
    background-color: #2d2d2d !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px !important;
}
.dark-theme .file-upload-btn {
    background-color: #3a3a3a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px !important;
    width: 100% !important;
}
.dark-theme .file-remove-btn {
    background-color: #5a1a1a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px !important;
    width: var(--button-width) !important;
    margin-left: 0 !important; /* Убираем лишний отступ */
}
.dark-theme .submit-btn {
    background-color: #1a3a5a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px !important;
    width: var(--button-width) !important;
}
.dark-theme .clear-btn {
    background-color: #3a3a3a !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px !important;
    width: var(--button-width) !important;
}
.file-info {
    display: flex;
    flex-direction: column; /* Меняем направление на вертикальное */
    gap: 10px;
    margin-top: 10px;
}
.file-name {
    color: #4a90e2;
    word-break: break-all;
}
.message-file {
    font-size: 0.8em;
    color: #888;
    margin-top: 3px;
}
.buttons-container {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}
.file-controls {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 10px;
}
"""

def respond(message: str, chat_history: list, file: Optional[gr.File] = None):
    if file:
        file_info = f"<div class='message-file'>📎 Прикреплён файл: {os.path.join(file.name)}</div>"
        message_md = f"{message}\n{file_info}"
    else:
        message_md = message
        
        
    query_emb = embeddings.encode(message)
    content = qdrant_client.query_points(
        collection_name='laiws',
        query=query_emb,
        limit=3,
        with_payload=True,
    ).points

    docs_content = "\n".join(doc.payload['page_content'] for doc in content)
    
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": TRANSLATION_PROMPT,
                },
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message + docs_content,
                },
            ]
        },
    ]

    answer = sync_openai_api(messages)
    answer += "\n\n Список использованных источников: \n" + '\n'.join(c.payload['metadata'] for c in content)
    answer.replace('\n', '<br>')
    chat_history.append((message_md, answer))
    return "", chat_history, None

def clear_chat():
    return []

def remove_file(file_info, file_name_component):
    return None, "", gr.update(visible=False)

with gr.Blocks(css=css, theme=gr.themes.Default()) as demo:
    gr.Markdown("""<h1 style='text-align: center; margin-bottom: 20px;'>LAIWS - ИИ-консультант по юридическим вопросам</h1>""")
    
    chatbot = gr.Chatbot(
        label="Чат с ИИ-юристом", 
        elem_classes="chatbot",
        height=600
    )
    file_output = gr.File(visible=False)
    
    with gr.Row():
        with gr.Column(scale=8):
            msg = gr.Textbox(
                placeholder="Задайте ваш юридический вопрос...",
                show_label=False,
                elem_classes="input-box",
                container=False
            )
        with gr.Column(scale=2):
            file_upload = gr.UploadButton(
                "📁 Прикрепить файл",
                file_types=[".pdf", ".docx", ".txt", ".md", ".html", ".jpg", ".png"],
                file_count="single",
                elem_classes="file-upload-btn"
            )
    
    with gr.Column(visible=False) as file_info_area:
        with gr.Column(elem_classes="file-controls"):
            file_name_component = gr.Markdown("", elem_classes="file-name")
            remove_btn = gr.Button(
                "❌ Удалить файл", 
                elem_classes="file-remove-btn",
                min_width=200
            )
    
    with gr.Row(elem_classes="buttons-container"):
        submit_btn = gr.Button("Отправить сообщение", elem_classes="submit-btn")
        clear_btn = gr.Button("Очистить историю", elem_classes="clear-btn")
    
    def show_file_info(file):
        if file:
            short_name = os.path.basename(file.name)
            shutil.copy(file.name, os.path.join('uploads', short_name))
            return (
                gr.update(visible=True),
                f"Файл: {short_name}",
                file
            )
        return gr.update(visible=False), "", None
    
    def hide_file_info():
        return gr.update(visible=False), "", None
    
    file_upload.upload(
        show_file_info,
        inputs=file_upload,
        outputs=[file_info_area, file_name_component, file_output]
    )
    
    remove_btn.click(
        hide_file_info,
        outputs=[file_info_area, file_name_component, file_output]
    )
    
    submit_btn.click(
        respond,
        inputs=[msg, chatbot, file_output],
        outputs=[msg, chatbot, file_output]
    ).then(
        hide_file_info,
        outputs=[file_info_area, file_name_component, file_output]
    )
    
    msg.submit(
        respond,
        inputs=[msg, chatbot, file_output],
        outputs=[msg, chatbot, file_output]
    ).then(
        hide_file_info,
        outputs=[file_info_area, file_name_component, file_output]
    )
    
    clear_btn.click(
        clear_chat,
        outputs=chatbot
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)