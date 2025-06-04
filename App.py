import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

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

# 체력 수치 입력 (별도 분리 보장)
hp_input = {
    "인내력": a,
    "충성심": b,
    "속도": c,
    "체력": d
}["체력"]

# 결과 계산 버튼
if st.button("결과 계산"):
    upgrades = level - 1
    num_sim = 100_000  # 고정

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

    # 레벨당 상승량 계산
    inc_a = (a - 6) / upgrades if upgrades > 0 else 0
    inc_b = (b - 6) / upgrades if upgrades > 0 else 0
    inc_c = (c - 6) / upgrades if upgrades > 0 else 0
    inc_d = (d - 16) / upgrades if upgrades > 0 else 0

    # 출력
    st.success(f"📌 총합: {user_total}")
    st.info(f"💡 {'체력 제외 시 ' if exclude_hp else ''}상위 약 {total_percentile:.2f}% 에 해당합니다.")

    st.subheader("📈 개별 스탯 상위 % (+Lv당 증가량)")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric(a_stat, f"{a}", f"상위 {a_percentile:.2f}% (+{inc_a:.2f}/Lv)")
    col_b.metric(b_stat, f"{b}", f"상위 {b_percentile:.2f}% (+{inc_b:.2f}/Lv)")
    col_c.metric(c_stat, f"{c}", f"상위 {c_percentile:.2f}% (+{inc_c:.2f}/Lv)")
    col_d.metric(d_stat, f"{d}", f"상위 {d_percentile:.2f}% (+{inc_d:.2f}/Lv)")

    # 그래프
    st.subheader("🎯 Total Stat Distribution and Your Position")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(total_sim, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total, color='red', linestyle='--', label='Your Total')
    ax.set_title(f"{'Excl. HP ' if exclude_hp else ''}Stat Total Distribution")
    ax.set_xlabel("Total Stat")
    ax.legend()
    st.pyplot(fig)
