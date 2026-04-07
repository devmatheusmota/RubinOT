import os
import time
import ssl
import easyocr
import cv2
import numpy as np
import dxcam  # Nova biblioteca para furar a tela preta
import traceback

# Ignora erro de SSL
ssl._create_default_https_context = ssl._create_unverified_context

# --- COORDENADAS (X1, Y1, X2, Y2) ---
X1, Y1, X2, Y2 = 462, 206, 1453, 841

try:
    print("="*40)
    print("    INICIALIZANDO CAPTURA DE ALTA PERFORMANCE")
    print("="*40)
    
    # Inicializa a IA e a Câmera de captura direta
    reader = easyocr.Reader(['en'], gpu=False)
    camera = dxcam.create()

    print("\n[!] Você tem 4 SEGUNDOS! Mude para o RubinOT!")
    for i in range(4, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    def executar_leitura():
        print("\n📸 Tentando capturar via DXCAM (Direto da GPU)...")
        
        # O DXCAM tira o print da região exata: (esquerda, topo, direita, baixo)
        img_cortada = camera.grab(region=(X1, Y1, X2, Y2))
        
        # Se falhar, tenta pegar a tela toda e cortar
        if img_cortada is None:
            print("Tentando captura total via DXCAM...")
            img_full = camera.grab()
            img_cortada = img_full[Y1:Y2, X1:X2]

        # Converte para BGR para o OpenCV salvar a foto
        img_bgr = cv2.cvtColor(img_cortada, cv2.COLOR_RGB2BGR)
        
        # Caminho para salvar
        pasta_atual = os.path.dirname(os.path.abspath(_file_))
        caminho_foto = os.path.join(pasta_atual, "o_que_o_bot_ve.png")
        cv2.imwrite(caminho_foto, img_bgr)
        
        # Validação final
        if np.mean(img_cortada) < 5:
            print("\n❌ AINDA PRETO. Isso é raríssimo com DXCAM.")
            print("DICA FINAL: Vá no RubinOT > Graphics e DESATIVE 'Antialiasing' ou 'V-Sync'.")
        else:
            print(f"✅ FINALMENTE! Imagem capturada: {caminho_foto}")
            print("🔍 Analisando textos... (Aguarde)")
            
            resultado = reader.readtext(img_cortada)

            print("\n" + "="*40)
            print("        TEXTOS ENCONTRADOS")
            print("="*40)
            for (bbox, texto, confidence) in resultado:
                print(f"Lido: '{texto}'")
            print("="*40)

    executar_leitura()

except Exception:
    print("\n" + "!"*40)
    traceback.print_exc()
    print("!"*40)

finally:
    print("\nPROCESSO FINALIZADO.")
    input("Aperte ENTER para fechar o terminal...")
