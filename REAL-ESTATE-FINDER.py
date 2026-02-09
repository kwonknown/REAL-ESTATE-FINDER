import streamlit as st
import pandas as pd
# !pip install PublicDataReader 로 설치 필요
from PublicDataReader import TransactionPrice

# 1. 페이지 설정
st.set_page_config(page_title="노운's 부동산 탐지기", layout="wide")

st.title("🏠 권노운의 실거래가 기반 급매 탐지 대시보드")

# 2. 사용자 설정 (사이드바)
with st.sidebar:
    st.header("💰 내 자금 설정")
    salary = st.number_input("연봉 (원)", value=63300000)
    interest_rate = st.slider("대출 금리 (%)", 3.0, 7.0, 4.5)
    cash_on_hand = st.number_input("보유 현금 (퇴직금 포함)", value=200000000)
    
    st.header("📍 관심 지역")
    location = st.selectbox("지역 선택", ["노원구 중계동", "동대문구 휘경동", "구리시 인창동"])

# 3. DSR 계산 로직 (이전 계산기 응용)
max_annual_pay = salary * 0.4
# (간단한 원리금 상환액 역산 로직 적용)
estimated_max_loan = (max_annual_pay / 12) * 12 * 20 # 단순화한 수치
buyable_price = estimated_max_loan + cash_on_hand

st.info(f"💡 현재 노운님의 매수 가능 예산은 약 **{buyable_price/100000000:.2f}억 원**입니다.")

# 4. 실거래 데이터 시뮬레이션 (API 연결 전 샘플 데이터)
# 실제 구현 시에는 PublicDataReader를 사용해 데이터를 프레임으로 만듭니다.
data = {
    '단지명': ['중계주공5단지', '휘경SK뷰', '구리더샵그리니티', '중계무지개'],
    '전용면적': [59, 84, 84, 59],
    '최근거래가': [780000000, 950000000, 820000000, 650000000],
    '전고점': [900000000, 1100000000, 950000000, 800000000]
}
df = pd.DataFrame(data)

# 5. 급매 및 예산 필터링
df['하락률(%)'] = ((df['전고점'] - df['최근거래가']) / df['전고점'] * 100).round(1)
df['매수성공가능'] = df['최근거래가'] <= buyable_price

st.subheader(f"🔍 {location} 주변 주요 단지 분석")
st.dataframe(df.style.highlight_max(axis=0, subset=['하락률(%)'], color='lightgreen'))

# 6. 시각화
st.bar_chart(df, x='단지명', y='하락률(%)')
