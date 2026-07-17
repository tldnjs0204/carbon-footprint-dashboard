import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="교통수단별 탄소배출 대시보드", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #F9FCF9; border: 2px solid #A3C9AE;
        padding: 18px 22px; border-radius: 20px;
        box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.03);
    }
    section[data-testid="stSidebar"] { background-color: #F4F7F4; }
</style>
""", unsafe_allow_html=True)

st.title("🌍 장거리 여행 교통수단별 탄소발자국 대시보드")
st.markdown("---")

data = {
    "교통수단": ["지하철 / 전기열차", "고속열차 (KTX/SRT)", "시내버스", "고속/시외버스", "전기 승용차 (BEV)", "하이브리드 승용차", "가솔린 승용차", "디젤 승용차", "국내선 항공기"],
    "1km당 CO2 배출량(g)": [6, 14, 28, 33, 40, 90, 150, 170, 255],
    "평균시속(km/h)": [40, 200, 20, 80, 35, 35, 35, 35, 600],
    "카테고리": ["대중교통", "대중교통", "대중교통", "대중교통", "개인교통", "개인교통", "개인교통", "개인교통", "항공"]
}
df = pd.DataFrame(data)
df["1시간당 배출량(g)"] = df["평균시속(km/h)"] * df["1km당 CO2 배출량(g)"]

st.sidebar.header("🚗 장거리 여행 계산기")
selected_transport = st.sidebar.selectbox("이용할 교통수단 선택:", df["교통수단"].tolist(), index=1)
time_hours = st.sidebar.slider("편도 이동 시간(시간):", 0.5, 6.0, 2.5, step=0.5)
frequency_per_trip = st.sidebar.slider("이용 횟수:", 1, 10, 2)

row = df.loc[df["교통수단"] == selected_transport].iloc[0]
total_emission_kg = (row["1시간당 배출량(g)"] * time_hours * frequency_per_trip) / 1000

c1, c2, c3 = st.columns(3)
c1.metric("편도 배출량", f"{(row['1시간당 배출량(g)'] * time_hours / 1000):,.1f} kg CO₂")
c2.metric("총 예상 배출량", f"{total_emission_kg:,.2f} kg CO₂")
c3.metric("상쇄 소나무", f"약 {(total_emission_kg / 6.6):,.2f} 그루")

st.markdown("---")
# 감축 효과 섹션 (로직 적용)
st.subheader("🌱 친환경 열차 전환 시 감축 효과")
if selected_transport in ["고속열차 (KTX/SRT)", "지하철 / 전기열차"]:
    st.markdown("<div style='background: #F8FCF8; border: 2px solid #A3C9AE; padding: 20px; border-radius: 20px;'>🎉 최고의 선택입니다!</div>", unsafe_allow_html=True)
else:
    reduction = total_emission_kg - (df.loc[df["교통수단"] == "고속열차 (KTX/SRT)", "1시간당 배출량(g)"].iloc[0] * time_hours * frequency_per_trip / 1000)
    st.success(f"🎉 고속열차로 전환 시 **{reduction:,.2f} kg CO₂**를 줄일 수 있습니다!")
    st.plotly_chart(px.pie(names=["현재", "전환"], values=[total_emission_kg, total_emission_kg - reduction], hole=0.4))
