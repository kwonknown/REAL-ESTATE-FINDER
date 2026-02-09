import streamlit as st
import pandas as pd
from PublicDataReader import TransactionPrice

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="노운's 부동산 탐지기", layout="wide")
st.title("🏠 권노운의 부동산 매수 적정가 & 목표 비교기")

# 2. 지역 코드 데이터
REGION_DATA = {
    "서울특별시": {
        "노원구": "11350", "동대문구": "11230", "강남구": "11680", "송파구": "11710"
    },
    "경기도": {
        "구리시": "41310", "남양주시": "41360", "하남시": "41450"
    }
}

# 3. 사이드바 - 설정 영역
with st.sidebar:
    st.header("💰 자금 및 대출 설정")
    salary = st.number_input("연봉 (원)", value=63300000)
    interest_rate = st.slider("대출 금리 (%)", 3.0, 7.0, 4.5, 0.1)
    
    st.subheader("보유 자산 상세")
    my_cash = st.number_input("실제 보유 현금 (원)", value=100000000)
    severance_pay = st.number_input("퇴직금 예상액 (원)", value=50000000)
    family_support = st.number_input("기타 지원금 (원)", value=50000000)
    total_cash = my_cash + severance_pay + family_support
    
    st.divider()

    # 🎯 목표 매물 입력 칸 추가
    st.header("🎯 목표 매물 설정")
    target_item_name = st.text_input("목표 단지/매물명", value="휘경SK뷰")
    target_item_price = st.number_input("목표 매물 가격 (억 원)", value=8.5, step=0.1) * 100000000
    
    st.divider()
    
    st.header("📍 지역 및 기간 조회")
    selected_sido = st.selectbox("시/도 선택", list(REGION_DATA.keys()))
    sigungu_list = list(REGION_DATA[selected_sido].keys())
    selected_sigungu = st.selectbox("시/군/구 선택", sigungu_list)
    target_month = st.text_input("조회 월 (YYYYMM)", value="202512")

    launch_button = st.button("🚀 분석 실행", use_container_width=True)

# 4. 내 예산 계산 로직
max_annual_pay = salary * 0.4
monthly_rate = (interest_rate / 100) / 12
total_months = 30 * 12
if monthly_rate > 0:
    estimated_max_loan = (max_annual_pay / 12) * ((1 + monthly_rate)**total_months - 1) / (monthly_rate * (1 + monthly_rate)**total_months)
else:
    estimated_max_loan = (max_annual_pay / 12) * total_months

buyable_price = estimated_max_loan + total_cash

# 5. 메인 화면 - 목표 비교 대시보드
st.subheader(f"📊 {target_item_name} 매수 가능성 분석")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("내 매수 가능 예산", f"{buyable_price/100000000:.2f}억")
with col2:
    st.metric("목표 매물 가격", f"{target_item_price/100000000:.2f}억")
with col3:
    gap = target_item_price - buyable_price
    if gap <= 0:
        st.metric("자금 격차", "매수 가능", delta="🎯 목표 달성", delta_color="normal")
    else:
        st.metric("부족한 자금", f"{gap/100000000:.2f}억", delta=f"-{gap/100000000:.2f}억", delta_color="inverse")

if gap > 0:
    st.warning(f"💡 **{target_item_name}**을(를) 사려면 현재보다 **{gap/1000000:.0f}만 원**의 시드가 더 필요합니다.")
else:
    st.balloons()
    st.success(f"🎊 축하합니다! **{target_item_name}**은(는) 현재 예산으로 매수 가능한 범위에 있습니다.")

# 6. 실거래 데이터 분석 (기존 로직 유지)
if launch_button:
    # (이하 실거래 데이터 로드 및 출력 로직 생략 - 이전 코드와 동일하게 적용 가능)
    st.divider()
    st.write(f"🔍 {selected_sigungu}의 {target_month} 실거래 내역을 불러옵니다...")
    # ... (생략된 API 호출 로직)
