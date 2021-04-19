import os
# os는 폴더 생성이나 파일 경로 준비 등을 위해 사용한다.
import logging
# logging 은 학습 과정의 정보를 기록하기 위해 사용한다.
import abc
# abc는 추상 클래스를 정의하기 위해 사용한다.
# abstract base class
import collections
import threading
import time
# time 은 학습 시간을 측정하기 위해 사용한다.
import numpy as np
# 배열 자료구조 조작을 위해 Numpy 임포트
from utils import sigmoid
from environment import Environment
from agent import Agent
from networks import Network, DNN, LSTMNetwork, CNN
from visualizer import Visualizer

# ReinforcementLearner 클래스는 DQNLearner, PolicyGradientLearner,
# ActorCriticLearner, A2CLearner 클래스가 상속하는 상위 클래스이다.

# ReinforcementLearner 클래스 생성자는 강화학습에 필요한 환경, 에이전트,
# 신경망 인스턴스들과 학습 데이터를 속성으로 가진다.
class ReinforcementLearner:
    __metaclass__ = abc.ABCMeta
    lock = threading.Lock()
    # threading.Lock() 은 쓰레드를 동기화 하는 것이다.
    # 즉 속도에 맞게 일을 행하도록

    def __init__(self, rl_method='rl', stock_code=None, 
                chart_data=None, training_data=None,
                min_trading_unit=1, max_trading_unit=2, 
                delayed_reward_threshold=.05, # 누적 수익률 5% 또는 -5% 일때 보상을 갱신한다.
                net='dnn', num_steps=1, lr=0.001,
                value_network=None, policy_network=None, # 기본값 None. 기존에 학습한애가 있으면 얠 넣어줘야 함.
                output_path='', reuse_models=True): # output_path 을 지정해줘야 해당 폴더명으로 저장된다.
        # 인자 확인
        # stock_code : 강화학습 대상 주식 종목 코드
        # chart_data : 주식 종목의 차트 데이터
        # environment : 강화학습 환경 객체
        # agent : 강화학습 에이전트 객체
        # training_data : 학습 데이터
        # value_network : 가치 신경망
        # policy_network : 정책 신경망

        assert min_trading_unit > 0
        assert max_trading_unit > 0
        assert max_trading_unit >= min_trading_unit
        assert num_steps > 0
        assert lr > 0
        # assert -> 보증한다 라는 의미
        # 즉, assert min_trading_unit > 0 으로 하게 되면,
        # min_trading_unit 이 0보다 큰게 확실하면 다음 줄을 시행하라는 의미.
        # 만약 0보다 작으면 AssertionError 가 뜬다. -> 0보다 작은게 있네? 에러!

        # 강화학습 기법 설정
        self.rl_method = rl_method
        # rl_method 변수를 'rl' 로 설정해준다. (default 값)

        # 환경 설정
        self.stock_code = stock_code
        # 종목코드 넣어준다.
        self.chart_data = chart_data
        # 차트 데이터 DataFrame 으로 넣어준다.
        self.environment = Environment(chart_data)
        # 환경을 넣어준다.

        # 에이전트 설정
        self.agent = Agent(self.environment,
                    min_trading_unit=min_trading_unit,
                    max_trading_unit=max_trading_unit,
                    delayed_reward_threshold=delayed_reward_threshold)
        # 에이전트를 설정한다.
        # 환경을 쥐어주고 (차트데이터)
        # 최소 거래 유닛, 최대 거래 유닛 넣어주고,
        # 지연보상을 넣어준다. (디폴트 5%, 0.05)


        # 학습 데이터
        self.training_data = training_data
        # 학습 데이터를 넣어준다. (학습데이터와 차트데이터는 동일한 듯?)
        # 트레이닝 데이터는 모든 컬럼이 담긴 데이터.

        self.sample = None
        self.training_data_idx = -1
        # 벡터 크기 = 학습 데이터 벡터 크기 + 에이전트 상태 크기
        self.num_features = self.agent.STATE_DIM
        # STATE_DIM = 2 임 (포트폴리오 가치비율 & 주식 보유비율)
        if self.training_data is not None:
            self.num_features += self.training_data.shape[1]
            # STATE_DIM = 2 임 (포트폴리오 가치비율 & 주식 보유비율)
            # num_features = STATE_DIM + 데이터의 컬럼 갯수
        # 신경망 설정
        self.net = net
        # 신경망을 뭘로 할 지 넣어준다. (dnn, lstm, ...)
        self.num_steps = num_steps
        # num_steps 값을 넣어준다.
        self.lr = lr
        # 학습율을 입력한 값으로 넣어준다.
        self.value_network = value_network
        self.policy_network = policy_network
        # value_network 와 policy_network 값이 들어가면
        # 이 저장된 모델들을 가치 신경망과 정책 신경망으로 사용한다.
        self.reuse_models = reuse_models

        # 가시화 모듈
        self.visualizer = Visualizer()
        # 메모리
        self.memory_sample = []
        self.memory_action = []
        self.memory_reward = []
        self.memory_value = []
        self.memory_policy = []
        self.memory_pv = []
        self.memory_num_stocks = []
        self.memory_exp_idx = []
        self.memory_learning_idx = []
        # 강화학습 과정에서 발생하는 각종 데이터를 쌓아두기 위해
        # memory_* 라는 이름의 리스트들을 만든다.
        # 그리고 학습 데이터 샘플, 수행한 행동, 획득한 보상,
        # 행동의 예측 가치, 행동의 예측 확률, 포트폴리오 가치,
        # 보유 주식 수, 탐험 위치, 학습 위치 등을 저장한다.

        # 에포크 관련 정보
        self.loss = 0.
        self.itr_cnt = 0
        self.exploration_cnt = 0
        self.batch_size = 0
        self.learning_cnt = 0
        # 그리고 에포크동안 학습에서 발생한 손실, 수익 발생 횟수,
        # 탐험 횟수, 학습 횟수, 배치 사이즈를 로그에 담아줘야 하기 때문에,
        # 대입하기에 앞서 초기화를 해줍니다.

        # learning_cnt 는 한 에포크 동안 수행한 미니배치 학습 회수를 저장한다.

        # 로그 등 출력 경로
        self.output_path = output_path
        # 로그 등 출력 경로를 지정해줍니다.
        # output_path 는 지정한 값이다. (c005930 이라고 하면 c005930 폴더가 생김)

    # 가치 신경망 생성 함수
    def init_value_network(self, shared_network=None, 
            activation='linear', loss='mse'):
        if self.net == 'dnn':
            # dnn 을 사용한다.
            self.value_network = DNN(
                input_dim=self.num_features, 
                output_dim=self.agent.NUM_ACTIONS, 
                lr=self.lr, shared_network=shared_network, 
                activation=activation, loss=loss)
            # self.num_features 은 엑셀 컬럼수에 맞춰 알아서 인풋 사이즈 맞춰줌.
            # 아웃풋은 행동의 갯수로 맞춰줌.
            # lr 은 학습율
            # shared_network, 공유신경망은 None 으로 하게 되면
            # default 값 (256 - 128 - ...) 로 신경망 만들어짐.
            # activation 을 linear 로 해줬으므로 활성화함수는 각 신경망 층에서
            # linear 로 통일되고,
            # loss 로는 mse 로 지정됨.
        elif self.net == 'lstm':
            # LSTM 을 사용한다.
            self.value_network = LSTMNetwork(
                input_dim=self.num_features,
                # num_features = 에이전트의 상태 2개 + 데이터의 컬럼 수
                # 만약 데이터에 컬럼이 26개이면 num_features 는 28이 됨.
                output_dim=self.agent.NUM_ACTIONS,
                # 아웃풋으론 에이전트의 행동을 출력한다.
                lr=self.lr, num_steps=self.num_steps, 
                shared_network=shared_network,
                # shared_network 디폴트 None
                # None 으로 하게 되면 기본 탑재 신경망으로 만듬.
                # 만약 신경망을 직접 지정하고 싶으면 shared_network 을 넣어줘야 함.
                activation=activation, loss=loss)
            # lstm은 다른 곳과는 다르게 num_steps 변수가 들어감.
            # 연속된 데이터를 분석해야 하기 때문.
        elif self.net == 'cnn':
            # CNN을 사용할 경우
            self.value_network = CNN(
                input_dim=self.num_features, 
                output_dim=self.agent.NUM_ACTIONS, 
                lr=self.lr, num_steps=self.num_steps, 
                shared_network=shared_network, 
                activation=activation, loss=loss)
            # CNN 또한 num_steps 를 넣어준다.
        if self.reuse_models and \
            os.path.exists(self.value_network_path):
            # value_network_path 에 해당 신경망 모델이 존재하는지 확인한다.
            # 그리고 reuse_models(재사용여부)가 True 인지도 확인한다.
            # 기존에 있는 모델을 사용할 경우 -> value_network, policy_network 이름 지정.
            # 만약 불러올거면 reuse_models = True
                self.value_network.load_model(
                    model_path=self.value_network_path)
            # 기존에 있는 모델을 로드한다.
        # 여기서 value_network_path 어떻게 지정되는지 잘 볼것.

    # 정책 신경망 생성 함수
    def init_policy_network(self, shared_network=None, 
            activation='sigmoid', loss='binary_crossentropy'):
        # 정책신경망은 둘 중 하나의 값이 추출되므로
        # sigmoid 와 binary_crossentropy 를 사용한다.
        if self.net == 'dnn':
            self.policy_network = DNN(
                input_dim=self.num_features, 
                output_dim=self.agent.NUM_ACTIONS, 
                lr=self.lr, shared_network=shared_network, 
                activation=activation, loss=loss)
        elif self.net == 'lstm':
            self.policy_network = LSTMNetwork(
                input_dim=self.num_features, 
                output_dim=self.agent.NUM_ACTIONS, 
                lr=self.lr, num_steps=self.num_steps, 
                shared_network=shared_network, 
                activation=activation, loss=loss)
        elif self.net == 'cnn':
            self.policy_network = CNN(
                input_dim=self.num_features, 
                output_dim=self.agent.NUM_ACTIONS, 
                lr=self.lr, num_steps=self.num_steps, 
                shared_network=shared_network, 
                activation=activation, loss=loss)
        if self.reuse_models and \
            os.path.exists(self.policy_network_path):
            # 만약 불러올거면 reuse_models = True
            self.policy_network.load_model(
                model_path=self.policy_network_path)

    # 환경, 에이전트, 가시화, 메모리 초기화 함수
    def reset(self):
        self.sample = None
        self.training_data_idx = -1
        # 시작지점 -1으로 지정. -> 처음부터 읽도록

        # 환경 초기화
        self.environment.reset()
        # 에이전트 초기화
        self.agent.reset()
        # 가시화 초기화
        self.visualizer.clear([0, len(self.chart_data)])
        # 메모리 초기화
        self.memory_sample = []
        self.memory_action = []
        self.memory_reward = []
        self.memory_value = []
        self.memory_policy = []
        self.memory_pv = []
        self.memory_num_stocks = []
        self.memory_exp_idx = []
        self.memory_learning_idx = []
        # 에포크 관련 정보 초기화
        self.loss = 0.
        self.itr_cnt = 0
        self.exploration_cnt = 0
        self.batch_size = 0
        self.learning_cnt = 0

    # 환경 객체에서 샘플을 획득하는 함수
    # (보상을 얻을때까지의 데이터들을 축적하기 위함)
    def build_sample(self):
        self.environment.observe()
        # 에이전트의 상태를 불러오는 get 함수
        if len(self.training_data) > self.training_data_idx + 1:
            # 훈련데이터 읽는 지점이 전체 훈련데이터 크기보단 작도록 해야함.
            self.training_data_idx += 1
            self.sample = self.training_data.iloc[
                self.training_data_idx].tolist()
            # 샘플을 추출한다.
            # 샘플엔 데이터의 컬럼들을 모두 넣고,
            # 아래에 에이전트의 상태도 넣어준다.
            self.sample.extend(self.agent.get_states())
            # append 와 extend 의 차이.
            # [4,5]를 append 하면 [1,2,3,[4,5]] 이렇게 되지만,
            # extend 하게 되면 [1,2,3,4,5] 로 된다.

            # 따라서 sample 데이터는
            # [해당 인덱스에서의 training_data(환경값 전부),주식 보유 비율, 포트폴리오 가치비율]
            # 따라서 v2 는 특징수가 26개이니, 에이전트 상태 2개 더하면
            #  sample은 결국 28개의 컬럼을 가지게 됨.
            return self.sample
        return None

    # 배치 학습 데이터 생성 함수
    @abc.abstractmethod
    def get_batch(self, batch_size, delayed_reward, discount_factor):
        pass
    # 배치 학습 데이터 생성 함수를 추상 메소드로 선정해 Network 클래스를 상속하는
    # 신경망들이 각자의 구조에 맞게 get_batch 할 수 있도록 각 자식 클래스에서 수정해서 쓴다.

    # 가치 신경망 및 정책 신경망 학습 함수
    def update_networks(self, 
            batch_size, delayed_reward, discount_factor):
        # 배치 학습 데이터 생성
        x, y_value, y_policy = self.get_batch(
            batch_size, delayed_reward, discount_factor)
        # delayed_reward 에 도달할 때 까지의 batch 데이터를 모으는 함수이다.


        if len(x) > 0:
            loss = 0
            if y_value is not None:
                # 가치 신경망 갱신
                loss += self.value_network.train_on_batch(x, y_value)
                # 축적된 데이터(x)와 정답(y_value - 가치신경망의 가치)로 loss를 구하고,
                # 얻은 loss 로 경사하강법을 실행해 매개변수를 업데이트 시킨다.
            if y_policy is not None:
                # 정책 신경망 갱신
                loss += self.policy_network.train_on_batch(x, y_policy)
            return loss
        return None

    # 가치 신경망 및 정책 신경망 학습 함수
    def fit(self, delayed_reward, discount_factor, full=False):
        batch_size = len(self.memory_reward) if full \
            else self.batch_size
        # 배치 학습 데이터 생성 및 신경망 갱신
        if batch_size > 0:
            _loss = self.update_networks(
                batch_size, delayed_reward, discount_factor)
            if _loss is not None:
                self.loss += abs(_loss)
                self.learning_cnt += 1
                self.memory_learning_idx.append(self.training_data_idx)
                # 축적 데이터에 트레이닝 데이터의 인덱스를 쌓는다.
            self.batch_size = 0

    # 에포크 정보 가시화 함수
    def visualize(self, epoch_str, num_epoches, epsilon):
        # 에이전트의 행동
        self.memory_action = [Agent.ACTION_HOLD] \
            * (self.num_steps - 1) + self.memory_action
        # 무의미없는 num_steps 만큼의 데이터에 + 실제 행동 기억재현함수를 넣는다.
        # 보유 주식 수
        self.memory_num_stocks = [0] * (self.num_steps - 1) \
            + self.memory_num_stocks
        # 가치 신경망 출력
        if self.value_network is not None:
            self.memory_value = [np.array([np.nan] \
                * len(Agent.ACTIONS))] * (self.num_steps - 1) \
                    + self.memory_value
        # 정책 신경망 출력
        if self.policy_network is not None:
            self.memory_policy = [np.array([np.nan] \
                * len(Agent.ACTIONS))] * (self.num_steps - 1) \
                    + self.memory_policy
        # 포트폴리오 가치
        self.memory_pv = [self.agent.initial_balance] \
            * (self.num_steps - 1) + self.memory_pv
        # LSTM 이나 CNN을 사용하는 겨우 에이전트 행동, 보유 주식 수,
        # 가치 신경망 출력, 정책 신경망 출력, 포트폴리오 가치는
        # 환경의 일봉 수 보다 num_steps-1 만큼 부족함.
        # 그래서 이를 메워주기 위해서 만듬.

       # 가시화 시작
        self.visualizer.plot(
            epoch_str=epoch_str, num_epoches=num_epoches, 
            epsilon=epsilon, action_list=Agent.ACTIONS, 
            actions=self.memory_action, 
            num_stocks=self.memory_num_stocks, 
            outvals_value=self.memory_value, 
            outvals_policy=self.memory_policy,
            exps=self.memory_exp_idx, 
            learning_idxes=self.memory_learning_idx,
            initial_balance=self.agent.initial_balance, 
            pvs=self.memory_pv,
        )
        # visualizer.plot 함수는 도화지(figure)에
        # 그래프를 완성해주는 함수.

        self.visualizer.save(os.path.join(
            self.epoch_summary_dir, 
            'epoch_summary_{}.png'.format(epoch_str))
        )
        # figure 을 png 로 저장한다.

    # 강화학습 수행 함수
    def run(
        self, num_epoches=100, balance=10000000,
        discount_factor=0.9, start_epsilon=0.5, learning=True):
        info = "[{code}] RL:{rl} Net:{net} LR:{lr} " \
            "DF:{discount_factor} TU:[{min_trading_unit}," \
            "{max_trading_unit}] DRT:{delayed_reward_threshold}".format(
            code=self.stock_code, rl=self.rl_method, net=self.net,
            lr=self.lr, discount_factor=discount_factor,
            min_trading_unit=self.agent.min_trading_unit, 
            max_trading_unit=self.agent.max_trading_unit,
            delayed_reward_threshold=self.agent.delayed_reward_threshold
        )
        # 변수 설명
        # num_epoches : 수행할 반복 학습 횟수
        # balance : 초기 투자 자본금
        # discount_factor : 할인율
        # start_epsilon : 초기 탐험 확률
        # learning : 학습 유무
        # run() : 함수에 들어오면 강화학습 설정을 로그로 기억한다.
        #         그리고 학습 시작 시간을 저장해준다.
        #         학습 종료 후의 시간과의 차이를 학습시간으로 기록하기 위함.

        # 학습된 모델로 투자 시뮬레이션을 돌리고 싶을 경우엔
        # learning 을 False 로 지정해준다.
        # 그래서 예를 들면 start_data end_data 를 20170101 20191231 로 학습 시키고,
        # 이후 --learning 을 False 로 지정하고, start_data, end_data 를 20200101 20200631 이렇게
        # 테스트를 해볼 수 있는거지.

        with self.lock:
            logging.info(info)

        # 시작 시간
        time_start = time.time()

        # 가시화 준비
        # 차트 데이터는 변하지 않으므로 미리 가시화
        self.visualizer.prepare(self.environment.chart_data, info)
        # prepare() : 가시화 준비 함수.
        # prepare() 함수는 에포크가 진행되도 변하지 않는 주식투자 환경인
        # 차트 데이터를 미리 가시화한다.

        # 가시화 결과 저장할 폴더 준비
        self.epoch_summary_dir = os.path.join(
            self.output_path, 'epoch_summary_{}'.format(
                self.stock_code))
        # 가시화 파일은 output_path 에 epoch_summary_종목코드 로 저장된다.

        if not os.path.isdir(self.epoch_summary_dir):
            os.makedirs(self.epoch_summary_dir)
            # 폴더가 존재하지 않으면 폴더 만들어준다.
        else:
            for f in os.listdir(self.epoch_summary_dir):
                os.remove(os.path.join(self.epoch_summary_dir, f))
                # 뭘 지우는거지?

        # 에이전트 초기 자본금 설정
        self.agent.set_balance(balance)
        # --initial_balance 설정해면 이 초기금액이 달라짐.

        # 학습에 대한 정보 초기화
        max_portfolio_value = 0
        epoch_win_cnt = 0

        # 학습 반복
        for epoch in range(num_epoches):
            # --epochs 10000 하면 이게 10000번 시행됨.
            time_start_epoch = time.time()

            # step 샘플을 만들기 위한 큐
            q_sample = collections.deque(maxlen=self.num_steps)
            
            # 환경, 에이전트, 신경망, 가시화, 메모리 초기화
            self.reset()

            # 학습을 진행할 수록 탐험 비율 감소
            if learning:
                epsilon = start_epsilon \
                    * (1. - float(epoch) / (num_epoches - 1))
                # 학습이 이루어졌을 경우 입실론 값을 감소시킨다.
                # 처음 입실론 값에서 (1-2)/10000, (1-3)/10000, ... (1-100)/10000 이 감소된다.
                self.agent.reset_exploration()
                # 탐험값을 리셋한다.
            else:
                epsilon = start_epsilon
                # 학습이 진행되지 않았으면 epsilon 을 그대로 냅둔다.
                self.agent.reset_exploration(alpha=0)

            while True:
                # 샘플 생성
                next_sample = self.build_sample()
                if next_sample is None:
                    break
                    # 샘플이 없으면 아예 학습이 진행되지 않도록
                    # break 한다.

                # num_steps만큼 샘플 저장
                q_sample.append(next_sample)
                # 다음 샘플 더한다.
                if len(q_sample) < self.num_steps:
                    continue
                # 샘플의 갯수가 num_steps 보다 작을 경우
                # 다시 처음부터 실행 -> q_sample 이 num_steps 개 만큼 쌓였을 때,
                # 그때 되서야 학습이 진행되도록 하기 위함.

                # 가치, 정책 신경망 예측
                pred_value = None
                pred_policy = None
                if self.value_network is not None:
                    # 가치신경망이 존재할 경우 (없는 경우 -> monkey)
                    pred_value = self.value_network.predict(
                        list(q_sample))
                    # q_sample 데이터를 가치신경망에 넣어서
                    # 나온 기대가치값을 pred_value에 담는다.
                if self.policy_network is not None:
                    # 정책신경망이 존재할 경우
                    pred_policy = self.policy_network.predict(
                        list(q_sample))
                    # 마찬가지로 q_sample 데이터를 정책신경망에 넣어서
                    # 나온 기대가치값을 pred_policy에 담는다.
                
                # 신경망 또는 탐험에 의한 행동 결정
                action, confidence, exploration = \
                    self.agent.decide_action(
                        pred_value, pred_policy, epsilon)
                # 에이전트가 가치값과 정책값을 기반으로 행동을 결정한다.
                # 그리고 어떤 행동인지, (매수:0, 매도:1 아마?)
                # 그리고 자신감은 얼마나 뿜뿜한지 (0~1 사이)
                # exploration 은 boolean, True 또는 False
                # 탐험일 경우 True, 신경망이 자기가 선택한 경우는 False

                # 결정한 행동을 수행하고 즉시 보상과 지연 보상 획득
                immediate_reward, delayed_reward = \
                    self.agent.act(action, confidence)
                # 지연보상에 도달했을 경우 즉시 보상은 0.
                # 지연보상에 도달하지 않았을 경우 저번 에포크에서의 즉시보상 넘겨받음.

                # 행동 및 행동에 대한 결과를 기억
                self.memory_sample.append(list(q_sample))
                # q_sample 은 num_steps 만큼 축적된 경험들에 대한 데이터.
                self.memory_action.append(action)
                # 그리고 그 경험들에 대한 데이터의 '결과' 로 action 1개 값이 선택되고,
                # 그걸 q_sample 안에 넣는다. [[그 상황에 대한 데이터들],1(매수를 선택했다)]
                self.memory_reward.append(immediate_reward)
                # 그 상황에서 얻은 즉시 보상도 넣는다.
                # [[그 상황에 대한 데이터들],1(매수했다),20(20의 보상을 얻었다)]
                if self.value_network is not None:
                    self.memory_value.append(pred_value)
                    # 신경망이 존재할 경우 예측 가치값을 넣는다.
                    # [[상황데이터들],행동,보상,기대 가치값]
                if self.policy_network is not None:
                    self.memory_policy.append(pred_policy)
                    # [[상황데이터들],행동,보상,기대가치값, 정책값(그 행동에 대한 확률)]
                    # 정책값은 [0.37, 0.63] 이런식으로 되어 있고,
                    # 1번째 인덱스 값을 선택했으므로 0.63이 담기는거지.
                self.memory_pv.append(self.agent.portfolio_value)
                # 그리고 pv, 포트폴리오 가치를 담는 리스트에 에이전트의 포트폴리오 가치를 담는다.
                self.memory_num_stocks.append(self.agent.num_stocks)
                # 보유 주식수를 담는 리스트에 에이전트가 가진 보유 주식수 값을 담는다.
                if exploration:
                    # 만약 탐험을 하는 경우라면
                    self.memory_exp_idx.append(self.training_data_idx)
                    # 탐험을 한 경우를 저장하기 위해
                    # 탐험 인덱스 리스트에 탐험을 했을 때의 인덱스를 담아준다.

                # 반복에 대한 정보 갱신
                self.batch_size += 1
                self.itr_cnt += 1
                # 반복 횟수
                self.exploration_cnt += 1 if exploration else 0
                # 탐험을 했을 경우 탐험cnt 에 1을 더한다.

                # 지연 보상 발생된 경우 미니 배치 학습
                if learning and (delayed_reward != 0):
                    # 학습이 진행되고, 지연보상이 0이 아닌 경우
                    self.fit(delayed_reward, discount_factor)
                    # 지연보상과 학습율로 배치학습을 시키고 가중치를 갱신시킨다.
                    # loss를 구하고, 보상에 근거해 경사하강법 시행한다.

            # 에포크 종료 후 학습
            if learning:
                self.fit(
                    self.agent.profitloss, discount_factor, full=True)
                # 에포크수 다 끝났을 경우엔,
                # 에이전트의 누적 손익/손실율과 할인율을 통해 다시 또 학습시킨다.

            # 에포크 관련 정보 로그 기록
            num_epoches_digit = len(str(num_epoches))
            epoch_str = str(epoch + 1).rjust(num_epoches_digit, '0')
            time_end_epoch = time.time()
            elapsed_time_epoch = time_end_epoch - time_start_epoch
            if self.learning_cnt > 0:
                self.loss /= self.learning_cnt
            logging.info("[{}][Epoch {}/{}] Epsilon:{:.4f} "
                "#Expl.:{}/{} #Buy:{} #Sell:{} #Hold:{} "
                "#Stocks:{} PV:{:,.0f} "
                "LC:{} Loss:{:.6f} ET:{:.4f}".format(
                    self.stock_code, epoch_str, num_epoches, epsilon, 
                    self.exploration_cnt, self.itr_cnt,
                    self.agent.num_buy, self.agent.num_sell, 
                    self.agent.num_hold, self.agent.num_stocks, 
                    self.agent.portfolio_value, self.learning_cnt, 
                    self.loss, elapsed_time_epoch))
            # Expl : Exploration Count 몇번 탐험했냐
            # LC : Learning Count 몇번 배웠냐
            # elapsed_time_epoch : 몇번까지 에포크수 돌렸는지.
            
            # 에포크 관련 정보 가시화
            self.visualize(epoch_str, num_epoches, epsilon)
            # 가시화 후 사진 output 폴더에 저장한다.

            # 학습 관련 정보 갱신
            max_portfolio_value = max(
                max_portfolio_value, self.agent.portfolio_value)
            if self.agent.portfolio_value > self.agent.initial_balance:
                epoch_win_cnt += 1

        # 종료 시간
        time_end = time.time()
        elapsed_time = time_end - time_start
        # 총 학습 시간 : elapsed_time

        # 학습 관련 정보 로그 기록
        with self.lock:
            logging.info("[{code}] Elapsed Time:{elapsed_time:.4f} "
                "Max PV:{max_pv:,.0f} #Win:{cnt_win}".format(
                code=self.stock_code, elapsed_time=elapsed_time, 
                max_pv=max_portfolio_value, cnt_win=epoch_win_cnt))

    # 가치 신경망 및 정책 신경망 저장 함수
    # 여기 가치 신경망과 정책 신경망 저장 위치 잘 공부하기.
    # 아마 value_network_name 이랑 policy_network_name 이 이 위치로 지정되지 않나 싶은데.
    # network_path 가 어떻게 들어가는지 잘 파악해서 정리해놓기.

    # 모델 저장하는 함수.
    def save_models(self):
        if self.value_network is not None and \
                self.value_network_path is not None:
            self.value_network.save_model(self.value_network_path)
        if self.policy_network is not None and \
                self.policy_network_path is not None:
            self.policy_network.save_model(self.policy_network_path)
    # value_network_path 를 지정했을 경우에만
    # 학습 후의 신경망 모델들을 저장한다.

    # 즉 신경망 이름 지정 안하면 아예 저장이 안되네.

