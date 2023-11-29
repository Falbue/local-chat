from tkinter import *
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import socket
import threading
import os


name = 'user'
rename_user = False

client_socket = ''
ip_server = ''

def receive_messages():
    print("Подключение...")
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(message)
        except ConnectionResetError:
            messages_area.configure(state = 'normal')
            messages_area.insert(tk.END, "Сервер отключен" + '\n')
            messages_area.configure(state = 'disabled')
            client_socket.close()
            break
        try:
            messages_area.configure(state = 'normal')
            messages_area.insert(tk.END,  message + '\n')
            messages_area.see(tk.END)
            messages_area.configure(state = 'disabled')
        except Exception as e:
            print("Ошибка" + e)

def send_message(event=None):
    global rename_user, name
    if rename_user == False:
        # Отправляем сообщение на сервер
        message = f"{name}: {entry_field.get()}"
        client_socket.sendall(message.encode())
        entry_field.delete(0, tk.END)
    if rename_user == True:
        rename_user = False
        name = entry_field.get()
        entry_field.delete(0, tk.END)
        messages_area.configure(state = 'normal')
        messages_area.insert(tk.END, 'Имя пользователя изменено!' + '\n')
        messages_area.see(tk.END)
        messages_area.configure(state = 'disabled')

def rename():
    global rename_user, name
    messages_area.configure(state = 'normal')
    messages_area.insert(tk.END, 'Введите новое имя пользователя...' + '\n')
    messages_area.see(tk.END)
    messages_area.configure(state = 'disabled')
    username_button.pack_forget()
    rename_user = True

# Создаем окно приложения
window = tk.Tk()
window.title("Chat")
window.geometry("400x700")

# Создаем поле для отображения сообщений
messages_area = ScrolledText(window, state = 'disabled')
messages_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Создаем поле для ввода сообщения
entry_field = tk.Entry(window, state = 'disabled')
entry_field.pack(padx=10, pady=10, fill=tk.X)

# Привязываем событие нажатия Enter к функции отправки сообщения
entry_field.bind('<Return>', send_message)

# Создаем кнопку для отправки сообщения
send_button = tk.Button(window, text="Подключение...", command=send_message, state = 'disabled', activebackground = '#14b814')
send_button.pack(side = RIGHT, padx=10, pady=5, fill=BOTH, expand = True)

username_button = Button(window, text="Никнейм", command=rename)

def exit(x):
    try:
        client_socket.sendall(x.encode())
        window.destroy()
    except:
        window.destroy()

window.protocol("WM_DELETE_WINDOW", lambda: exit("/close"))


def find_server():
    global client_socket
    try:
        message = "/login"
        open_servers = []
    
        def handle_clients(ip_adresesses):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((ip_adresesses, 12345))
                client_socket.sendall(message.encode())
                while True:
                    try:
                        response = client_socket.recv(1024).decode()
                        open_servers.append(f"{ip_adresesses}")
                    except:
                        print(f"Работа с сервером {ip_adresesses} завершена")
                        client_socket.close()
                        return  # остановка выполнения функции
                    print(f"Ответ сервера {ip_adresesses}: {response}")
                    client_socket.close()
                    break
            except:
                print(f"Сервер {ip_adresesses} недоступен")
                client_socket.close()
            finally:
                client_socket.close()
        
        threads = []
        for port in range (1,256):
            ip_adresesses = f"172.20.1.{port}"
            thread = threading.Thread(target=handle_clients, args=(ip_adresesses,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
    
        
        print(f"Доступный сервер: {open_servers}")
        if len (open_servers) == 0:
            print("Массив пустой")
            threading.Thread(target=server).start()
            print(f"ip server = {ip_server}")
            ip_address = ip_server
        else:
            ip_address = open_servers[0]
        username_button.pack(side = LEFT, padx=10, pady=5)
        send_button.configure(bg = "#00ff00", state = 'normal', text = 'Отправить')
        entry_field.configure(state = 'normal')
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip_address, 12345))
        except Exception as e:
            error()
            print(e)
        # Запускаем поток для приема сообщений
        threading.Thread(target=receive_messages).start()

    except Exception as e:
        print(e)
ip_server = socket.gethostbyname(socket.gethostname())

def server():
    global ip_server
    # Создаем сокет сервера
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip_address = socket.gethostbyname(socket.gethostname())
    ip_server = socket.gethostbyname(socket.gethostname())
    server_socket.bind((ip_address, 12345))
    print(f"Адрес: {ip_address}")
    server_socket.listen(1)
    login = "test"
    # Список подключенных клиентов
    clients = []
    
    print("Сервер запущен...")
    def handle_client(client_socket, client_address):
        while True:
            # Принимаем сообщение от клиента
            try:
                message = client_socket.recv(1024).decode()
                print(message)
            
                if message == "/close":
                    # Если сообщения нет, отключаем клиента
                    clients.remove(client_socket)
                    client_socket.close()
                    print("Отключился...")
                    break
    
                if message == "/login":
                    for client in clients:
                        message = login
                        client.sendall(message.encode())
                        client.remove(client_socket)
                        client_socket.close()
                        print("Поиск окончен")
                        break
                # Отправляем сообщение всем клиентам
                else:
                    for client in clients:
                        try:
                            client.sendall(message.encode())
                        except Exception as e:
                            print(e)
                            break
            except Exception as e:
                print("Ошибка на стороне клиента")
                print(e)
                break
    while True:
        # Принимаем подключение клиента
        client_socket, client_address = server_socket.accept()
        
        # Добавляем клиента в список
        clients.append(client_socket)
        
        # Запускаем обработчик клиента в отдельном потоке
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

def error():
    messages_area.insert(tk.END, "Сервер отключен, дождитесь запуска сервера и повторите попытку" + '\n')
    btn_exit = Button(window, text = 'Выход', command = lambda: exit("/close"))
    send_button.pack_forget()
    username_button.pack_forget()
    btn_exit.pack(side = RIGHT, padx=10, pady=5, fill=BOTH, expand = True)

threading.Thread(target=find_server).start()

# Запускаем главный цикл обработки событий
window.mainloop()