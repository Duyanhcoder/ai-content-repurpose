import streamlit as st
import google.generativeai as genai

# 1. Cấu hình giao diện trang web
st.set_page_config(page_title="AI Content Repurposer", layout="wide")
st.title("⚡ AI Content Repurposing Tool")
st.write("Biến 1 bài viết dài thành Kịch bản TikTok, Bài đăng Threads & Email Newsletter chỉ trong 5 giây.")

# 2. Thanh bên (Sidebar) - Quản lý Bản Pro & API Key
st.sidebar.header("🔑 Kích hoạt bản PRO")
license_key = st.sidebar.text_input("Nhập License Key (Nếu có):", type="password")

# Lấy API Key bí mật từ hệ thống Streamlit Cloud
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# Khung nhập bổ sung API Key nếu bạn muốn test trên máy cá nhân
if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("Nhập Gemini API Key (để chạy thử):", type="password")

# 3. Khung nhập liệu nội dung chính
user_text = st.text_area("Dán bài viết, kịch bản thô hoặc nội dung dài vào đây:", height=200)

# Khởi tạo bộ đếm số lần sử dụng miễn phí trong phiên làm việc
if "usage_count" not in st.session_state:
    st.session_state.usage_count = 0

# 4. Xử lý logic khi bấm nút "Tái bản"
if st.button("🚀 Tái bản Nội dung ngay"):
    if not GEMINI_API_KEY:
        st.error("❌ Chưa tìm thấy Gemini API Key! Vui lòng nhập API Key ở thanh bên tả để thử nghiệm.")
    elif not user_text.strip():
        st.warning("⚠️ Vui lòng dán nội dung vào ô trống trước khi bấm tạo!")
    else:
        # Kiểm tra License Key (Mã PRO giả định, bạn có thể thay đổi)
        is_pro = (license_key == "PRO2026VIP")

        # Kiểm tra hạn ngạch Freemium
        if not is_pro and st.session_state.usage_count >= 3:
            st.error("❌ Bạn đã hết 3 lượt dùng thử miễn phí hôm nay!")
            st.markdown("[👉 Bấm vào đây để Mua License Key Pro ($9/tháng) trên Gumroad](https://gumroad.com)")
        else:
            with st.spinner("🤖 AI đang phân tích và tái bản nội dung..."):
                try:
                    genai.configure(api_key=GEMINI_API_KEY)
                    model = genai.GenerativeModel('gemini-1.5-flash')

                    # Thiết lập các Prompt chuyên biệt
                    prompt_tiktok = f"Bạn là chuyên gia kịch bản. Hãy chuyển văn bản sau thành kịch bản TikTok 30s ngắn gọn, thu hút (gồm Hook 3s, Thân bài 20s, CTA 7s):\n\n{user_text}"
                    prompt_threads = f"Chuyển văn bản sau thành 1 bài đăng Threads dưới 400 ký tự, ngắn gọn, tự nhiên, có câu hỏi tương tác ở cuối:\n\n{user_text}"
                    prompt_email = f"Tóm tắt văn bản sau thành Email Newsletter ngắn gồm: Tiêu đề, 3 ý chính dạng bullet, 1 câu kết luận hành động:\n\n{user_text}"

                    # Gọi API sinh nội dung đồng thời
                    res_tiktok = model.generate_content(prompt_tiktok).text
                    res_threads = model.generate_content(prompt_threads).text
                    res_email = model.generate_content(prompt_email).text

                    # Tăng số lần dùng nếu là tài khoản Free
                    if not is_pro:
                        st.session_state.usage_count += 1
                        st.info(f"ℹ️ Bạn đã dùng {st.session_state.usage_count}/3 lượt miễn phí.")

                    # Hiển thị kết quả ra 3 cột song song
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.subheader("📱 Kịch bản TikTok")
                        st.markdown(res_tiktok)
                    with col2:
                        st.subheader("💬 Bài đăng Threads")
                        st.markdown(res_threads)
                    with col3:
                        st.subheader("✉️ Email Summary")
                        st.markdown(res_email)

                except Exception as e:
                    st.error(f"❌ Xảy ra lỗi khi kết nối với AI: {e}")
                    