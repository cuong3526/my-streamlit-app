import streamlit as st
import io, csv

# --- Core calculation functions (adapted from your CLI code) ---
def calculate_weighted_average(rsiv_values, investments):
    total_investment = sum(investments)
    if total_investment == 0:
        raise ValueError("Tổng số tiền đầu tư không thể bằng 0.")
    weights = [(inv / total_investment) * 100 for inv in investments]
    weighted_sum = sum(rsiv * (weight / 100) for rsiv, weight in zip(rsiv_values, weights))
    return weighted_sum, weights

def suggest_holding_ratio(safety_level, weighted_sum):
    return safety_level * 10 * (weighted_sum / 50)

def analyze_weak_stocks(rsiv_values):
    return [f"Cổ phiếu {i+1} (RSIV = {rsiv:.2f})" for i, rsiv in enumerate(rsiv_values) if rsiv < 50]

def calculate_actual_weights(investments, cash_balance):
    total_portfolio_value = sum(investments) + cash_balance
    if total_portfolio_value == 0:
        return 0.0, 0.0, 0.0
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
        amount = 0.0
    return action, amount

# --- Streamlit UI ---
st.set_page_config(page_title="RSIV - Tính tỷ trọng danh mục", layout="centered")
st.title("RSIV - Tính tỷ trọng danh mục (Web app)")
st.write("Nhập dữ liệu danh mục, app sẽ tính trung bình RSIV có trọng số, gợi ý tỷ trọng nắm giữ, và xuất file CSV.")

with st.form("input_form"):
    safety_level = st.slider("Mức an toàn của VnIndex (0-9):", min_value=0, max_value=9, value=5)
    n = st.number_input("Số lượng cổ phiếu:", min_value=1, value=3, step=1)
    cash_balance = st.number_input("Số tiền mặt hiện có:", min_value=0.0, value=0.0, step=100000.0, format="%.2f")
    rsiv_values = []
    investments = []
    st.info("Nhập RSIV và số tiền đầu tư cho từng cổ phiếu:")
    for i in range(int(n)):
        c1, c2 = st.columns(2)
        rsiv = c1.number_input(f"RSIV cổ phiếu {i+1}:", min_value=0.0, value=50.0, step=0.1, key=f"rsiv_{i}")
        inv = c2.number_input(f"Số tiền đầu tư cổ phiếu {i+1}:", min_value=0.0, value=1000000.0, step=10000.0, key=f"inv_{i}")
        rsiv_values.append(rsiv)
        investments.append(inv)
    submitted = st.form_submit_button("Tính toán")

if submitted:
    try:
        weighted_sum, weights = calculate_weighted_average(rsiv_values, investments)
        suggested_ratio = suggest_holding_ratio(safety_level, weighted_sum)
        total_stock_weight, cash_weight, total_portfolio_value = calculate_actual_weights(investments, cash_balance)
        action, amount = generate_recommendation(total_stock_weight, suggested_ratio, total_portfolio_value)
        weak_stocks = analyze_weak_stocks(rsiv_values)

        st.subheader("KẾT QUẢ")
        st.write(f"**Giá trị trung bình RSIV của danh mục:** {weighted_sum:.2f}")
        st.write(f"**Tỷ trọng gợi ý nắm giữ:** {suggested_ratio:.2f}%")
        st.write(f"**Tổng giá trị danh mục hiện tại:** {total_portfolio_value:,.2f}")
        st.write(f"**Tỷ trọng thực tế của cổ phiếu:** {total_stock_weight:.2f}%")
        st.write(f"**Tỷ trọng tiền mặt:** {cash_weight:.2f}%")
        st.write(f"**Gợi ý điều chỉnh:** {action} tỷ trọng cổ phiếu với số tiền = {amount:,.2f}")

        if weak_stocks:
            st.warning("Các cổ phiếu yếu (RSIV < 50):")
            for s in weak_stocks:
                st.write(f"- {s}\n  > Gợi ý: cân nhắc chuyển sang cổ phiếu khỏe hơn.")
        else:
            st.success("Không có cổ phiếu yếu (tất cả RSIV >= 50).")

        # Prepare CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Cổ phiếu", "RSIV", "Số tiền đầu tư"])
        for i, (rsiv, inv) in enumerate(zip(rsiv_values, investments), start=1):
            writer.writerow([f"Cổ phiếu {i}", f"{rsiv:.2f}", f"{inv:.2f}"])
        writer.writerow([])
        writer.writerow(["Tổng số tiền đầu tư vào cổ phiếu", f"{sum(investments):.2f}"])
        writer.writerow(["Tiền mặt", f"{cash_balance:.2f}"])
        writer.writerow([])
        writer.writerow(["Tỷ trọng thực tế của cổ phiếu (%)", f"{total_stock_weight:.2f}", "%"])
        writer.writerow(["Tỷ trọng gợi ý nắm giữ (%)", f"{suggested_ratio:.2f}", "%"])
        writer.writerow(["Hành động", action, ""])
        writer.writerow(["Số tiền cần điều chỉnh", f"{amount:.2f}", ""])
        writer.writerow([])
        writer.writerow(["Nhận xét về cổ phiếu yếu:"])
        if weak_stocks:
            for s in weak_stocks:
                writer.writerow([s])
        else:
            writer.writerow(["Không có cổ phiếu yếu."])

        csv_data = output.getvalue()
        st.download_button("Tải file CSV kết quả", data=csv_data, file_name="ket_qua_rsiv.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Lỗi khi tính toán: {e}")

st.markdown("---")
st.caption("Hướng dẫn nhanh: cài Python -> pip install streamlit pandas -> chạy: streamlit run app.py. Để dùng trên điện thoại, deploy lên Streamlit Community và mở link, sau đó 'Add to Home Screen'.")
