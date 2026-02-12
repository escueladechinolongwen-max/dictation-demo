import streamlit as st
import random
import asyncio
import edge_tts
import os

# --- 0. 手机端适配 CSS (更紧凑，字体更大) ---
st.markdown("""
<style>
    .stApp { background-color: #FFFDF5; }
    
    /* 手机上标题不要太大 */
    h1 { 
        color: #FF9AA2; 
        font-family: 'Comic Sans MS', sans-serif; 
        font-size: 28px !important; /* 强制改小一点适配手机 */
        text-align: center;
    }
    
    /* 输入框和按钮变大，方便手指点击 */
    .stTextInput input { 
        border-radius: 15px; 
        border: 2px solid #B5EAD7; 
        padding: 12px; 
        font-size: 18px; 
    }
    .stButton button { 
        width: 100%; /* 按钮在手机上撑满整行，更好点 */
        border-radius: 20px; 
        height: 50px;
        font-size: 18px !important;
    }

    /* 隐藏多余的菜单 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 1. 题库 (保持不变，您可以继续往里加) ---
DATABASE = {
    "hsk1_u1": ["你好", "谢谢", "不客气", "对不起"], 
    "hsk1_u2": ["你叫什么名字", "你是哪国人", "认识你很高兴"],
    "default": ["这是默认练习", "请检查网址参数"]
}

# --- 2. 获取参数 ---
query_params = st.query_params
current_unit_id = query_params.get("id", "default")
if current_unit_id in DATABASE:
    current_word_list = DATABASE[current_unit_id]
else:
    current_word_list = DATABASE["default"]

# --- 3. 语言包 ---
UI_TEXT = {
    "English": {
        "title": "🎈 Fun Dictation",
        "instruction": "Listen & Type",
        "submit": "✨ Check Answer",
        "next": "➡️ Next Sentence",
        "slow": "🐢 Slow Mode",
        "replay": "🔊 Replay Audio", # 新增重播按钮
        "settings": "⚙️ Settings (Level/Language)", # 新增设置折叠文案
        "correct": "🎉 Perfect!",
        "wrong": "🧸 Try again!"
    },
    "Español": {
        "title": "🎈 Dictado Divertido",
        "instruction": "Escucha y Escribe",
        "submit": "✨ Comprobar",
        "next": "➡️ Siguiente",
        "slow": "🐢 Modo Lento",
        "replay": "🔊 Escuchar de nuevo", # 新增重播按钮
        "settings": "⚙️ Configuración", # 新增设置折叠文案
        "correct": "🎉 ¡Perfecto!",
        "wrong": "🧸 ¡Casi!"
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
# 默认语言设为西班牙语，因为这是给您的学生用的
if 'user_lang' not in st.session_state:
    st.session_state.user_lang = "Español"

# --- 5. 语音功能 ---
async def generate_speech(text, rate="-10%"):
    voice = "zh-CN-XiaoxiaoNeural"
    if st.session_state.slow_mode:
        rate = "-35%"
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save("audio_temp.mp3")

def play_audio_logic(text):
    asyncio.run(generate_speech(text))
    st.audio("audio_temp.mp3", format="audio/mp3")

# --- 6. 界面构建 (针对手机优化的布局) ---

# A. 把“侧边栏”改成顶部的“折叠设置”，这样手机上一眼就能看到
with st.expander(UI_TEXT[st.session_state.user_lang]["settings"]):
    st.session_state.user_lang = st.selectbox("Idioma / Language", ["Español", "English"], index=0)
    st.caption(f"Current Unit ID: {current_unit_id}")

ui = UI_TEXT[st.session_state.user_lang]

st.title(ui["title"])

# B. 音频播放区
# 专门加一个“重播”按钮，解决手机不自动播放的问题
col_play, col_slow = st.columns([3, 1])
with col_play:
    if st.button(ui["replay"], type="secondary"):
        # 点击按钮强制触发播放
        play_audio_logic(st.session_state.current_sentence)
        
# 只有在初始化时尝试自动播放一次（电脑有效，手机可能无效）
if 'auto_played' not in st.session_state:
    play_audio_logic(st.session_state.current_sentence)
    st.session_state.auto_played = True

# C. 输入与反馈
with st.form("dictation"):
    user_input = st.text_input(ui["instruction"], key="input_field")
    submitted = st.form_submit_button(ui["submit"])

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
        
        # 红绿纠错
        html = "<div style='font-size:20px; letter-spacing:1px; text-align:center; margin-bottom:10px;'>"
        for i in range(max(len(clean), len(target))):
            if i < len(clean) and i < len(target):
                if clean[i] == target[i]:
                    html += f"<span style='color:#6B8E23; background:#E2F0CB; padding:2px;'>{clean[i]}</span>"
                else:
                    html += f"<span style='color:#CD5C5C; text-decoration:line-through;'>{clean[i]}</span>"
            elif i < len(clean):
                html += f"<span style='color:#CD5C5C; text-decoration:line-through;'>{clean[i]}</span>"
            else:
                html += "<span style='color:#aaa;'>_</span>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

# D. 底部操作区 (手机上会自动竖向排列)
# 我们不分两列了，直接竖着放，手指更容易点
if st.session_state.is_solved:
    if st.button(ui["next"], type="primary"):
        st.session_state.current_sentence = random.choice(current_word_list)
        st.session_state.is_solved = False
        st.session_state.mistake_count = 0
        st.session_state.slow_mode = False
        if 'auto_played' in st.session_state:
            del st.session_state.auto_played # 重置自动播放状态
        st.rerun()

# 慢速模式按钮
if st.session_state.mistake_count >= 3 and not st.session_state.is_solved:
    if st.button(ui["slow"]):
        st.session_state.slow_mode = True
        st.rerun()
