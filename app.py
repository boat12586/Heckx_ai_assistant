#!/usr/bin/env python3
"""
Heckx AI - Enhanced Railway Version with Features
"""
import os
import json
import random
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Enhanced quotes by category
QUOTES_BY_CATEGORY = {
    "wisdom": [
        {"text": "ความสุขไม่ขึ้นอยู่กับสิ่งที่เกิดขึ้น แต่ขึ้นอยู่กับการตอบสนอง", "author": "Epictetus"},
        {"text": "คุณมีอำนาจเหนือจิตใจ ไม่ใช่เหตุการณ์ภายนอก", "author": "Marcus Aurelius"},
        {"text": "ความยากลำบากเปิดเผยตัวตนที่แท้จริง", "author": "Seneca"}
    ],
    "resilience": [
        {"text": "สิ่งที่ขวางทาง จะกลายเป็นทาง", "author": "Marcus Aurelius"},
        {"text": "เราทุกข์ในจินตนาการมากกว่าความเป็นจริง", "author": "Seneca"},
        {"text": "ไฟจะไหม้ไม้ แต่ทำให้ทองคำบริสุทธิ์", "author": "Seneca"}
    ],
    "mindfulness": [
        {"text": "วันนี้เป็นของขวัญ เพราะเราเรียกมันว่า 'ปัจจุบัน'", "author": "Eleanor Roosevelt"},
        {"text": "ความสงบอยู่ในใจ ไม่ใช่ข้างนอก", "author": "Buddha"},
        {"text": "จิตใจที่สงบเป็นพลังที่ยิ่งใหญ่", "author": "Lao Tzu"}
    ],
    "motivation": [
        {"text": "ความเป็นเลิศไม่ใช่การกระทำ แต่เป็นนิสัย", "author": "Aristotle"},
        {"text": "เริ่มต้นที่ไหนก็ได้ แต่ให้เริ่มต้นเดี๋ยวนี้", "author": "John F. Kennedy"},
        {"text": "ทางเดียวที่จะทำสิ่งยิ่งใหญ่ได้คือการรักในสิ่งที่คุณทำ", "author": "Steve Jobs"}
    ]
}

