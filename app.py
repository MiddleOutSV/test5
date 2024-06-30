import streamlit as st
import finnhub
from transformers import pipeline
from datetime import datetime, timedelta

# Finnhub API 키 설정 (Secrets에서 불러오기)
finnhub_api_key = st.secrets["finnhub"]["api_key"]
finnhub_client = finnhub.Client(api_key=finnhub_api_key)

def fetch_news(ticker, period='1d'):
    # 현재 날짜와 기간에 따른 날짜 계산
    to_date = datetime.today()
    if period == '1d':
        from_date = to_date - timedelta(days=1)
    elif period == '1wk':
        from_date = to_date - timedelta(weeks=1)
    elif period == '1mo':
        from_date = to_date - timedelta(weeks=4)
    
    # 날짜 형식 변환
    from_date_str = from_date.strftime('%Y-%m-%d')
    to_date_str = to_date.strftime('%Y-%m-%d')
    
    # 뉴스 가져오기
    news = finnhub_client.company_news(ticker, _from=from_date_str, to=to_date_str)
    return news

def summarize_news_combined(news_list):
    # 모델 지정 및 설정
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

    # 텍스트 분할 및 요약
    combined_text = ' '.join([news['summary'] if news['summary'] else news['headline'] for news in news_list])
    max_input_length = 512  # 모델이 한 번에 처리할 수 있는 최대 토큰 수
    input_texts = [combined_text[i:i+max_input_length] for i in range(0, len(combined_text), max_input_length)]
    
    summaries = []
    for input_text in input_texts:
        try:
            summary = summarizer(input_text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            summaries.append("요약을 생성하는 데 실패했습니다.")
    
    combined_summary = ' '.join(summaries)
    return combined_summary

def main():
    st.title('주식 뉴스 요약 앱')
    
    ticker = st.text_input('주식 Ticker를 입력하세요 (예: AAPL)')
    period = st.selectbox('기간을 선택하세요', ['1d', '1wk', '1mo'])
    
    if st.button('뉴스 가져오기'):
        with st.spinner('뉴스를 가져오는 중...'):
            news_list = fetch_news(ticker, period)
            if news_list:
                combined_summary = summarize_news_combined(news_list)
                st.success('뉴스 요약 완료!')
                st.write(combined_summary)

if __name__ == '__main__':
    main()
