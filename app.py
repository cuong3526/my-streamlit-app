import streamlit as st
import pandas as pd
from datetime import datetime

# === Các hàm tính toán gốc của bạn ===
def calculate_weighted_average(rsiv_values, investments):
    total_investment = sum(investments)
    if total_investment == 0:
        raise ValueError("Tổng số tiền đầu tư không thể bằng 0.")
    weights = [(investment / total_investment) * 100 for investment in investments]
    weighted_sum = sum(rsiv * (weight / 100) for rsiv, weight in zip(rsiv_values, weights))
    return weighted_sum, weights

def suggest_holding_ratio(safety_level, weighted_sum):
    suggested_ratio = safety_level * 10 * (weighted_sum / 50)
    return suggested_ratio

def analyze_weak_stocks(rsiv_values):
    weak_stocks = []
    for i, rsiv in enumerate(rsiv_values):
        if rsiv < 50:
            weak_stocks.append(f"Cổ phiếu {i+1} (RSIV = {rsiv:.2f})")
    return weak_stocks

def calculate_actual_weights(investments, cash_balance):
    total_portfolio_value = sum(investments) + cash_balance
    total_stock_weight = (sum(investments) / total_portfolio_value) * 100
    cash_weight = (cash_balance / total_portfolio_value) * 100
    return total_stock_weight, cash_weight, total_portfolio_value

def generate_recommendation(total_stock_weight, suggested_ratio, total_portfolio_value):
    difference = suggested_ratio - total_stock_weight
    if difference > 0:
        action = "Tăng"
        amount = total_portfolio_value * (difference / 100)
    elif difference < 0:
        action = "Giảm"
        amount = total_portfolio_value * (abs(difference) / 100)
    else:
        action = "Giữ nguyên"
        amount = 0
    return action, amount


# === Giao diện Streamlit ===
st.markdown("""
<h2 style='text-align: center; color: #a259ff; margin-bottom: 0.01em;'>KHÁM SỨC KHỎE</h2>
<h2 style='text-align: center; color: #a259ff; margin-top: 0; margin-bottom: 0.1em;'>DANH MỤC CỔ PHIẾU</h2>
""", unsafe_allow_html=True)

# Nhập dữ liệu


n_safety_col1, n_safety_col2 = st.columns([2, 5])
with n_safety_col1:
    safety_level = st.number_input("Nhập mức an toàn của Vnindex (0-9):", min_value=0, max_value=9, step=1, value=None, placeholder="", key="safety_level")
with n_safety_col2:
    if safety_level is not None:
        if safety_level >= 5:
            st.markdown(f"<div style='background-color:#d4edda; color:#155724; border-radius:6px; padding:0.5em 1em; display:inline-block;'>Mức an toàn: <b>{safety_level}</b> (An toàn)</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color:#f8d7da; color:#721c24; border-radius:6px; padding:0.5em 1em; display:inline-block;'>Mức an toàn: <b>{safety_level}</b> (Cảnh báo thấp)</div>", unsafe_allow_html=True)
n = st.number_input("Số lượng cổ phiếu trong danh mục của bạn:", min_value=1, step=1, value=None, placeholder="")
cash_balance = st.number_input("Nhập số tiền mặt hiện có (triệu):", min_value=0, step=1, value=None, format="%d", placeholder="Nhập số tiền mặt (triệu)")


# Nhập từng thành phần cho từng cổ phiếu
rsiv_values = []
investments = []
for i in range(int(n) if n else 0):
    col1, col2 = st.columns([2,1])
    with col1:
        rsiv = st.number_input(f"RSIV của cổ phiếu {i+1}:", min_value=0, step=1, value=None, format="%d", placeholder="Nhập RSIV", key=f"rsiv_{i}")
    with col2:
        if rsiv is not None:
            if rsiv >= 50:
                st.markdown("""
                <div style='background-color:#28a745; color:white; border-radius:6px; height:2.4em; margin-top:0.4em; display:flex; align-items:center; justify-content:center; font-weight:bold;'>
                    Khá hơn Vnindex
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background-color:#dc3545; color:white; border-radius:6px; height:2.4em; margin-top:0.4em; display:flex; align-items:center; justify-content:center; font-weight:bold;'>
                    Yếu hơn Vnindex
                </div>
                """, unsafe_allow_html=True)
    invest = st.number_input(f"Số tiền đầu tư cho cổ phiếu {i+1} (triệu):", min_value=0, step=1, value=None, format="%d", placeholder="Nhập số tiền (triệu)", key=f"invest_{i}")
    rsiv_values.append(rsiv)
    investments.append(invest)

