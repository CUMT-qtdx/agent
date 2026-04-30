import streamlit as st
from openai import OpenAI
import os

# ==========================================
# 页面基础配置
# ==========================================
st.set_page_config(page_title="AI 自动化内容工场", page_icon="🤖", layout="wide")

st.title("🚀 Multi-Agent 全自动多媒体内容工场 MVP")
st.markdown("通过多 Agent 协作，将一个简单的**关键词**自动转化为**多平台分发就绪**的图文/短视频内容。")

# ==========================================
# 侧边栏：配置参数
# ==========================================
with st.sidebar:
    st.header("⚙️ 系统配置")
    api_key = st.text_input("OpenAI API Key (必需)", type="password", help="输入你的 API Key。如果使用国内中转模型，请在下方修改 Base URL")
    base_url = st.text_input("Base URL (可选)", value="https://api.openai.com/v1", help="如果你使用 Kimi/DeepSeek 等兼容接口，请修改此项")
    model_name = st.text_input("模型名称", value="gpt-4o")
    
    st.divider()
    st.markdown("### 👨‍💻 关于此 MVP")
    st.markdown("包含 4 个协作 Agent:\n1. 🧠 策划 Agent\n2. ✍️ 主笔 Agent\n3. 🎨 视觉 Agent\n4. 📱 SEO/排版 Agent")

# ==========================================
# 核心 Agent 引擎
# ==========================================
def run_agent(client, model, system_prompt, user_content, temperature=0.7):
    """通用 Agent 调用函数"""
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 运行失败: {str(e)}"

# ==========================================
# 主界面：任务输入
# ==========================================
st.header("📝 建立内容生产任务")
col1, col2 = st.columns([3, 1])
with col1:
    topic_input = st.text_input("请输入内容主题或关键词：", placeholder="例如：新能源汽车该买纯电还是混动？", value="职场人如何避免内耗，提升核心竞争力")
with col2:
    platform_input = st.selectbox("目标分发平台：", ["小红书", "知乎", "微信公众号", "短视频脚本"])

start_btn = st.button("⚡ 启动多 Agent 协作引擎", type="primary")

# ==========================================
# 运行逻辑与 UI 渲染
# ==========================================
if start_btn:
    if not api_key:
        st.error("⚠️ 请先在左侧边栏输入 API Key！")
        st.stop()
        
    # 初始化客户端
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 使用 Tabs 来展示每个 Agent 的思考过程和结果
    tab1, tab2, tab3, tab4 = st.tabs(["🧠 1. 策划方案", "✍️ 2. 深度文案", "🎨 3. 视觉提示词", "🚀 4. 最终发布版"])
    
    with st.status("🤖 Multi-Agent 引擎正在全力运转中...", expanded=True) as status:
        
        # ---------------------------
        # Agent 1: 策划
        # ---------------------------
        st.write("🕵️ **策划 Agent** 正在挖掘痛点和角度...")
        sys_prompt_1 = """你是一个资深的新媒体爆款策划专家。
        请根据关键词分析受众心理，输出一个具有爆款潜质的内容大纲。
        包含：吸睛标题候选（3个）、核心痛点分析、行文框架。请用 Markdown 格式输出。"""
        plan_result = run_agent(client, model_name, sys_prompt_1, f"关键词：{topic_input}", 0.9)
        with tab1:
            st.markdown(plan_result)
        
        # ---------------------------
        # Agent 2: 主笔
        # ---------------------------
        st.write("✍️ **主笔 Agent** 正在撰写深度长文案...")
        sys_prompt_2 = """你是一位金牌文案，精通故事化叙事与情绪价值输出。
        请根据提供的大纲，撰写一篇800字左右的深度内容。
        要求：开头设置悬念，中间提供干货或情绪共鸣，结尾强引导。用流畅的中文表达。"""
        article_result = run_agent(client, model_name, sys_prompt_2, f"参考大纲：\n{plan_result}")
        with tab2:
            st.markdown(article_result)
            
        # ---------------------------
        # Agent 3: 视觉
        # ---------------------------
        st.write("🎨 **视觉 Agent** 正在提取画面生成 Midjourney 提示词...")
        sys_prompt_3 = """你是一位专业的 AI 绘画提示词工程师。
        请阅读这篇文案，提取出3个最核心的视觉场景，并为每个场景写一段英文的图像生成 Prompt。
        格式要求：场景1：[中文描述] \n Prompt: [英文提示词，包含光影、画质、风格等修饰词]"""
        visual_result = run_agent(client, model_name, sys_prompt_3, f"文案内容：\n{article_result}")
        with tab3:
            st.markdown(visual_result)
            
        # ---------------------------
        # Agent 4: SEO 与排版
        # ---------------------------
        st.write(f"📱 **SEO Agent** 正在适配【{platform_input}】的平台算法...")
        prompts = {
            "小红书": "将文章提炼和改写为小红书爆款风格。大量使用 Emoji (📌💡✨等)，提炼出前3句作为强吸引力标题。正文分段要短，多用列表。末尾加上5-8个高流量 Tag (带#号)。",
            "知乎": "将文章改写为知乎高赞回答风格。语气专业、理性、客观，增加“谢邀”开头，模拟真实的经验分享口吻，分点论述。",
            "微信公众号": "排版为公众号深度文章风格。增加【导读】、【正文】、【写在最后】等小标题，语气真诚，适合深度阅读。",
            "短视频脚本": "将文章拆解为短视频分镜头脚本。请用表格形式输出，表头包含：【镜头序号】、【画面描述】、【配音/台词】、【时长估算】。"
        }
        sys_prompt_4 = prompts.get(platform_input, "请优化文章排版。")
        final_result = run_agent(client, model_name, sys_prompt_4, f"原文案：\n{article_result}")
        with tab4:
            st.markdown(final_result)
        
        status.update(label="✅ 内容流水线处理完成！", state="complete", expanded=False)
        
    st.success("🎉 生成完毕！请点击上方 Tabs 查看每个 Agent 的工作成果。你可以直接复制『最终发布版』进行使用。")
