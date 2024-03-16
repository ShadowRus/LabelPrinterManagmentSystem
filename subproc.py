import subprocess

# Запуск первого скрипта
p1 = subprocess.Popen(["python", "start_web_server.py"])

# Запуск второго скрипта
p2 = subprocess.Popen(["streamlit","run", "./web_ui/web_ui_console.py"])

# Ждем окончания выполнения обоих скриптов
p1.wait()
p2.wait()