# Database initialization
def init_db():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            message TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            category TEXT,
            rating INTEGER
        )
    ''')
    
    # Create user preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            favorite_category TEXT DEFAULT 'wisdom',
            theme TEXT DEFAULT 'dark',
            language TEXT DEFAULT 'thai',
            notifications BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Heckx AI - Enhanced Assistant</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { 
                font-size: 3.5em; 
                margin-bottom: 20px; 
                text-align: center;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .features-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
                margin: 30px 0;
            }
            .feature-card { 
                background: rgba(255,255,255,0.15); 
                border-radius: 15px; 
                padding: 25px; 
                text-align: center;
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }
            .feature-card:hover { transform: translateY(-5px); }
            .feature-card h3 { margin-bottom: 15px; font-size: 1.5em; }
            .controls { 
                display: flex; 
                flex-wrap: wrap; 
                gap: 15px; 
                justify-content: center; 
                margin: 30px 0;
            }
            button { 
                background: linear-gradient(45deg, #4CAF50, #45a049);
                color: white; 
                border: none; 
                padding: 15px 25px; 
                font-size: 1.1em; 
                border-radius: 25px; 
                cursor: pointer; 
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                min-width: 160px;
            }
            button:hover { 
                transform: translateY(-3px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.3);
            }
            select { 
                padding: 10px 15px; 
                border-radius: 10px; 
                border: none; 
                background: rgba(255,255,255,0.9);
                color: #333;
                font-size: 1em;
            }
            #result { 
                background: rgba(0,0,0,0.4); 
                padding: 25px; 
                border-radius: 15px; 
                margin-top: 25px; 
                min-height: 120px;
                border: 1px solid rgba(255,255,255,0.1);
                animation: fadeIn 0.5s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                gap: 15px; 
                margin: 20px 0;
            }
            .stat-item { 
                background: rgba(255,255,255,0.1); 
                padding: 15px; 
                border-radius: 10px; 
                text-align: center;
            }
            .conversation-history { 
                max-height: 300px; 
                overflow-y: auto; 
                background: rgba(0,0,0,0.2); 
                border-radius: 10px; 
                padding: 15px; 
                margin-top: 20px;
            }
            @media (max-width: 768px) {
                .container { padding: 20px; }
                h1 { font-size: 2.5em; }
                .controls { flex-direction: column; align-items: center; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Heckx AI Assistant</h1>
            <p style="text-align: center; font-size: 1.2em; margin-bottom: 30px;">
                ✨ Enhanced with conversation history, categories, and personalization
            </p>
            
            <div class="features-grid">
                <div class="feature-card">
                    <h3>🎭 Smart Quotes</h3>
                    <p>Categorized wisdom quotes with intelligent recommendations</p>
                </div>
                <div class="feature-card">
                    <h3>💬 Conversation History</h3>
                    <p>Track your interactions and build personalized experiences</p>
                </div>
                <div class="feature-card">
                    <h3>⚡ Performance Monitoring</h3>
                    <p>Real-time health checks and usage analytics</p>
                </div>
                <div class="feature-card">
                    <h3>🎨 Personalization</h3>
                    <p>Customize your experience with preferences and themes</p>
                </div>
            </div>
            
            <div class="controls">
                <select id="category">
                    <option value="random">Random Category</option>
                    <option value="wisdom">Wisdom</option>
                    <option value="resilience">Resilience</option>
                    <option value="mindfulness">Mindfulness</option>
                    <option value="motivation">Motivation</option>
                </select>
                <button onclick="getQuote()">📝 Get Quote</button>
                <button onclick="checkHealth()">❤️ Health Check</button>
                <button onclick="getStats()">📊 Statistics</button>
                <button onclick="getHistory()">📜 History</button>
                <button onclick="clearHistory()">🗑️ Clear History</button>
            </div>
            
            <div id="result">🎯 Select a category and click "Get Quote" to start...</div>
        </div>
        
        <script>
            let userId = localStorage.getItem('heckx_user_id') || 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('heckx_user_id', userId);
            
            function getQuote() {
                const category = document.getElementById('category').value;
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '🔄 Loading wisdom...';
                
                fetch('/api/quote', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        category: category,
                        user_id: userId
                    })
                })
                .then(r => r.json())
                .then(data => {
                    resultDiv.innerHTML = `
                        <div style="border-left: 4px solid #4CAF50; padding-left: 20px;">
                            <h3>📝 ${data.category.toUpperCase()} QUOTE</h3>
                            <p style="font-style: italic; font-size: 1.3em; margin: 15px 0;">"${data.quote}"</p>
                            <p><strong>👤 Author:</strong> ${data.author}</p>
                            <p><strong>🔢 Quote #:</strong> ${data.id}</p>
                            <p><strong>⏰ Time:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                            <div style="margin-top: 15px;">
                                <button onclick="rateQuote(${data.id}, 1)" style="background: #4CAF50; margin: 5px;">👍 Like</button>
                                <button onclick="rateQuote(${data.id}, 0)" style="background: #f44336; margin: 5px;">👎 Dislike</button>
                            </div>
                        </div>
                    `;
                })
                .catch(e => {
                    resultDiv.innerHTML = `<div style="color: #f44336;"><h3>❌ Error</h3><p>${e.message}</p></div>`;
                });
            }
            
            function checkHealth() {
                document.getElementById('result').innerHTML = '🔄 Checking system health...';
                fetch('/health')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('result').innerHTML = `
                        <div style="border-left: 4px solid #2196F3; padding-left: 20px;">
                            <h3>❤️ System Health</h3>
                            <p><strong>Status:</strong> <span style="color: #4CAF50;">${data.status}</span></p>
                            <p><strong>App:</strong> ${data.app}</p>
                            <p><strong>Version:</strong> ${data.version}</p>
                            <p><strong>Uptime:</strong> ${Math.floor(data.uptime || 0)} seconds</p>
                            <p><strong>Database:</strong> <span style="color: #4CAF50;">${data.database_status}</span></p>
                            <p><strong>Timestamp:</strong> ${new Date(data.timestamp).toLocaleString()}</p>
                        </div>
                    `;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `<div style="color: #f44336;"><h3>❌ Health Check Failed</h3><p>${e.message}</p></div>`;
                });
            }
            
            function getStats() {
                document.getElementById('result').innerHTML = '📊 Loading statistics...';
                fetch('/api/stats?user_id=' + userId)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('result').innerHTML = `
                        <div style="border-left: 4px solid #FF9800; padding-left: 20px;">
                            <h3>📊 Your Statistics</h3>
                            <div class="stats">
                                <div class="stat-item">
                                    <h4>${data.total_quotes}</h4>
                                    <p>Total Quotes</p>
                                </div>
                                <div class="stat-item">
                                    <h4>${data.favorite_category}</h4>
                                    <p>Favorite Category</p>
                                </div>
                                <div class="stat-item">
                                    <h4>${data.total_conversations}</h4>
                                    <p>Conversations</p>
                                </div>
                                <div class="stat-item">
                                    <h4>${data.avg_rating}/5</h4>
                                    <p>Avg Rating</p>
                                </div>
                            </div>
                        </div>
                    `;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `<div style="color: #f44336;"><h3>❌ Stats Error</h3><p>${e.message}</p></div>`;
                });
            }
            
            function getHistory() {
                document.getElementById('result').innerHTML = '📜 Loading conversation history...';
                fetch('/api/history?user_id=' + userId)
                .then(r => r.json())
                .then(data => {
                    let historyHtml = '<div style="border-left: 4px solid #9C27B0; padding-left: 20px;"><h3>📜 Recent Conversations</h3>';
                    if (data.conversations.length === 0) {
                        historyHtml += '<p>No conversations yet. Start by getting a quote!</p>';
                    } else {
                        historyHtml += '<div class="conversation-history">';
                        data.conversations.forEach(conv => {
                            historyHtml += `
                                <div style="margin-bottom: 15px; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px;">
                                    <p><strong>Category:</strong> ${conv.category}</p>
                                    <p><strong>Quote:</strong> "${conv.message}"</p>
                                    <p><strong>Time:</strong> ${new Date(conv.timestamp).toLocaleString()}</p>
                                </div>
                            `;
                        });
                        historyHtml += '</div>';
                    }
                    historyHtml += '</div>';
                    document.getElementById('result').innerHTML = historyHtml;
                })
                .catch(e => {
                    document.getElementById('result').innerHTML = `<div style="color: #f44336;"><h3>❌ History Error</h3><p>${e.message}</p></div>`;
                });
            }
            
            function clearHistory() {
                if (confirm('Are you sure you want to clear all conversation history?')) {
                    fetch('/api/history', {
                        method: 'DELETE',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({user_id: userId})
                    })
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('result').innerHTML = `
                            <div style="border-left: 4px solid #4CAF50; padding-left: 20px;">
                                <h3>✅ History Cleared</h3>
                                <p>${data.message}</p>
                            </div>
                        `;
                    })
                    .catch(e => {
                        document.getElementById('result').innerHTML = `<div style="color: #f44336;"><h3>❌ Clear Error</h3><p>${e.message}</p></div>`;
                    });
                }
            }
            
            function rateQuote(quoteId, rating) {
                fetch('/api/rate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        quote_id: quoteId,
                        rating: rating,
                        user_id: userId
                    })
                })
                .then(r => r.json())
                .then(data => {
                    if (data.success) {
                        alert('Thanks for your feedback! 🙏');
                    }
                })
                .catch(e => console.error('Rating error:', e));
            }
            
            // Auto-refresh health check every 60 seconds
            setInterval(() => {
                fetch('/health').catch(() => {}); // Silent health ping
            }, 60000);
        </script>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    """Enhanced health check with database status"""
    try:
        # Test database connection
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'OK',
            'app': 'Heckx AI Enhanced',
            'version': '2.0',
            'timestamp': datetime.now().isoformat(),
            'database_status': 'Connected',
            'total_conversations': total_conversations,
            'uptime': time.time() if 'time' in globals() else 0
        })
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'app': 'Heckx AI Enhanced',
            'timestamp': datetime.now().isoformat(),
            'database_status': 'Error',
            'error': str(e)
        }), 500

@app.route('/api/quote', methods=['POST'])
def get_quote():
    """Enhanced quote endpoint with categories and history"""
    try:
        data = request.get_json() or {}
        category = data.get('category', 'random')
        user_id = data.get('user_id', 'anonymous')
        
        # Select category
        if category == 'random' or category not in QUOTES_BY_CATEGORY:
            category = random.choice(list(QUOTES_BY_CATEGORY.keys()))
        
        # Get quote from selected category
        quote_data = random.choice(QUOTES_BY_CATEGORY[category])
        quote_id = random.randint(1000, 9999)
        
        # Save to database
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_id, message, response, category)
            VALUES (?, ?, ?, ?)
        ''', (user_id, quote_data['text'], quote_data['author'], category))
        conn.commit()
        conn.close()
        
        return jsonify({
            'quote': quote_data['text'],
            'author': quote_data['author'],
            'category': category,
            'id': quote_id,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get user statistics"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        
        # Total quotes
        cursor.execute('SELECT COUNT(*) FROM conversations WHERE user_id = ?', (user_id,))
        total_quotes = cursor.fetchone()[0]
        
        # Total conversations
        cursor.execute('SELECT COUNT(DISTINCT category) FROM conversations WHERE user_id = ?', (user_id,))
        total_conversations = cursor.fetchone()[0]
        
        # Favorite category
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM conversations 
            WHERE user_id = ? 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 1
        ''', (user_id,))
        fav_result = cursor.fetchone()
        favorite_category = fav_result[0] if fav_result else 'None'
        
        # Average rating
        cursor.execute('SELECT AVG(rating) FROM conversations WHERE user_id = ? AND rating IS NOT NULL', (user_id,))
        avg_rating = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            'total_quotes': total_quotes,
            'total_conversations': total_conversations,
            'favorite_category': favorite_category,
            'avg_rating': round(avg_rating, 1)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get conversation history"""
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message, category, timestamp 
            FROM conversations 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 20
        ''', (user_id,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'message': row[0],
                'category': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        
        return jsonify({
            'conversations': conversations,
            'count': len(conversations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Clear conversation history"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversations WHERE user_id = ?', (user_id,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} conversations'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rate', methods=['POST'])
def rate_quote():
    """Rate a quote"""
    try:
        data = request.get_json() or {}
        quote_id = data.get('quote_id')
        rating = data.get('rating')
        user_id = data.get('user_id', 'anonymous')
        
        conn = sqlite3.connect('conversations.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE conversations 
            SET rating = ? 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (rating, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import time
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Heckx AI Enhanced on port {port}")
    print("Features: Categories, History, Statistics, Rating System")
    app.run(host='0.0.0.0', port=port, debug=False)