import simplemodernpy.Client as client
from time import sleep
import random
from pprint import pprint as pprint

myname = 'human'


class Agent(object):

    def __init__(self, agent_name):
        self.myname = agent_name

    def initialize(self, player_id, info):
        """
        ゲーム開始時に呼ばれる
        __init__ではない
        """
        self.id = player_id
        pprint(info)
        print('ゲームを開始します。あなたのエージェント番号は', ag(player_id), 'です。')
        print('手札:', info['player'][self.id]['hand'])
        return self.myname

    def purchase(self, result, info):
        """
        購入が成立した時に呼ばれる
        purchaseには買い手、絵、価格、売り手
        """

        pprint(result)
        print(result['bid'])
        print(ag(result['buyer']) if result['buyer'] is not self.id else 'あなた',
              'が',
              ag(result['seller']) if result['seller'] is not self.id else 'あなた', 'から')
        print(result['item'], 'を', str(result['price'])+',000$で購入しました。')
        for p in info['player']:
            print(ag(p['id']), ':', p['purchased'])
        # pprint(info)
        return

    def sell(self, info):
        """
        自分が出品する番になったら呼ばれる
        絵の番号を返せば良い
        手札にない番号を指定するとランダムで勝手に出品される
        """
        pprint(info)
        print('手札:', info['player'][self.id]['hand'])
        print('あなたのターンです。出品する絵を手札から選んでください。')

        return input('SELL> ')

    def bid(self, item, info):
        """
        入札する時に呼ばれる
        入札価格を返せば良い
        itemは購入する絵
        所持金を超える入札は所持金と同額に
        """
        pprint(info)

        print(item, 'に対する入札額を決めてください。')
        return input('BID '+str(item)+'> ')

    def roundover(self, settle, info):
        """
        ラウンド終了時に呼ばれる
        """
        pprint(settle)
        print('第', 4-info['remaining_round'], 'ラウンドが終了しました。')
        print(str(settle['settle'][self.id])+',000$を獲得しました。')
        return

    def finish(self, winner, info):
        """
        ゲーム終了時に呼ばれる
        ここで得られるinfoには全てのゲームデータが格納されている
        """
        pprint(info)
        pprint(winner)
        print(winner, 'が勝利しました。')
        return


agent = Agent(myname)


def ag(num):
    return "Agent["+"{0:02d}".format(num) + "]"


def pprint(a):
    # pprintを無効化するためだけの関数
    return


# run
if __name__ == '__main__':
    client.connect(agent)
