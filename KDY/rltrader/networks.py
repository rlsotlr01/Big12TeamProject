import os
import threading
import numpy as np


class DummyGraph:
    def as_default(self): return self
    def __enter__(self): pass
    def __exit__(self, type, value, traceback): pass

def set_session(sess): pass


graph = DummyGraph()
sess = None

# 필요한 Keras 클래스를 모두 임포트한다.
# 백엔드가 tensorflow 이냐, plaidml 이냐에 따라
# 클래스나 모듈 명이 다르기에 이렇게 조건별로 따로 임포트 해준다.
if os.environ['KERAS_BACKEND'] == 'tensorflow':
    from tensorflow.keras.models import Model # 모델 객체를 담아주고
    from tensorflow.keras.layers import Input, Dense, LSTM, Conv2D, \
        BatchNormalization, Dropout, MaxPooling2D, Flatten # 필요한 층들을 가져오고
    from tensorflow.keras.optimizers import SGD # 최적화기, Stochastic Gradient Descent 가져온다.
    from tensorflow.keras.backend import set_session # 그리고 신경망을 시작해주는 함수 set_session 을 가져온다.
    import tensorflow as tf # 텐서플로우 가져오고
    graph = tf.get_default_graph()
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.compat.v1.Session(config=config)
elif os.environ['KERAS_BACKEND'] == 'plaidml.keras.backend':
    from keras.models import Model
    from keras.layers import Input, Dense, LSTM, Conv2D, \
        BatchNormalization, Dropout, MaxPooling2D, Flatten
    from keras.optimizers import SGD

# Network 클래스는 RLTrader 에서
# 신경망이 공통으로 가질 속성과 함수를 정의해놓은 클래스이다.
# 이 자체를 사용한다기 보단 DNN, LSTMNetwork, CNN 클래스가
# 해당 Network 클래스를 상속한다.
class Network:
    lock = threading.Lock()

    def __init__(self, input_dim=0, output_dim=0, lr=0.001, 
                shared_network=None, activation='sigmoid', loss='mse'):
        self.input_dim = input_dim
        # 인풋 값이 몇차원 값인지 설정
        self.output_dim = output_dim
        # 아웃풋의 차원수 설정 (매수와 매도일 경우 2로 설정)
        self.lr = lr
        # 학습율을 설정한다.
        self.shared_network = shared_network
        # 공유되는 신경망을 따로 지정해준다.
        self.activation = activation
        # 활성화 함수를 지정해준다
        self.loss = loss
        # 손실함수를 지정한다. (MSE, ASE, ...)
        self.model = None

    def predict(self, sample):
        with self.lock:
            with graph.as_default():
                if sess is not None:
                    set_session(sess)
                return self.model.predict(sample).flatten()

    def train_on_batch(self, x, y):
        loss = 0.
        with self.lock:
            with graph.as_default():
                if sess is not None:
                    set_session(sess)
                loss = self.model.train_on_batch(x, y)
                # 경사하강법을 실시한다.
        return loss
    # 그리고 손실값을 리턴한다.

    # 신경망 모델을 model_path 경로에 저장하는 함수
    def save_model(self, model_path):
        if model_path is not None and self.model is not None:
            # 가중치들을 저장한다. 덮어쓰기 허용
            self.model.save_weights(model_path, overwrite=True)

    # 신경망 모델을 model_path 경로에서 가져오는 함수
    def load_model(self, model_path):
        if model_path is not None:
            # 가중치를 불러온다.
            self.model.load_weights(model_path)

    # 신경망의 종류에 따라 공유 신경망을 획득하는 클래스 함수
    # DNN, LSTM, CNN 신경망의 공유 신경망을 생성하는 클래스 함수이다.
    @classmethod
    def get_shared_network(cls, net='dnn', num_steps=1, input_dim=0):
        with graph.as_default():
            if sess is not None:
                set_session(sess)
            if net == 'dnn':
                return DNN.get_network_head(Input((input_dim,)))
            elif net == 'lstm':
                return LSTMNetwork.get_network_head(
                    Input((num_steps, input_dim)))
            elif net == 'cnn':
                return CNN.get_network_head(
                    Input((1, num_steps, input_dim)))
    # dnn만 (?,)차원 데이터로 넣어주고, (input_dim,)
    # lstm은 (num_steps, input_dim) 차원 데이터로,
    # cnn 은 (1, num_steps, input_dim) 차원 데이터로 넣어줌.
    # cnn 은 3차원 데이터를 받아들이기 때문에 3차원 방식으로 넣어준다.

