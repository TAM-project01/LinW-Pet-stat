import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.rcParams['font.family'] = 'DejaVu Sans'

# 페이지 설정
st.set_page_config(page_title="스탯 시뮬레이터", layout="centered")
st.title("📊펫 스탯 시뮬레이터")
st.markdown("""
레벨과 스탯 수치를 입력하면, 당신의 총합이 상위 몇 %인지 계산합니다.  
주 스탯을 포함한 **인내력, 충성심, 속도, 체력** 기준이며,  
**특기로 얻은 스탯은 제외하고 입력**해 주세요.
""")

# 종별 D 스탯 고정
d_stat_map = {
    "도베르만": "충성심",
    "비글": "속도",
    "셰퍼드": "인내력",
    "늑대": "체력"
}
stat_order = ["인내력", "충성심", "속도", "체력"]

# 종 선택
category = st.selectbox("🐶 견종 선택", list(d_stat_map.keys()))
d_stat = d_stat_map[category]
remaining_stats = [s for s in stat_order if s != d_stat]
a_stat, b_stat, c_stat = remaining_stats

# 체력 제외 모드
exclude_hp = st.checkbox("🛑 체력 스탯 제외하고 계산하기")

# 입력
col1, col2 = st.columns(2)
level = col1.number_input("레벨 (2 이상)", min_value=2, value=2, step=1)
a = col1.number_input(f"{a_stat} 수치", min_value=0, value=6, step=1)
b = col2.number_input(f"{b_stat} 수치", min_value=0, value=6, step=1)
c = col1.number_input(f"{c_stat} 수치", min_value=0, value=6, step=1)
d = col2.number_input(f"{d_stat} 수치", min_value=0, value=16, step=1)

# 결과 계산 버튼
if st.button("결과 계산"):
    upgrades = level - 1
    num_sim = 100_000

    # 확률 테이블
    ac_vals = [0, 1, 2, 3]
    ac_probs = [0.15, 0.5, 0.3, 0.05]
    d_vals = [1, 2, 3, 4, 5, 6, 7]
    d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

    # 시뮬레이션
    a_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    b_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    c_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    d_sim = 16 + np.random.choice(d_vals, (num_sim, upgrades), p=d_probs).sum(axis=1)

    # 어떤 스탯이 체력인지 파악
    hp_sim = {
        a_stat: a_sim,
        b_stat: b_sim,
        c_stat: c_sim,
        d_stat: d_sim
    }["체력"]

    # 총합 계산
    user_total = 0
    total_sim = np.zeros(num_sim)

    for stat_name, user_val, sim_val in zip(
        [a_stat, b_stat, c_stat, d_stat],
        [a, b, c, d],
        [a_sim, b_sim, c_sim, d_sim]
    ):
        if exclude_hp and stat_name == "체력":
            continue
        user_total += user_val
        total_sim += sim_val

    # 퍼센타일 계산
    total_percentile = np.sum(total_sim > user_total) / num_sim * 100

    a_percentile = np.sum(a_sim > a) / num_sim * 100
    b_percentile = np.sum(b_sim > b) / num_sim * 100
    c_percentile = np.sum(c_sim > c) / num_sim * 100
    d_percentile = np.sum(d_sim > d) / num_sim * 100

    # 평균 증가량 계산
    inc_a = (a - 6) / upgrades
    inc_b = (b - 6) / upgrades
    inc_c = (c - 6) / upgrades
    inc_d = (d - 16) / upgrades

   # 출력
st.success(f"📌 총합: {user_total}")
st.info(f"💡 {'체력 제외 시 ' if exclude_hp else ''}상위 약 {total_percentile:.2f}% 에 해당합니다.")

# ✅ 견종과 레벨 정보 표시
st.markdown(f"### 🐾 선택한 견종: **{category}** / 레벨: **{level}**")

st.subheader("📊 개별 스탯 요약 테이블")
data = {
    "스탯": [a_stat, b_stat, c_stat, d_stat],
    "현재 수치": [a, b, c, d],
    "상위 %": [f"{a_percentile:.2f}%", f"{b_percentile:.2f}%", f"{c_percentile:.2f}%", f"{d_percentile:.2f}%"],
    "Lv당 평균 증가량": [f"+{inc_a:.2f}", f"+{inc_b:.2f}", f"+{inc_c:.2f}", f"+{inc_d:.2f}"]
}
df = pd.DataFrame(data)
st.table(df)


    # 그래프
    st.subheader("🎯 Total Stat Distribution and Your Position")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(total_sim, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total, color='red', linestyle='--', label='Your Total')
    ax.set_title(f"{'Excl. HP ' if exclude_hp else ''}Stat Total Distribution")
    ax.set_xlabel("Total Stat")
    ax.legend()
    st.pyplot(fig)
