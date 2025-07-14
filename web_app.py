#!/usr/bin/env python3
"""
Web version of Heckx AI Assistant for Railway deployment
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import whisper
from rich.console import Console
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize components
console = Console()

# For Railway deployment, we'll use a simpler setup
class SimpleAI:
    def __init__(self):
        self.template = """
        คุณคือ Heckx ผู้ช่วย AI ภาษาไทย สร้างโดย bobo
        คุณตอบคำถามอย่างเป็นมิตรและให้ข้อมูลที่เป็นประโยชน์
        
        ประวัติการสนทนา: {history}
        คำถาม: {input}
        คำตอบ:
        """
        
        self.prompt = PromptTemplate(
            input_variables=["history", "input"], 
            template=self.template
        )
        
        # Simple memory for conversation
        self.conversation_history = []
    
    def get_response(self, user_input):
        # Simple response logic for Railway deployment
        responses = {
            "สวัสดี": "สวัสดีครับ! ผม Heckx ยินดีที่ได้รู้จักคุณ",
            "คุณคือใคร": "ผมคือ Heckx ผู้ช่วย AI ที่สร้างโดย bobo เพื่อช่วยเหลือคุณในงานต่างๆ",
            "ขอบคุณ": "ยินดีครับ! มีอะไรให้ช่วยอีกไหม?",
        }
        
        # Simple keyword matching
        for keyword, response in responses.items():
            if keyword in user_input:
                return response
                
        return f"ขอบคุณสำหรับคำถาม: '{user_input}' ขณะนี้ระบบกำลังพัฒนาอยู่ครับ"

# Initialize AI
ai = SimpleAI()

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Heckx AI Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
            .chat-box { height: 400px; border: 1px solid #ddd; padding: 20px; overflow-y: scroll; margin-bottom: 20px; }
            .input-box { width: 70%; padding: 10px; }
            .send-btn { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #e3f2fd; text-align: right; }
            .ai { background: #f1f8e9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Heckx AI Assistant</h1>
            <p>สวัสดีครับ! ผมคือ Heckx ผู้ช่วย AI ของคุณ</p>
            
            <div id="chatBox" class="chat-box">
                <div class="message ai">สวัสดีครับ! มีอะไรให้ผมช่วยไหม?</div>
            </div>
            
            <div>
                <input type="text" id="userInput" class="input-box" placeholder="พิมพ์ข้อความของคุณ..." onkeypress="handleEnter(event)">
                <button onclick="sendMessage()" class="send-btn">ส่ง</button>
            </div>
        </div>

        <script>
            function sendMessage() {
                const input = document.getElementById('userInput');
                const chatBox = document.getElementById('chatBox');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Add user message
                chatBox.innerHTML += `<div class="message user">คุณ: ${message}</div>`;
                
                // Clear input
                input.value = '';
                
                // Send to server
                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                })
                .then(response => response.json())
                .then(data => {
                    chatBox.innerHTML += `<div class="message ai">Heckx: ${data.response}</div>`;
                    chatBox.scrollTop = chatBox.scrollHeight;
                })
                .catch(error => {
                    chatBox.innerHTML += `<div class="message ai">ขออภัย เกิดข้อผิดพลาด: ${error}</div>`;
                });
                
                chatBox.scrollTop = chatBox.scrollHeight;
            }
            
            function handleEnter(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Get AI response
        response = ai.get_response(user_message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Heckx AI Assistant'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)