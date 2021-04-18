class Environment:
    PRICE_IDX = 4  # 종가의 위치

    # 생성자 (차트데이터를 넣는다. -> 환경이 차트데이터니깐.)
    def __init__(self, chart_data=None):
        # 차트 데이터를 받아온다. (아마 DataFrame 형태일 듯)
        self.chart_data = chart_data
        # observation 은 agent가 바라보는 현재 가격이다.
        # 즉 상태함수 = observation
        self.observation = None
        # 초기 인덱스 값을 -1로 준다.
        self.idx = -1

    # 값을 초기화한다. (시작과 끝에서 사용할 값)
    def reset(self):
        # AGENT 가 처한 상태를 초기화한다.
        self.observation = None
        # 인덱스도 초기화 해준다.
        self.idx = -1

    # 에이전트의 상태를 불러오는 get 함수이다.
    def observe(self):
        # 만약 차트데이터의 길이가 인덱스+1 보다 클 경우
        # (Out of index 방지)
        if len(self.chart_data) > self.idx + 1:
            # 인덱스에 +1 한다
            self.idx += 1
            # 해당 인덱스의 주가데이터를 불러온다. (상태 업데이트)
            self.observation = self.chart_data.iloc[self.idx]
            # 상태를 리턴한다.
            return self.observation
        # 만약 차트데이터 끝까지 다 했을 경우엔
        # None 을 출력한다.
        return None

    # 에이전트가 처한 상태에서의 주가 가격을 가져오는 get 함수
    def get_price(self):
        # 만약 에이전트가 상태 데이터를 가지고 있다면
        if self.observation is not None:
            # 가격데이터를 출력해준다.
            return self.observation[self.PRICE_IDX]
        # 에이전트가 상태 데이터를 갖고 있지 않다면 None 을 출력한다.
        return None

    # 차트데이터를 set 하는 세터메소드
    def set_chart_data(self, chart_data):
        # 차트데이터를 set 한다 (DataFrame)
        self.chart_data = chart_data
