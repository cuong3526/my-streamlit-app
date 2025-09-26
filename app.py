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
st.title("📊 CHƯƠNG TRÌNH TÍNH TOÁN RSIV DANH MỤC")

# Nhập dữ liệu
safety_level = st.number_input("Nhập mức an toàn của Vnindex (0-9):", min_value=0, max_value=9, step=1)
n = st.number_input("Nhập số lượng cổ phiếu:", min_value=1, step=1)
cash_balance = st.number_input("Nhập số tiền mặt hiện có:", min_value=0.0, step=1000.0)

rsiv_values = []
investments = []

for i in range(int(n)):
    rsiv = st.number_input(f"RSIV của cổ phiếu {i+1}:", min_value=0.0, step=1.0)
    invest = st.number_input(f"Số tiền đầu tư cho cổ phiếu {i+1}:", min_value=0.0, step=1000.0)
    rsiv_values.append(rsiv)
    investments.append(invest)

if st.button("Tính toán"):
    try:
        weighted_sum, _ = calculate_weighted_average(rsiv_values, investments)
        suggested_ratio = suggest_holding_ratio(safety_level, weighted_sum)
        total_stock_weight, cash_weight, total_portfolio_value = calculate_actual_weights(investments, cash_balance)
        action, amount = generate_recommendation(total_stock_weight, suggested_ratio, total_portfolio_value)
        weak_stocks = analyze_weak_stocks(rsiv_values)

        # Hiển thị kết quả chi tiết
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.subheader("=== KẾT QUẢ ===")
        st.write(f"📅 Thời gian tính toán: {now}")
        st.write(f"Giá trị trung bình RSIV của danh mục: {weighted_sum:.2f}")
        st.write(f"Tỷ trọng gợi ý nắm giữ: {suggested_ratio:.2f}%")
        st.write(f"Tổng giá trị danh mục hiện tại: {total_portfolio_value:.2f}")
        st.write(f"Tỷ trọng thực tế của cổ phiếu: {total_stock_weight:.2f}%")
        st.write(f"Tỷ trọng tiền mặt: {cash_weight:.2f}%")
        st.write(f"Gợi ý điều chỉnh: **{action}** tỷ trọng cổ phiếu với số tiền = {amount:.2f}")

        # Nhận xét cổ phiếu yếu
        if weak_stocks:
            st.subheader("=== NHẬN XÉT VỀ CỔ PHIẾU YẾU ===")
            st.write("Các cổ phiếu sau đây đang yếu hơn so với Vnindex:")
            for stock in weak_stocks:
                st.write(f"- {stock}: Nên chuyển sang cổ phiếu khỏe hơn Vnindex, có sức mạnh nội tại HL đảm bảo và có điểm vào theo phương pháp.")
        else:
            st.subheader("=== NHẬN XÉT VỀ CỔ PHIẾU ===")
            st.write("Không có cổ phiếu nào yếu hơn Vnindex (tất cả đều có RSIV >= 50).")

        # Xuất file CSV đúng tiếng Việt
        data = {
            "Cổ phiếu": [f"Cổ phiếu {i+1}" for i in range(int(n))],
            "RSIV": rsiv_values,
            "Số tiền đầu tư": investments
        }
        df = pd.DataFrame(data)
        df.loc[len(df.index)] = ["Tổng số tiền đầu tư vào cổ phiếu", "", sum(investments)]
        df.loc[len(df.index)] = ["Tiền mặt", "", cash_balance]
        df.loc[len(df.index)] = ["Tỷ trọng thực tế cổ phiếu (%)", "", total_stock_weight]
        df.loc[len(df.index)] = ["Tỷ trọng tiền mặt (%)", "", cash_weight]
        df.loc[len(df.index)] = ["Tỷ trọng gợi ý nắm giữ (%)", "", suggested_ratio]
        df.loc[len(df.index)] = ["Hành động", action, amount]

        csv = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 Tải xuống kết quả CSV", data=csv, file_name="ket_qua_rsiv.csv", mime="text/csv")

    except ValueError as e:
        st.error(f"Lỗi: {e}")
