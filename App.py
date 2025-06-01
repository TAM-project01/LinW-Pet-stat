import streamlit as st
import numpy as np

st.set_page_config(page_title="스탯 시뮬레이터", layout="centered")
st.title("📊 스탯 시뮬레이터")
st.markdown("단계와 스탯 수치를 입력하면, 당신의 총합이 상위 몇 %인지 계산합니다.")

# 사용자 입력
col1, col2 = st.columns(2)
stage = col1.number_input("단계 (2 이상)", min_value=2, value=2, step=1)
a = col1.number_input("A 수치", min_value=0, value=6, step=1)
b = col2.number_input("B 수치", min_value=0, value=6, step=1)
c = col1.number_input("C 수치", min_value=0, value=6, step=1)
d = col2.number_input("D 수치", min_value=0, value=16, step=1)

if st.button("결과 계산"):
    upgrades = stage - 1
    num_sim = 100_000

    ac_vals = [0, 1, 2, 3]
    ac_probs = [0.15, 0.5, 0.3, 0.05]
    d_vals = [1, 2, 3, 4, 5, 6, 7]
    d_probs = [0.05, 0.15, 0.3, 0.2, 0.15, 0.1, 0.05]

    a_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    b_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    c_sim = 6 + np.random.choice(ac_vals, (num_sim, upgrades), p=ac_probs).sum(axis=1)
    d_sim = 16 + np.random.choice(d_vals, (num_sim, upgrades), p=d_probs).sum(axis=1)

    total_sim = a_sim + b_sim + c_sim + d_sim
    user_total = a + b + c + d

    percentile_above = np.sum(total_sim > user_total) / num_sim * 100

    st.success(f"📌 입력한 총합: {user_total}\n")
    st.info(f"💡 상위 약 {percentile_above:.2f}% 에 해당합니다.")

    # 시각화
    st.subheader("시뮬레이션 결과 분포")
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(total_sim, bins=50, kde=True, ax=ax, color='skyblue')
    ax.axvline(user_total, color='red', linestyle='--', label='내 총합')
    ax.set_title("총합 분포와 나의 위치")
    ax.set_xlabel("스탯 총합")
    ax.legend()
    st.pyplot(fig)
