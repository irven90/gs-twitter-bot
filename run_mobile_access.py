import socket
import os
import subprocess

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    ip = get_local_ip()
    port = 8501
    mobile_url = f"http://{ip}:{port}"
    
    print("\n" + "="*60)
    print("📱 GALATASARAY X BOTU - MOBİL ANDROİD ERİŞİM REHBERİ")
    print("="*60)
    print(f"\n1. Telefonunuz ile bilgisayarınız aynı Wi-Fi ağına bağlı olsun.")
    print(f"2. Android telefonunuzun Chrome tarayıcısında şu adresi açın:\n")
    print(f"   👉  {mobile_url}\n")
    print("3. İPUCU (Uygulama İkonu Ekleme):")
    print("   Chrome menüsünden (üç nokta) 'Ana ekrana ekle' (Add to Home Screen)")
    print("   seçeneğine basarak telefonunuza tıpkı bir Android uygulaması gibi ekleyebilirsiniz!")
    print("="*60 + "\n")
    
    print("🚀 Streamlit başlatılıyor...")
    subprocess.run(["python", "-m", "streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", str(port)])
