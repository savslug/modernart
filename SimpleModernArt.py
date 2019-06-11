import numpy as np
import random
from collections import Counter
import Server as server


class SimpleModernArt(object):

    def __init__(self, player_size):
        self.base_info = {
            "player_size": player_size,
            "sell_price": [30, 20, 10],
            "hand_receive_per_round": [8, 3, 3, 0],
            "total_paintings": [12, 13, 14, 15, 16],
            "base_value": [0, 0, 0, 0, 0],
            "hand_will_receive": None,
            "remaining_round": 4,
            "turn_player": random.randint(0, player_size - 1),
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
                "limit": 5,
                "kinds": 5
            }

        }
        self.base_info["hand_will_receive"] = initialize_hand(self.base_info)

    def game(self,):
        """
        1ゲーム
        """
        while self.base_info["remaining_round"] > 0:
            tp = self.base_info["turn_player"]
            ps = self.base_info["player_size"]
            if self.auction(tp) == "ROUND CLOSE":
                # pprint(self.base_info["player"])
                self.round_close()
                #print("REMAINING ROUND:", self.base_info["remaining_round"])
                # pprint(self.base_info)
            # pprint(self.base_info["player"])
            # pprint(self.base_info["purchased_paintings"])
            self.base_info["turn_player"] = (tp + 1) % ps
            for player in self.base_info["player"]:
                if player["hand"] != []:
                    break
            else:
                break
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
        server.broadcast(str({'request':'FINISH','arg':winner,'info':self.base_info}))
        server.log(s)
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
            return "ROUND CLOSE"

        bid = []
        psize = len(self.base_info["player"])

        for priority in range(psize):
            bidder = (seller+priority+1) % psize
            bid.append((
                request_bid(
                    painting, self.base_info["player"][bidder]["id"], self.base_info),
                -priority,
                bidder
            ))
        # print(bid)
        bid = list(sorted(bid, reverse=True))
        buyer = bid[0][2]
        result = self.transaction(buyer, seller, bid[0][0], painting)
        bid_hist={}
        for i in bid:
            bid_hist[i[2]]=i[0]
        server.broadcast_personal({'request':'PURCHASE','arg':{
            'result':dict(zip(
                    ['buyer','paint','price','seller'],
                    list(result)
                    )),
            'bids':bid_hist}}
            ,self.base_info)
        return result

    def check_finish(self):
        for kind in range(len(self.base_info["base_value"])):
            # print(self.base_info["purchased_paintings"].count(kind))
            if self.base_info["purchased_paintings"].count(kind) >= self.base_info["game_modifier"]["limit"]:
                return True
        return False

    def round_close(self,):
        """
        ラウンド終了時の処理
        """
        self.base_info["remaining_round"] -= 1
        self.deal()
        return self.settle()

    def settle(self,):
        """
        購入カードの清算
        """
        purchased = [i for i in range(len(self.base_info["base_value"]))]
        selp = self.base_info["sell_price"]
        for player in self.base_info["player"]:
            purchased.extend(player["purchased"])
        c = Counter(purchased)
        top = list(zip(*c.most_common(len(selp))))[0]
        # print(top)
        payment = [0 for i in range(len(self.base_info["player"]))]
        for i in range(len(selp)):
            self.base_info["base_value"][top[i]] += selp[i]
            tmp = 0
            for player in self.base_info["player"]:
                while top[i] in player["purchased"]:
                    player["purchased"].remove(top[i])
                    player["cash"] += selp[i]
                    payment[tmp] += selp[i]
                tmp += 1

        for player in self.base_info["player"]:
            player["purchased"].clear()
        self.base_info["purchased_paintings"].clear()

        ret = "ROUNDOVER"
        for i in payment:
            ret += (" "+str(i))
        server.log(ret)

        server.broadcast_personal({'request':'ROUNDOVER',
                            'arg':dict(zip([i for i in range(self.base_info['player_size'])],payment))
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
        else:
            # 普通の取引
            self.base_info["player"][buyer]["cash"] -= cost
            self.base_info["player"][buyer]["purchased"].append(painting)
            self.base_info["player"][seller]["cash"] += cost
            self.base_info["player"][seller]["hand"].remove(painting)
        server.log('PURCHASE '+agent(seller)+" "+str(painting)+" "+str(cost)+" "+agent(seller))
        return agent(buyer),str(painting),str(cost),agent(seller)

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
    bid = min(bid, info["player"][bidder]["cash"])
    server.log('BID '+agent(bidder)+' '+str(bid))
    return bid


def initialize_hand(info,):
    """
    手札の初期化
    """
    if sum(info["hand_receive_per_round"]) * info["player_size"] > sum(info["total_paintings"]):
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
        for j in info["hand_receive_per_round"]:
            hand[i].append(paintings[: j])
            paintings = paintings[j:]
            c += 1

    return hand


from pprint import pprint as pprint
size=5
game = SimpleModernArt(size)
socks=server.connect(size,game.base_info)
game.deal()
"""
s.deal()
# pprint(s.base_info)
print(s.transaction(0, 1, 20, 0))
print(s.transaction(1, 2, 20, 1))
print(s.transaction(2, 3, 20, 2))
print(s.transaction(3, 4, 20, 2))
print(s.transaction(4, 0, 20, 1))
pprint(s.base_info)
print(s.round_finish())
pprint(s.base_info)
"""
# print(s.auction(0))
game.game()
#pprint(game.base_info["player"])
