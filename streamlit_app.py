import streamlit as st
import time
from gtts import gTTS
import io
import random

# --- 1. 配置区：这里就是您的“题库” ---
# 您可以在这里无限添加句子
QUESTION_BANK = {
    "Level 1 (Easy)": [
        "你好", 
        "谢谢", 
        "再见", 
        "我不吃肉"
    ],
    "Level 2 (Medium)": [
        "今天天气真不错", 
        "我想去图书馆看书", 
        "这个周末你有空吗"
    ],
    "Level 3 (Hard)": [
        "吃葡萄不吐葡萄皮", 
        "学习汉语需要每天坚持练习", 
        "这个智能体真的非常方便"
    ]
}

# --- 2. 界面语言包 (English & Spanish) ---
UI_TEXT = {
    "English": {
        "title": "🎧 Smart Dictation Agent",
        "instruction": "Listen to the audio and type what you hear.",
        "play_btn": "Play Audio",
        "submit_btn": "Check Answer",
        "correct": "Correct! Well done.",
        "wrong": "Incorrect. Look at the colors below:",
        "input_label": "Type here:",
        "difficulty": "Select Difficulty",
        "slow_mode_ask": "Too difficult? Need slow mode?",
        "slow_mode_btn": "Yes, Slow Mode please",
        "retry_msg": "Try again.",
        "hint_green": "Green = Correct",
        "hint_red": "Red = Wrong/Missing"
    },
    "Español": {
        "title": "🎧 Agente de Dictado Inteligente",
        "instruction": "Escucha el audio y escribe lo que oyes.",
        "play_btn": "Reproducir Audio",
        "submit_btn": "Comprobar Respuesta",
        "correct": "¡Correcto! Muy bien.",
        "wrong": "Incorrecto. Mira los colores abajo:",
        "input_label": "Escribe aquí:",
        "difficulty": "Seleccionar Dificultad",
        "slow_mode_ask": "¿Muy difícil? ¿Necesitas modo lento?",
        "slow_mode_btn": "Sí, modo lento por favor",
        "retry_msg": "Inténtalo de nuevo.",
        "hint_green": "Verde = Correcto",
        "hint_red": "Rojo = Incorrecto/Falta"
    }
}

# --- 3. 初始化状态 ---
if 'current_sentence' not in st.session_state:
    st.session_state.current_sentence = random.choice(QUESTION_BANK["Level 1 (Easy)"])
if 'mistake_count' not in st.session_state:
    st.session_state.mistake_count = 0
if 'slow_mode' not in st.session_state:
    st.session_state.slow_mode = False

# --- 4. 侧边栏设置 ---
with st.sidebar:
    language = st.selectbox("Interface Language / Idioma", ["English", "Español"])
    difficulty = st.selectbox(UI_TEXT[language]["difficulty"], list(QUESTION_BANK.keys()))
    
    # 如果换了难度，自动换题
    if st.button("New Sentence / Nueva Frase"):
        st.session_state.current_sentence = random.choice(QUESTION_BANK[difficulty])
        st.session_state.mistake_count = 0
        st.session_state.slow_mode = False
        st.rerun()

ui = UI_TEXT[language] # 获取当前语言的文本字典

# --- 5. 核心功能函数 ---

def play_audio(text, slow=False):
    tts = gTTS(text=text, lang='zh-cn', slow=slow)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    st.audio(audio_fp, format='audio/mp3')

# 这是一个生成“红绿字”HTML的魔法函数
def color_diff(user_text, target_text):
    html_output = ""
    # 取两个句子中最长的长度
    max_len = max(len(user_text), len(target_text))
    
    for i in range(max_len):
        # 如果这个位置在两个句子里都有字
        if i < len(user_text) and i < len(target_text):
            u_char = user_text[i]
            t_char = target_text[i]
            if u_char == t_char:
                # 正确：绿色
                html_output += f"<span style='color:green; font-weight:bold; font-size:20px'>{u_char}</span>"
            else:
                # 错误：红色（显示用户打错的字）
                html_output += f"<span style='color:red; text-decoration:line-through; font-size:20px'>{u_char}</span>"
        elif i < len(user_text):
            # 用户打多了：红色
            html_output += f"<span style='color:red; text-decoration:line-through; font-size:20px'>{user_text[i]}</span>"
        else:
            # 用户漏打了：显示下划线或提示
            html_output += f"<span style='color:gray; font-size:20px'>_</span>"
            
    return html_output

# --- 6. 主界面 ---

st.title(ui["title"])
st.info(f"{ui['instruction']} (Difficulty: {difficulty})")

# 播放区
play_audio(st.session_state.current_sentence, slow=st.session_state.slow_mode)

# 输入区
with st.form("dictation_box"):
    user_input = st.text_input(ui["input_label"], key="input_field")
    submitted = st.form_submit_button(ui["submit_btn"])

    if submitted:
        target = st.session_state.current_sentence
        # 去掉空格，防止学生误打空格导致报错
        clean_input = user_input.replace(" ", "")
        
        if clean_input == target:
            st.balloons()
            st.success(ui["correct"])
            # 答对后，显示一个按钮去下一题
            if st.button("Next / Siguiente"):
                 st.session_state.current_sentence = random.choice(QUESTION_BANK[difficulty])
                 st.rerun()
        else:
            st.session_state.mistake_count += 1
            st.error(ui["wrong"])
            
            # 显示红绿比对
            diff_html = color_diff(clean_input, target)
            st.markdown(diff_html, unsafe_allow_html=True)
            st.caption(f"{ui['hint_green']} | {ui['hint_red']}")
            
            # 5次错误后的慢速模式逻辑
            if st.session_state.mistake_count >= 5:
                st.warning(ui["slow_mode_ask"])
                if st.form_submit_button(ui["slow_mode_btn"]):
                    st.session_state.slow_mode = True
                    st.rerun()