# Network 를 상속받아 심층 신경망을 구현한 DNN 클래스
class DNN(Network):
    # 생성자
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with graph.as_default():
            if sess is not None:
                set_session(sess)
            inp = None
            output = None
            if self.shared_network is None:
                inp = Input((self.input_dim,))
                output = self.get_network_head(inp).output
            else:
                inp = self.shared_network.input
                output = self.shared_network.output
            output = Dense(
                self.output_dim, activation=self.activation, 
                kernel_initializer='random_normal')(output)
            self.model = Model(inp, output)
            self.model.compile(
                optimizer=SGD(lr=self.lr), loss=self.loss)

    # DNN 클래스 : 신경망 구조 설정 클래스 함수
    @staticmethod
    def get_network_head(inp):
        # 인풋 - 256(시그모이드) - 드롭아웃(0.1) - 128(시그모이드) - 드롭아웃(0.1) - 64(시그모이드) - 드롭아웃(0.1) - 32(시그모이드) - 드롭아웃(0.1)
        # 그리고 중간중간 매 층마다 batchNormalization 을 넣어 학습을 안정화 함.
        # -> 배치 정규화는 은닉 레이어의 입력을 정규화해서 학습을 가속화한다.

        # 드롭아웃은 과적합을 어느정도 피하기 위함이다.

        output = Dense(256, activation='sigmoid', 
            kernel_initializer='random_normal')(inp)
        output = BatchNormalization()(output)
        output = Dropout(0.1)(output)
        output = Dense(128, activation='sigmoid', 
            kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = Dropout(0.1)(output)
        output = Dense(64, activation='sigmoid', 
            kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = Dropout(0.1)(output)
        output = Dense(32, activation='sigmoid', 
            kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = Dropout(0.1)(output)
        return Model(inp, output)

    # DNN 클래스 : 배치 학습 함수와 예측 함수
    # 배치 학습 함수와 predict 함수는
    # 샘플의 형태(shape)를 적절히 변경하고,
    # 상위 클래스의 함수를 호출합니다.
    def train_on_batch(self, x, y):
        # x : 배치 크기, y : 자질 벡터 차원
        x = np.array(x).reshape((-1, self.input_dim))
        # 인풋 모양으로 바꿔주고,
        return super().train_on_batch(x, y)
    # x,y 사이즈로 훈련시킨다.

    # predict 함수는 여러 샘플을 한꺼번에 받아서 신경망의 출력을 반환한다.
    def predict(self, sample):
        sample = np.array(sample).reshape((1, self.input_dim))
        # 인풋 모양으로 알아서 변경해주고,
        return super().predict(sample)
    # 상위 클래스의 예측 함수를 불러준다.
    

# LSTM 클래스
# Network 클래스를 상속해서 LSTM 신경망을 구현한 것이다.
class LSTMNetwork(Network):
    # 생성자
    def __init__(self, *args, num_steps=1, **kwargs):
        # num_steps 는 몇 개의 샘플을 묶어서 LSTM 신경망의 입력으로 사용할 지 결정하는 것이다.
        # 예를 들어 주식 데이터에서
        # num_steps 가 90이면 90일의 데이터로 그 다음날 주가를 예측하는 것이다.

        super().__init__(*args, **kwargs)
        with graph.as_default():
            if sess is not None:
                set_session(sess)
            self.num_steps = num_steps
            # 몇일 데이터로 다음날 걸 예측할지 설정한다.
            inp = None
            output = None
            # 인풋과 아웃풋을 초기화 해주고,
            if self.shared_network is None:
                inp = Input((self.num_steps, self.input_dim))
                # num_steps 차원의 길이의 input_dim 의 데이터를 input 으로 설정해준다.
                output = self.get_network_head(inp).output
                # get_network_head 를 통해 LSTM 신경망의 구조를 정한다.

            else:
                inp = self.shared_network.input
                # 만약 공유신경망이 존재한다면
                # 인풋을 공유신경망의 인풋 크기로 해주고,
                output = self.shared_network.output
                # 아웃풋을 공유신경망의 아웃풋 크기로 해준다.
            output = Dense(
                self.output_dim, activation=self.activation, 
                kernel_initializer='random_normal')(output)
            # 그리고 아웃풋 출력층을 만들어주고,
            self.model = Model(inp, output)
            #  해당 층으로 모델을 만들어준다.
            self.model.compile(
                optimizer=SGD(lr=self.lr), loss=self.loss)

    # 이 메소드를 수정함으로써 원하는 신경망을 만들 수 있다.
    @staticmethod
    def get_network_head(inp):
        # 256LSTM+DO(0.1) - 128LSTM+DO(0.1) - 64LSTM+DO(0.1) - 32LSTM+DO(0.1)
        output = LSTM(256, dropout=0.1, 
            return_sequences=True, stateful=False,
            kernel_initializer='random_normal')(inp)
        # 입력층으로 LSTM 층을 만들어주고,
        # 인풋 값으로 inp 즉 정해준 입력층을 넣어준다.
        output = BatchNormalization()(output)
        # 그리고 첫 LSTM 층에서 나온 값(LSTM의 output)은 배치 정규화를 해줘 계산을 가속한다.
        output = LSTM(128, dropout=0.1,
            return_sequences=True, stateful=False,
            kernel_initializer='random_normal')(output)
        # 그리고 그 다음 LSTM 층으로
        output = BatchNormalization()(output)
        output = LSTM(64, dropout=0.1,
            return_sequences=True, stateful=False,
            kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = LSTM(32, dropout=0.1,
            stateful=False,
            kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        return Model(inp, output)

    # 트레이닝 함수 (배치로 자동 전환 후 훈련을 해준다)
    def train_on_batch(self, x, y):
        x = np.array(x).reshape((-1, self.num_steps, self.input_dim))
        # input_dim 사이즈의 데이터를 num_steps 만큼 뭉탱이로 묶는다.
        return super().train_on_batch(x, y)
        # 그리고 뭉탱이로 훈련시킨다.

    # 값을 예측하는 함수
    def predict(self, sample):
        sample = np.array(sample).reshape(
            (1, self.num_steps, self.input_dim))
        # 샘플 값도 num_steps 뭉탱이로 묶어준다.
        return super().predict(sample)
        # 뭉탱이로 묶은 값으로 예측한다.

# CNN 클래스
class CNN(Network):
    # 생성자
    def __init__(self, *args, num_steps=1, **kwargs):
        super().__init__(*args, **kwargs)
        with graph.as_default():
            if sess is not None:
                set_session(sess)
            self.num_steps = num_steps
            inp = None
            output = None
            # 공유신경망이 따로 존재하지 않으면,
            # 주어진 조건으로 인풋층을 만들고, 아웃풋도 만든다.
            if self.shared_network is None:
                inp = Input((self.num_steps, self.input_dim, 1))
                output = self.get_network_head(inp).output
                # get_network_head 를 해주면 신경망이 만들어져 Model 이 생성된다.
            else:
                # 만약 존재한다면 공유신경망의 인풋과 아웃풋으로 inp, output 에 넣는다.
                # 인풋으로 신경망 모델을 넣어줄 경우
                inp = self.shared_network.input
                output = self.shared_network.output
            output = Dense(
                self.output_dim, activation=self.activation,
                kernel_initializer='random_normal')(output)

            self.model = Model(inp, output)
            # 모델을 해당 인풋층과 아웃풋층으로 만든다.
            self.model.compile(
                optimizer=SGD(lr=self.lr), loss=self.loss)
            # 해당 모델을 컴파일한다.
            # 그리고 최적화기로는 SGD로 쓰되, 학습율은 넣어준 lr로 넣어준다.
            # 그리고 손실함수도 입력해준 손실함수로 넣어준다.
            # 손실함수의 디폴트 값은 MSE 이다.

    # 이제 CNN 층을 만드는 함수이다.
    @staticmethod
    def get_network_head(inp):
        # 256(CNN, same, sigmoid) - 풀링(1/2) - 128(CNN, same, sigmoid) - 풀링(1/2) - 64(CNN, same, sigmoid)
        # - 풀링(1/2) - 32(CNN, same, sigmoid) - 풀링(1/2) - Flatten 한다.
        # 각 층 사이에 배치정규화와 드롭아웃층이 존재한다.
        output = Conv2D(256, kernel_size=(1, 5),
            padding='same', activation='sigmoid',
            kernel_initializer='random_normal')(inp)
        output = BatchNormalization()(output)
        output = MaxPooling2D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)
        output = Conv2D(128, kernel_size=(1, 5),
            padding='same', activation='sigmoid',
            kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = MaxPooling2D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)
        output = Conv2D(64, kernel_size=(1, 5),
            padding='same', activation='sigmoid',
            kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = MaxPooling2D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)
        output = Conv2D(32, kernel_size=(1, 5),
            padding='same', activation='sigmoid',
            kernel_initializer='random_normal')(output)
        output = BatchNormalization()(output)
        output = MaxPooling2D(pool_size=(1, 2))(output)
        output = Dropout(0.1)(output)
        output = Flatten()(output)
        return Model(inp, output)
    # 신경망 모델을 만들고 출력해준다.

    # 데이터 사이즈에 맞게 정제해서 훈련과 예측하는 함수

    def train_on_batch(self, x, y):
        x = np.array(x).reshape((-1, self.num_steps, self.input_dim, 1))
        return super().train_on_batch(x, y)

    def predict(self, sample):
        sample = np.array(sample).reshape(
            (-1, self.num_steps, self.input_dim, 1))
        return super().predict(sample)
