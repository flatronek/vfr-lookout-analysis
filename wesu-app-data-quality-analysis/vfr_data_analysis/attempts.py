import pandas as pd
import numpy as np

# Próba detekcji skrętu szybowca operując na oknach w danych
# ZA WOLNE!

def check_turning_condition_vector(x, threshold):
    return int(np.abs(x.iloc[-1] - x.iloc[0]) > threshold)

def check_turning_contidion_df(ii, df, threshold):
    x_vec = df[df.columns[5]][ii]
    y_vec = df[df.columns[6]][ii]
    z_vec = df[df.columns[7]][ii]
    res = check_turning_condition_vector(x_vec, threshold) \
          + check_turning_condition_vector(y_vec, threshold) \
          + check_turning_condition_vector(z_vec, threshold)
    return res

def detect_turnings(data):
    window_size = 50
    threshold = 40
    df = data.df
    df['ii'] = range(len(df))
    res = pd.rolling_apply(df.ii, window_size, lambda x: check_turning_contidion_df(x, df, threshold))
