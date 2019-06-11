# -*- coding: utf-8 -*-
import socket
import ast
import argparse

port = 10000
backlog = 10
bufsize = 4096


def connect(agent):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    soc.connect((host, port))

    while(1):
        data = soc.recv(bufsize).decode()
        request=''
        info=''
        arg=''
        #print(data)
        try:
            d=ast.literal_eval(data)
            #print(d)
            request=d['request']
            if 'info' in d:
                info=d['info']
            if 'arg' in d:
                arg=d['arg']
        except:
            break
            #raise Exception("received data can't translate into dict",data)

        #print("Server|", request)      # サーバー側の書き込みを表示
        #print(request)
        #print(info)
        # data = input("Client>")  # 入力待機
        # soc.send(data.encode())              # ソケットに入力したデータを送信
        if request=='INITIALIZE':
            #print('initialize')
            name=agent.initialize(arg,info)
            soc.send(name.encode())

        if request.startswith('PURCHASE'):
            agent.purchase(arg,info)

        if request.startswith('SELL'):
            #print('sell')
            #data = input("Client> ")  # 入力待機
            data=agent.sell(info)
            soc.send(str(data).encode())              # ソケットに入力したデータを送信

        if request.startswith('BID'):
            #print('bid')
            #data = input("Client> ")  # 入力待機
            data=agent.bid(arg,info)
            soc.send(str(data).encode())              # ソケットに入力したデータを送信

        if request.startswith('ROUNDOVER'):
            agent.roundover(arg,info)

        if request.startswith("FINISH"):             # qが押されたら終了
            agent.finish(arg,info)

        if request.startswith("DISCONNECT"):
            print('received DISCONNECT request.')
            break

    soc.close()
    return

#if __name__ == '__main__':
#    main()

parser = argparse.ArgumentParser(
        prog="Server.py", #プログラム名
        usage="run this", #プログラムの利用方法
        description="desc", #「optional arguments」の前に表示される説明文
        epilog = "with no args, connect to localhost:10000.", #「optional arguments」後に表示される文字列
        add_help = True #[-h],[--help]オプションをデフォルトで追加するか
        )
parser.add_argument("-t","--host", #オプション引数
                help="host to connect", #引数の説明
                default='localhost'
                )
parser.add_argument("-p","--port", #オプション引数
                    help="port to connect", #引数の説明
                    default=10000
                    )
args = parser.parse_args()
host=args.host
port=int(args.port)
