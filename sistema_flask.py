from flask import Flask, request, redirect

app = Flask(__name__)

# Variáveis do sistema (simulação idêntica ao seu código ESP32)
repique1 = repique2 = repique3 = repique4 = repique5 = repativa = reppanico = repalarmeled3 = repalarmeled4 = 0
alarme = 0
modo = 2
verificacao = False
panico_ativo = 0

status_janela = 0
status_porta = 0
status_externa = 0
status_muro = 0
status_portao = 0
status_sistema = 0

# Função para gerar o HTML igual ao seu original, só substituindo as variáveis dinâmicas
def pagina():
    global status_janela, status_porta, status_externa, status_muro, status_portao, status_sistema, panico_ativo
    
    status_acionamento_text = "Ativado" if status_sistema == 1 else "Desativado"
    status_panico_text = "Modo pânico ligado" if panico_ativo == 1 else "Modo pânico desligado"
    
    status_bot1_text = "Sensor da Janela ativado!" if status_janela == 1 else "Sem movimentação"
    status_bot2_text = "Sensor da Porta ativado!" if status_porta == 1 else "Sem movimentação"
    status_bot3_text = "Sensor da Área Externa ativado!" if status_externa == 1 else "Sem movimentação"
    status_bot4_text = "Sensor do Muro ativado!" if status_muro == 1 else "Sem movimentação"
    status_bot5_text = "Sensor do Portão ativado!" if status_portao == 1 else "Sem movimentação"
    
    html = f"""
<html>
<head>
    <title>Sistema de Segurança</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="data:,">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        h1 {{
            color: white;
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 30px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
            animation: fadeInDown 0.8s ease-out;
        }}
        
        .status-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            animation: fadeInUp 0.8s ease-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .status-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }}
        
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .status-item {{
            background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
            padding: 15px;
            border-radius: 12px;
            border-left: 4px solid #4CAF50;
            transition: all 0.3s ease;
        }}
        
        .status-item:hover {{
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .status-text {{
            font-size: 1.1rem;
            font-weight: 500;
            margin: 0;
        }}
        
        .main-status {{
            text-align: center;
            margin-bottom: 25px;
        }}
        
        .main-status p {{
            font-size: 1.3rem;
            font-weight: 600;
            margin: 10px 0;
        }}
        
        .divider {{
            height: 2px;
            background: linear-gradient(90deg, transparent, #ddd, transparent);
            margin: 25px 0;
            border: none;
        }}
        
        .controls {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 30px;
        }}
        
        .btn {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 18px 35px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.3);
            position: relative;
            overflow: hidden;
        }}
        
        .btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        
        .btn:hover::before {{
            left: 100%;
        }}
        
        .btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(76, 175, 80, 0.4);
        }}
        
        .btn:active {{
            transform: translateY(-1px);
        }}
        
        .btn-panic {{
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
            box-shadow: 0 8px 25px rgba(244, 67, 54, 0.3);
        }}
        
        .btn-panic:hover {{
            box-shadow: 0 12px 35px rgba(244, 67, 54, 0.4);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            color: white;
            font-weight: 500;
            animation: fadeIn 1s ease-out 0.5s both;
        }}
        
        @keyframes fadeInDown {{
            from {{
                opacity: 0;
                transform: translateY(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes fadeIn {{
            from {{
                opacity: 0;
            }}
            to {{
                opacity: 1;
            }}
        }}
        
        @media (max-width: 768px) {{
            h1 {{
                font-size: 2rem;
            }}
            
            .status-card {{
                padding: 20px;
                margin: 15px 0;
            }}
            
            .controls {{
                flex-direction: column;
                align-items: center;
            }}
            
            .btn {{
                width: 100%;
                max-width: 300px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Sistema de Segurança</h1>

        <div class="status-card">
            <div class="main-status">
                <p>🟢 <strong>Status do sistema:</strong> {status_acionamento_text}</p>
                <p>🚨 <strong>Status do pânico:</strong> {status_panico_text}</p>
            </div>
            
            <hr class="divider">
            
            <div class="status-grid">
                <div class="status-item">
                    <p class="status-text">🪟 <strong>Janela:</strong> {status_bot1_text}</p>
                </div>
                <div class="status-item">
                    <p class="status-text">🧱 <strong>Muro:</strong> {status_bot4_text}</p>
                </div>
                <div class="status-item">
                    <p class="status-text">📡 <strong>Área externa:</strong> {status_bot3_text}</p>
                </div>
                <div class="status-item">
                    <p class="status-text">🚪 <strong>Porta:</strong> {status_bot2_text}</p>
                </div>
                <div class="status-item">
                    <p class="status-text">🛡️ <strong>Portão:</strong> {status_bot5_text}</p>
                </div>
            </div>
        </div>

        <div class="status-card">
            <div class="controls">
                <a href="/toggle_sistema" class="btn">
                    ⚡ Alternar Sistema
                </a>
                <a href="/toggle_panico" class="btn btn-panic">
                    🚨 Alternar Pânico
                </a>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Feito por:</strong> Paulo Lima, Gysele Torga, Lays Paula, Natanael Lima Neto</p>
        </div>
    </div>
</body>
</html>
    """
    return html

# Rotas para alternar sistema e pânico
@app.route('/')
def home():
    return pagina()

@app.route('/toggle_sistema')
def toggle_sistema():
    global verificacao, status_sistema, modo
    verificacao = not verificacao
    status_sistema = 1 if verificacao else 0
    if verificacao:
        modo = 0
    else:
        modo = 2
    return redirect('/')

@app.route('/toggle_panico')
def toggle_panico():
    global panico_ativo, alarme, modo
    panico_ativo = 0 if panico_ativo == 1 else 1
    if panico_ativo == 1:
        alarme = 1
        modo = 0
    else:
        alarme = 0
        modo = 2
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