if st.button("Tính toán"):
    from fpdf import FPDF
    import tempfile

    try:
        weighted_sum, _ = calculate_weighted_average(rsiv_values, investments)
        suggested_ratio = suggest_holding_ratio(safety_level, weighted_sum)
        total_stock_weight, cash_weight, total_portfolio_value = calculate_actual_weights(investments, cash_balance)
        action, amount = generate_recommendation(total_stock_weight, suggested_ratio, total_portfolio_value)
        weak_stocks = analyze_weak_stocks(rsiv_values)

        # Hiển thị kết quả chi tiết
        now = (datetime.now() + pd.Timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
        st.subheader("=== KẾT QUẢ ===")
        st.write(f"📅 Thời gian tính toán: {now}")
        st.write(f"Giá trị trung bình RSIV của danh mục: {weighted_sum:.2f}")
        # Nhận xét về RSIV danh mục so với thị trường chung
        if weighted_sum > 50:
            st.success("Nhận xét: Danh mục này đang khá hơn thị trường chung (RSIV > 50).")
        else:
            st.warning("Nhận xét: Danh mục này đang yếu hơn thị trường chung (RSIV ≤ 50).")
        st.write(f"Tỷ trọng gợi ý nắm giữ: {suggested_ratio:.2f}%")
        st.write(f"Tổng giá trị danh mục hiện tại: {total_portfolio_value:.2f}")
        st.write(f"Tỷ trọng thực tế của cổ phiếu: {total_stock_weight:.2f}%")
        st.write(f"Tỷ trọng tiền mặt: {cash_weight:.2f}%")
        st.write(f"Gợi ý điều chỉnh: **{action}** tỷ trọng cổ phiếu với số tiền = {amount:.2f}")

        # Tạo file PDF kết quả


        pdf = FPDF()
        pdf.add_page()
        # Sử dụng font Unicode NotoSans-Regular.ttf trong thư mục dự án
        pdf.add_font('NotoSans', '', 'NotoSans-Regular.ttf', uni=True)
        pdf.set_font('NotoSans', '', 14)
        pdf.set_text_color(162, 89, 255)
        pdf.cell(0, 10, "KHÁM SỨC KHỎE DANH MỤC CỔ PHIẾU", ln=True, align="C")
        pdf.set_text_color(0,0,0)
        pdf.set_font('NotoSans', '', 12)
        pdf.cell(0, 10, f"Thời gian tính toán: {now}", ln=True)
        pdf.cell(0, 10, f"Giá trị trung bình RSIV của danh mục: {weighted_sum:.2f}", ln=True)
        if weighted_sum > 50:
            pdf.set_text_color(40,167,69)
            pdf.cell(0, 10, "Nhận xét: Danh mục này đang khá hơn thị trường chung (RSIV > 50)", ln=True)
        else:
            pdf.set_text_color(220,53,69)
            pdf.cell(0, 10, "Nhận xét: Danh mục này đang yếu hơn thị trường chung (RSIV ≤ 50)", ln=True)
        pdf.set_text_color(0,0,0)
        pdf.cell(0, 10, f"Tỷ trọng gợi ý nắm giữ: {suggested_ratio:.2f}%", ln=True)
        pdf.cell(0, 10, f"Tổng giá trị danh mục hiện tại: {total_portfolio_value:.2f}", ln=True)
        pdf.cell(0, 10, f"Tỷ trọng thực tế của cổ phiếu: {total_stock_weight:.2f}%", ln=True)
        pdf.cell(0, 10, f"Tỷ trọng tiền mặt: {cash_weight:.2f}%", ln=True)
        pdf.cell(0, 10, f"Gợi ý điều chỉnh: {action} tỷ trọng cổ phiếu với số tiền = {amount:.2f}", ln=True)

        # Nhận xét cổ phiếu yếu
        if weak_stocks:
            pdf.set_text_color(220,53,69)
            pdf.cell(0, 10, "CỔ PHIẾU YẾU:", ln=True)
            pdf.set_text_color(0,0,0)
            for stock in weak_stocks:
                pdf.cell(0, 10, f"- {stock}", ln=True)
        else:
            pdf.set_text_color(40,167,69)
            pdf.cell(0, 10, "Không có cổ phiếu nào yếu hơn Vnindex (tất cả đều có RSIV >= 50)", ln=True)
        pdf.set_text_color(0,0,0)

        # Lưu PDF ra file tạm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf.output(tmp_pdf.name)
            tmp_pdf.seek(0)
            pdf_data = tmp_pdf.read()

        # Nhận xét cổ phiếu yếu
        if weak_stocks:
            st.subheader("= CỔ PHIẾU YẾU =")
            st.write("Các cổ phiếu sau đây đang yếu hơn so với Vnindex:")
            for stock in weak_stocks:
                st.write(f"- {stock}: Nên chuyển sang cổ phiếu khỏe hơn Vnindex, có sức mạnh nội tại HL đảm bảo và có điểm vào theo phương pháp.")
        else:
            st.subheader("= NHẬN XÉT VỀ CỔ PHIẾU =")
            st.write("Không có cổ phiếu nào yếu hơn Vnindex (tất cả đều có RSIV >= 50).")

        # Nút tải PDF đặt dưới cùng
        st.markdown("""
<style>
#custom-download-btn button {
    background: #1976d2;
    color: white;
    font-size: 1.1em;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 0.7em 2em;
    box-shadow: 0 2px 8px rgba(25,118,210,0.18);
    transition: background 0.2s, transform 0.1s;
    margin-top: 1.5em;
}
#custom-download-btn button:hover {
    background: #0d47a1;
    transform: scale(1.05);
}
</style>
        """, unsafe_allow_html=True)
        st.download_button(
            label="📄 Tải xuống kết quả PDF",
            data=pdf_data,
            file_name="ket_qua_danh_muc.pdf",
            mime="application/pdf",
            key="custom-download-btn"
        )

        # ...bỏ phần xuất file CSV...

    except ValueError as e:
        st.error(f"Lỗi: {e}")
        
