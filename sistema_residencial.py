#importações
from machine import PWM,Pin
from time import sleep_ms, ticks_ms, sleep
import network
import socket
import _thread

repique1 = 0
repique2 = 0
repique3 = 0
repique4 = 0
repique5 = 0
repativa = 0
reppanico = 0
repalarmeled3 = 0
repalarmeled4 = 0

led1 = Pin(15, Pin.OUT)

led1.value(0)

led2 = Pin(21, Pin.OUT)

led2.value(1)

led3 = Pin(22, Pin.OUT)
led4 = Pin(23, Pin.OUT)
bot1 = Pin(2, Pin.IN, Pin.PULL_UP)
bot2 = Pin(0, Pin.IN, Pin.PULL_UP)
bot3 = Pin(4, Pin.IN, Pin.PULL_UP)
bot4 = Pin(16, Pin.IN, Pin.PULL_UP)
bot5 = Pin(17, Pin.IN, Pin.PULL_UP)
botativa = Pin(18, Pin.IN, Pin.PULL_UP)
botpanico = Pin(19, Pin.IN, Pin.PULL_UP)
servo = PWM(Pin(13), freq=50)
verificacao = False
alarme = 0
modo = 2
som = PWM(Pin(12,Pin.OUT), freq=500, duty_u16=0)
i = 0
j = 0

#inicialização do servidor web via socket 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(4)

# Variáveis para controle via website
status_janela = 0 #bot1
status_porta = 0 # #bot2
status_externa = 0 #bot3
status_muro = 0 #bot4
status_portao = 0 #bot5
# Controle do botão de ligar/desligar e de pânico
status_sistema = 0
panico_ativo = 0

def conectar_wifi(ssid, senha): # Conexão com o wi-fi
    print("Conectando-se ao Wi-Fi", end="")
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, senha)
    while not sta.isconnected():
        print(".", end="")
        sleep(0.1)
    print(" Conectado!")
    print("IP:", sta.ifconfig()[0])
    return sta

wlan = conectar_wifi("Wokwi-GUEST", "") ## Rede Wowki (Para Testes, substituir ou fazer prompt)

print('O Sistema pode ser ativado!')

def mover_servo(angulo): # Calcula o movimento do servo (Travado/Destravado)
    duty = int((angulo / 180) * 75 + 40)
    servo.duty(duty)

def bot1ativo (pino): #Controle do botão 1

    global modo
    global alarme
    global verificacao
    global repique1
    global status_janela
    
    if(((ticks_ms() - repique1) > 300) and verificacao == True):
        print('O sensor da janela foi ativado! Cuidado')
        status_janela = 1
        alarme = 1
        repique1 = ticks_ms()
        print(status_janela)
        if(led3.value() == 0 and led4.value() == 0):
            modo = 0
            status_janela = 0
    

def bot2ativo(pino): #Controle do botão 2

    global modo 
    global alarme
    global verificacao
    global repique2
    global status_porta


    if(((ticks_ms() - repique2) > 300) and verificacao == True):
        print('O sensor da porta foi ativado! Cuidado')
        status_porta = 1
        alarme = 1
        repique2 = ticks_ms()
        if(led3.value() == 0 and led4.value() == 0):
            modo = 0
            status_porta = 0
    

def bot3ativo(pino): #Controle do botão 3

    global modo
    global alarme
    global verificacao
    global repique3
    global status_externa


    if(((ticks_ms() - repique3) > 300) and verificacao == True):
        print('O sensor da área externa foi ativado! Cuidado')
        status_externa = 1
        alarme = 1
        repique3 = ticks_ms()
        if(led3.value() == 0 and led4.value() == 0):
            modo = 0
            status_externa = 0

def bot4ativo(pino): #Controle do botão 4

    global modo
    global alarme
    global verificacao
    global repique4
    global status_muro

    if(((ticks_ms() - repique4) > 300) and verificacao == True):
        print('O sensor do muro foi ativado! Cuidado')
        status_muro = 1
        alarme = 1
        repique4 = ticks_ms()
        if(led3.value() == 0 and led4.value() == 0):
            modo = 0
            status_muro = 0

