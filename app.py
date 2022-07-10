from doctest import ELLIPSIS_MARKER
import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title("株可視化アプリ")

st.sidebar.write("""
# 株可視化アプリ

以下のオプションから表示日数を指定してください。

""")  # このように、writeの中身をマークアップ記法で書くことも可能。

st.sidebar.write("""
## 表示日数選択
""")
days = st.sidebar.slider("日数", 1, 100, 20)  # daysに代入


st.write(f"""
### 過去 **{days}日間** の自社・他社株価
""")

# 株価取得関数


@st.cache  # 取得した値を保存
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():

        tkr = yf.Ticker(tickers[company])

        hist = tkr.history(period=f"{days}d")
        hist.index = hist.index.strftime("%d %B %Y")
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = "Name"

        df = pd.concat([df, hist])
    return df

# データ成形


def data_shape(df, companies):
    data = df.loc[companies]
    st.write("### 株価")
    st.dataframe(data.sort_index())

    data = data.T.reset_index()
    data = pd.melt(data, id_vars=['Date']).rename(
        columns={"value": "Stock Prices (Yen)"}
    )
    return data


try:
    # 株価の範囲を選択
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider(
        "範囲を選択", 0.0, 65000.0, (0.0, 10000.0)
    )

    # 株取得会社の一覧
    tickers = {
        'Keyence': '6861.T',
        'Omron': '6645.T',
        'Murata': '6981.T'
    }

    df = get_data(days, tickers)

    companies = st.multiselect(
        "会社名を選択してください",
        list(df.index),
        ["Keyence", "Omron", "Murata"]
    )

    if not companies:
        st.error("少なくとも一社は選択してください")
    else:
        data = data_shape(df, companies)

        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)  # clip=True:外に出ているデータを表示しない
            .encode(
                x="Date:T",  # :Tは時系列
                y=alt.Y("Stock Prices (Yen):Q", stack=None, scale=alt.Scale(
                  domain=[ymin, ymax])),  # :Q定量化, stack:積み上げ
                color="Name:N"
            )
        )

        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
      """
      Oops! Error has happened.
      """
    )
