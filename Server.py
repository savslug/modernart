from __future__ import print_function
import socket
import select
import json
import copy
from time import sleep

host = '127.0.0.1'
port = 10000
backlog = 10
bufsize = 4096

playersize = 3
socks = []
log_data=[]

def connect(size,info):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(size)
    print('waiting for',size, 'connection...')
    for i in range(size):
        soc, addr = s.accept()          # 要求が来るまでブロック
        socks.append(soc)
        print("conneted from", str(addr),)  # サーバ側の合図
    print('successfully connected with', len(socks), 'clients.')

    for soc in socks:
        soc.send(str({'request':'INITIALIZE','info':info}).encode())
        #print('initialize')

    tmp = 0
    for soc in socks:
        tmp += 1
        data = soc.recv(bufsize).decode()
        #print('Client[' + str(tmp) + ']> ', data)
        if data != 'accept':
            raise Exception('initialize failed.')
    return socks


def request_sell(sock,info):
    command='SELL'
    #print(command)
    msg=str({'request':command,'info':info})
    sock.send(msg.encode())
    recv = sock.recv(bufsize).decode()
    result=-1
    try:
        result=int(recv)
    except:
        raise Exception('painting id must be int.')
    return int(recv)

def request_bid(sock,item,info):
    command = 'BID'
    #print(command)
    msg=str({'request':command,'arg':item,'info':info})
    sock.send(msg.encode())
    recv = sock.recv(bufsize).decode()
    return int(recv)

def request_finish(sock,winner,cash):
    command='FINISH'
    #print(command)
    msg=str({'request':command,'info':info})
    msg+=agent(winner)+' '+ cash
    sock.send(msg.encode())


def accessible_info(player,info):
    ret=copy.deepcopy(info)
    ret.pop('hand_will_receive')
    for p in range(info["player_size"]):
        if p!=player:
            ret['player'][p]['hand']=len(info['player'][p]['hand'])
    return ret

def broadcast(s):
    #print("BROAD:", s)
    for sock in socks:
        sock.send(s.encode())
    sleep(0.01)
    return

def broadcast_personal(dic,info):
    #print("BROPE:",dic)
    for i in range(info['player_size']):
        ret=accessible_info(i,info)
        dic['info']=ret
        socks[i].send(str(dic).encode())
    sleep(0.01)
    return

def log(s):
    #if 'BID' not in s and 'SELL' not in s:
    print(s)
    log_data.append(s)



def agent(num):
    return "Agent["+"{0:02d}".format(num) + "]"

if __name__ == '__main__':
    connect(3)
