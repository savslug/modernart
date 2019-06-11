import simplemodernpy.Client as client
from time import sleep
import random
from collections import Counter

myname = 'test1'


class Agent(object):

    def __init__(self, agent_name):
        self.myname = agent_name

    def initialize(self, player_id, info):
        """
        ゲーム開始時に呼ばれる
        __init__ではない
        """
        self.id = player_id

        return self.myname

    def purchase(self, result, info):
        """
        購入が成立した時に呼ばれる
        purchaseには買い手、絵、価格、売り手
        """
        return

    def sell(self, info):
        """
        2ラウンドまでは手持ちが一番少ない絵を、
        それ以降は手持ちが一番多い絵を
        """
        myhand = info['player'][self.id]['hand']
        if info['remaining_round'] >= 2:
            return most_common_hand(myhand, least=False)
        else:
            return most_common_hand(myhand, least=True)

    def bid(self, item, info):
        """
        手札と場札の合計の順位に基づいて期待値を計算
        その値の半分を提示する
        """
        all_hands = info['player'][self.id]['hand']
        for player in info['player']:
            all_hands.extend(player['purchased'])
        ranking = hand_ranking(all_hands)

        if item not in ranking:
            return random.randint(0, 5)
        elif ranking.index(item) == 0:
            return (info['base_value'][item]+30)//2
        elif ranking.index(item) == 1:
            return (info['base_value'][item]+20)//2
        elif ranking.index(item) == 2:
            return (info['base_value'][item]+10)//2
        else:
            return random.randint(0, 5)

    def roundover(self, payment, info):
        """
        ラウンド終了時に呼ばれる
        """
        return

    def finish(self, winner, info):
        """
        ゲーム終了時に呼ばれる
        ここで得られるinfoには全てのゲームデータが格納されている
        """
        return


def most_common_hand(myhand, least=False):
    """
    手札から最多/最小枚数の絵を返す
    """
    c = Counter(myhand)
    if least:
        return c.most_common()[-1][0]
    else:
        return c.most_common()[0][0]


def hand_ranking(myhand):
    """
    手札にある絵の枚数ランキングを返す
    """
    c = Counter(myhand)
    common = c.most_common(len(c))
    ranking = list(map(lambda x: x[0], common))
    return ranking


agent = Agent(myname)

# run
if __name__ == '__main__':
    client.connect(agent)
