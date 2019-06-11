import numpy as np
import random
from collections import Counter
import Server as server
import argparse

RPR={
    3:[10,6,6],
    4:[9,4,4],
    5:[8,3,3],
}

class SimpleModernArt(object):

    def __init__(self, player_size):
        self.base_info = {
            "player_size": player_size,
            "total_paintings": [12, 13, 14, 15, 16],
            "base_value": [0, 0, 0, 0, 0],
            "hand_will_receive": None,
            "remaining_round": 4,
            "turn_player": 0,
            "purchased_paintings": [],
            "player": [{
                "id": i,
                "cash": 100,
                "hand": [],
                "purchased": []
            } for i in range(player_size)],
            "game_modifier": {
                "deal_evenly": False,
                "seed": 6,
                "limit": int(args.limit),
                "kinds": 5,
                "sell_price": [30, 20, 10],
                "hand_receive_per_round": RPR[5] if player_size==5 else RPR[4] if player_size==4 else RPR[3],
            }

        }
        self.base_info["hand_will_receive"] = initialize_hand(self.base_info)

    def game(self,):
        """
        1ゲーム
        """
        self.deal()
        while self.base_info["remaining_round"] > 0:
            tp = self.base_info["turn_player"]
            ps = self.base_info["player_size"]
            if self.auction(tp) == "ROUND OVER":
                self.round_over()
            self.base_info["turn_player"] = (tp + 1) % ps
            for player in self.base_info["player"]:
                if player["hand"] != []:
                    break
            else:
                self.round_over()
        self.finish()

    def finish(self,):
        players = self.base_info["player"]
        cashs = []
        for p in players:
            cashs.append((p["cash"], p["id"]))
        cashs = sorted(cashs, reverse=True)
        winner = []
        win_cash = -1
        winner.append(cashs[0][1])
        win_cash = cashs[0][0]
        cashs.pop(0)
        
        while len(cashs)>0 and cashs[0][1] == win_cash:
            winner.append(cashs.pop(0)[0])

        s = "FINISH "+str(win_cash)
        for i in winner:
            s += (" " + agent(i))
        for i in winner:
            s+=(' '+server.get_name(i))
        server.log(s)
        server.broadcast(str({'request':'FINISH','arg':winner,'info':self.base_info}))
        return s

    def auction(self, seller):
        """
        オークション
        """
        painting = request_auction(seller, self.base_info)
        if painting == "PASS":
            return painting
        self.base_info["purchased_paintings"].append(painting)
        if self.check_finish():
            self.base_info["player"][seller]["hand"].remove(painting)
            return "ROUND OVER"

        bid = []
        psize = len(self.base_info["player"])

        for priority in range(psize):
            bidder = (seller+priority+1) % psize
            price=request_bid(
                    painting, self.base_info["player"][bidder]["id"], self.base_info)
            bid.append((
                price,
                -priority,
                bidder
            ))
        # print(bid)

        #全員0ならsellerが最優先
        bid = list(sorted(bid, reverse=True))
        buyer = seller
        for i in bid:
            if i[0] != 0:
                buyer = bid[0][2]
                break

        result = self.transaction(buyer, seller, bid[0][0], painting)
        bid_hist={}
        for i in bid:
            bid_hist[i[2]]=i[0]

        j={'request':'PURCHASE',
            'arg':{'bid':bid_hist},
            }
        j['arg'].update(dict(zip(
                    ['buyer','item','price','seller'],
                    list(result)
                    )))
        server.broadcast_personal(j,self.base_info)
        return result

    def check_finish(self):
        for kind in range(len(self.base_info["base_value"])):
            # print(self.base_info["purchased_paintings"].count(kind))
            if self.base_info["purchased_paintings"].count(kind) >= self.base_info["game_modifier"]["limit"]:
                return True
        return False

    def round_over(self,):
        """
        ラウンド終了時の処理
        """
        self.base_info["remaining_round"] -= 1
        self.settle()
        self.deal()

    def settle(self,):
        """
        購入カードの清算
        """
        #purchased = [i for i in range(len(self.base_info["base_value"]))]
        purchased=[]
        selp = self.base_info['game_modifier']["sell_price"]
        for player in self.base_info["player"]:
            purchased.extend(player["purchased"])
        c = Counter(purchased)
        top=[]
        payment = [0 for i in range(len(self.base_info["player"]))]
        if(len(c))!=0:
            top = list(zip(*c.most_common(len(selp))))[0]
            le=min(len(selp),len(top))
            for i in range(le):
                self.base_info["base_value"][top[i]] += selp[i]
                bv=self.base_info["base_value"]
                tmp = 0
                for player in self.base_info["player"]:
                    while top[i] in player["purchased"]:
                        player["purchased"].remove(top[i])
                        player["cash"] += bv[top[i]]
                        payment[tmp] += bv[top[i]]
                    tmp += 1

        for player in self.base_info["player"]:
            player["purchased"].clear()
        self.base_info["purchased_paintings"].clear()

        ret ='ROUNDOVER'
        for i in top:
            ret+=' '+str(i)
        server.log(ret)

        
        for i in range(len(payment)):
            ret = "SETTLE "+agent(i)+' '+str(payment[i])
            server.log(ret)

        server.broadcast_personal({'request':'ROUNDOVER',
                                    'arg':{
                                        'roundover':top,
                                        'settle':payment,
                                    }
                                },self.base_info)

        return ret

    def deal(self):
        """
        カードを配る
        """

        # 手札補充
        # print(self.base_info["hand_will_receive"][0])
        if self.base_info["hand_will_receive"][0] == []:
            return
        for player in range(self.base_info["player_size"]):
            receive=self.base_info["hand_will_receive"][player].pop(0)
            server.log('DEAL '+agent(player)+' '+str(sorted(receive)))
            self.base_info["player"][player]["hand"].extend(receive)
            self.base_info["player"][player]["hand"] = sorted(
                self.base_info["player"][player]["hand"])
        return

    def transaction(self, buyer, seller, cost, painting):
        """
        取引成立時
        """
        if self.base_info["player"][buyer]["cash"] - cost < 0:
            raise Exception("お金が足りません")
        if painting not in self.base_info["player"][seller]["hand"]:
            raise Exception("売る絵がありません")

        # 自分で購入
        if buyer == seller:
            self.base_info["player"][seller]["cash"] -= cost
            self.base_info["player"][seller]["hand"].remove(painting)
            self.base_info["player"][seller]["purchased"].append(painting)
            server.log('PURCHASE '+agent(seller)+" "+str(painting)+" "+str(cost)+" "+agent(seller))
        else:
            # 普通の取引
            self.base_info["player"][buyer]["cash"] -= cost
            self.base_info["player"][buyer]["purchased"].append(painting)
            self.base_info["player"][seller]["cash"] += cost
            self.base_info["player"][seller]["hand"].remove(painting)
            server.log('PURCHASE '+agent(buyer)+" "+str(painting)+" "+str(cost)+" "+agent(seller))
        return buyer,str(painting),str(cost),seller

