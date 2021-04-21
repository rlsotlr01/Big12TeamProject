# https://www.google.com/search?q=%EB%A9%80%ED%8B%B0%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8+%EA%B0%95%ED%99%94%ED%95%99%EC%8A%B5&ei=c099YNWcD4y9mAXwpr2ICg&oq=%EB%A9%80%ED%8B%B0%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8+%EA%B0%95%ED%99%94%ED%95%99%EC%8A%B5&gs_lcp=Cgdnd3Mtd2l6EAMyAggAOgUIABCwAzoJCAAQsAMQBxAeUNUHWMkQYI0RaANwAHgCgAF4iAHvCJIBBDEyLjGYAQCgAQGqAQdnd3Mtd2l6yAEFwAEB&sclient=gws-wiz&ved=0ahUKEwiVosGsgYrwAhWMHqYKHXBTD6EQ4dUDCA4&uact=5
# 멀티에이전트 기존에 생각한 아이디어.
# 신경망 앙상블이 아니라, 에이전트가 멀티인 것.
# 잘 생각해보기.

import os
import sys
import logging
import argparse
import json

import settings
import utils
import data_manager


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stock_code', nargs='+')
    parser.add_argument('--ver', choices=['v1', 'v2', 'v3'], default='v2')
    parser.add_argument('--rl_method', 
        choices=['dqn', 'pg', 'ac', 'a2c', 'a3c', 'monkey'])
    # dqn : 땡(우세) 무동작 -> 진짜 단순한 강화학습장치 -> 가치만 보고 움직이는 애. -> 본능에 가까운 침팬지
    # pg : [0.5 0.5] -> [0.6 0.4] -> [0.7 0.3] -> 동물보단 똑똑한애.
    # ac : actor-critic actor - pg, critic - dqn -> 조금 더 똑똑한 애. 사람
    # a2c : actor-critic 보단 조금 더 똑똑한 애. 하지만 생각이 많아.
    # a3c : 나루토 그림자 분신술
    # monkey -> 아무렇게나.

    parser.add_argument('--net', 
        choices=['dnn', 'lstm', 'cnn', 'monkey'], default='dnn')
    # 신경망 쓸건지.
    # dnn -> 동물 -> 단순한 신경망
    # lstm -> 사람 -> LSTM도 괜찮은데 CNN을 쓰는것도 좋은 방법.
    # cnn -> 합성곱 신경망 -> 여러 다양한 컬럼들을 배울 수 있다. -> 여러 종목

    parser.add_argument('--num_steps', type=int, default=1) # 몇일을 배워서 그 다음날을 예측할 것이냐.
    parser.add_argument('--lr', type=float, default=0.01)
    parser.add_argument('--discount_factor', type=float, default=0.9)
    parser.add_argument('--start_epsilon', type=float, default=0)
    parser.add_argument('--balance', type=int, default=10000000)
    parser.add_argument('--num_epoches', type=int, default=100)
    parser.add_argument('--delayed_reward_threshold', 
        type=float, default=0.05)
    # --delayed_reward_threshold 0.03 +0.03 -0.03
    parser.add_argument('--backend', 
        choices=['tensorflow', 'plaidml'], default='tensorflow')
    parser.add_argument('--output_name', default=utils.get_time_str()) # 얘 꼭 지정
    parser.add_argument('--value_network_name') # 얘 꼭 지정
    parser.add_argument('--policy_network_name') # 얘 꼭 지정
    parser.add_argument('--reuse_models', action='store_true') # 재사용할거면 얘를 True
    parser.add_argument('--learning', action='store_true') # True : 학습, False : 시뮬레이션
    parser.add_argument('--start_date', default='20160104')
    parser.add_argument('--end_date', default='20191230')
    args = parser.parse_args()

    # Keras Backend 설정
    if args.backend == 'tensorflow':
        os.environ['KERAS_BACKEND'] = 'tensorflow'
    elif args.backend == 'plaidml':
        os.environ['KERAS_BACKEND'] = 'plaidml.keras.backend'

    # 출력 경로 설정
    output_path = os.path.join(settings.BASE_DIR,
        'output/{}_{}_{}'.format(args.output_name, args.rl_method, args.net))
    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # 파라미터 기록
    with open(os.path.join(output_path, 'params.json'), 'w') as f:
        f.write(json.dumps(vars(args)))
    
    # 로그 기록 설정
    file_handler = logging.FileHandler(filename=os.path.join(
        output_path, "{}.log".format(args.output_name)), encoding='utf-8')
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.INFO)
    logging.basicConfig(format="%(message)s",
        handlers=[file_handler, stream_handler], level=logging.DEBUG)
        
    # 로그, Keras Backend 설정을 먼저하고 RLTrader 모듈들을 이후에 임포트해야 함
    from agent import Agent
    from learners import ReinforcementLearner, DQNLearner, \
        PolicyGradientLearner, ActorCriticLearner, A2CLearner, A3CLearner

    # 모델 경로 준비
    value_network_path = ''
    policy_network_path = ''
    if args.value_network_name is not None:
        # value_network_name 을 지정해야 불러옴.
        value_network_path = os.path.join(settings.BASE_DIR,
            'models/{}.h5'.format(args.value_network_name))
    else:
        value_network_path = os.path.join(
            output_path, '{}_{}_value_{}.h5'.format(
                args.rl_method, args.net, args.output_name))
    if args.policy_network_name is not None:
        policy_network_path = os.path.join(settings.BASE_DIR,
            'models/{}.h5'.format(args.policy_network_name))
    else:
        policy_network_path = os.path.join(
            output_path, '{}_{}_policy_{}.h5'.format(
                args.rl_method, args.net, args.output_name))

    common_params = {}
    list_stock_code = []
    # list_stock_codes = []  # a3c 용도. -> 보류
    list_chart_data = []
    list_training_data = []
    list_min_trading_unit = []
    list_max_trading_unit = []
    

    for stock_code in args.stock_code:
        # 차트 데이터, 학습 데이터 준비
        if args.ver != 'v3':
            chart_data, training_data = data_manager.load_data(
                os.path.join(settings.BASE_DIR,
                'data/{}/{}.csv'.format(args.ver, stock_code)),
                args.start_date, args.end_date, ver=args.ver)

        else: # args.ver == 'v3' 일 경우
            list_chart_data, list_training_data \
                = data_manager.load_data(
                os.path.join(settings.BASE_DIR,
                             'data/{}/{}.csv'.format(args.ver, stock_code)),
                args.start_date, args.end_date, ver=args.ver)
            # v3의 경우는 코드명까지만 넣어준다. 뒤에 .csv 안붙인다.

        # 3개 엑셀 받아들이도록 변경. -> load_data 를 수정해야댐.
        #  chart_data1, training_data1, chart_data2, training_data2, ...
        #  'data/{}/{}f.csv', 'data/{}/{}g.csv', 'data/{}/{}t.csv'
        # 튜플형식으로 묶든.
        # load_data 수정 완료.
        
        # 최소/최대 투자 단위 설정
        min_trading_unit = max(int(100000 / chart_data.iloc[-1]['close']), 1)
        max_trading_unit = max(int(1000000 / chart_data.iloc[-1]['close']), 1)
        # 이부분 v3의 경우 문제가 되지 않을 것인가? 문제 안되겠지?

        # 공통 파라미터 설정
        common_params = {'rl_method': args.rl_method, 
            'delayed_reward_threshold': args.delayed_reward_threshold,
            'net': args.net, 'num_steps': args.num_steps, 'lr': args.lr,
            'output_path': output_path, 'reuse_models': args.reuse_models}

        # 강화학습 시작
        learner = None
        if args.rl_method != 'a3c':
            # if v3 -> common_params.update 3번 돌리면 되나? X ->
            # [chart_data1, chart_data2, chart_data3]
            # else
            common_params.update({'stock_code': stock_code,
                'chart_data': chart_data, 
                'training_data': training_data,
                'min_trading_unit': min_trading_unit, 
                'max_trading_unit': max_trading_unit})
            if args.rl_method == 'dqn':
                learner = DQNLearner(**{**common_params, 
                'value_network_path': value_network_path})
            elif args.rl_method == 'pg':
                learner = PolicyGradientLearner(**{**common_params, 
                'policy_network_path': policy_network_path})
            elif args.rl_method == 'ac':
                learner = ActorCriticLearner(**{**common_params, 
                    'value_network_path': value_network_path, 
                    'policy_network_path': policy_network_path})
            elif args.rl_method == 'a2c':
                learner = A2CLearner(**{**common_params, 
                    'value_network_path': value_network_path, 
                    'policy_network_path': policy_network_path})
            elif args.rl_method == 'monkey':
                args.net = args.rl_method
                args.num_epoches = 1
                args.discount_factor = None
                args.start_epsilon = 1
                args.learning = False
                learner = ReinforcementLearner(**common_params)
            if learner is not None:
                learner.run(balance=args.balance, 
                    num_epoches=args.num_epoches, 
                    discount_factor=args.discount_factor, 
                    start_epsilon=args.start_epsilon,
                    learning=args.learning)
                learner.save_models()
        elif args.rl_method =='a3c' and args.ver != 'v3': # 얘 그대로 써도 되고,
            list_stock_code.append(stock_code)
            list_chart_data.append(list_chart_data)
            list_training_data.append(list_training_data)
            list_min_trading_unit.append(min_trading_unit)
            list_max_trading_unit.append(max_trading_unit)
        else: # args.rl_method 가 a3c 이고 args.ver 가 v3일 경우
            list_stock_code = [stock_code, stock_code, stock_code]
            # v3 하면 stock_code 하나만 넣을 수 있도록 해줘야 함.
            # 만약 v3 할 때 여러개 돌리고 싶으면 이 코드를 수정해줘야 함.

            # v3일 경우 stock_code 를 어떻게 넣어줘야 할까.
            # 만약 [stock_code stock_code stock_code] 로 넣어주면
            # A3C에 바로 적용할 수 있음.
            # 하지만 만약 여러개 한꺼번에 돌릴 수 있도록 만들려면?
            # 그 경우 [stock_code1, stock_code2, stock_code3] 로 해야 되는데,
            # 그 경우는 A3C(learners 모듈 안에 있는거)를 수정해줘야 함.
            list_chart_data = list_chart_data
            list_training_data = list_training_data
            # list_chart랑 list_training 은 아까 로드 했음.
            for i in range(len(list_chart_data)):
                list_min_trading_unit.append(min_trading_unit)
                list_max_trading_unit.append(max_trading_unit)
                # 이부분 문제 없지? -> 내 생각엔 문제 없을 듯.
            # 만약 a3c 여러개 돌리면 여기 모든 데이터들 다 list 의 list 로 만들어야 함.


    if args.rl_method == 'a3c' and args.ver != 'v3':
        learner = A3CLearner(**{
            **common_params, 
            'list_stock_code': list_stock_code, 
            'list_chart_data': list_chart_data, 
            'list_training_data': list_training_data,
            'list_min_trading_unit': list_min_trading_unit, 
            'list_max_trading_unit': list_max_trading_unit,
            'value_network_path': value_network_path, 
            'policy_network_path': policy_network_path})

        learner.run(balance=args.balance, num_epoches=args.num_epoches, 
                    discount_factor=args.discount_factor, 
                    start_epsilon=args.start_epsilon,
                    learning=args.learning)
        learner.save_models()

    if args.rl_method == 'a3c' and args.ver == 'v3':
        learner = A3CLearner(**{
            **common_params,
            'list_stock_code': list_stock_code,
            'list_chart_data': list_chart_data,
            'list_training_data': list_training_data,
            'list_min_trading_unit': list_min_trading_unit,
            'list_max_trading_unit': list_max_trading_unit,
            'value_network_path': value_network_path,
            'policy_network_path': policy_network_path})

        learner.run(balance=args.balance, num_epoches=args.num_epoches,
                    discount_factor=args.discount_factor,
                    start_epsilon=args.start_epsilon,
                    learning=args.learning)
        learner.save_models()

        # 만약 여러개 돌리고 싶으면 여기 list의 list 를 for문 돌려줘야 하고,
        # 거기다가 a3c 코드도 고쳐서 신경망 모델 여러개 저장되도록 해줘야 함.
        # 너무 어려운데?

        # 가져와서 예측할 땐, learners.init_value_network 로 가치신경망 탑재하고,
        # learners.init_policy_network 로 정책신경망 탑재하고,
        # 그다음 predict 하면 될 것 같은데?
        # 이후 데이터가 쌓일 때마다, 학습은 위 해당 코딩 그대로 해서 학습시키고.
        # 그 다음날 다시 predict 해서 결과값 출력.
        # 장 끝나면 다시 또 학습.