# Deep Q Network 학습기 - DQN 은 가치신경망만 사용한다.
class DQNLearner(ReinforcementLearner):
    def __init__(self, *args, value_network_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_network_path = value_network_path
        self.init_value_network()

    def get_batch(self, batch_size, delayed_reward, discount_factor):
        memory = zip(
            reversed(self.memory_sample[-batch_size:]),
            reversed(self.memory_action[-batch_size:]),
            reversed(self.memory_value[-batch_size:]),
            reversed(self.memory_reward[-batch_size:]),
        )
        x = np.zeros((batch_size, self.num_steps, self.num_features))
        y_value = np.zeros((batch_size, self.agent.NUM_ACTIONS))
        value_max_next = 0
        reward_next = self.memory_reward[-1]
        for i, (sample, action, value, reward) in enumerate(memory):
            x[i] = sample
            y_value[i] = value
            r = (delayed_reward + reward_next - reward * 2) * 100
            y_value[i, action] = r + discount_factor * value_max_next
            value_max_next = value.max()
            reward_next = reward
        return x, y_value, None


class PolicyGradientLearner(ReinforcementLearner):
    def __init__(self, *args, policy_network_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy_network_path = policy_network_path
        self.init_policy_network()

    def get_batch(self, batch_size, delayed_reward, discount_factor):
        memory = zip(
            reversed(self.memory_sample[-batch_size:]),
            reversed(self.memory_action[-batch_size:]),
            reversed(self.memory_policy[-batch_size:]),
            reversed(self.memory_reward[-batch_size:]),
        )
        x = np.zeros((batch_size, self.num_steps, self.num_features))
        y_policy = np.full((batch_size, self.agent.NUM_ACTIONS), .5)
        reward_next = self.memory_reward[-1]
        for i, (sample, action, policy, reward) in enumerate(memory):
            x[i] = sample
            y_policy[i] = policy
            r = (delayed_reward + reward_next - reward * 2) * 100
            y_policy[i, action] = sigmoid(r)
            reward_next = reward
        return x, None, y_policy


class ActorCriticLearner(ReinforcementLearner):
    def __init__(self, *args, shared_network=None, 
        value_network_path=None, policy_network_path=None, **kwargs):
        super().__init__(*args, **kwargs)
        if shared_network is None:
            self.shared_network = Network.get_shared_network(
                net=self.net, num_steps=self.num_steps, 
                input_dim=self.num_features)
        else:
            self.shared_network = shared_network
        self.value_network_path = value_network_path
        self.policy_network_path = policy_network_path
        if self.value_network is None:
            self.init_value_network(shared_network=shared_network)
        if self.policy_network is None:
            self.init_policy_network(shared_network=shared_network)

    def get_batch(self, batch_size, delayed_reward, discount_factor):
        memory = zip(
            reversed(self.memory_sample[-batch_size:]),
            reversed(self.memory_action[-batch_size:]),
            reversed(self.memory_value[-batch_size:]),
            reversed(self.memory_policy[-batch_size:]),
            reversed(self.memory_reward[-batch_size:]),
        )
        x = np.zeros((batch_size, self.num_steps, self.num_features))
        y_value = np.zeros((batch_size, self.agent.NUM_ACTIONS))
        y_policy = np.full((batch_size, self.agent.NUM_ACTIONS), .5)
        value_max_next = 0
        reward_next = self.memory_reward[-1]
        for i, (sample, action, value, policy, reward) \
            in enumerate(memory):
            x[i] = sample
            y_value[i] = value
            y_policy[i] = policy
            r = (delayed_reward + reward_next - reward * 2) * 100
            y_value[i, action] = r + discount_factor * value_max_next
            y_policy[i, action] = sigmoid(value[action])
            value_max_next = value.max()
            reward_next = reward
        return x, y_value, y_policy


class A2CLearner(ActorCriticLearner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_batch(self, batch_size, delayed_reward, discount_factor):
        memory = zip(
            reversed(self.memory_sample[-batch_size:]),
            reversed(self.memory_action[-batch_size:]),
            reversed(self.memory_value[-batch_size:]),
            reversed(self.memory_policy[-batch_size:]),
            reversed(self.memory_reward[-batch_size:]),
        )
        x = np.zeros((batch_size, self.num_steps, self.num_features))
        y_value = np.zeros((batch_size, self.agent.NUM_ACTIONS))
        y_policy = np.full((batch_size, self.agent.NUM_ACTIONS), .5)
        value_max_next = 0
        reward_next = self.memory_reward[-1]
        for i, (sample, action, value, policy, reward) \
            in enumerate(memory):
            x[i] = sample
            r = (delayed_reward + reward_next - reward * 2) * 100
            y_value[i, action] = r + discount_factor * value_max_next
            advantage = value[action] - value.mean()
            y_policy[i, action] = sigmoid(advantage)
            value_max_next = value.max()
            reward_next = reward
        return x, y_value, y_policy


class A3CLearner(ReinforcementLearner):
    def __init__(self, *args, list_stock_code=None, 
        list_chart_data=None, list_training_data=None,
        list_min_trading_unit=None, list_max_trading_unit=None, 
        value_network_path=None, policy_network_path=None,
        **kwargs):
        assert len(list_training_data) > 0
        super().__init__(*args, **kwargs)
        self.num_features += list_training_data[0].shape[1]

        # 공유 신경망 생성
        self.shared_network = Network.get_shared_network(
            net=self.net, num_steps=self.num_steps, 
            input_dim=self.num_features)
        self.value_network_path = value_network_path
        self.policy_network_path = policy_network_path
        if self.value_network is None:
            self.init_value_network(shared_network=self.shared_network)
        if self.policy_network is None:
            self.init_policy_network(shared_network=self.shared_network)

        # A2CLearner 생성
        self.learners = []
        for (stock_code, chart_data, training_data, 
            min_trading_unit, max_trading_unit) in zip(
                list_stock_code, list_chart_data, list_training_data,
                list_min_trading_unit, list_max_trading_unit
            ):
            learner = A2CLearner(*args, 
                stock_code=stock_code, chart_data=chart_data, 
                training_data=training_data,
                min_trading_unit=min_trading_unit, 
                max_trading_unit=max_trading_unit, 
                shared_network=self.shared_network,
                value_network=self.value_network,
                policy_network=self.policy_network, **kwargs)
            self.learners.append(learner)

    def run(
        self, num_epoches=100, balance=10000000,
        discount_factor=0.9, start_epsilon=0.5, learning=True):
        threads = []
        for learner in self.learners:
            threads.append(threading.Thread(
                target=learner.run, daemon=True, kwargs={
                'num_epoches': num_epoches, 'balance': balance,
                'discount_factor': discount_factor, 
                'start_epsilon': start_epsilon,
                'learning': learning
            }))
        for thread in threads:
            thread.start()
            time.sleep(1)
        for thread in threads: thread.join()
