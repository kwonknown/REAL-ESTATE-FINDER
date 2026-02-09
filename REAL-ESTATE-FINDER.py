import streamlit as st
import pandas as pd
from PublicDataReader import TransactionPrice

# 1. 페이지 설정
st.set_page_config(page_title="노운's 부동산 탐지기", layout="wide")

st.title("🏠 권노운의 실거래가 기반 급매 탐지 대시보드")

# 2. 사용자 설정 (사이드바 - 자금 항목 세분화)
with st.sidebar:
    st.header("💰 내 자금 설정")
    salary = st.number_input("연봉 (원)", value=63300000)
    interest_rate = st.slider("대출 금리 (%)", 3.0, 7.0, 4.5)
    
    st.subheader("보유 자산 상세")
    my_cash = st.number_input("실제 보유 현금 (원)", value=100000000)
    severance_pay = st.number_input("퇴직금 중간정산 예상액 (원)", value=50000000)
    family_support = st.number_input("부모님 지원금 등 기타 (원)", value=50000000)
    
    total_cash = my_cash + severance_pay + family_support
    st.info(f"총 가용 현금: {total_cash/100000000:.2f}억 원")
    
    st.header("📍 관심 지역")
    # API 호출을 위해 법정동 코드가 필요하지만, 여기서는 검색어로 대체하는 로직 예시
    location = st.selectbox("지역 선택", ["노원구 중계동", "동대문구 휘경동", "구리시 인창동"])

# 3. DSR 기반 매수 가능 예산 계산
max_annual_pay = salary * 0.4
# 30년 만기 원리금균등상환 가정
estimated_max_loan = (max_annual_pay / 12) * 12 * 25 # 보수적 계산
buyable_price = estimated_max_loan + total_cash

st.success(f"✅ 권노운님의 최종 매수 가능 예산은 약 **{buyable_price/100000000:.2f}억 원**입니다.")

# 4. 실제 데이터 가져오기 로직
# 주의: 공공데이터포털에서 발급받은 인증키가 필요합니다.
service_key = st.secrets.get("SERVICE_KEY", "인증키를_입력하세요")

if service_key == "인증키를_입력하세요":
    st.warning("⚠️ 실제 데이터를 보려면 Streamlit Secrets에 SERVICE_KEY를 설정해야 합니다. 지금은 샘플을 보여드립니다.")
    # (기존 샘플 데이터 로직...)
    data = {
        '단지명': ['중계주공5단지', '휘경SK뷰', '구리더샵그리니티', '중계무지개'],
        '최근거래가': [780000000, 950000000, 820000000, 650000000],
        '전고점': [900000000, 1100000000, 950000000, 800000000]
    }
    df = pd.DataFrame(data)
else:
    # PublicDataReader 활용 (예시: 2024년 1월 데이터)
    api = TransactionPrice(service_key)
    # 실제 구현 시 시군구 코드 매핑이 필요합니다.
    df = api.get_data(property_type="아파트", trade_type="매매", sanc_year="2024", sanc_month="01")
    # 노운님이 선택한 지역(location)으로 필터링하는 로직 추가 필요

# 5. 결과 필터링 및 출력
df['하락률(%)'] = ((df['전고점'] - df['최근거래가']) / df['전고점'] * 100).round(1)
df['매수성공가능'] = df['최근거래가'] <= buyable_price

st.subheader(f"🔍 {location} 주변 분석 결과")
st.table(df) # 데이터를 정적으로 보여주려면 table, 인터랙티브하게 보려면 dataframe
