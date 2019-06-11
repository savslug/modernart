import simplemodernpy.Client as client
from time import sleep
import random

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
        print(info)
        return self.myname

    def purchase(self, result, info):
        """
        購入が成立した時に呼ばれる
        purchaseには買い手、絵、価格、売り手
        """
        print('result:', result)
        # print(info)
        return

    def sell(self, info):
        """
        自分が出品する番になったら呼ばれる
        絵の番号を返せば良い
        手札にない番号を指定するとランダムで勝手に出品される
        手札がゼロの場合呼ばれるが何を返してもパスになる
        """
        print('sell request')
        sleep(0.001)
        return random.randint(0, 4)

    def bid(self, item, info):
        """
        入札する時に呼ばれる
        入札価格を返せば良い
        itemは購入する絵
        所持金を超える入札は所持金と同額に
        """
        print('bid requset:', item)
        sleep(0.001)
        return random.randint(0, 30)

    def roundover(self, payment, info):
        """
        ラウンド終了時に呼ばれる
        """
        print(info)
        print('roundover:', payment)
        return

    def finish(self, winner, info):
        """
        ゲーム終了時に呼ばれる
        ここで得られるinfoには全てのゲームデータが格納されている
        """
        print(info)
        return


agent = Agent(myname)

# run
if __name__ == '__main__':
    client.connect(agent)
