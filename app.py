import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="교통수단별 탄소배출 대시보드", page_icon="🌍", layout="wide")

# 2. 스타일 커스텀 (딥 포레스트 그린 & 파스텔 테마)
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #F9FCF9;
        border: 2px solid #A3C9AE;
        padding: 18px 22px;
        border-radius: 20px;
        box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.03);
    }
    section[data-testid="stSidebar"] { background-color: #F4F7F4; }
</style>
""", unsafe_allow_html=True)

st.title("🌍 장거리 여행 교통수단별 탄소발자국 대시보드")
st.markdown("여행의 이동 수단과 시간을 선택하여 탄소 예산을 확인해보세요.")
st.markdown("---")

# 3. 데이터 정의
ANNUAL_CARBON_BUDGET_KG = 5900.0
data = {
    "교통수단": ["지하철 / 전기열차", "고속열차 (KTX/SRT)", "시내버스", "고속/시외버스", "전기 승용차 (BEV)", "하이브리드 승용차", "가솔린 승용차", "디젤 승용차", "국내선 항공기"],
    "1km당 CO2 배출량(g)": [6, 14, 28, 33, 40, 90, 150, 170, 255],
    "평균시속(km/h)": [40, 200, 20, 80, 35, 35, 35, 35, 600],
    "카테고리": ["대중교통", "대중교통", "대중교통", "대중교통", "개인교통", "개인교통", "개인교통", "개인교통", "항공"]
}
df = pd.DataFrame(data)
df["1시간당 배출량(g)"] = df["평균시속(km/h)"] * df["1km당 CO2 배출량(g)"]

# 4. 사이드바 입력
st.sidebar.header("🚗 장거리 여행 계산기")
selected_transport = st.sidebar.selectbox("교통수단 선택:", df["교통수단"].tolist(), index=1)
time_hours = st.sidebar.slider("편도 이동 시간(시간):", 0.5, 6.0, 2.5, step=0.5)
frequency_per_trip = st.sidebar.slider("이용 횟수:", 1, 10, 2)

selected_row = df.loc[df["교통수단"] == selected_transport].iloc[0]
emission_per_hour = selected_row["1시간당 배출량(g)"]
total_emission_kg = (emission_per_hour * time_hours * frequency_per_trip) / 1000

# 5. 요약 매트릭스
st.subheader(f"📊 '{selected_transport}' 여행 탄소발자국 분석")
col1, col2, col3 = st.columns(3)
col1.metric("편도 1회 배출량", f"{(emission_per_hour * time_hours / 1000):,.1f} kg CO₂")
col2.metric("이번 여행 총 예상 배출량", f"{total_emission_kg:,.2f} kg CO₂")
col3.metric("상쇄 소나무", f"약 {(total_emission_kg / 6.6):,.2f} 그루")

st.markdown("---")

# 6. 예산 그래프 (원형)
col_l, col_r = st.columns(2)
with col_l:
    st.subheader("🎯 연간 허용량 대비 소진 비율")
    fig_pie = px.pie(values=[total_emission_kg, max(0, ANNUAL_CARBON_BUDGET_KG - total_emission_kg)], 
                     names=["사용량", "잔여"], color_discrete_sequence=["#34624C", "#F2C4B1"], hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_r:
    st.subheader("💡 예산 영향")
    st.write(f"이 여행으로 2030년 1인당 연간 목표 배출량의 **{(total_emission_kg / ANNUAL_CARBON_BUDGET_KG)*100:.2f}%**를 사용합니다.")
    st.progress(min(total_emission_kg / ANNUAL_CARBON_BUDGET_KG, 1.0))

st.markdown("---")

# 7. 전체 비교 그래프
st.subheader("💡 동일 시간 이동 시 전체 수단 비교")
df["비교배출량(g)"] = df["1시간당 배출량(g)"] * time_hours
fig_bar = px.bar(df.sort_values("비교배출량(g)"), x="비교배출량(g)", y="교통수단", color="카테고리", 
                 color_discrete_map={"대중교통":"#34624C", "개인교통":"#E0E8A5", "항공":"#F2C4B1"}, orientation='h')
st.plotly_chart(fig_bar, use_container_width=True)

# 8. 감축 효과 (오류 해결된 최종 버전)
st.subheader("🌱 친환경 열차 전환 시 감축 효과")
train_row = df.loc[df["교통수단"] == "고속열차 (KTX/SRT)"].iloc[0]
reduction_kg = total_emission_kg - (train_row["1시간당 배출량(g)"] * time_hours * frequency_per_trip / 1000)

if selected_transport in ["고속열차 (KTX/SRT)", "지하철 / 전기열차"]:
    st.markdown("<div style='background-color: #F8FCF8; border: 2px solid #A3C9AE; padding: 20px; border-radius: 18px; text-align: center;'>🎉 지구를 살리는 최고의 선택입니다!</div>", unsafe_allow_html=True)
else:
    st.success(f"🎉 동일 거리를 **'고속열차(KTX/SRT)'**로 전환 시, **{reduction_kg:,.2f} kg CO₂**를 줄일 수 있습니다!\n\n(연간 탄소 예산의 **{(reduction_kg / ANNUAL_CARBON_BUDGET_KG)*100:.2f}%** 절약 효과)")
    compare_df = pd.DataFrame({"구분": ["현재 선택", "고속열차 전환"], "배출량(kg)": [total_emission_kg, total_emission_kg - reduction_kg]})
    st.plotly_chart(px.pie(compare_df, names="구분", values="배출량(kg)", color_discrete_sequence=["#F2C4B1", "#A3C9AE"], hole=0.4), use_container_width=True)
