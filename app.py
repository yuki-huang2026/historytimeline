import re
import requests
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# 1. 配置
# ============================================================
API_KEY = "sk-59f7ba787a4f46c7846157a043f463e9"
API_URL = "https://api.deepseek.com/chat/completions"
MODEL_NAME = "deepseek-chat"

st.set_page_config(page_title="时空经纬", layout="wide")

# ============================================================
# 2. 素材库
# ============================================================
bg1 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/qianli.png"
bg2 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/fuchun.png"
bg3 = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/daolian.png"
logo_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/logo.png"
node_icon_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/timeline.png"
backtop_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/backtop.png"
search_url = "https://cdn.jsdelivr.net/gh/yuki-huang2026/historytimeline@main/search.png"

# ============================================================
# 3. 页面样式
# ============================================================
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

    /* tab2 / tab3 正文白底：AI 输出的段落、列表、小标题、引用统一铺白卡片，
       与 tab1 表格白底观感一致。tab1 的大标题是 h1、时间轴走 iframe，均不受影响。 */
    .stMarkdown p, .stMarkdown ul, .stMarkdown ol, .stMarkdown blockquote,
    .stMarkdown h2, .stMarkdown h3 {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 0 0 8px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,1);
        color: #333 !important;
        line-height: 1.9;
    }}
    .stMarkdown h2, .stMarkdown h3 {{
        color: #1C3A5E !important;
        padding: 12px 18px;
        border-left: 5px solid rgba(135, 180, 220, 0.9);
    }}
    .stMarkdown li {{ color: #333 !important; line-height: 1.9; margin-bottom: 4px; }}
    .stMarkdown li::marker {{ color: #1C3A5E; }}
    .stMarkdown strong {{ color: #1C3A5E !important; }}
    /* 表格与正文卡片之间的间距收紧，整页拼起来更像一张完整的纸 */
    .stMarkdown table {{ margin: 6px 0 14px 0 !important; }}
    .stMarkdown code {{ background-color: rgba(255,255,255,0.95) !important; padding: 2px 6px; border-radius: 5px; }}


    .global-backtop {{ position: fixed; bottom: 40px; right: 40px; z-index: 9999; width: 50px; height: 50px; cursor: pointer; opacity: 0.8; }}
    </style>

    <a href="#top"><img src="{backtop_url}" class="global-backtop" alt="Back to top"></a>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
        <img src="{logo_url}" style="width: 60px; height: 40px; object-fit: contain; margin-right: 15px;">
        <h1 style="margin: 0; font-size: 40px;">时空经纬：数字人文历史助手</h1>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# 4. 提示词：system 定规则，user 给任务
# ============================================================
SYSTEM_TIMELINE = """你是历史数据提取引擎。只输出数据行，禁止输出任何解释、序号、标题、前言、代码块。

每行一个事件，6 个字段用竖线分隔：
年份|事件名称|分类|背景|过程|影响

硬性规则：
1. 年份写数字；公元前写成"前221"这种形式。
2. 分类只能取自 政治 / 经济 / 文化 / 军事，可用 + 组合。
3. 背景、过程、影响每项不超过 25 字，必须写实质内容，禁止写"暂无"。
4. 事件必须真实存在，时间要均匀覆盖指定阶段的早期、中期、晚期。
5. 上面那行字段名只是格式说明，绝对不要把它写进答案，直接从第一条数据开始输出。"""

SYSTEM_COMPARE = """你是严谨的历史史料对比研究助手。
【防胡编铁律】只引用真实存在的史料，不确定的一律标注"存疑"；记载冲突时并列呈现不同说法，不得强行调和。
每条史料标注五级证据等级：一手实物 / 一手文献 / 二手研究 / 后世追述 / 传说存疑。
【输出格式】
## 史料档案表
Markdown 表格，列：史料名称|成书年代|作者或来源|证据等级|核心记载|可信度说明
## 逐维度对比表
Markdown 表格，列：对比维度|说法A|说法B|学界倾向
## 结论
3 条要点。直接输出结果，不要寒暄。"""

SYSTEM_HYPOTHESIS = """你是严谨的历史学专家，请围绕用户提出的假设做客观的反事实推演，推理要有史料与逻辑支撑，不得虚构史实作为前提。
【输出格式】
## 一、事实基线与偏离点（约150字）
## 二、多情景逻辑推演（分短期1-5年、中期10-50年、长期百年以上）
## 三、逻辑边界与免责声明（约100字）
直接输出结果，不要寒暄。"""


def user_timeline(topic, stage, count):
    return "主题：%s\n目标阶段：%s\n请输出 %d 条属于%s（%s）的核心历史事件，兼顾政治、经济、文化、军事。" % (
        topic, stage, count, topic, stage)

# ============================================================
# 5. 调用大模型
# ============================================================
def call_ai(system_prompt, user_prompt, max_tokens=3000):
    headers = {"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "max_tokens": max_tokens,
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=180)
        if resp.status_code == 429:
            st.warning("接口触发限流（HTTP 429），请等待 30 秒后再点一次按钮。")
            return None
        if resp.status_code == 402:
            st.error("账户余额不足（HTTP 402），请到 DeepSeek 开放平台充值后重试。")
            return None
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error("AI 请求失败：%s" % e)
        return None

# ============================================================
# 6. 解析竖线文本：剔除表头行 / 分隔行 / 加粗符号
# ============================================================
def parse_events(text):
    events = []
    for raw in text.splitlines():
        line = raw.strip().strip("|").replace("**", "").replace(chr(96), "")
        if "|" not in line:
            continue
        if set(line) <= set("-:| "):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 6:
            continue
        head = parts[0]
        if any(w in head for w in ("年份", "年代", "时间", "Year", "year")):
            continue
        m = re.search(r"(\d+)", head)
        if not m:
            continue
        num = int(m.group(1))
        is_bc = ("前" in head) or bool(re.search(r"(?i)(bce|bc)", head))
        if is_bc:
            num = -num
        year_text = ("公元前%d" % abs(num)) if is_bc else str(num)
        events.append({
            "sort_key": num,
            "year_text": year_text,
            "event": parts[1],
            "tags": parts[2],
            "background": parts[3],
            "process": parts[4],
            "impact": parts[5],
        })
    return events


def merge_events(items):
    merged = {}
    for ev in items:
        merged.setdefault((ev["sort_key"], ev["event"]), ev)
    return sorted(merged.values(), key=lambda x: x["sort_key"])

# ============================================================
# 7. 导航
# ============================================================
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

# ============================================================
# 8. 内容区
# ============================================================
if st.session_state.tab == "time":
    col1, col2, col3 = st.columns([3, 1.2, 1])
    with col1:
        timeline_input = st.text_input("请输入朝代或历史时期：", placeholder="如：唐朝、宋朝", key="in1")
    with col2:
        per_stage = st.number_input("每阶段事件数", min_value=4, max_value=12, value=8, step=1, key="num1")
    with col3:
        st.write("")
        st.write("")
        generate_btn = st.button("🚀 生成时间轴", key="btn1")

    if generate_btn:
        if not timeline_input.strip():
            st.info("请先输入朝代或历史时期。")
        else:
            topic = timeline_input.strip()
            per = int(per_stage)
            collected = []
            with st.spinner("AI 正在分段提取 %s 的事件（前 / 中 / 晚期）..." % topic):
                for stage in ("早期", "中期", "晚期"):
                    text = call_ai(SYSTEM_TIMELINE, user_timeline(topic, stage, per))
                    if text:
                        collected.extend(parse_events(text))

            events = merge_events(collected)

            if not events:
                st.error("未能解析出事件。可能原因：接口限流，或模型未按格式输出。请重试一次。")
            else:
                st.success("✅ 成功提取 %d 个历史事件（去重后）" % len(events))

                header_html = (
                    '<div style="display:flex; justify-content:space-between; align-items:center;'
                    ' margin-bottom:30px; border-bottom:2px solid rgba(210,180,140,0.5); padding-bottom:15px;">'
                    '<div style="font-size:26px; font-weight:bold; color:#1C3A5E;">%s 历史大事记</div>'
                    '<div style="font-size:14px; color:#666;">共 %d 条</div></div>' % (topic, len(events))
                )

                html_items = ""
                for e in events:
                    tags = e["tags"]
                    if "政治" in tags:
                        tag_bg = "rgba(135, 180, 220, 0.9)"
                    elif "经济" in tags:
                        tag_bg = "rgba(220, 160, 135, 0.9)"
                    else:
                        tag_bg = "rgba(150, 180, 150, 0.9)"

                    html_items += f"""
                    <div style="display:flex; margin-bottom:20px; align-items:flex-start;">
                        <div style="width:110px; text-align:right; padding-right:20px; font-weight:bold;
                                    color:#1C3A5E; font-size:18px; padding-top:15px;">{e['year_text']}年</div>
                        <div style="width:30px; display:flex; flex-direction:column; align-items:center; margin-right:20px;">
                            <img src="{node_icon_url}" style="width:26px; height:26px; margin-top:10px; z-index:2; object-fit:contain;" />
                            <div style="width:2px; flex-grow:1; background-color:rgba(150,150,150,0.4); min-height:100px; z-index:1;"></div>
                        </div>
                        <div style="background:rgba(255,255,255,0.95); border-radius:15px; padding:20px;
                                    box-shadow:0 4px 15px rgba(0,0,0,0.05); flex-grow:1; border:1px solid rgba(255,255,255,1);">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                <h3 style="margin:0; color:#1C3A5E; font-size:22px;">{e['event']}</h3>
                                <span style="background:{tag_bg}; color:white; padding:5px 14px; border-radius:20px;
                                             font-size:13px; font-weight:bold;">{tags}</span>
                            </div>
                            <div style="font-size:15px; color:#333; line-height:1.8;">
                                <div><strong style="color:#1C3A5E;">【背景】</strong> {e['background']}</div>
                                <div><strong style="color:#1C3A5E;">【过程】</strong> {e['process']}</div>
                                <div><strong style="color:#1C3A5E;">【影响】</strong> {e['impact']}</div>
                            </div>
                        </div>
                    </div>
                    """

                full_html = (
                    '<!DOCTYPE html><html><head><meta charset="utf-8"></head>'
                    '<body style="margin:0; padding:10px; font-family:KaiTi, sans-serif; background:transparent;">'
                    + header_html + '<div style="max-width:100%; margin:0 auto;">' + html_items
                    + "</div></body></html>"
                )

                # 关键：iframe 高度按卡片数动态计算。写死 800 会把第 4 条之后的卡片裁掉。
                components.html(full_html, height=140 + 240 * len(events), scrolling=False)

                with st.expander("查看解析结果（调试用）"):
                    st.code("\n".join(
                        "%s|%s|%s|%s|%s|%s" % (e["year_text"], e["event"], e["tags"],
                                               e["background"], e["process"], e["impact"]) for e in events),
                        language="text")

elif st.session_state.tab == "compare":
    st.subheader("多源史料互证与考证")
    compare_input = st.text_input("请输入要对比的历史事件：", placeholder="如：玄武门之变", key="in2")
    if st.button("⚖️ 开启史料对比", key="btn2"):
        if not compare_input.strip():
            st.info("请先输入要对比的历史事件。")
        else:
            with st.spinner("AI 正在翻阅古籍..."):
                ai_text = call_ai(SYSTEM_COMPARE, "事件：%s" % compare_input.strip(), max_tokens=4000)
            if ai_text:
                st.markdown("---")
                st.markdown(ai_text)

elif st.session_state.tab == "hypothesis":
    st.subheader("反事实逻辑沙盘")
    hypothesis_input = st.text_input("请输入你的历史假设：", placeholder="如：如果安禄山没有造反", key="in3")
    if st.button("🔮 开启历史推演", key="btn3"):
        if not hypothesis_input.strip():
            st.info("请先输入你的历史假设。")
        else:
            with st.spinner("AI 正在推演..."):
                ai_text = call_ai(SYSTEM_HYPOTHESIS, "假设：%s" % hypothesis_input.strip(), max_tokens=4000)
            if ai_text:
                st.markdown("---")
                st.markdown(ai_text)
