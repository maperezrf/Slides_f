import pandas as pd
import plotly.express as px
from   datetime import timedelta, datetime
from calendar import monthrange
from data import var_f4
from general import generate_structure,  set_columns_sum, unif_colors, ord_mes
pd.set_option('display.max_columns', 500)

class F3():

    dt_string = datetime.now().strftime('%y%m%d')

    def __init__(self) -> None:
        