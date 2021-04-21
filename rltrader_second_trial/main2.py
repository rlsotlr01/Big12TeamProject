# 주식 매매용 코드
# 하기에 앞서서 32비트 윈도우 가상환경을 만들어줘야 한다.

# 여기서부터 따오면 주식 매매 프로그램 만들 수 있을 듯
# (코드수정요망)
# 일단 이거 하기에 앞서서,
# 1.신경망 저장해놓은 거 탑재해놓고 load
# value_network, policy_network 탑재.
# from environment import Environment
# from agent import Agent
from networks import Network, DNN, LSTMNetwork, CNN
# from visualizer import Visualizer
from learners import A3CLearner
import pandas as pd

# 원숭이 책에서 나온 투자 시뮬레이션 방식
# 1. 학습된 정책 신경망(HDF5 파일) 사용
# 2. 학습 기능을 비활성화 - learning : False
# 3. 초기 무작위 투자 비율 0% - e = 0


# 2. 가치, 정책 신경망 예측

list_stock_code = [] # 강화학습 에이전트로 거래할 종목들 (미리 학습 끝낸것들)

pred_value = None
pred_policy = None
# common_params 는 **kwargs 에 들어간다.
common_params = {'rl_method': 'a3c', 
            'delayed_reward_threshold': 0.05,
            'net': 'lstm', 'num_steps': 15, 'lr': 0.001,
            'output_path': '신경망들이 담겨있는 폴더위치', 'reuse_models': True}
discount_factor = 0.9
# 위 값들은 초기에 신경망 훈련했을 때 넣어준 데이터

list_chart_data = [] # 차트 데이터 담을 공간
list_training_data = [] # 훈련 데이터 담을 공간
list_min_trading_unit = []
list_max_trading_unit = []
for stock_code in list_stock_code:
    # 차트 데이터, 학습 데이터 준비
    # chart_data, training_data = data_manager.load_data(
    #     os.path.join(settings.BASE_DIR,
    #                  'data/{}/{}.csv'.format(args.ver, stock_code)),
    #     args.start_date, args.end_date, ver=args.ver)
    # 이 부분을 3종목에 대한 15일치 데이터로 넣어줘야 함.
    # 데이터타입은 pd.Dataframe.
    # 안에 들어가는 컬럼은 data_manager 참고해서 넣기.
    # 아니면 차라리 data_manager 의 load_data 함수를 수정할까?
    # 투자용도일 경우 boolean 넣어서 실전 투자 데이터 가져오는 용도로...
    chart_data = [] # 테스트용 차트 데이터 집어 넣음.
    training_data = [] # 테스트용 재무/추세/정세 데이터 집어 넣음.
    # 차트데이터는 ohlc + v 까지만.
    list_chart_data.append(chart_data)   # 차트 데이터를 담는다.
    list_training_data.append(training_data) # 훈련 데이터를 담는다.
    # 만약 3종목이라면 3종목의 차트데이터 각각 넣어줘야 함. pd.DataFrame 으로

    # 최소/최대 투자 단위 설정
    min_trading_unit = max(int(100000 / chart_data.iloc[-1]['close']), 1)
    max_trading_unit = max(int(1000000 / chart_data.iloc[-1]['close']), 1)
    # 최소 주문을 10만원 근처로, 최대 주문을 100만원 근처로 한다.
    list_min_trading_unit.append(min_trading_unit)
    list_max_trading_unit.append(max_trading_unit)

value_network_path = '' # 가치신경망 파일 위치 지정
policy_network_path = '' # 정책신경망 파일 위치 지정


a3c_learner = A3CLearner(**{
            **common_params, 
            'list_stock_code': list_stock_code, 
            'list_chart_data': list_chart_data, 
            'list_training_data': list_training_data,
            'list_min_trading_unit': list_min_trading_unit, 
            'list_max_trading_unit': list_max_trading_unit,
            'value_network_path': value_network_path, 
            'policy_network_path': policy_network_path})
# A3C learner 클래스 안에 learners 엔 각각의 종목코드에 해당하는 학습기가 존재.

# 4. 여기 행동을 API랑 연결하면 곧 주식 매매프로그램 완성.
# 5. 거기다가 API 에 수익 시각화 기능도 만들어야 될 듯.
# 실시간 계좌 출력.
for learner in a3c_learner.learners:
    epsilon = 0
    q_sample = learner.build_sample()
    # 상태가 담긴 데이터로 변환해줌.
    if learner.value_network is not None:
        pred_value = learner.value_network.predict(list(q_sample))
    if learner.policy_network is not None:
        pred_policy = learner.policy_network.predict(list(q_sample))

    action, confidence, exploration = \
                        learner.agent.decide_action(
                            pred_value, pred_policy, epsilon)
    # 해야할 행동과 자신감, 그리고 탐험 여부를 가져온다.

    number_of_trading = learner.agent.decide_trading_unit(confidence) # 거래할 단위를 신경망이 알아낸다.
    # 그리고 action 을 API에 대입해 행동한다.

    immediate_reward, delayed_reward = learner.agent.act(action, confidence)
    # 그리고 한 행동을 에이전트 상에서도 실행시킨다.

    # 그렇게 action 과 number_of_trading 이 있으면 바로 구매 가능.

# 실행을 하고 다음날 데이터가 모두 만들어지면 update ?
#learner.update_networks(batch_size, delayed_reward, discount_factor)