import streamlit as st
import time
from gtts import gTTS
import io
import random

# --- 0. 魔法化妆间 (CSS样式设计) ---
# 这里是把界面变成“奶油童趣风”的关键代码
st.markdown("""
<style>
    /* 全局背景色 - 暖暖的奶油白 */
    .stApp {
        background-color: #FFFDF5;
    }
    
    /* 标题样式 - 圆润可爱 */
    h1 {
        color: #FF9AA2; /* 马卡龙粉 */
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
        text-shadow: 2px 2px #FFF0F5;
    }
    
    /* 输入框样式 - 圆角 */
    .stTextInput input {
        border-radius: 20px;
        border: 2px solid #B5EAD7; /* 马卡龙绿 */
        padding: 10px;
        font-size: 18px;
    }
    
    /* 按钮通用样式 - 圆角、阴影 */
    .stButton button {
        border-radius: 25px;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    
    /* 针对不同按钮的配色 */
    /* 提交按钮 (Form Submit) - 默认是主要按钮颜色 */
    
    /* 成功提示框 */
    .stSuccess {
        background-color: #E2F0CB;
        color: #556B2F;
        border-radius: 15px;
    }
    
    /* 错误提示框 */
    .stError {
        background-color: #FFB7B2;
        color: #8B0000;
        border-radius: 15px;
    }
    
</style>
""", unsafe_allow_html=True)

# --- 1. 题库配置 ---
QUESTION_BANK = {
    "Level 1 (Easy)": ["你好", "谢谢", "再见", "大熊猫", "我不吃肉"],
    "Level 2 (Medium)": ["今天天气真不错", "我想去图书馆", "你喜欢什么颜色", "我要喝一杯水"],
    "Level 3 (Hard)": ["吃葡萄不吐葡萄皮", "学习汉语需要坚持", "这个周末你有空吗"]
}

# --- 2. 界面语言包 ---
UI_TEXT = {
    "English": {
        "title": "🎈 Fun Dictation Time!",
        "instruction": "Listen & Type what you hear~",
        "play_btn": "▶️ Play Audio",
        "submit_btn": "✨ Check Answer",
        "correct_msg": "🎉 Correct! You are amazing!",
        "wrong_msg": "🧸 Oops! Not quite right.",
        "input_label": "Type your answer here:",
        "next_btn": "➡️ Next Sentence",
        "slow_ask": "Too fast? Try Slow Mode 🐢",
        "slow_btn": "🐢 Slow Mode On",
        "hint_green": "Green = Right",
        "hint_red": "Red = Wrong"
    },
    "Español": {
        "title": "🎈 ¡Tiempo de Dictado Divertido!",
        "instruction": "Escucha y escribe lo que oyes~",
        "play_btn": "▶️ Reproducir",
        "submit_btn": "✨ Comprobar",
        "correct_msg": "🎉 ¡Correcto! ¡Eres genial!",
        "wrong_msg": "🧸 ¡Vaya! Casi lo tienes.",
        "input_label": "Escribe tu respuesta:",
        "next_btn": "➡️ Siguiente Frase",
        "slow_ask": "¿Muy rápido? Prueba modo tortuga 🐢",
        "slow_btn": "🐢 Modo Lento",
        "hint_green": "Verde = Bien",
        "hint_red": "Rojo = Mal"
    }
}

# --- 3. 初始化状态 ---
if 'current_sentence' not in st.session_state:
    st.session_state.current_sentence = random.choice(QUESTION_BANK["Level 1 (Easy)"])
if 'mistake_count' not in st.session_state:
    st.session_state.mistake_count = 0
if 'slow_mode' not in st.session_state:
    st.session_state.slow_mode = False
if 'is_solved' not in st.session_state:
    st.session_state.is_solved = False # 标记当前题目是否已解决

# --- 4. 侧边栏 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712038.png", width=100) # 加个可爱的小图标
    language = st.selectbox("Language / Idioma", ["Español", "English"]) # 既然您主要用西语，我把西语放默认了
    difficulty = st.selectbox("Level / Nivel", list(QUESTION_BANK.keys()))
    
    if st.button("🔄 Change Level / Cambiar"):
        st.session_state.current_sentence = random.choice(QUESTION_BANK[difficulty])
        st.session_state.mistake_count = 0
        st.session_state.slow_mode = False
        st.session_state.is_solved = False
        st.rerun()

