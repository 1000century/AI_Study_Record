import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.image("https://storage.googleapis.com/mle-courses-prod/users/61b6fa1ba83a7e37c8309756/private-files/678dadd0-603b-11ef-b0a7-998b84b38d43-ProtonX_logo_horizontally__1_.png", width=100)

def build_rotation_matrix(m, d):
    # d는 반드시 짝수여야 함 (2개씩 묶여 있음)
    assert d % 2 == 0, "Embedding dimension d must be even."
    theta = [10000 ** (-2 * k / d) for k in range(d // 2)]
    R = np.zeros((d, d))
    for k in range(d // 2):
        theta_k = m * theta[k]
        rot_matrix = np.array([
            [np.cos(theta_k), -np.sin(theta_k)],
            [np.sin(theta_k),  np.cos(theta_k)]
        ])
        R[2*k:2*k+2, 2*k:2*k+2] = rot_matrix
    return R

def generate_rotation_matrix_latex():
    latex_matrix = rf"""
    R(\theta) =
    \begin{{bmatrix}}
    \cos(m\theta) & -\sin(m\theta) \\
    \sin(m\theta) & \cos(m\theta)
    \end{{bmatrix}}
    """
    return latex_matrix

def generate_angular_distance_latex():
    latex_formula = r"""
    \theta_k = m \cdot 10000^{-2k/d}
    """
    return latex_formula

def apply_rope(embedding, position, d):
    R = build_rotation_matrix(position, d)
    rotated_embedding = R @ embedding
    return rotated_embedding

def visualize_embeddings(word, embedding, rotated_embedding, m):
    fig, ax = plt.subplots(figsize=(6,6))
    # 두 좌표씩 묶어 2차원 벡터로 시각화
    first_org = np.array(embedding[:2])
    second_org = np.array(embedding[2:])
    first_rot = np.array(rotated_embedding[:2])
    second_rot = np.array(rotated_embedding[2:])
    
    # 원래 벡터 그리기
    ax.quiver(0, 0, first_org[0], first_org[1], angles='xy', scale_units='xy', scale=1, color='blue', alpha=0.5, label='Original 0-1')
    ax.text(first_org[0], first_org[1], f'[{first_org[0]:.2f}, {first_org[1]:.2f}]', fontsize=8)
    ax.quiver(0, 0, second_org[0], second_org[1], angles='xy', scale_units='xy', scale=1, color='blue', alpha=0.5, label='Original 2-3')
    ax.text(second_org[0], second_org[1], f'[{second_org[0]:.2f}, {second_org[1]:.2f}]', fontsize=8)
    
    # 회전된 벡터 그리기
    ax.quiver(0, 0, first_rot[0], first_rot[1], angles='xy', scale_units='xy', scale=1, color='red', alpha=0.5, label='Rotated 0-1')
    ax.text(first_rot[0], first_rot[1], f'[{first_rot[0]:.2f}, {first_rot[1]:.2f}]', fontsize=8)
    ax.quiver(0, 0, second_rot[0], second_rot[1], angles='xy', scale_units='xy', scale=1, color='red', alpha=0.5, label='Rotated 2-3')
    ax.text(second_rot[0], second_rot[1], f'[{second_rot[0]:.2f}, {second_rot[1]:.2f}]', fontsize=8)
    
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.set_title(f"Vector Rotation for '{word}' (m={m})")
    ax.legend(fontsize=8)
    ax.grid(True)
    ax.set_aspect('equal')
    st.pyplot(fig)

st.markdown("### Rotary Position Embedding Visualization")

# 샘플 문장과 각 단어에 해당하는 임베딩 (행: 단어, 열: 임베딩 차원)
sentence = ["the", "cat", "sat", "on", "the", "mat"]
embeddings = np.array([
    [0.1, 0.2, -0.3, -0.4],
    [0.5, 0.6, 0.7, 0.8],
    [-0.25, 1.08, -0.52, 0.91],
    [0.4, 0.3, -0.2, 0.8],
    [0.2, 0.5, -0.1, 0.3],
    [0.5, 0.6, 0.7, 0.8]
])
d = embeddings.shape[1]  # 여기서는 4

st.markdown("Rotation Matrix")
st.latex(generate_rotation_matrix_latex())
st.latex(generate_angular_distance_latex())

# 단어 선택 (선택된 단어만 시각화 및 표로 출력)
if "selected_position" not in st.session_state:
    st.session_state.selected_position = 0

cols = st.columns(len(sentence))
for i, word in enumerate(sentence):
    if cols[i].button(word, key=f"word_button_{i}"):
        st.session_state.selected_position = i

selected_position = st.session_state.selected_position
selected_word = sentence[selected_position]
original_embedding = embeddings[selected_position]
rotated_embedding = apply_rope(original_embedding, selected_position, d)
visualize_embeddings(selected_word, original_embedding, rotated_embedding, selected_position)

# 선택된 단어에 대한 표 작성 (각 pair의 x, y를 별도 행으로)
table_md = """
| Pair Indices | Coordinate | Original | After ROPE | 계산식 | 세타 |
|--------------|------------|----------|------------|--------|------|
"""

for k in range(d // 2):
    # 각 pair에 대한 세타 계산 (같은 세타가 x, y 모두에 해당)
    theta_k = selected_position * (10000 ** (-2 * k / d))
    
    # x 좌표 행
    calc_formula_x = f"x' = cos({theta_k:.2f})*x - sin({theta_k:.2f})*y"
    table_md += f"| {2*k}-{2*k+1} | x | {original_embedding[2*k]:.2f} | {rotated_embedding[2*k]:.2f} | {calc_formula_x} | {theta_k:.2f} |\n"
    
    # y 좌표 행
    calc_formula_y = f"y' = sin({theta_k:.2f})*x + cos({theta_k:.2f})*y"
    table_md += f"| {2*k}-{2*k+1} | y | {original_embedding[2*k+1]:.2f} | {rotated_embedding[2*k+1]:.2f} | {calc_formula_y} | {theta_k:.2f} |\n"

st.markdown("### 선택된 단어의 임베딩 및 ROPE 적용 계산 과정 (좌표별 분리)")
st.markdown(table_md, unsafe_allow_html=True)

st.markdown("[Paper](https://arxiv.org/pdf/2104.09864v5)")
