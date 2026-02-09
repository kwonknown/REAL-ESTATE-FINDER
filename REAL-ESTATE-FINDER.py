import streamlit as st
import pandas as pd
from PublicDataReader import TransactionPrice

# 1. 페이지 설정
st.set_page_config(page_title="노운's 부동산 탐지기", layout="wide")
st.title("🏠 권노운의 실거래가 기반 급매 탐지 대시보드")

# 시군구 코드 매핑 (PublicDataReader용)
SIGUNGU_CODES = {
    "서울 노원구": "11350",
    "서울 동대문구": "11230",
    "경기 구리시": "41310",
    "서울 강남구": "11680",
    "서울 송파구": "11710"
}

# 2. 사용자 설정 (사이드바)
with st.sidebar:
    st.header("💰 내 자금 설정")
    salary = st.number_input("연봉 (원)", value=63300000)
    interest_rate = st.slider("대출 금리 (%)", 3.0, 7.0, 4.5, 0.1)
    
    st.subheader("보유 자산 상세")
    my_cash = st.number_input("실제 보유 현금 (원)", value=100000000)
    severance_pay = st.number_input("퇴직금 예상액 (원)", value=50000000)
    family_support = st.number_input("기타 지원금 (원)", value=50000000)
    
    total_cash = my_cash + severance_pay + family_support
    
    st.header("📍 지역 선택")
    selected_loc = st.selectbox("조회할 시군구", list(SIGUNGU_CODES.keys()))
    target_year_month = st.text_input("조회 월 (YYYYMM)", value="202512")

    # 🚀 런칭 버튼 추가
    launch_button = st.button("🔍 데이터 분석 런칭", use_container_width=True)

# 3. 계산 로직 (버튼 클릭 전에도 상단 요약은 보여줌)
max_annual_pay = salary * 0.4
monthly_rate = (interest_rate / 100) / 12
total_months = 30 * 12
estimated_max_loan = (max_annual_pay / 12) * ((1 + monthly_rate)**total_months - 1) / (monthly_rate * (1 + monthly_rate)**total_months)
buyable_price = estimated_max_loan + total_cash

st.success(f"✅ 권노운님의 현재 매수 가능 예산은 약 **{buyable_price/100000000:.2f}억 원**입니다.")

# 4. 버튼 클릭 시 데이터 로드
if launch_button:
    service_key = st.secrets.get("SERVICE_KEY", None)
    
    if not service_key:
        st.warning("⚠️ SERVICE_KEY가 설정되지 않아 샘플 데이터를 표시합니다.")
        # 샘플 데이터 (실제 데이터와 형식을 맞춤)
        df = pd.DataFrame({
            '단지': ['중계주공5단지', '휘경SK뷰', '인창주공', '중계무지개'],
            '전용면적': [59, 84, 59, 59],
            '거래금액': [78000, 95000, 62000, 65000], # 만원 단위
            '층': [10, 15, 5, 8]
        })
    else:
        try:
            api = TransactionPrice(service_key)
            # 최신 버전 인터페이스 반영
            df = api.get_data(
                property_type="아파트",
                trade_type="매매",
                sigungu_code=SIGUNGU_CODES[selected_loc],
                year_month=target_year_month
            )
        except Exception as e:
            st.error(f"데이터 로드 실패: {e}")
            df = pd.DataFrame()

    # 5. 결과 시각화
    if not df.empty:
        st.subheader(f"📊 {selected_loc} ({target_year_month}) 실거래 분석")
        
        # 금액 단위 변환 및 필터링 (거래금액이 문자열로 올 수 있어 처리 필요)
        if '거래금액' in df.columns:
            # 매수 가능 여부 체크 (샘플 데이터 기준 만원 단위)
            df['매수성공가능'] = df['거래금액'] * 10000 <= buyable_price
            
            # 보기 좋게 하이라이트
            st.dataframe(df.style.applymap(
                lambda x: 'background-color: #d4edda' if x == True else '', 
                subset=['매수성공가능']
            ), use_container_width=True)
            
            # 평단가 분석 차트 등 추가 가능
            st.bar_chart(df.set_index('단지')['거래금액'])
    else:
        st.info("해당 기간에 거래 내역이 없습니다.")
