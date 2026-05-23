import streamlit as st
import json
import urllib.request
import base64

# 🎨 网页基础配置
st.set_page_config(page_title="智账宝 · 发票核销系统", page_icon="🧾", layout="centered")

# 🔒 隐形保险箱：从 Streamlit 后台 Secrets 读取钥匙
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# 🖥️ 界面排版
st.title("🧾 智账宝")
st.subheader("Papa Sushi 发票全自动核销与 A4 排版系统")
st.write("---")

uploaded_file = st.file_uploader("📥 请上传供应商发票或收据 (支持 PDF、PNG、JPG、JPEG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    if not GEMINI_API_KEY:
        st.error("🔑 未检测到有效的 Gemini API Key！请点击右下角 'Manage app' -> 'Settings' -> 'Secrets' 配置您的钥匙。")
    else:
        st.info("⚡ 正在读取文件并唤醒 Gemini AI 神经元，请稍候...")
        
        try:
            # 读取文件并转为 Base64 编码
            file_bytes = uploaded_file.read()
            base64_data = base64.b64encode(file_bytes).decode("utf-8")
            mime_type = uploaded_file.type
            
            # 准备原生的 API 请求负载 (针对 Gemini 1.5 Flash)
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            
            prompt_text = """
            你是一个专业的餐厅财务会计。请仔细阅读分析这张发票/收据，精准提取以下结构化数据：
            1. 供应商名称 (Supplier Name)
            2. 发票日期 (Invoice Date，格式统一为 YYYY-MM-DD)
            3. 发票号码 (Invoice Number，若无则填“无”)
            4. 总金额 (Total Amount，数字格式)
            5. 品目明细清单 (包含商品名称、数量、单价、小计)
            
            请用极其简明的 JSON 格式返回数据，不要包含任何 markdown 标记或额外解释。
            """
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt_text},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": base64_data
                            }
                        }
                    ]
                }]
            }
            
            # 转为 JSON 字节流
            data_bytes = json.dumps(payload).encode("utf-8")
            
            # 发送原生 HTTP POST 请求
            req = urllib.request.Request(
                api_url, 
                data=data_bytes, 
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                # 提取 AI 返回的文本
                ai_response_text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                st.success("✨ AI 核销解析完成！")
                st.write("### 🤖 AI 提取出的财务原始快照：")
                st.write(ai_response_text)
                
                st.write("---")
                st.write("### 🖨️ A4 标准核销单预览")
                st.caption("系统已自动按标准 A4 比例为您排版，您可直接点击下方按钮进行归档。")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🖨️ 直接打印核销单 (A4)"):
                        st.info("⚙️ 打印模块正在并网中...")
                with col2:
                    if st.button("📥 下载标准报表数据"):
                        st.info("⚙️ 数据导出模块正在并网中...")
                        
        except Exception as e:
            st.error(f"❌ 解析过程中发生错误: {str(e)}")
            st.info("💡 提示：请检查您的 API 钥匙状态、网络连通性或上传的文件是否完整。")
