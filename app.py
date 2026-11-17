import os
import re
import time
import requests
import streamlit as st
import streamlit.components.v1 as components

# =========================================
# [改动6] Key 不再写死在源码里
# =========================================
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")   # 换模型只改环境变量

st.set_page_config(page_title="时空经纬", layout="wide")

if not API_KEY:
    st.error(
        "未检测到 DEEPSEEK_API_KEY 环境变量。请先执行：\n\n"
        "    export DEEPSEEK_API_KEY=\"sk-xxx\"\n"
        "    streamlit run app_修复版.py\n\n"
        "（原来写死在代码里的那个 key 已经随公开仓库泄露，务必去后台删掉重建。）"
    )
    st.stop()

# ==========================================
# 素材库
# ==========================================
bg1 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/qianli.png"
bg2 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/fuchun.png"
bg3 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/daolian.png"
logo_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/logo.png"
node_icon_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/timeline.png"
backtop_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/backtop.png"
search_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/search.png"

# ==========================================
# 全局 CSS（保持原样，内联渲染后仍然生效）
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
    div[data-testid="stHorizontalBlock"] button:active {{
        box-shadow: inset 5px 5px 10px rgba(0,0,0,0.1), inset -5px -5px 10px rgba(255,255,255,0.8) !important;
        transform: translateY(2px) !important;
    }}

    .stMarkdown table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background-color: rgba(255, 255, 255, 0.95) !important; border-radius: 10px; overflow: hidden; }}
    .stMarkdown th {{ background-color: #1C3A5E !important; color: white !important; padding: 12px; }}
    .stMarkdown td {{ border-bottom: 1px solid rgba(0,0,0,0.05); padding: 12px; color: #333 !important; }}

    .global-backtop {{ position: fixed; bottom: 40px; right: 40px; z-index: 9999; width: 50px; height: 50px; cursor: pointer; opacity: 0.8; }}

    /* [改动1] 时间轴卡片样式改走 class：内联渲染后由本页全局 CSS 控制，不受 iframe 隔离影响 */
    .tl-wrap {{ font-family: 'KaiTi', '思源黑体', sans-serif; }}
    .tl-title {{ font-size: 26px; font-weight: bold; color: #1C3A5E;
                 border-bottom: 2px solid rgba(210,180,140,0.5); padding-bottom: 15px; margin-bottom: 30px; }}
    .tl-row {{ display: flex; margin-bottom: 20px; align-items: flex-start; }}
    .tl-year {{ width: 110px; text-align: right; padding-right: 20px; font-weight: bold;
                color: #1C3A5E; font-size: 18px; padding-top: 15px; flex-shrink: 0; }}
    .tl-axis {{ width: 30px; display: flex; flex-direction: column; align-items: center;
                margin-right: 20px; flex-shrink: 0; }}
    .tl-axis img {{ width: 26px; height: 26px; margin-top: 10px; z-index: 2; object-fit: contain; }}
    .tl-axis .line {{ width: 2px; flex-grow: 1; background-color: rgba(150,150,150,0.4); min-height: 100px; }}
    .tl-card {{ background: rgba(255,255,255,0.95); border-radius: 15px; padding: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05); flex-grow: 1; border: 1px solid rgba(255,255,255,1); }}
    .tl-card .hd {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
    .tl-card .hd h3 {{ margin: 0; color: #1C3A5E; font-size: 22px; }}
    .tl-card .body {{ font-size: 15px; color: #333; line-height: 1.8; }}
    .tl-card .body b {{ color: #1C3A5E; }}
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
# [改动3/4/5] Prompt：格式铁律放 system，主题与条数放 user
# ==========================================
SYS_TIMELINE = """你是一个历史数据提取引擎，只输出数据行，不输出任何解释、标题、序号、代码块。
输出格式（每行一个事件，6 个字段用竖线 | 分隔）：
年份|事件名称|分类|背景|过程|影响
硬性约束：
1. 年份用数字；公元前写"公元前221"这种形式。
2. 分类只能从 政治 / 经济 / 文化 / 军事 中组合（如"政治+军事"）。
3. 背景、过程、影响各不超过 25 字，务必简短，把篇幅留给事件条数。
4. 必须输出指定条数，不允许少于要求；不要编造，不确定的事件宁可换成确实存在的史实。
"""

USER_TIMELINE_TMPL = """主题：{topic}
需要覆盖的时间阶段：{stage_desc}
请输出 {count} 个该阶段的核心历史事件，涵盖政治、经济、文化、军事。
直接输出 {count} 行数据，每行 6 个字段用竖线分隔。"""

# 三段划分：把一次"要 20 条"的压力拆成三次"要 8 条"
STAGES = [
    ("前期", "该时期的建立/兴起阶段，直到第一个重大转折为止"),
    ("中期", "该时期政权稳固后的发展阶段"),
    ("后期", "该时期的衰落、危机与终结阶段"),
]

PROMPT_COMPARE_SYS = """你是一名极其严谨的历史史料对比研究助手。
【防胡编乱造铁律】只引用真实存在的史书篇目；无法确认的写"存疑"。每条史料标注五级证据等级：
一级(同时代一手出土/传世文献) 二级(当代官方史书) 三级(后代官修正史) 四级(私家笔记) 五级(后世演绎)。
相互矛盾的记载必须并列呈现，不许自行调和。
【输出格式】依次给出两个 Markdown 表格：
### 史料档案表
| 史料名称 | 成书年代 | 证据等级 | 相关篇目 | 核心记载 |
### 逐维度对比表
| 对比维度 | 记载A | 记载B | 差异性质 | 可信度判断 |
只输出表格与必要的简短结论，不要开场白。"""

PROMPT_HYPOTHESIS_SYS = """你是一名严谨的历史学专家，进行客观的反事实推演。
必须基于真实史实，不许编造史实来支撑推演；每个推断注明依赖的条件与不确定性。
【输出格式】
一、事实基线与偏离点（约150字）
二、多情景逻辑推演（分短期10年内 / 中期数十年 / 长期百年以上）
三、逻辑边界与免责声明（约100字）
直接输出内容，不要开场白。"""


# =========================================
# [改动7] 请求层：限流与失败分开处理
# =========================================
def call_ai(system_prompt, user_prompt, max_tokens=8000, retries=2):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},   # [改动3] 不再只有 system
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.6,
        "max_tokens": max_tokens,
    }
    for attempt in range(retries + 1):
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=180)
            if resp.status_code == 429:                      # [改动7] 限额/限流单独提示
                if attempt < retries:
                    time.sleep(3 * (attempt + 1))
                    continue
                st.warning("⚠️ DeepSeek 触发限流(429)。这是平台配额限制，稍等十几秒重试即可；"
                           "若持续出现，说明本月额度已用完，需充值或更换模型。")
                return None
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            if attempt < retries:
                time.sleep(2)
                continue
            st.error(f"AI 请求失败: {e}")
            return None
    return None


# =========================================
# [改动2] 解析层：过滤污染行 + 公元前负数排序 + 去重
# =========================================
def parse_events(raw_text):
    if not raw_text:
        return []
    events, seen = [], set()
    for line in raw_text.splitlines():
        if "|" not in line:
            continue
        # 兼容 "| 618 | 李渊建唐 | ... |" 这种 Markdown 表格写法
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        cells = [c for c in cells if c != ""]      # 丢空列，避免字段整体右移一列
        if len(cells) < 6:
            continue
        head, fields = cells[0], cells[1:7]
        if re.fullmatch(r"[:\-\s]+", head):         # 分隔行 |---|---|
            continue
        if not re.search(r"\d", head):              # 表头行"年份|事件名称|..."
            continue
        m = re.search(r"\d+", head)
        if not m:
            continue
        num = int(m.group())
        is_bc = bool(re.search(r"(前|BCE|BC)", head, re.IGNORECASE))
        year_label = f"公元前{num}" if is_bc else str(num)
        key = (year_label, fields[0])
        if key in seen:                             # 三段结果合并去重
            continue
        seen.add(key)
        events.append({
            "year": year_label,
            "_k": -num if is_bc else num,
            "event": fields[0],
            "tags": fields[1],
            "background": fields[2],
            "process": fields[3],
            "impact": fields[4],
        })
    events.sort(key=lambda x: x["_k"])              # 公元前排在前，不会插到唐朝后面
    return events


# =========================================
# 导航（3D 按钮，逻辑不变）
# =========================================
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

# =========================================
# 内容区
# =========================================
if st.session_state.tab == "time":
    col1, col2 = st.columns([3, 1])
    with col1:
        timeline_input = st.text_input("请输入朝代或历史时期：", placeholder="如：唐朝、宋朝", key="in1")
    with col2:
        st.write(""); st.write("")
        generate_btn = st.button("🚀 生成时间轴", key="btn1")

    per_stage = st.slider("每阶段事件数（总数 = 3 × 该值）", 6, 12, 8, key="per_stage")

    if generate_btn and timeline_input:
        events = []
        bar = st.progress(0.0, text="AI 正在分段提取...")
        for i, (name, desc) in enumerate(STAGES, 1):
            with st.spinner(f"提取【{name}】事件..."):
                user_prompt = USER_TIMELINE_TMPL.format(topic=timeline_input, stage_desc=desc, count=per_stage)
                txt = call_ai(SYS_TIMELINE, user_prompt)
                got = parse_events(txt)
                events.extend(got)
                if not got:
                    st.warning(f"【{name}】这一段没解析到数据，可能模型这次没按格式输出。")
            bar.progress(i / len(STAGES), text=f"已完成 {i}/{len(STAGES)} 段，累计 {len(events)} 条")

        # 跨段去重后再排序
        uniq, seen2 = [], set()
        for e in events:
            k = (e["year"], e["event"])
            if k not in seen2:
                seen2.add(k)
                uniq.append(e)
        uniq.sort(key=lambda x: x["_k"])
        events = uniq

        if not events:
            st.error("没解析到任何事件。大概率是限流或格式跑偏，请再点一次；"
                     "若每次都是 0 条，把上面的报错信息截图发我。")
        else:
            st.success(f"✅ 成功提取 {len(events)} 个历史事件！")
            if len(events) < per_stage:
                st.info("提示：条数偏少通常是 token 配额或限流导致，可减少每阶段事件数，或换用更大配额的模型。")

            html_items = ""
            for e in events:
                tags = e.get("tags", "") or "综合"
                if "政治" in tags:
                    tag_bg = "rgba(135, 180, 220, 0.9)"
                elif "经济" in tags:
                    tag_bg = "rgba(220, 160, 135, 0.9)"
                else:
                    tag_bg = "rgba(150, 180, 150, 0.9)"
                html_items += f"""
                <div class="tl-row">
                    <div class="tl-year">{e['year']}年</div>
                    <div class="tl-axis">
                        <img src="{node_icon_url}" />
                        <div class="line"></div>
                    </div>
                    <div class="tl-card">
                        <div class="hd">
                            <h3>{e['event']}</h3>
                            <span style="background:{tag_bg}; color:white; padding:5px 14px; border-radius:20px; font-size:13px; font-weight:bold;">{tags}</span>
                        </div>
                        <div class="body">
                            <div><b>【背景】</b> {e.get('background') or '暂无'}</div>
                            <div><b>【过程】</b> {e.get('process') or '暂无'}</div>
                            <div><b>【影响】</b> {e.get('impact') or '暂无'}</div>
                        </div>
                    </div>
                </div>
                """

            page_html = f"""
            <div class="tl-wrap">
                <div class="tl-title">{timeline_input} 历史大事记</div>
                {html_items}
            </div>
            """
            

elif st.session_state.tab == "compare":
    st.subheader("多源史料互证与考证")
    compare_input = st.text_input("请输入要对比的历史事件：", placeholder="如：玄武门之变", key="in2")
    if st.button("⚖️ 开启史料对比", key="btn2") and compare_input:
        with st.spinner("AI 正在翻阅古籍..."):
            ai_text = call_ai(PROMPT_COMPARE_SYS, f"请对以下历史事件做多源史料深度对比：{compare_input}")
            if ai_text:
                st.markdown("---")
                st.markdown(ai_text)

elif st.session_state.tab == "hypothesis":
    st.subheader("反事实逻辑沙盘")
    hypothesis_input = st.text_input("请输入你的历史假设：", placeholder="如：如果安禄山没有造反", key="in3")
    if st.button("🔮 开启历史推演", key="btn3") and hypothesis_input:
        with st.spinner("AI 正在推演..."):
            ai_text = call_ai(PROMPT_HYPOTHESIS_SYS, f"我的历史假设是：{hypothesis_input}")
            if ai_text:
                st.markdown("---")
                st.markdown(ai_text)
