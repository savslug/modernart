# -*- coding: utf-8 -*-
import socket

host = '127.0.0.1'
port = 10000
backlog = 10
bufsize = 4096


def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((host, port))

    while(1):
        data = soc.recv(1024).decode()
        print("Server>", data)      # サーバー側の書き込みを表示
        # data = input("Client>")  # 入力待機
        # soc.send(data.encode())              # ソケットに入力したデータを送信
        if data=='INITIALIZE':
            print('initialize')
            soc.send('accept'.encode())
        if data=='SELL':
            print('sell')
            data = input("Client>")  # 入力待機
            soc.send(data.encode())              # ソケットに入力したデータを送信
        if data=='BID':
            print('bid')
            data = input("Client>")  # 入力待機
            soc.send(data.encode())              # ソケットに入力したデータを送信

        if data == "quit":             # qが押されたら終了
            soc.close()
            break


if __name__ == '__main__':
    main()
