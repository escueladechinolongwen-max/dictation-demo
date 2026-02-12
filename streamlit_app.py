import streamlit as st
import random
import asyncio
import edge_tts
import os

# --- 0. 魔法化妆间 (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #FFFDF5; }
    h1 { color: #FF9AA2; font-family: 'Comic Sans MS', sans-serif; }
    .stTextInput input { border-radius: 20px; border: 2px solid #B5EAD7; padding: 10px; }
    .stButton button { border-radius: 25px; border: none; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }
    /* 隐藏顶部彩条和菜单 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 1. 超级题库 (这是重点！) ---
# 格式： "单元ID": ["句子1", "句子2", ...]
# 您可以把全书的句子都贴在这里
DATABASE = {
    # 单元 1 的练习
    "u1_s1": ["你好", "谢谢", "再见", "我不吃肉"],
    "u1_s2": ["今天天气真不错", "我想去图书馆", "我们要学习汉语"],
    
    # 单元 2 的练习
    "u2_s1": ["你喜欢什么颜色", "这件衣服多少钱", "太贵了"],
    "u2_s2": ["我要一杯咖啡", "不要加糖", "请给我发票"],
    
    # 默认兜底 (如果网址写错了就用这个)
    "default": ["这是默认练习", "请检查网址参数"]
}

# --- 2. 获取当前单元 ID ---
# 智能体通过读取网址末尾的 ?id=xxx 来决定出什么题
query_params = st.query_params
current_unit_id = query_params.get("id", "default") # 如果没填，就用 default

# 从题库里把这一个单元的句子拿出来
if current_unit_id in DATABASE:
    current_word_list = DATABASE[current_unit_id]
else:
    current_word_list = DATABASE["default"]

# --- 3. 语言包设置 ---
UI_TEXT = {
    "English": {
        "title": "🎈 Fun Dictation",
        "instruction": "Listen & Type!",
        "submit": "✨ Check",
        "next": "➡️ Next",
        "slow": "🐢 Slow Mode",
        "correct": "🎉 Perfect!",
        "wrong": "🧸 Try again!",
        "unit_info": "Current Unit:"
    },
    "Español": {
        "title": "🎈 Dictado Divertido",
        "instruction": "¡Escucha y Escribe!",
        "submit": "✨ Comprobar",
        "next": "➡️ Siguiente",
        "slow": "🐢 Modo Lento",
        "correct": "🎉 ¡Perfecto!",
        "wrong": "🧸 ¡Casi!",
        "unit_info": "Unidad Actual:"
    }
}

# --- 4. 状态初始化 ---
if 'current_sentence' not in st.session_state:
    st.session_state.current_sentence = random.choice(current_word_list)
if 'mistake_count' not in st.session_state:
    st.session_state.mistake_count = 0
if 'slow_mode' not in st.session_state:
    st.session_state.slow_mode = False
if 'is_solved' not in st.session_state:
    st.session_state.is_solved = False

# --- 5. 核心：真人级语音生成 (Edge-TTS) ---
async def generate_speech(text, rate="-10%"):
    # 声音选择：zh-CN-XiaoxiaoNeural (女声，温暖) 或者 zh-CN-YunxiNeural (男声，沉稳)
    voice = "zh-CN-XiaoxiaoNeural"
    # 如果是慢速模式，语速设为 -30%
    if st.session_state.slow_mode:
        rate = "-35%"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save("audio_temp.mp3")

def play_audio(text):
    # 运行异步生成函数
    asyncio.run(generate_speech(text))
    # 播放生成的音频
    st.audio("audio_temp.mp3", format="audio/mp3")

# --- 6. 界面构建 ---
with st.sidebar:
    language = st.selectbox("Language / Idioma", ["Español", "English"])
    # 显示当前是哪个单元，方便老师调试
    st.info(f"{UI_TEXT[language]['unit_info']} {current_unit_id}")

ui = UI_TEXT[language]

st.title(ui["title"])

# 播放音频
play_audio(st.session_state.current_sentence)

# 输入框
with st.form("dictation"):
    user_input = st.text_input(ui["instruction"], key="input_field")
    submitted = st.form_submit_button(ui["submit"])

# 逻辑判断
if submitted:
    target = st.session_state.current_sentence.strip()
    clean = user_input.replace(" ", "").strip()
    
    if clean == target:
        st.session_state.is_solved = True
        st.session_state.mistake_count = 0
        st.balloons()
        st.success(ui["correct"])
    else:
        st.session_state.is_solved = False
        st.session_state.mistake_count += 1
        st.error(ui["wrong"])
        
        # 红绿纠错显示
        html = "<div style='font-size:24px; letter-spacing:2px;'>"
        for i in range(max(len(clean), len(target))):
            if i < len(clean) and i < len(target):
                if clean[i] == target[i]:
                    html += f"<span style='color:#6B8E23; background:#E2F0CB;'>{clean[i]}</span>"
                else:
                    html += f"<span style='color:#CD5C5C; text-decoration:line-through;'>{clean[i]}</span>"
            elif i < len(clean):
                html += f"<span style='color:#CD5C5C; text-decoration:line-through;'>{clean[i]}</span>"
            else:
                html += "<span style='color:#aaa;'>_</span>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

# 按钮组
col1, col2 = st.columns(2)
with col1:
    if st.session_state.is_solved:
        if st.button(ui["next"], type="primary"):
            st.session_state.current_sentence = random.choice(current_word_list)
            st.session_state.is_solved = False
            st.session_state.mistake_count = 0
            st.session_state.slow_mode = False
            st.rerun()

with col2:
    if st.session_state.mistake_count >= 3 and not st.session_state.is_solved:
        if st.button(ui["slow"]):
            st.session_state.slow_mode = True
            st.rerun()