def agent(num):
    return "Agent["+"{0:02d}".format(num) + "]"


def request_auction(seller, info):
    """
    出品リクエスト
    """
    # 手札ゼロならパス
    if info["player"][seller]["hand"] == []:
        #server.broadcast("PASS "+agent(seller))
        return "PASS"

    #item = random.randint(0, 4)
    item=server.request_sell(socks[seller],server.accessible_info(seller,info))
    while item not in info["player"][seller]["hand"]:
        item = random.randint(0, info["game_modifier"]["kinds"])
    server.log('SELL '+agent(seller)+' '+str(item))
    return item


def request_bid(item, bidder, info):
    """
    見積もりリクエスト
    """
    #bid = random.randint(0, 30)
    bid=server.request_bid(socks[bidder],item,server.accessible_info(bidder,info))
    bid = max(min(bid, info["player"][bidder]["cash"]),0)
    server.log('BID '+agent(bidder)+' '+str(bid))
    return bid


def initialize_hand(info,):
    """
    手札の初期化
    """
    if sum(info['game_modifier']["hand_receive_per_round"]) * info["player_size"] > sum(info["total_paintings"]):
        raise Exception("配布予定の絵が全体の枚数を超えています")
    if info["game_modifier"]["seed"] != None:
        np.random.seed(info["game_modifier"]["seed"])

    hand = [[] for i in range(info["player_size"])]
    paintings = []
    c = 0
    for i in info["total_paintings"]:
        paintings.extend([c]*i)
        c += 1

    if info["game_modifier"]["deal_evenly"]:

        pass
    else:
        np.random.shuffle(paintings)
    # print(paintings)

    for i in range(info["player_size"]):
        c = 0
        for j in info['game_modifier']["hand_receive_per_round"]:
            hand[i].append(paintings[: j])
            paintings = paintings[j:]
            c += 1

    return hand

def games(remain):
    if remain==0:
        server.disconnect()
        return
    game = SimpleModernArt(size)
    server.initialize(size,game.base_info)
    game.game()
    games(remain-1)
    return

parser = argparse.ArgumentParser(
        prog="Server.py", #プログラム名
        usage="run this", #プログラムの利用方法
        description="desc", #「optional arguments」の前に表示される説明文
        epilog = "With no args, use port 10000 and wait 5 players.", #「optional arguments」後に表示される文字列
        add_help = True #[-h],[--help]オプションをデフォルトで追加するか
        )

parser.add_argument("-p","--port", #オプション引数
                    help="port to connect", #引数の説明
                    default=10000
                    )
parser.add_argument("-s","--size", #オプション引数
                    help="how many player joins this game", #引数の説明
                    default=5
                    )
parser.add_argument("-v","--verbose", #オプション引数
                    help="detail of console output (not applied to log file.)", #引数の説明
                    default=3
                    )
parser.add_argument('-g',"--game",
                    help="how many games to run",
                    default=1
                    )
parser.add_argument('-l',"--limit",
                    help="how many paintings needed to end round",
                    default=5
                    )
parser.add_argument('-t',"--timeout",
                    help="how long the server can wait client's response",
                    default=10000000
                    )

args = parser.parse_args()
server.port=int(args.port)
server.verbose=int(args.verbose)
server.timeout=int(args.timeout)*0.001
size=int(args.size)

if int(args.game)>1:
    print('will play',args.game,'game')
socks=server.connect(size)
games(int(args.game))
