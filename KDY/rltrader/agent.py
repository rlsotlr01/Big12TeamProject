import numpy as np
import utils

# 에이전트 클래스이다.
class Agent:
    # 에이전트 상태가 구성하는 값 개수
    STATE_DIM = 2  # 주식 보유 비율, 포트폴리오 가치 비율
    # exp : STATE_DIM 은 에이전트 상태의 차원이다.
    # RLTrader 에서 에이전트의 상태는 주식보유비율, 포트폴리오 가치 비율 2개의 값을 가지므로,
    # 2차원이다.

    # 매매 수수료 및 세금
    TRADING_CHARGE = 0.00015  # 거래 수수료 0.015%
    # TRADING_CHARGE = 0.00011  # 거래 수수료 0.011%
    # TRADING_CHARGE = 0  # 거래 수수료 미적용
    TRADING_TAX = 0.0025  # 거래세 0.25%
    # TRADING_TAX = 0  # 거래세 미적용

    # exp : 주식에서 거래수수료와 거래세를 고려해준다.
    # 이 책에선 거래수수료와 거래세를 적용하지 않기 때문에 0으로 적용해주는데,
    # 우린 포함해야 하므로 0으로 설정 안함.

    # 행동
    ACTION_BUY = 0  # 매수
    ACTION_SELL = 1  # 매도
    ACTION_HOLD = 2  # 홀딩
    # 인공 신경망에서 확률을 구할 행동들
    ACTIONS = [ACTION_BUY, ACTION_SELL]
    NUM_ACTIONS = len(ACTIONS)  # 인공 신경망에서 고려할 출력값의 개수

    # 매도 : 0 / 매수 : 1 / 홀딩 : 2
    # 행동들 중에서 정책 신경망이 확률을 계산할 행동들을 ACTIONS 리스트에 저장한다.
    # 즉, 0 또는 1 두가지 중 하나를 선택하게 될 것이다.
    # 그리고 RLTrader 가 매수와 매도 중 결정한 행동을 할 수 없는 때만 관망(홀딩)을 한다.

    # ------ 여기까지가 에이전트 클래스 상수 선언 부분 ------

    def __init__(
        self, environment, min_trading_unit=1, max_trading_unit=2, 
        delayed_reward_threshold=.05):
        # Environment 객체
        # 현재 주식 가격을 가져오기 위해 환경 참조
        self.environment = environment
        # environment 는 environment 클래스의 객체이다.

        # 최소 매매 단위, 최대 매매 단위, 지연보상 임계치
        self.min_trading_unit = min_trading_unit  # 최소 단일 거래 단위
        self.max_trading_unit = max_trading_unit  # 최대 단일 거래 단위
        # 지연보상 임계치
        self.delayed_reward_threshold = delayed_reward_threshold

        # min_trading_unit 은 최소한의 매매 단위이고,
        # max_trading_unit 은 최대한의 매매 단위이다.
        # max_trading_unit 을 크게 잡으면
        # 그만큼 에이전트가 확신이 들 때 더 많이 구매할 수 있다.
        # delayed_reward_threshold 는 지연보상임계치로,
        # 손익률이 이 값을 넘어가면 지연 보상이 발생한다.

        # --- 여기부터 공부부

       # Agent 클래스의 속성
        self.initial_balance = 0  # 초기 자본금
        self.balance = 0  # 현재 현금 잔고
        self.num_stocks = 0  # 보유 주식 수
        # 포트폴리오 가치: balance + num_stocks * {현재 주식 가격}
        self.portfolio_value = 0 
        self.base_portfolio_value = 0  # 직전 학습 시점의 PV
        self.num_buy = 0  # 매수 횟수
        self.num_sell = 0  # 매도 횟수
        self.num_hold = 0  # 홀딩 횟수
        self.immediate_reward = 0  # 즉시 보상
        self.profitloss = 0  # 현재 손익
        self.base_profitloss = 0  # 직전 지연 보상 이후 손익
        self.exploration_base = 0  # 탐험 행동 결정 기준

        # initial_balance 는 초기 자본금.
        # self.balance 는 현재 주식을 제외한 현금
        # self.num_stocks 는 해당 주식을 몇개 가지고 있는지.
        # self.portfolio_value 는 포트폴리오가 얼마만큼의 가치를 지녔는지.
        # num_buy는 매수 횟수
        # num_sell 은 매도 횟수
        # num_hold 는 관망 횟수
        # immediate_reward 는 가장 최근에 한 행동에 대한 즉시 보상값.


        # Agent 클래스의 상태
        self.ratio_hold = 0  # 주식 보유 비율
        self.ratio_portfolio_value = 0  # 포트폴리오 가치 비율

        # 에이전트의 상태는 ratio_hold (주식 보유 비율)과 - 100만원 중 50만원의 주식을 갖고 있다면 50%
        # ratio_portfolio_value(포트폴리오 가치 비율) 를 가진다. - 100만원이 있었는데 110만원이 된다면 1.10이 된다.


    # 에이전트의 상태를 초기화하는 함수
    def reset(self):
        self.balance = self.initial_balance
        self.num_stocks = 0
        self.portfolio_value = self.initial_balance
        self.base_portfolio_value = self.initial_balance
        self.num_buy = 0
        self.num_sell = 0
        self.num_hold = 0
        self.immediate_reward = 0
        self.ratio_hold = 0
        self.ratio_portfolio_value = 0

        # 초기화
        # 초기값은 balance(잔고 금액)와
        # portfolio_value 와 base_portfolio_value 세 값만 0이 아니다.
        # balance 는 초기 계좌 금액이 들어갈 것이고,
        # portfolio_value 와 base_portfolio_value 역시 초기 금액이 들어가야 마땅하다.

    # 탐험의 기준이 되는 exploration_base 를 새로 정하는 함수이다.
    def reset_exploration(self, alpha=None):
        if alpha is None:
            alpha = np.random.rand() / 2
        self.exploration_base = 0.5 + alpha

        # reset_exploration 은 탐험 확률을 부여하는 것이다. 응?
        # 예를 들어, 매수 탐험을 선호하기 위해 50%의 매수 탐험 확률을 미리 부여함.
        # 이게 어디 쓰이지? 이따가 보자.

    # 초기 자본금을 설정하는 함수
    def set_balance(self, balance):
        self.initial_balance = balance

        # 에이전트의 초기 자본금을 설정한다.
        # 디폴트 값은 1000만원으로 해주는 것 같다.


    # 에이전트 상태를 획득(get)하는 함수
    def get_states(self):
        self.ratio_hold = self.num_stocks / int(
            self.portfolio_value / self.environment.get_price())
        self.ratio_portfolio_value = (
            self.portfolio_value / self.base_portfolio_value
        )
        return (
            self.ratio_hold,
            self.ratio_portfolio_value
        )

    # 에이전트의 상태를 돌려준다.
    # 앞서 말한대로 에이전트의 상태로는 2가지가 존재한다.
    # 주식 보유 비율과, 포트폴리오 가치 비율이 존재한다.
    # 주식 보유 비율 = 현재 주식 수 / (포트폴리오 가치 / 주식의 가격)
    #   -> 포트폴리오 가치 / 주식의 가격 은 곧 내가 현재 가진 포트폴리오 가치로
    #       최대 얼마만큼의 주식을 살수 있는가를 의미한다. 즉
    #       지금 가진 주식수 / 최대로 가질 수 있는 주식 수 이다.

    # 주식 수가 너무 적으면 매수 관점에서 투자를 임하고,
    # 주식 수가 너무 많으면 매도 관점에서 투자를 임해야 한다.

    # 즉, 보유 주식 수를 통해 투자 행동 결정에 영향을 주기 위해서
    # 나중에 정책 신경망의 입력에 포함시킨다.

    # 포트폴리오 가치 비율 = 현재 포트폴리오의 가치 / 기준 포트폴리오 가치
    # 포트폴리오 가치 비율은 기준 포트폴리오 가치 대비 현재 포트폴리오의 가치 이다.
    # 기준 포트폴리오 가치는 직전에 목표 수익 또는 손익률을 달성했을 때의 포트폴리오 가치이다.
    # 포트폴리오 가치 비율이 0에 가까우면 손실이 그만큼 큰거고,
    # 1에 가까우면 원금, 1보다 크면 수익이 발생한 것이다.

    # 수익률이 목표 수익률에 가까우면 매도의 관점에서 투자를 할 것이다.

    # 수익률이 투자 행동 결정에 영향을 줄 수 있기에 이 또한
    # 나중에 정책 신경망의 입력에 포함시킨다.

    # 따라서 상태엔 2가지,
    # 주식 보유 비율과, 포트폴리오 가치 비율 두가지를 반환해야 하기 때문에
    # 튜플로 return 한다.

    # 탐험 또는 정책 신경망에 의한 행동 결정 - 행동 결정 검사 함수
    def decide_action(self, pred_value, pred_policy, epsilon):
        # 가치값과 정책값을 받아들여
        # 두 값을 기준으로 행동을 결정하는 함수이다.
        # epsilon 의 확률로 무작위 행동을 하고,
        # 그 외의 확률로는 신경망을 통해 행동을 결정한다.

        confidence = 0.

        pred = pred_policy
        # 정책망의 출력인 pred_policy 가 존재하면
        # pred_policy 를 기반으로 행동을 결정한다.

        if pred is None:
            # 만약 정책망의 출력이 존재하지 않는다면
            pred = pred_value
            # 가치신경망의 출력을 기반으로 행동을 결정한다.

        if pred is None:
            # 예측 값이 없을 경우 탐험
            epsilon = 1
            # epsilon 이 1 이라는 값은 완전 무작위 탐색을 한다는 뜻이다.

        else:
            # 만약 pred 값이 존재한다면

            # 값이 모두 같은 경우 탐험
            maxpred = np.max(pred)
            # 예측값이 가장 큰 값을 골라낸다.
            if (pred == maxpred).all():
                # 만약 예측값의 모든 값이 같은 값일 경우
                epsilon = 1
                # 이 또한 무작위 탐색을 한다.
                # (에이전트 입장에선 주어진 모든 선택지가 좋다고 여긴거니깐.)

        # 탐험 결정
        if np.random.rand() < epsilon:
            # epsilon 의 확률로
            exploration = True
            # 탐험을 한다.
            if np.random.rand() < self.exploration_base:
                # 그리고 exploration_base 확률로
                action = self.ACTION_BUY
                # 매수를 진행한다. (매수탐험확률)
            else:
                # exploration_base 이외의 확률로는
                action = np.random.randint(self.NUM_ACTIONS - 1) + 1
                # 매도만한다. 왜이렇게 짜놓은거지?
                # np.random.randint(2-1)+1

        else:
            # epsilon 이외의 확률일 때 (무작위가 아닌 신경망의 선택)
            exploration = False
            # 탐험을 하지 않는다.
            action = np.argmax(pred)
            # 그리고 예측값이 가장 큰 인덱스를 action 변수에 담고,

        confidence = .5
        # 자신감을 0.5로 지정해주고
        if pred_policy is not None:
            # 만약 정책신경망의 값이 존재하면
            confidence = pred[action]
            # 정책신경망의 해당 action 의 값이 신경망의 자신감이 된다.

            # 즉 confidence = 정책신경망에서 softmax 를 통해 산출된 확률값.

            # ex : 신경망이 이건 꼭 사야된다 라고 확신할 경우
            #      정책값은 1에 가까워 질 것이고, 이에 따라
            #      자신감도 1에 가까워 질 것이다.

        elif pred_value is not None:
            # 만약 정책신경망이 존재하지 않는다면
            confidence = utils.sigmoid(pred[action])
            # 자신감의 값은 가치 신경망 값에 sigmoid 값을 씌워
            # 0~1 사이의 값을 가진다.
            # 가치가 높으면 곧 자신감도 높아질 것이다.

        return action, confidence, exploration
        # 그리고 행동(인덱스 값), 자신감, 그리고 탐험 여부를 출력한다.

    # 행동의 유효성을 판단하는 함수
    def validate_action(self, action):
        # action 즉 행동의 인덱스 값을 받는다.
        if action == Agent.ACTION_BUY:
            # 만약 행동이 Agent 의 매수(0)에 해당한다면

            # 최소 단일 거래의 주식 수 만큼 구매할 수 있는지 여부를 확인한다.
            # (그만큼 현금이 계좌에 있는지 - balance : 현금)
            # 그리고 수수료도 포함해야 하기 때문에
            # 수수료를 포함한 주식가격 * 최소 거래 단위 이다.

            # 만약 계좌 내의 현금이 그 금액보다 작다면
            if self.balance < self.environment.get_price() * (
                1 + self.TRADING_CHARGE) * self.min_trading_unit:
                # 구매 불가능 -> False 를 날린다 (행동 거절)
                return False

        # 만약 인풋으로 받은 행동의 인덱스가 매도(1)에 해당한다면
        elif action == Agent.ACTION_SELL:
            # 계좌 내에 주식 잔고가 있는지 확인한다.
            # 만약 주식이 존재하지 않는다면
            if self.num_stocks <= 0:
                # 판매 불가능 -> False 를 날린다. (행동 거절)
                return False
        # 두 조건에 모두 해당하지 않는다면
        # 구매 가능하고 판매 가능한 상태이기에
        # action -> True, 실행할 수 있음을 출력한다.
        return True

    # 매수 또는 매도할 주식 수를 결정하는 함수 (정책 신경망이 행동에 대한 신뢰가 높을 경우 많이 산다)
    def decide_trading_unit(self, confidence):
        # 매수와 매도엔 agent의 "자신감"이 모든걸 결정한다.
        if np.isnan(confidence):
            # 만약 자신감이 없다면
            return self.min_trading_unit
            # 최소 거래 단위로 지정한다. (최소만 사거나 최소만 팔도록 한다)

        # 최소 거래단위 기준 얼마만큼의 주식을 더 살 것인지 계산한다.
        # 자신감이 1이면 풀매수
        # 자신감이 0.5면 그 중간수로 매수
        # 0이면 최소단위만 매수

        # 1. 자신감 * (최대단위-최소단위) 와
        # 2. 최대단위 - 최소단위
        # 둘 중 더 작은 값을 고르고,
        # 그 값과 0 중에서 최대값을 골라
        # added_traiding 에 넣어준다.
        # -> 음수도 걸러주고,
        # 최대단위-최소단위 를 넘어가는 값도 걸러줌.
        added_traiding = max(min(
            int(confidence * (self.max_trading_unit - 
                self.min_trading_unit)),
            self.max_trading_unit-self.min_trading_unit
        ), 0)

        # 그리고 최소 구매 단위 + 자신감에 근거한 추가구매수량을 리턴해준다.
        return self.min_trading_unit + added_traiding

    # 행동을 수행하는 함수
    def act(self, action, confidence):
        # 인풋 값으로 어떤 행동을 할 지에 대한 행동 인덱스 값
        # (행동인덱스 - 무작위 탐색으로 인해 결정되었거나, 신경망에 의해 결정되었거나)과,
        # 에이전트가 얼마나 자신감이 뿜뿜한지 자신감 지수를 건네 받는다.
        # (여기서 자신감 값은 정책신경망이 결정한 행동에 대한 소프트맥스 확률 값이다.)

        # 만약 행동이 유효하지 않다면
        # -> 행동이 유효하지 않는 경우 :
        #           1. 구매하려는데 주식 살 돈이 없을 때,
        #           2. 팔려고 하는데 팔 주식이 없을 때
        if not self.validate_action(action):
            action = Agent.ACTION_HOLD
            # 홀딩! 관망한다!

        # 환경에서 현재 주식 가격 얻기
        curr_price = self.environment.get_price()
        # 현재 에이전트가 처한 상태에서의 주가를 데이터에서 얻어 현재가에 넣어준다.

        # 즉시 보상 초기화
        self.immediate_reward = 0
        # 보상은 에이전트가 행동할 때마다 결정되기 때문에 초기화한다.
        # 따라서 보상은 행동할 때마다 달라지기 때문에
        # 매번 새로운 값을 받아들여야 한다.

        # 1. 매수, 2. 매도
        # 1. 만약 매수하는거면
        if action == Agent.ACTION_BUY:
            # 우선 얼마나 매수할 지를 자신감에 근거해 판단한다.
            # confidence = 0 -> 최소 단위
            # confidence = 1 -> 가능한 금액에 한해 풀매수 또는 풀매도
            trading_unit = self.decide_trading_unit(confidence)

            # 계좌 내 현금액은
            # 기존의 현금액 - 현재 주식가*(1+거래수수료)*거래할 단위
            # 로 갱신해준다.
            balance = (
                self.balance - curr_price * (1 + self.TRADING_CHARGE) \
                    * trading_unit
            )
            # 보유 현금이 모자랄 경우 보유 현금으로 가능한 만큼 최대한 매수
            if balance < 0:
                # 만약 그렇게 빼준 금액이 0보다 작으면
                trading_unit = max(
                    min(
                        int(self.balance / (
                            curr_price * (1 + self.TRADING_CHARGE))),
                        self.max_trading_unit
                    ),
                    self.min_trading_unit
                )
                # 거래 단위를 조정해주는데,
                # 계좌 현금액/(현재주가*(1+수수료))
                # 와
                # 최대 거래 단위
                # 사이의 최소값으로 지정해주고,
                # 그렇게 구해준 값과 최소 거래단위를 비교해
                # 그 둘 중 최대값을 거래할 단위로 넣어준다.

            # 수수료를 적용하여 총 매수 금액 산정
            invest_amount = curr_price * (1 + self.TRADING_CHARGE) \
                * trading_unit
            # 투자금으로는 현재가 * (1+거래수수료) * 거래 주식수
            # 를 해준다.
            # 이제 주식 수는 에이전트가 현재 상황에서 가능한 상태이다.
            # (불가능한 상태 다 걸러냄)

            # 투자금이 0보다 클 경우
            if invest_amount > 0:
                # 보유 현금에 투자금을 빼주어 갱신해주고,
                self.balance -= invest_amount  # 보유 현금을 갱신
                # 가진 주식 수에 거래 주식수를 더해주고,
                # 매수 횟수에 1 더해준다.
                self.num_stocks += trading_unit  # 보유 주식 수를 갱신
                self.num_buy += 1  # 매수 횟수 증가

        # 2. 만약 매도하는 거라면
        elif action == Agent.ACTION_SELL:
            # 매도할 단위를 판단
            # 얼마나 매도할 지 자신감에 근거해 판단한다.
            trading_unit = self.decide_trading_unit(confidence)
            # 보유 주식이 모자랄 경우 가능한 만큼 최대한 매도
            # 즉 가지고 있는 주식 모두 매도.
            trading_unit = min(trading_unit, self.num_stocks)
            # 매도
            # 그리고 투자 금액에
            # 현재가 * (1-거래세-거래수수료) * 판매할 주식 수
            # 를 하여 수수료를 제외한 판매금을 더해준다.
            invest_amount = curr_price * (
                1 - (self.TRADING_TAX + self.TRADING_CHARGE)) \
                    * trading_unit
            # 만약 invest_amount 가 0보다 크다면
            if invest_amount > 0:
                # 보유 주식 수에 거래한 주식 갯수를 빼주고,
                self.num_stocks -= trading_unit  # 보유 주식 수를 갱신
                # 계좌에 있는 현금에 투자금을 더해준다.
                self.balance += invest_amount  # 보유 현금을 갱신
                # 그리고 매도 횟수에 1을 더해준다.
                self.num_sell += 1  # 매도 횟수 증가

        # 홀딩
        elif action == Agent.ACTION_HOLD:
            # 홀드에 해당할 경우 홀드 횟수에 1을 더해준다.
            self.num_hold += 1  # 홀딩 횟수 증가

        # 포트폴리오 가치 갱신
        # 계좌 내 현금 + (현재 주가)*(가진 주식 수) = 포트폴리오 가치 (PV)
        self.portfolio_value = self.balance + curr_price \
            * self.num_stocks
        # 얼마나 손익/손해를 봤는지
        # (현재 포트폴리오 가치 - 초기 금액) / 초기 금액
        self.profitloss = (
            (self.portfolio_value - self.initial_balance) \
                / self.initial_balance
        )
        
        # 즉시 보상 - 수익률
        # 즉 즉시 보상으로 수익률을 준다.
        self.immediate_reward = self.profitloss

        # 지연 보상 - 익절, 손절 기준
        # 기준 대비 손익률 = (PV - 직전PV)/직전PV
        delayed_reward = 0
        self.base_profitloss = (
            (self.portfolio_value - self.base_portfolio_value) \
                / self.base_portfolio_value
        )
        # 만약 기준 대비 손익률이 역치(threshold)보다 크거나, -역치보다 작으면
        if self.base_profitloss > self.delayed_reward_threshold or \
            self.base_profitloss < -self.delayed_reward_threshold:
            # 목표 수익률 달성하여 기준 포트폴리오 가치 갱신
            # 또는 손실 기준치를 초과하여 기준 포트폴리오 가치 갱신

            # 현재 기준 PV를 현재 PV로 갱신해주고,
            # (만약 현재까지 보상을 받은 적이 없으면 기준PV는 곧 초기 금액(initial_balance)로 세팅되어 있음.
            self.base_portfolio_value = self.portfolio_value
            # 지연보상으로 손익률을 넣어준다. (보상 완료!)
            delayed_reward = self.immediate_reward
        else:
            # 만약 역치를 넘지 않으면 보상은 0
            # 그리고 기준PV는 바뀌지 않는다.
            delayed_reward = 0
        # 그렇게 구한 즉시 보상과 지연 보상을 넘겨준다.
        # 즉시 보상은 현재까지 쌓인 보상. -> 다음 단계로 넘겨줌
        # 지연 보상은 역치를 넘었을 때의 보상. -> 에이전트에 보상을 더해줌.
        return self.immediate_reward, delayed_reward

    # 즉 지연보상(delayed_reward)이 0이 아닐 때만 학습을 진행한다.
    # 학습을 진행하지 않을 경우는 즉시보상을 다음 단계로 넘어준다.
