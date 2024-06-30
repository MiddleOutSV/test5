import streamlit as st
import finnhub
from transformers import pipeline, MarianMTModel, MarianTokenizer
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

def summarize_news(news_list):
    summarizer = pipeline("summarization")
    summaries = []
    for news in news_list:
        try:
            # 뉴스 요약
            input_text = news['summary'] if news['summary'] else news['headline']
            max_length = min(len(input_text) // 2, 50)  # 입력 텍스트 길이에 따른 max_length 조정
            summary = summarizer(input_text, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']
        except Exception as e:
            summary = "요약을 생성하는 데 실패했습니다."
        summaries.append({"title": news['headline'], "summary": summary, "link": news['url']})
    return summaries

def translate_to_korean(text):
    model_name = 'Helsinki-NLP/opus-mt-en-ko'
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    
    translated = model.generate(**tokenizer(text, return_tensors="pt", padding=True))
    korean_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return korean_text

def main():
    st.title('주식 뉴스 요약 및 번역 앱')
    
    ticker = st.text_input('주식 Ticker를 입력하세요 (예: AAPL)')
    period = st.selectbox('기간을 선택하세요', ['1d', '1wk', '1mo'])
    
    if st.button('뉴스 가져오기'):
        with st.spinner('뉴스를 가져오는 중...'):
            news_list = fetch_news(ticker, period)
            if news_list:
                summaries = summarize_news(news_list)
                st.success('뉴스 가져오기 및 요약 완료!')
                
                for news in summaries:
                    st.subheader(news['title'])
                    st.write("요약:")
                    st.write(news['summary'])
                    korean_summary = translate_to_korean(news['summary'])
                    st.write("번역된 요약:")
                    st.write(korean_summary)
                    st.write(f"[링크]({news['link']})")

if __name__ == '__main__':
    main()
