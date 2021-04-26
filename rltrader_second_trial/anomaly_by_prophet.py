import warnings

warnings.filterwarnings(action='ignore')

import pandas as pd
import numpy as np
from fbprophet import Prophet
from tqdm import tqdm

import fipc

fipc.debug = False


def detect_anomaly(pred, y):
    """
    detect anomalies
    add columns anomaly, importance and score
    """
    andf = pred[['ds', 'trend', 'yhat', 'yhat_lower', 'yhat_upper']]
    andf['y'] = y

    andf['anomaly'] = 0
    andf.loc[andf['y'] > andf['yhat_upper'], 'anomaly'] = 1
    andf.loc[andf['y'] < andf['yhat_lower'], 'anomaly'] = -1

    andf['importance'] = 0
    andf.loc[andf['anomaly'] == 1, 'importance'] = \
        (andf['y'] - andf['yhat_upper']) / andf['y']
    andf.loc[andf['anomaly'] == -1, 'importance'] = \
        (andf['yhat_lower'] - andf['y']) / andf['y']

    # simply unified infomation flag and importance
    andf['score'] = andf['anomaly'] * andf['importance']

    return andf


def get_how_long_anomaly(values):
    how_long = 0
    values = values[::-1]  # rev
    for val in values:
        if val < 0:
            how_long += 1
        else:
            break
    return how_long


totits = fipc.get_tot_items()

topN = 5
itsscores = []
for fit in tqdm(np.random.choice(totits, 1000), desc='propheting...'):
    try:
        tsdf = fipc.get_tseries(itcode=fit, count=100)
        ppdf = pd.DataFrame({'ds': tsdf.index, 'y': tsdf['close']})

        # create Porphet instance
        m = Prophet()

        # train
        m = m.fit(ppdf)

        # predict
        future = m.make_future_dataframe(periods=0)
        pred = m.predict(future)

        # tag anomality
        andf = detect_anomaly(pred, ppdf['y'].values.tolist())

        is_anomaly_lastday = andf['score'].values[-1] < 0
        how_long_anomaly = get_how_long_anomaly(andf['score'].values)
        anodiff = andf['score'] - andf['score'].shift(1)

        if is_anomaly_lastday:
            if how_long_anomaly >= 3:
                if anodiff.values[-1] > 0:
                    itsscores.append((fit, andf['score'].values[-how_long_anomaly:].sum()))
    except Exception as e:
        print(e, fit)

if len(itsscores) > topN:
    itsscores.sort(key=lambda x: x[1])
    itsscores = itsscores[:topN]

# buy via itsscores
for it, _ in itsscores:
    price = fipc.get_curp(it)
    quantity = 1
    if quantity > 0:
        fipc.buy(it, quantity=quantity, price=price)
