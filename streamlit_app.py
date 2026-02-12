import streamlit as st
import time
from gtts import gTTS  # 这是一个免费的谷歌文字转语音库
import io

# --- 1. 初始化“大脑”（设置变量） ---
if 'count' not in st.session_state:
    st.session_state.count = 0  # 计数器：记录重复了几次
if 'target_sentence' not in st.session_state:
    st.session_state.target_sentence = "今天天气真不错"  # 这里模拟从知识库调取的句子
if 'slow_mode' not in st.session_state:
    st.session_state.slow_mode = False # 默认不是慢速
if 'success' not in st.session_state:
    st.session_state.success = False

# --- 2. 定义功能函数 ---

# 播放语音的函数
def play_audio(text, slow=False):
    # 使用 gTTS 生成语音
    tts = gTTS(text=text, lang='zh-cn', slow=slow)
    # 把音频存入内存文件
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    # 在界面上显示播放器
    st.audio(audio_fp, format='audio/mp3', start_time=0)

# 核心逻辑：检查作业
def check_answer():
    user_input = st.session_state.user_input_text
    target = st.session_state.target_sentence
    
    if user_input == target:
        st.session_state.success = True
        st.balloons() # 放个气球庆祝一下
        st.success(f"完全正确！答案是：{target}")
    else:
        st.session_state.count += 1 # 错误次数 +1
        st.session_state.success = False
        
        # 找出是哪个字错了 (简单的比对逻辑)
        diff_msg = ""
        min_len = min(len(user_input), len(target))
        for i in range(min_len):
            if user_input[i] != target[i]:
                diff_msg += f"第 {i+1} 个字不对 (你输入的是'{user_input[i]}')。 "
                break # 找到第一个错字就停，避免打击学生
        
        if len(user_input) != len(target):
            diff_msg += "字数也不对哦。"
            
        st.error(f"还不对：{diff_msg} 请再听一遍。")

# 开启慢速模式的函数
def activate_slow_mode():
    st.session_state.slow_mode = True
    st.session_state.count = 0 # 重置计数，给学生新机会
    st.rerun() # 刷新页面

# --- 3. 界面布局 (UI) ---

st.title("🎧 智能听写练习 (原型演示)")

st.write(f"当前任务：请听写句子 (调试信息: 目标句子是 '{st.session_state.target_sentence}')")

# 显示音频播放器
# 如果在这里，我们会自动播放，并用 st.empty() 模拟 5秒倒计时
st.write("点击下方播放按钮开始听写：")
play_audio(st.session_state.target_sentence, slow=st.session_state.slow_mode)

if not st.session_state.success:
    # 模拟“每说完一遍，停顿5秒”的逻辑
    # 在Web应用中，这体现为给学生留出输入时间，或者我们可以做一个倒计时条
    
    with st.form("dictation_form"):
        st.text_input("请输入你听到的句子：", key="user_input_text")
        submitted = st.form_submit_button("提交检查")
        
        if submitted:
            check_answer()

# --- 4. 智能反馈逻辑 ---

# 如果错误次数超过 5 次，并且还没成功
if st.session_state.count >= 5 and not st.session_state.success:
    st.warning("⚠️ 看起来这个句子有点难，你已经试了 5 次了。")
    st.write("是否需要开启 **慢速模式 (Slow Mode)** 来帮你听清卡壳的字？")
    
    if st.button("是的，请慢读"):
        activate_slow_mode()

# 显示当前状态 (调试用)
st.divider()
st.caption(f"当前错误次数: {st.session_state.count} | 模式: {'慢速' if st.session_state.slow_mode else '常速'}")