def bot5ativo(pino): #Controle do botão 5

    global modo
    global alarme
    global verificacao
    global repique5
    global status_portao

    if(((ticks_ms() - repique5) > 300) and verificacao == True):
        print('O sensor do portão foi ativado! Cuidado')
        status_portao = 1
        alarme = 1
        repique5 = ticks_ms()
        if(led3.value() == 0 and led4.value() == 0):
            modo = 0
            status_portao = 0

def apertoubotaoativa(pino): #Controle do botão de ativação

    global verificacao
    global repativa
    global status_sistema

    if((ticks_ms() - repativa) > 300):
        verificacao = not verificacao
        led1.value(not led1.value())
        led2.value(not led2.value())
        if(verificacao==True):
            print('Sistema de segurança ON')
            mover_servo(0)
            status_sistema = 1
        if(verificacao==False):
            print('Sistema de segurançao OFF')
            mover_servo(90)
            status_sistema = 0
        repativa = ticks_ms()

def apertoubotaopanico(pino): #Controle do botão de pânico
    global verificacao, alarme, modo, reppanico, panico_ativo, ldpanico

    if ((ticks_ms() - reppanico) > 1000) and verificacao:
        panico_ativo = not panico_ativo  # alterna o estado (liga/desliga)

        if panico_ativo:
            print('Botão de pânico ON')
            alarme = 1
            modo = 0
            ldpanico = 1
        else:
            print('Botão de pânico OFF')
            alarme = 0
            modo = 2
            ldpanico = 0
            led3.value(0)
            led4.value(0)
            som.duty_u16(0)
            panico_ativo = 0

        reppanico = ticks_ms()

def pagina(): # Função que define as variaveis para serem usadas para controle da pagina e o html da página
    global status_muro, status_janela, status_porta, status_sistema, status_externa, panico_ativo, status_portao
    
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
                <a href="/?toggle_sistema" class="btn">
                    ⚡ Alternar Sistema
                </a>
                <a href="/?toggle_panico" class="btn btn-panic">
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

def website(): # Função que escuta os requests e ultilza as funções de ligar o sistema e botão de pânico

    while True:
        global s 
        conexao, endereco = s.accept()
        print(f'Conexão recebida de {str(endereco)}')
        request = conexao.recv(1024)
        request = str(request)
        print(f'Solicitação recebida: {request}')
    
        if '/?toggle_sistema' in request:
            apertoubotaoativa(None)
        if '/?toggle_panico' in request:
            apertoubotaopanico(None)

_thread.start_new_thread(website, ()) #Inicia o site paralelamente com o resto do código 


# Controle dos botões e quais funções vão ser usadas
bot1.irq(trigger=Pin.IRQ_FALLING, handler=bot1ativo)
bot2.irq(trigger=Pin.IRQ_FALLING, handler=bot2ativo)
bot3.irq(trigger=Pin.IRQ_FALLING, handler=bot3ativo)
bot4.irq(trigger=Pin.IRQ_FALLING, handler=bot4ativo)
bot5.irq(trigger=Pin.IRQ_FALLING, handler=bot5ativo)
botativa.irq(trigger=Pin.IRQ_FALLING, handler=apertoubotaoativa)
botpanico.irq(trigger=Pin.IRQ_FALLING, handler=apertoubotaopanico)

# Faz o sistema do buzzer e dos leds do Estrobo e do led de ativação
while True:
    if((alarme == 1) and verificacao == True):
        if((ticks_ms() - repalarmeled3 > 300) and modo == 0):
            led3.value(1)
            led4.value(0)
            som.duty_u16(0)
            modo = 1
            repalarmeled4 = ticks_ms()
        if((ticks_ms() - repalarmeled4 > 300) and modo == 1):
            i+=1
            led3.value(0)
            led4.value(1)
            som.duty_u16(512)
            if(i%2 == 0):
                som.freq(300)
            else:
                som.freq(250)
            repalarmeled3 = ticks_ms()
            modo=0
    else :
        led3.value(0)
        led4.value(0)
        alarme = 0
        modo=2
        som.duty_u16(0)

