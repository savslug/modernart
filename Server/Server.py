from __future__ import print_function
import socket
import select
import json
import copy
import random
from time import sleep


host = '127.0.0.1'
port = 10000
backlog = 10
bufsize = 4096
timeout=0

verbose=3
playersize = 3
socks = []
names=[]
log_data=[]

def connect(size):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(size)
    print('port:',port)
    print('waiting for',size, 'connection...')
    for i in range(size):
        soc, addr = s.accept()          # 要求が来るまでブロック
        soc.settimeout(timeout)
        socks.append(soc)
        print("conneted ", str(addr),)  # サーバ側の合図
    print('successfully connected with', len(socks), 'clients.')
    s.close()
    return socks

def initialize(size,info):
    #global socks
    random.shuffle(socks)
    tmp = 0
    for soc in socks:
        msg=str({'request':'INITIALIZE','arg':tmp,'info':accessible_info(tmp,info)})
        data=send_recv(msg,soc)
        #print('Client[' + str(tmp) + ']> ', data)
        while data in names:
            data+='*'
        names.append(data)
        tmp += 1

    for i in range(size):
        ret='INITIALIZE '+agent(i)+' '+names[i]
        log(ret)
    return

def request_sell(sock,info):
    command='SELL'
    #print(command)
    msg=str({'request':command,'info':info})
    recv=send_recv(msg,sock)
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
    recv=send_recv(msg,sock)
    return int(recv)

"""
def request_finish(sock,winner,cash,info):
    command='FINISH'
    #print(command)
    msg=str({'request':command,'arg':winner,'info':info})
    msg+=agent(winner)+' '+ cash
    sock.send(msg.encode())
"""

def accessible_info(player,info):
    ret=copy.deepcopy(info)
    ret.pop('hand_will_receive')
    ret.pop('game_modifier')
    for p in range(info["player_size"]):
        if p!=player:
            ret['player'][p]['hand']=len(info['player'][p]['hand'])
    return ret

def send_recv(msg,sock):
    sock.send(msg.encode())
    try:
        recv=sock.recv(bufsize)
        return recv.decode()
    except socket.timeout:
        sock.close()
        timeout_sock=socks.index(sock)
        #socks.remove(sock)
        print('TIMEOUT Agent['+'{0:02d}'.format(timeout_sock)+']')
        raise Exception('TIMEOUT Agent['+'{0:02d}'.format(timeout_sock)+']')

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

def info_cutter(info):
    ret=copy.deepcopy(info)
    ret.pop('game_modifier')
    return ret

def disconnect():
    for i in socks:
        i.send(str({'request':'DISCONNECT'}).encode())
        i.close()
    return

def log(s):
    log_data.append(s)
    if verbose<=3 and ('BID' in s or 'SELL' in s):
        return
    if verbose<=2 and ('PURCHASE' in s):
        return
    if verbose<=1 and ('DEAL' in s or 'ROUNDOVER' in s or 'SETTLE' in s):
        return
    if verbose==0:
        return
    print(s)


def agent(num):
    return "Agent["+"{0:02d}".format(num) + "]"

def get_name(num):
    return names[num]
