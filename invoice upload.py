import streamlit as st
import json
import urllib.request
import base64

# 🎨 网页基础配置
st.set_page_config(page_title="智账宝 · 批量发票核销系统", page_icon="🧾", layout="centered")

# 🔒 隐形保险箱：从 Streamlit 后台 Secrets 读取钥匙
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# 🖥️ 界面排版
st.title("🧾 智账宝 (批量流水线版)")
st.subheader("Papa Sushi 发票多图全自动核销系统")
st.write("---")

# 📥 多文件上传组件
uploaded_files = st.file_uploader(
    "📥 请一次性选择或拖入单张/多张发票 (支持 PDF, PNG, JPG, JPEG, HEIC, HEIF)", 
    type=["pdf", "png", "jpg", "jpeg", "heic", "heif"],
    accept_multiple_files=True
)

# 🛠️ 核心后端请求函数
def request_gemini_backend(api_key, mime_type, base64_data):
    # 💡 终极修正点：使用官方最标准、对多模态图片/PDF 支持最完美的正式版 v1 接口路径
    api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt_text = """
    你是一个专业的餐厅财务会计。请仔细阅读分析这张发票/收据，精准提取以下结构化数据：
    1. 供应商名称 (Supplier Name)
    2. 发票日期 (Invoice Date，格式统一为 YYYY-MM-DD)
    3. 发票号码 (Invoice Number，若无则填“无”)
    4. 总金额 (Total Amount，数字格式)
    5. 品目明细清单 (包含商品名称、数量、单价、小计)
    
    请用极其简明的 JSON 格式返回数据，不要包含任何 markdown 标记或额外解释。
    """
    
    # 💡 标准多模态 JSON 载荷结构，严格对齐 Google 官方标准
    payload = {
        "contents": [{
            "parts": [
                {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": base64_data
                    }
                },
                {"text": prompt_text}
            ]
        }]
    }
    
    data_bytes = json.dumps(payload).encode("utf-8")
    
    # 在 Streamlit 服务器后端发起原生请求
    req = urllib.request.Request(
        api_url, 
        data=data_bytes, 
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))
        # 稳妥提取返回文本
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except KeyError:
            # 如果返回结构有变，尝试兜底解析
            return json.dumps(result, ensure_ascii=False, indent=2)

# 🔄 流水线处理
if uploaded_files:
    if not GEMINI_API_KEY:
        st.error("🔑 未检测到有效的 Gemini API Key！请在 Streamlit 后台 Secrets 中配置您的钥匙。")
    else:
        st.success(f"📚 成功捕获到 {len(uploaded_files)} 张单据！AI 纯后端流水线已全速启动...")
        st.write("---")
        
        for index, uploaded_file in enumerate(uploaded_files, start=1):
            with st.expander(f"📄 单据 {index}：{uploaded_file.name}", expanded=True):
                st.info("⚡ AI 后端神经元正在全力识别该单据内容...")
                
                try:
                    # 在后端读取并处理文件流
                    file_bytes = uploaded_file.read()
                    base64_data = base64.b64encode(file_bytes).decode("utf-8")
                    
                    mime_type = uploaded_file.type
                    # 如果是 iPhone 的 HEIC/HEIF，统一伪装成 jpeg 让底层顺利读取
                    if not mime_type or "heic" in uploaded_file.name.lower() or "heif" in uploaded_file.name.lower():
                        mime_type = "image/jpeg"
                    
                    # 调用后端请求
                    ai_response_text = request_gemini_backend(GEMINI_API_KEY, mime_type, base64_data)
                    
                    st.success("✅ 该单据核销解析成功！")
                    st.markdown("**🤖 财务结构化快照：**")
                    st.code(ai_response_text, language="json")
                                
                except Exception as e:
                    st.error(f"❌ 该单据解析发生错误: {str(e)}")
                    st.info("💡 提示：请确保单据字迹清晰，或检查网络状况与 Secrets 配置。")
                    
        # 底部操作区
        st.write("---")
        st.write("### 🖨️ 批量处理动作")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🖨️ 一键打印全部核销单"):
                st.info("⚙️ 批量打印模块正在并网中...")
        with col2:
            if st.button("📥 导出合并 Excel 账目报表"):
                st.info("⚙️ 批量数据合并模块正在并网中...")
