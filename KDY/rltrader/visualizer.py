import threading
import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend('agg')

from mplfinance.original_flavor import candlestick_ohlc
from agent import Agent

lock = threading.Lock()


class Visualizer:
    COLORS = ['r', 'b', 'g']
    # 색깔

    def __init__(self, vnet=False):
        self.canvas = None
        # 캔버스 같은 역할을 하는 Matplotlib의 Figure 클래스 객체
        self.fig = None
        # 차트를 그리기 위한 Matplotlib의 Axes 클래스 객체
        self.axes = None
        self.title = ''  # 그림 제목

        # fig는 전체 가시화 결과를 관리하는 객체.
        # axes 는 fig에 포함되는 차트의 배열이다.

    # Visualizer 클래스 : 가시화 준비 함수
    def prepare(self, chart_data, title):
        self.title = title
        # 제목을 지정해준다.

        with lock:
            # 캔버스를 초기화하고 5개의 차트를 그릴 준비
            self.fig, self.axes = plt.subplots(
                nrows=5, ncols=1, facecolor='w', sharex=True)
            # fig을 plt.subplots 로 지정해 여러 차트가 들어가도록 설정해주고,
            # axes 로는 5행 1열 구조를 넣어준다.
            # facecolor, 즉 뒷바탕색은 white 색상으로 지정한다.
            # subplots 로 하게 되면 튜플 형태로 두가지가 산출되는데,
            # 첫번째론 figure(도화지). figure 은 fig에 담기고,
            # 두번째론 5행 1열이기에 5개의 Axes 객체가 리스트로서 튀어나오고,
            # 그 Axes 객체 5개가 담긴 리스트가 axes 에 담긴다.

            for ax in self.axes:
                # 이제 Axes 객체 하나하나를 꺼내온다.

                # 보기 어려운 과학적 표기 비활성화
                # x 축과 y 축에 과학적 표기 기능을 끈다. (켜져 있으면 너무 복잡해.)
                ax.get_xaxis().get_major_formatter() \
                    .set_scientific(False)
                ax.get_yaxis().get_major_formatter() \
                    .set_scientific(False)
                # y axis 위치 오른쪽으로 변경
                ax.yaxis.tick_right()

            # 차트 1. 일봉 차트
            self.axes[0].set_ylabel('Env.')  # y 축 레이블 표시
            # 첫번째 차트의 y축 의 이름을 'Env.'로 지정해준다.
            x = np.arange(len(chart_data))
            # 그리고 x값은 차트의 데이터 하나하나를 np.arange 로 만들어준다.

            # open, high, low, close 순서로된 2차원  (ohlc)
            ohlc = np.hstack((
                x.reshape(-1, 1), np.array(chart_data)[:, 1:-1]))
            # ohlc 데이터의 리스트가 hstack 자료 구조로 담긴다.
            # x값으론 인덱스 값, y 론 ohlc 값들.
            # 양봉은 빨간색으로 음봉은 파란색으로 표시
            candlestick_ohlc(
                self.axes[0], ohlc, colorup='r', colordown='b')
            # candlestick_ohlc 는 mpl_finance 의 메소드.
            # 양봉과 음봉을 그려주는 함수이다.
            # 입력값으론 Axes 객체(차트공간)와 ohlc 데이터가 들어간다.
            # 양봉 음봉 색깔은 맘대로 지정 가능하다.

            # 거래량 가시화
            ax = self.axes[0].twinx()
            # twinx()란 x 축을 공유하는 트윈 Axes 객체를 하나 더 만드는 메소드이다.
            volume = np.array(chart_data)[:, -1].tolist()
            # 거래량을 volume 에 담아준다.
            ax.bar(x, volume, color='b', alpha=0.3)
            # 그리고 twin axes 에 x값을 x축으로, 거래량(volume)을 y축으로 하는 값을 넣어준다.

    # Visualizer 클래스 : 가시화 함수 (1)
    # 에포크 결과를 가시화 해주는 함수이다.
    def plot(self, epoch_str=None, num_epoches=None, epsilon=None,
            action_list=None, actions=None, num_stocks=None,
            outvals_value=[], outvals_policy=[], exps=None, 
            learning_idxes=None, initial_balance=None, pvs=None):
        # 인자 설명
        # epoch_str : Figure 제목으로 표시할 에포크
        # num_epoches : 총 수행할 에포크 수
        # epsilon : 탐험률
        # action_list : 에이전트가 수행할 수 있는 전체 행동 리스트
        # num_stocks : 주식 보유 수 배열
        # outvals_value : 가치 신경망의 출력 배열
        # outvals_policy : 정책 신경망의 출력 배열
        # exps : 탐험 여부 배열
        # learning_idxes : 학습 위치 배열
        # initial_balance : 초기 자본금
        # pvs : 포트폴리오 가치 배열

        with lock:
            x = np.arange(len(actions))  # 모든 차트가 공유할 x축 데이터
            # actions, num_stocks, outvals_value 등 모든 배열의 크기가 같기 때문에
            # 그중 하나인 actions의 길이만 골라서 x축을 생성합니다.
            actions = np.array(actions)  # 에이전트의 행동 배열
            # 가치 신경망의 출력 배열
            outvals_value = np.array(outvals_value)
            # 정책 신경망의 출력 배열
            outvals_policy = np.array(outvals_policy)
            # 초기 자본금 배열
            pvs_base = np.zeros(len(actions)) + initial_balance
            # 포트폴리오 value 의 base 값을 지정한다. (모든 배열값이 초기자본금으로 동일)

            # 차트 2. 에이전트 상태 (행동, 보유 주식 수) - 에이전트의 상태차트를 그려준다.
            for action, color in zip(action_list, self.COLORS):
                # action_list = ['buy','sell','hold'] 일듯
                # COLORS = ['r','b','g']
                for i in x[actions == action]:
                    # 배경 색으로 행동 표시
                    # action 과 같은 행동을 한 인덱스를 하나하나 불러오고,
                    # - 첫번째, buy -> color 은 r

                    self.axes[1].axvline(i, color=color, alpha=0.1)
                    # 첫번째 Axes 객체(두번째 차트)에 수행한 행동을 배경색으로 표현한다. (color)
                    # 해당 행동을 한 인덱스에 해당 색깔을 칠한다.
                    # 매수(buy) 했으면 그 인덱스는 빨간색 배경,
                    # 매도(sell) 했으면 그 인덱스는 파란색 배경으로 채운다.
            self.axes[1].plot(x, num_stocks, '-k')  # 보유 주식 수 그리기
            # 그리고 보유 주식수를 그 두번째 차트에 선형으로 그린다.

            # ---------------- 여기까지 공부함. 210415

            # 차트 3. 가치 신경망
            if len(outvals_value) > 0:
                max_actions = np.argmax(outvals_value, axis=1)
                for action, color in zip(action_list, self.COLORS):
                    # 배경 그리기
                    for idx in x:
                        if max_actions[idx] == action:
                            self.axes[2].axvline(idx, 
                                color=color, alpha=0.1)
                    # 가치 신경망 출력의 tanh 그리기
                    self.axes[2].plot(x, outvals_value[:, action], 
                        color=color, linestyle='-')
            
            # 차트 4. 정책 신경망
            # 탐험을 노란색 배경으로 그리기
            for exp_idx in exps:
                self.axes[3].axvline(exp_idx, color='y')
            # 행동을 배경으로 그리기
            _outvals = outvals_policy if len(outvals_policy) > 0 \
                else outvals_value
            for idx, outval in zip(x, _outvals):
                color = 'white'
                if np.isnan(outval.max()):
                    continue
                if outval.argmax() == Agent.ACTION_BUY:
                    color = 'r'  # 매수 빨간색
                elif outval.argmax() == Agent.ACTION_SELL:
                    color = 'b'  # 매도 파란색
                self.axes[3].axvline(idx, color=color, alpha=0.1)
            # 정책 신경망의 출력 그리기
            if len(outvals_policy) > 0:
                for action, color in zip(action_list, self.COLORS):
                    self.axes[3].plot(
                        x, outvals_policy[:, action], 
                        color=color, linestyle='-')

            # 차트 5. 포트폴리오 가치
            self.axes[4].axhline(
                initial_balance, linestyle='-', color='gray')
            self.axes[4].fill_between(x, pvs, pvs_base,
                where=pvs > pvs_base, facecolor='r', alpha=0.1)
            self.axes[4].fill_between(x, pvs, pvs_base,
                where=pvs < pvs_base, facecolor='b', alpha=0.1)
            self.axes[4].plot(x, pvs, '-k')
            # 학습 위치 표시
            for learning_idx in learning_idxes:
                self.axes[4].axvline(learning_idx, color='y')

            # 에포크 및 탐험 비율
            self.fig.suptitle('{} \nEpoch:{}/{} e={:.2f}'.format(
                self.title, epoch_str, num_epoches, epsilon))
            # 캔버스 레이아웃 조정
            self.fig.tight_layout()
            self.fig.subplots_adjust(top=0.85)

    def clear(self, xlim):
        with lock:
            _axes = self.axes.tolist()
            for ax in _axes[1:]:
                ax.cla()  # 그린 차트 지우기
                ax.relim()  # limit를 초기화
                ax.autoscale()  # 스케일 재설정
            # y축 레이블 재설정
            self.axes[1].set_ylabel('Agent')
            self.axes[2].set_ylabel('V')
            self.axes[3].set_ylabel('P')
            self.axes[4].set_ylabel('PV')
            for ax in _axes:
                ax.set_xlim(xlim)  # x축 limit 재설정
                ax.get_xaxis().get_major_formatter() \
                    .set_scientific(False)  # 과학적 표기 비활성화
                ax.get_yaxis().get_major_formatter() \
                    .set_scientific(False)  # 과학적 표기 비활성화
                # x축 간격을 일정하게 설정
                ax.ticklabel_format(useOffset=False)

    def save(self, path):
        with lock:
            self.fig.savefig(path)
