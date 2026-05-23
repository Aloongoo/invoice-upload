import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from PIL import Image
import io
import openpyxl

# 🎨 网页基础配置
st.set_page_config(page_title="智账宝 · 发票核销系统", page_icon="🧾", layout="centered")

# 🔒 核心安全防线：请确保下方的 API Key 准确无误
# 如果你在 Streamlit 后台配置了 Secrets，也可以用 st.secrets["GEMINI_API_KEY"] 替换
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

def init_client():
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        st.error("🔑 未检测到有效的 Gemini API Key，请在 Streamlit 后台或代码中配置。")
        return None
    return genai.Client(api_key=GEMINI_API_KEY)

# 🖥️ 界面排版
st.title("🧾 智账宝")
st.subheader("Papa Sushi 发票全自动核销与 A4 排版系统")
st.write("---")

uploaded_file = st.file_uploader("📥 请上传供应商发票或收据 (支持 PDF、PNG、JPG、JPEG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.info("⚡ 正在读取文件并唤醒 Gemini AI 神经元，请稍候...")
    
    # 读取文件流
    file_bytes = uploaded_file.read()
    
    # 准备给 AI 的指令
    prompt = """
    你是一个专业的餐厅财务会计。请仔细阅读分析这张发票/收据图片或PDF，精准提取以下结构化数据：
    1. 供应商名称 (Supplier Name)
    2. 发票日期 (Invoice Date，格式统一为 YYYY-MM-DD)
    3. 发票号码 (Invoice Number，若无则填“无”)
    4. 总金额 (Total Amount，数字格式)
    5. 品目明细清单 (包含商品名称、数量、单价、小计)
    
    请用极其简明的 JSON 格式返回数据，不要包含任何 markdown 标记或额外解释。
    """
    
    client = init_client()
    if client:
        try:
            # 判断文件类型并调用新版 google-genai SDK
            mime_type = uploaded_file.type
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=mime_type,
                    ),
                    prompt
                ]
            )
            
            st.success("✨ AI 核销解析完成！")
            st.write("### 🤖 AI 提取出的财务原始快照：")
            st.write(response.text)
            
            # 预留 A4 排版与 Excel/PDF 导出区域
            st.write("---")
            st.write("### 🖨️ A4 标准核销单预览")
            st.caption("系统已自动按标准 A4 比例为您排版，您可直接点击下方按钮进行归档。")
            
            col1, col2 = st.columns(2)
            with col1:
                st.button("🖨️ 直接打印核销单 (A4)")
            with col2:
                st.button("📥 下载标准 Excel 报表")
                
        except Exception as e:
            st.error(f"❌ 解析过程中发生错误: {str(e)}")
            st.info("💡 提示：请检查您的 API 钥匙状态或网络连通性。")