ui = UI_TEXT[language]

# --- 5. 功能函数 ---
def play_audio(text, slow=False):
    tts = gTTS(text=text, lang='zh-cn', slow=slow)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    # 这里的 key 是为了强制刷新播放器，否则换了音频它可能不更新
    st.audio(audio_fp, format='audio/mp3')

def color_diff(user_text, target_text):
    html_output = "<div style='font-size:24px; letter-spacing: 2px;'>"
    max_len = max(len(user_text), len(target_text))
    
    for i in range(max_len):
        if i < len(user_text) and i < len(target_text):
            u_char = user_text[i]
            t_char = target_text[i]
            if u_char == t_char:
                html_output += f"<span style='color:#6B8E23; background-color:#E2F0CB; padding:2px; border-radius:5px;'>{u_char}</span>"
            else:
                html_output += f"<span style='color:#CD5C5C; text-decoration:line-through; margin-right:5px;'>{u_char}</span>"
        elif i < len(user_text):
             html_output += f"<span style='color:#CD5C5C; text-decoration:line-through;'>{user_text[i]}</span>"
        else:
            html_output += f"<span style='color:#aaa; border-bottom: 2px dashed #aaa;'>__</span>"
    html_output += "</div>"
    return html_output

# --- 6. 主界面逻辑 ---

st.title(ui["title"])
st.caption(f"{ui['instruction']} (Level: {difficulty})")

# 播放器 (根据是否开启慢速模式变化)
if st.session_state.slow_mode:
    st.info(f"🐢 Slow Mode Active / Modo Lento Activo")
play_audio(st.session_state.current_sentence, slow=st.session_state.slow_mode)

# 表单区域
with st.form("dictation_box"):
    # 如果已经答对了，就清空输入框让它看起来像新的（通过 key 重新渲染）
    # 但由于 Streamlit 机制，我们用一个变量来控制显示
    user_input = st.text_input(ui["input_label"], key="input_field")
    submitted = st.form_submit_button(ui["submit_btn"])

# 表单提交后的逻辑（注意：这部分代码在 form 外面，这是为了解决那个报错）
if submitted:
    target = st.session_state.current_sentence.strip()
    clean_input = user_input.replace(" ", "").strip()
    
    if clean_input == target:
        st.session_state.is_solved = True
        st.session_state.mistake_count = 0
    else:
        st.session_state.is_solved = False
        st.session_state.mistake_count += 1

# --- 7. 反馈展示区 (在表单下方) ---

if submitted: # 只有点了提交才显示反馈
    if st.session_state.is_solved:
        st.balloons()
        st.success(ui["correct_msg"])
    else:
        st.error(ui["wrong_msg"])
        st.markdown(color_diff(user_input, st.session_state.current_sentence), unsafe_allow_html=True)
        st.caption(f"{ui['hint_green']} | {ui['hint_red']}")

# --- 8. 按钮控制区 (解决报错的关键：按钮全放在表单外面) ---

col1, col2 = st.columns(2)

with col1:
    # 只有答对了才显示“下一题”
    if st.session_state.is_solved:
        if st.button(ui["next_btn"], type="primary"):
            st.session_state.current_sentence = random.choice(QUESTION_BANK[difficulty])
            st.session_state.is_solved = False
            st.session_state.mistake_count = 0
            st.session_state.slow_mode = False
            st.rerun()

with col2:
    # 只有错了 5 次以上，且还没答对，才显示“慢速模式”
    if st.session_state.mistake_count >= 5 and not st.session_state.is_solved:
        st.warning(ui["slow_ask"])
        if st.button(ui["slow_btn"]):
            st.session_state.slow_mode = True
            st.rerun()

# 底部调试信息 (上线时可以删掉)
# st.divider()
# st.write(f"Debug: Mistakes={st.session_state.mistake_count}, Slow={st.session_state.slow_mode}")
