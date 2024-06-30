import streamlit as st
import finnhub
from transformers import pipeline

# Finnhub API 키 설정 (Secrets에서 불러오기)
finnhub_api_key = st.secrets["finnhub"]["api_key"]
finnhub_client = finnhub.Client(api_key=finnhub_api_key)

def fetch_news(ticker):
    # 뉴스 가져오기
    news = finnhub_client.company_news(ticker, _from="2022-01-01", to="2024-12-31")
    return news

def summarize_news(news_list):
    summarizer = pipeline("summarization")
    summaries = []
    for news in news_list:
        try:
            summary = summarizer(news['summary'], max_length=50, min_length=25, do_sample=False)[0]['summary_text']
        except Exception as e:
            summary = "요약을 생성하는 데 실패했습니다."
        summaries.append({"title": news['headline'], "summary": summary, "link": news['url']})
    return summaries

def main():
    st.title('주식 뉴스 요약 앱')
    
    ticker = st.text_input('주식 Ticker를 입력하세요 (예: AAPL)')
    
    if st.button('뉴스 가져오기'):
        with st.spinner('뉴스를 가져오는 중...'):
            news_list = fetch_news(ticker)
            if news_list:
                summaries = summarize_news(news_list)
                st.success('뉴스 가져오기 완료!')
                
                for news in summaries:
                    st.subheader(news['title'])
                    st.write(news['summary'])
                    st.write(f"[링크]({news['link']})")

if __name__ == '__main__':
    main()
