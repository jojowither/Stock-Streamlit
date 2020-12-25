from datetime import datetime

import plotly.graph_objs as go
import streamlit as st
import twstock
from plotly.subplots import make_subplots
from twstock import BestFourPoint, Stock

from stock import Stock_info


# 利用st.cache()快取沒有改變過的data
@st.cache()
def get_stock_data(stock_code, month):
    return Stock_info(stock_code, month).get_all_data()


# ---------------------------------- sidebar --------------------------------- #


st.sidebar.header('Parameter Setting')
stock_code = st.sidebar.text_input('Please input the stock code')
month = st.sidebar.number_input('from month...',
                                value=datetime.now().month - 3,
                                step=1,
                                max_value=12,
                                min_value=1)
data_colums = ['外資', '自營商', '投信', '成交量']
bubble_info = st.sidebar.selectbox('Bubble information', data_colums)
bubble_size = st.sidebar.number_input('Bubble Size', step=1, value=5)
sub_info = st.sidebar.selectbox('Sub information', data_colums)

# ----------------------------------- body ----------------------------------- #
st.title('股票資訊圖表')

# ----------------------------------- plot ----------------------------------- #

if stock_code and month:
    data = get_stock_data(stock_code, month)
    stock_name = twstock.codes[stock_code].name
    group = twstock.codes[stock_code].group
    start_date = twstock.codes[stock_code].start

    def iserror(func, *args, **kw):
        try:
            stock = func(*args, **kw)
            return stock
        except Exception:
            return True

    err_or_not = iserror(Stock, stock_code)  
    if err_or_not==True:
        st.warning('Can not load the stock analysis!')
    else:
        stock = err_or_not                        
        ma_p = stock.moving_average(stock.price, 5)       # 計算五日均價
        ma_c = stock.moving_average(stock.capacity, 5)    # 計算五日均量
        ma_p_cont = stock.continuous(ma_p)                # 計算五日均價持續天數
        ma_br = stock.ma_bias_ratio(5, 10)                # 計算五日、十日乖離值

        stock_name = twstock.codes[stock_code].name
        group = twstock.codes[stock_code].group
        start_date = twstock.codes[stock_code].start

        bfp = BestFourPoint(stock)
        tobuy = bfp.best_four_point_to_buy()     # 判斷是否為四大買點
        tosell = bfp.best_four_point_to_sell()   # 判斷是否為四大賣點
        _bfp = bfp.best_four_point()             # 綜合判斷

        st.success('Load data success!')

    
    if bubble_info!='成交量':
        trace1 = go.Scatter(x=data['日期'],
                            y=data['收盤價'],
                            mode='lines+markers',
                            marker=dict(size=data[bubble_info].abs(),
                                        sizeref=data[bubble_info].abs().mean() /
                                        bubble_size,
                                        color=data[f'{bubble_info}買賣顏色']),
                            line=dict(dash='dot'),
                            hovertemplate="<b>日期%{x}</b><br> 收盤價 %{y} " + f"{bubble_info} :" +
                            "%{marker.size}<br>",
                            name='收盤價')
    else:
        trace1 = go.Scatter(x=data['日期'],
                            y=data['收盤價'],
                            mode='lines+markers',
                            marker=dict(
                                size=data[bubble_info].abs(),
                                sizeref=data[bubble_info].abs().mean() /
                                bubble_size,
        ),
                            line=dict(dash='dot'),
                            hovertemplate="<b>日期%{x}</b><br> 收盤價 %{y}",
                            name='收盤價')

    trace2 = go.Bar(x=data['日期'],
                    y=data[f'{sub_info}'],
                    name=f'{sub_info}',
                    marker_color=data[f'{sub_info}買賣顏色'])

    fig = make_subplots(rows=2,
                        cols=1,
                        shared_xaxes=True,
                        row_heights=[0.7, 0.3])
    fig.add_trace(trace1, row=1, col=1)
    fig.add_trace(trace2, row=2, col=1)

    fig.update_layout(title=f'{stock_name}技術圖', template='plotly_dark')

    st.plotly_chart(fig)

    st.header('三大法人買賣超及股價基本資訊')
    st.dataframe(data)

