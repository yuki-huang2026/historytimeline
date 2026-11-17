import streamlit as st
import streamlit.components.v1 as components
import requests
import re

# =========================================
API_KEY = "sk-59f7ba787a4f46c7846157a043f463e9" 
# =========================================

API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-chat"

st.set_page_config(page_title="时空经纬", layout="wide")

# ==========================================
# 🔥 素材库
# ==========================================
bg1 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/qianli.png"
bg2 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/fuchun.png"
bg3 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/daolian.png"
logo_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/logo.png"
node_icon_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/timeline.png"
backtop_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/backtop.png"
search_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/search.png"

# ==========================================
# 🎨 顶级 CSS：3D 悬浮按钮
# ==========================================
st.markdown('<div id="top"></div>', unsafe_allow_html=True)

st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .stApp {{
        background-size: cover; background-position: center; background-attachment: fixed;
        animation: bgSlider 24s infinite;
    }}
    @keyframes bgSlider {{
        0%, 30% {{ background-image: url('{bg1}'); }}
        33%, 63% {{ background-image: url('{bg2}'); }}
        66%, 100% {{ background-image: url('{bg3}'); }}
    }}
    
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(245, 235, 210, 0.85); 
        z-index: -1;
    }}

    .main .block-container {{
        max-width: 1000px !important; margin: 0 auto !important;
        background-color: rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px); border-radius: 20px;
        padding: 2rem 3rem; margin-top: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1); border: 1px solid rgba(255,255,255,0.8);
    }}
    
    h1, h2, h3 {{ font-family: 'KaiTi', '思源黑体', sans-serif; color: #1C3A5E !important; }}
    
    /* 搜索框和普通按钮 */
    .stTextInput>div>div>input {{
        border-radius: 20px !important; background-color: rgba(255, 255, 255, 0.9) !important;
        background-image: url('{search_url}'); background-size: 20px;
        background-position: 12px center; background-repeat: no-repeat; padding-left: 40px !important;
    }}
    .stButton>button {{
        background-color: rgba(135, 180, 220, 0.8) !important; color: #1C3A5E !important;
        border-radius: 20px !important; border: none !important; font-weight: bold; width: 100%; transition: all 0.3s;
    }}
    .stButton>button:hover {{ background-color: rgba(100, 150, 200, 0.9) !important; color: white !important; }}
    
    /* 🔥 核心：把三个 Tab 按钮变成 3D 实体按键 */
    div[data-testid="stHorizontalBlock"] button {{
        background: linear-gradient(145deg, #ffffff, #e6e6e6) !important;
        color: #1C3A5E !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.8) !important;
        box-shadow: 5px 5px 10px rgba(0,0,0,0.1), -5px -5px 10px rgba(255,255,255,0.8) !important;
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 15px 0 !important;
        transition: all 0.1s ease !important;
    }}
    /* 按下去的凹陷效果 */
    div[data-testid="stHorizontalBlock"] button:active {{
        box-shadow: inset 5px 5px 10px rgba(0,0,0,0.1), inset -5px -5px 10px rgba(255,255,255,0.8) !important;
        transform: translateY(2px) !important;
    }}
    
    /* 表格白底 */
    .stMarkdown table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background-color: rgba(255, 255, 255, 0.95) !important; border-radius: 10px; overflow: hidden; }}
    .stMarkdown th {{ background-color: #1C3A5E !important; color: white !important; padding: 12px; }}
    .stMarkdown td {{ border-bottom: 1px solid rgba(0,0,0,0.05); padding: 12px; color: #333 !important; }}
    
    .global-backtop {{ position: fixed; bottom: 40px; right: 40px; z-index: 9999; width: 50px; height: 50px; cursor: pointer; opacity: 0.8; }}
    </style>
    
    <a href="#top"><img src="{backtop_url}" class="global-backtop" alt="回到顶部"></a>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
        <img src="{logo_url}" style="width: 60px; height: 40px; object-fit: contain; margin-right: 15px;">
        <h1 style="margin: 0; font-size: 40px;">时空经纬：数字人文历史助手</h1>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# 🔥 放弃 JSON，改用竖线文本！绝对不会截断！
# ==========================================
PROMPT_TIMELINE = """
你是一个历史数据提取引擎。请提取【{user_input}】至少 20 个核心历史事件！
不要偷懒，必须涵盖政治、经济、文化、军事，横跨早中晚三个时期！
请严格按照以下格式输出，每一行是一个事件，用竖线 | 分隔，不要输出任何序号，不要有任何废话：
年份|事件名称|分类|背景|过程|影响
618|李渊建唐|政治|隋末大乱|晋阳起兵|建立唐朝
626|玄武门之变|政治+军事|夺嫡之争|伏兵杀兄弟|太宗即位
（再次强调：必须给我列出 20 行这样的数据！）
"""

PROMPT_COMPARE = """
你是一名极其严谨的历史史料对比研究助手。请针对指定的历史事件，进行多源史料的深度对比。
【防胡编乱造铁律】标注五级证据等级。矛盾并列。
【输出格式】输出【史料档案表】和【逐维度对比表】，格式为 Markdown 表格。
事件是：【{user_input}】。直接输出结果。
"""

PROMPT_HYPOTHESIS = """
你是一名严谨的历史学专家。请围绕用户提出的历史假设进行客观的反事实推演。
【输出格式】
一、事实基线与偏离点（约150字）
二、多情景逻辑推演（短、中、长期）
三、逻辑边界与免责声明（约100字）
假设是：【{user_input}】。
"""

def call_ai(system_prompt):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME, 
        "messages": [{"role": "system", "content": system_prompt}], 
        "temperature": 0.7, 
        "max_tokens": 4000
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=180)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"AI 请求失败: {e}")
        return None

# ==========================================
# 🚀 使用 Session State 制作 3D 按钮导航
# ==========================================
if "tab" not in st.session_state:
    st.session_state.tab = "time"

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📅 AI 智能时间轴", use_container_width=True):
        st.session_state.tab = "time"
with col2:
    if st.button("⚖️ 史料互证", use_container_width=True):
        st.session_state.tab = "compare"
with col3:
    if st.button("🔮 假设互动", use_container_width=True):
        st.session_state.tab = "hypothesis"

st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.5); margin-bottom: 30px;'>", unsafe_allow_html=True)

# ==========================================
# 内容区
# ==========================================
if st.session_state.tab == "time":
    col1, col2 = st.columns([3, 1])
    with col1:
        timeline_input = st.text_input("请输入朝代或历史时期：", placeholder="如：唐朝、宋朝", key="in1")
    with col2:
        st.write(""); st.write("")
        generate_btn = st.button("🚀 生成时间轴", key="btn1")
    
    if generate_btn and timeline_input:
        with st.spinner("AI 正在深度提取 20 个事件..."):
            prompt = PROMPT_TIMELINE.replace("{user_input}", timeline_input)
            ai_text = call_ai(prompt)
            if ai_text:
                try:
                    # 🔥 暴力解析文本，彻底摆脱 JSON 报错
                    lines = ai_text.strip().split('\n')
                    events = []
                    for line in lines:
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 6:
                                year_num = re.search(r'\d+', parts[0])
                                year = str(int(year_num.group())) if year_num else "0"
                                events.append({
                                    "year": year,
                                    "event": parts[1].strip(),
                                    "tags": parts[2].strip(),
                                    "background": parts[3].strip(),
                                    "process": parts[4].strip(),
                                    "impact": parts[5].strip()
                                })
                    
                    events.sort(key=lambda x: int(x["year"]))

                    if len(events) == 0:
                        st.error("解析失败，AI 没有按竖线格式输出，请再点一次！")
                    else:
                        st.success(f"✅ 成功提取 {len(events)} 个历史事件！")

                        header_html = f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 2px solid rgba(210, 180, 140, 0.5); padding-bottom: 15px;">
                            <div style="font-size: 26px; font-weight: bold; color: #1C3A5E;">{timeline_input} 历史大事记</div>
                        </div>
                        """

                        html_items = ""
                        for e in events:
                            tags = e.get('tags', '')
                            tag_bg = "rgba(135, 180, 220, 0.9)" if "政治" in tags else "rgba(220, 160, 135, 0.9)" if "经济" in tags else "rgba(150, 180, 150, 0.9)"
                            
                            html_items += f"""
                            <div style="display: flex; margin-bottom: 20px; align-items: flex-start;">
                                <div style="width: 90px; text-align: right; padding-right: 20px; font-weight: bold; color: #1C3A5E; font-size: 18px; padding-top: 15px;">{e['year']}年</div>
                                <div style="width: 30px; display: flex; flex-direction: column; align-items: center; margin-right: 20px;">
                                    <img src="{node_icon_url}" style="width: 26px; height: 26px; margin-top: 10px; z-index: 2; object-fit: contain;" />
                                    <div style="width: 2px; flex-grow: 1; background-color: rgba(150, 150, 150, 0.4); min-height: 100px; z-index: 1;"></div>
                                </div>
                                <div style="background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); flex-grow: 1; border: 1px solid rgba(255,255,255,1);">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                        <h3 style="margin: 0; color: #1C3A5E; font-size: 22px;">{e['event']}</h3>
                                        <span style="background: {tag_bg}; color: white; padding: 5px 14px; border-radius: 20px; font-size: 13px; font-weight: bold;">{tags}</span>
                                    </div>
                                    <div style="font-size: 15px; color: #333; line-height: 1.8;">
                                        <div><strong style="color:#1C3A5E;">【背景】</strong> {e.get('background', '暂无')}</div>
                                        <div><strong style="color:#1C3A5E;">【过程】</strong> {e.get('process', '暂无')}</div>
                                        <div><strong style="color:#1C3A5E;">【影响】</strong> {e.get('impact', '暂无')}</div>
                                    </div>
                                </div>
                            </div>
                            """
                        
                        full_html = f"""
                        <!DOCTYPE html><html><head><meta charset="utf-8"></head>
                        <body style="margin:0; padding:10px; font-family: 'KaiTi', '思源黑体', sans-serif; background: transparent;">
                            {header_html}
                            <div style="max-width: 100%; margin: 0 auto;">{html_items}</div>
                            <script>
                                function resizeIframe() {{
                                    var height = document.body.scrollHeight;
                                    window.parent.postMessage({{ type: 'streamlit:setFrameHeight', height: height }}, '*');
                                }}
                                window.addEventListener('load', resizeIframe);
                                setTimeout(resizeIframe, 1000);
                            </script>
                        </body></html>
                        """
                        components.html(full_html, height=800, scrolling=False)
                except Exception as e:
                    st.error("解析出了点小错，再点一次！")

elif st.session_state.tab == "compare":
    st.subheader("多源史料互证与考证")
    compare_input = st.text_input("请输入要对比的历史事件：", placeholder="如：玄武门之变", key="in2")
    if st.button("⚖️ 开启史料对比", key="btn2") and compare_input:
        with st.spinner("AI 正在翻阅古籍..."):
            prompt = PROMPT_COMPARE.replace("{user_input}", compare_input)
            ai_text = call_ai(prompt)
            if ai_text:
                st.markdown("---")
                st.markdown(ai_text)

elif st.session_state.tab == "hypothesis":
    st.subheader("反事实逻辑沙盘")
    hypothesis_input = st.text_input("请输入你的历史假设：", placeholder="如：如果安禄山没有造反", key="in3")
    if st.button("🔮 开启历史推演", key="btn3") and hypothesis_input:
        with st.spinner("AI 正在推演..."):
            prompt = PROMPT_HYPOTHESIS.replace("{user_input}", hypothesis_input)
            ai_text = call_ai(prompt)
            if ai_text:
                st.markdown("---")
                st.markdown(ai_text)
