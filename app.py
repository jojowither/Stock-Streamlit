from datetime import datetime

import plotly.graph_objs as go
import streamlit as st
import twstock
from plotly.subplots import make_subplots
from twstock import BestFourPoint, Stock

from stock import StockInfo


# 利用st.cache()快取沒有改變過的data
@st.cache()
def get_stock_info(stock_code, month):
    return StockInfo(stock_code, month)

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
# ---------------------------------------------------------------------------- #

st.title('股票資訊圖表')
if stock_code and month:
    stock_info = get_stock_info(stock_code, month)
    data = stock_info.get_all_data()

    stock_name = stock_info.stock_name
    st.markdown(f'# **{stock_name}**')
 
    if stock_info.err_or_not==True:
        st.warning('Can not load the stock analysis!')
    else:

        st.success('Load stock analysis success!')

        st.markdown(f'## 買賣建議')
        st.markdown(f'#### {stock_info._bfp[1]}')
        st.markdown(f'#### {"看多，建議買" if stock_info._bfp[0] else "看空，建議賣"}')
        st.text('')
        st.text('**投資一定有風險，基金投資有賺有賠，申購前應詳閱公開說明書。')
        st.markdown('---')
    

        st.header(f'股票資訊')
        ma_chart = go.Figure()
        ma_chart.add_trace(go.Scatter(x=stock_info.trade_date, 
                                    y=stock_info.ma5_p,
                                    marker=dict(color='#f37121'),
                                    hovertemplate='日期%{x}<br> MA5 %{y}',
                                    name='MA5'))
        ma_chart.add_trace(go.Scatter(x=stock_info.trade_date, 
                                    y=stock_info.ma10_p,
                                    marker=dict(color='#a7c5eb'),
                                    hovertemplate='日期%{x}<br> MA10 %{y}',
                                    name='MA10'))
        ma_chart.add_trace(go.Scatter(x=stock_info.trade_date, 
                                    y=stock_info.ma20_p,
                                    marker=dict(color='#b088f9'),
                                    hovertemplate='日期%{x}<br> MA20 %{y}',
                                    name='MA20'))
        ma_chart.update_layout(title='移動平均線圖', template='plotly_dark')
        st.plotly_chart(ma_chart)

    
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
                            marker=dict(size=data[bubble_info].abs(),
                                        sizeref=data[bubble_info].abs().mean() /
                                        bubble_size,),
                            line=dict(dash='dot'),
                            hovertemplate="<b>日期%{x}</b><br> 收盤價 %{y}",
                            name='收盤價')

    trace2 = go.Bar(x=data['日期'],
                    y=data[sub_info],
                    name=sub_info,
                    marker_color=data[f'{sub_info}買賣顏色'])

    fig = make_subplots(rows=2,
                        cols=1,
                        shared_xaxes=True,
                        row_heights=[0.7, 0.3])
    fig.add_trace(trace1, row=1, col=1)
    fig.add_trace(trace2, row=2, col=1)
    fig.update_layout(title='法人買賣技術圖', template='plotly_dark')
    st.plotly_chart(fig)

    st.header('三大法人買賣超及股價基本資訊')
    col_list = ['日期',	'外資',	'投信',	'自營商', '單日合計', '開盤價', '最高價', '最低價',
                '收盤價', '成交量']
    st.dataframe(data[col_list])

