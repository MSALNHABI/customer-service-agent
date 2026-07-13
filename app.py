from pathlib import Path
from services.customer_service import get_customer_profile
import streamlit as st
from agent.agent import agent

def extract_tool_activity(response):
    tool_labels = {
        "check_order_status": "📦 Checking order status",
        "check_inventory": "🏪 Checking branch inventory",
        "verify_vip": "⭐ Checking VIP membership",
        "check_branch_open_now": "🕒 Checking branch opening status",
        "find_product_in_other_branches": "🔎 Finding product in other branches",
    }

    activities = []

    for msg in response["messages"]:
        # Detect AI tool calls
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get("name")
                if tool_name:
                    activities.append(
                        tool_labels.get(tool_name, f"🔧 Using {tool_name}")
                    )

        # Detect returned ToolMessage
        if msg.__class__.__name__ == "ToolMessage":
            tool_name = getattr(msg, "name", None)
            if tool_name:
                activities.append(
                    f"✅ Result received from {tool_name}"
                )

    return activities
def render_customer_status(customer: dict) -> None:
    """
    Display the signed-in customer profile using Nawader Coffee
    brand colors instead of Streamlit's default green and blue alerts.
    """

    customer_type = customer.get("customer_type", "new")
    points = customer.get("loyalty_points", 0)
    is_eligible = customer.get("free_drink_eligible", False)
    masked_phone = customer.get("masked_phone", "")

    if customer_type == "vip":
        status_icon = "⭐"
        status_title = "عميل VIP"
        status_description = "عضوية نوادر المميزة"
        status_badge = "عضوية مميزة"

    elif customer_type == "regular":
        status_icon = "👤"
        status_title = "عميل مسجل"
        status_description = "أهلًا بعودتك إلى نوادر"
        status_badge = "عميل مسجل"

    else:
        status_icon = "☕"
        status_title = "عميل جديد"
        status_description = "حياك الله في نوادر"
        status_badge = "عميل جديد"

    if is_eligible:
        eligibility_class = "eligible"
        eligibility_icon = "🎁"
        eligibility_title = "مؤهل لمشروب مجاني"
        eligibility_description = (
            "تقدر تستفيد من مكافأتك في زيارتك القادمة."
        )

    else:
        eligibility_class = "not-eligible"
        eligibility_icon = "☕"
        eligibility_title = "غير مؤهل حالياً لمشروب مجاني"
        eligibility_description = (
            "واصل جمع نقاط الولاء للحصول على مكافآت نوادر."
        )

    html = f"""
<div class="customer-status-card">
    <div class="customer-status-top">
        <div class="customer-status-icon">{status_icon}</div>

        <div class="customer-status-text">
            <h4>{status_title}</h4>
            <p>{status_description}</p>
        </div>
    </div>

    <div class="customer-status-badge">
        {status_badge}
    </div>

    <div class="customer-phone">
        📱 {masked_phone}
    </div>

    <div class="customer-points-box">
        <div class="customer-points-label">
            نقاط الولاء
        </div>

        <div class="customer-points-value">
            {points}
        </div>
    </div>

    <div class="customer-eligibility {eligibility_class}">
        <div class="customer-eligibility-icon">
            {eligibility_icon}
        </div>

        <div>
            <div class="customer-eligibility-title">
                {eligibility_title}
            </div>

            <div class="customer-eligibility-description">
                {eligibility_description}
            </div>
        </div>
    </div>
</div>
"""

    st.html(html)

st.set_page_config(
    page_title="Nawader Coffee Agent",
    page_icon="☕",
    layout="centered",
    initial_sidebar_state="expanded",
)
# ----------------------------------------------------------------------
# Load external CSS
# ----------------------------------------------------------------------
def load_css(file_path: str):
    css_path = Path(file_path)

    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


load_css("assets/style.css")

# ----------------------------------------------------------------------
# Customer session state
# ----------------------------------------------------------------------
if "customer_signed_in" not in st.session_state:
    st.session_state.customer_signed_in = False

if "customer_profile" not in st.session_state:
    st.session_state.customer_profile = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "tool_activities" not in st.session_state:
    st.session_state.tool_activities = []

# ----------------------------------------------------------------------
# Customer identification screen
# ----------------------------------------------------------------------
if not st.session_state.customer_signed_in:

    st.markdown(
    """
    <div class="customer-login-header">
        <div class="customer-login-logo">☕</div>
        <h1>Nawader Coffee</h1>
        <p>سجّل رقم جوالك وابدأ تجربتك مع بدر</p>
    </div>
    """,
    unsafe_allow_html=True,
)

    login_left, login_center, login_right = st.columns(
        [1, 2 , 1]
    )

    with login_center:
        with st.form("customer_sign_in_form"):
            phone_number = st.text_input(
                "رقم الجوال",
                placeholder="05XXXXXXXX",
                max_chars=14,
            )

            submitted = st.form_submit_button(
                "الدخول إلى بدر ☕",
                use_container_width=True,
            )

        if submitted:
            with st.spinner("جاري التحقق من حسابك..."):
                profile = get_customer_profile(phone_number)

            if not profile["success"]:
                st.error(profile["error"])

            else:
                st.session_state.customer_signed_in = True
                st.session_state.customer_profile = profile

                # Start a clean conversation for this customer
                st.session_state.messages = []
                st.session_state.tool_activities = []

                st.rerun()

        st.caption(
            "يستخدم رقم الجوال لتخصيص تجربة العميل داخل هذا العرض التجريبي."
        )

    # Stop here so the chat does not appear before sign-in
    st.stop()



# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class="brew-header">
        <h1>☕ Nawader Coffee</h1>
        <p>Chat with Bader (بدر) — Autonomous Agent</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.title("☕ Bader Agent")
    
    customer = st.session_state.customer_profile

    
    if st.button("🧹 New Conversation"):
        st.session_state.messages = []
        st.session_state.tool_activities = []
        st.rerun()
    

    st.divider()
    
    activity_placeholder = st.empty()

    st.divider()
    render_customer_status(customer)
    if st.button(
        "تغيير العميل",
        use_container_width=True,
    ):
        st.session_state.customer_signed_in = False
        st.session_state.customer_profile = None
        st.session_state.messages = []
        st.session_state.tool_activities = []
        st.rerun()
    


def render_tool_activity():
    with activity_placeholder.container():
        st.subheader("🛠️ Agent Activity")

        if st.session_state.tool_activities:
            for activity in st.session_state.tool_activities:
                st.markdown(activity)
        else:
            st.caption("No tools used yet.")


render_tool_activity()
# ----------------------------------------------------------------------
# Quick Start Button 
# ----------------------------------------------------------------------
quick_prompt = None

col1, col2, col3 = st.columns(3)
col4, col5 = st.columns(2)
with col1:
    if st.button(
        "📦 تتبع الطلب",
        use_container_width=True,
        key="quick_order"
    ):
        quick_prompt = "وش وضع طلبي رقم 12345؟"

with col2:
    if st.button(
        "☕ فحص المخزون",
        use_container_width=True,
        key="quick_inventory"
    ):
        quick_prompt = "هل عندكم سبانش لاتيه في فرع حطين؟"

with col3:
    if st.button(
        "⭐ نقاط VIP",
        use_container_width=True,
        key="quick_vip"
    ):
        quick_prompt = "هل عندي نقاط؟"

with col4:
    if st.button(
        "🕒 الفرع مفتوح؟",
        use_container_width=True,
        key="quick_open_now"
    ):
        quick_prompt = "هل فرع حطين مفتوح حالياً؟"
with col5:
    if st.button(
        "🔎 اقتراح فرع بديل",
        use_container_width=True,
        key="quick_recommendation"
    ):
        quick_prompt = "هل عندكم فلات وايت في فرع الزهراء؟"


st.divider()
# ----------------------------------------------------------------------
# Render chat history
# ----------------------------------------------------------------------
for message in st.session_state.messages:
    avatar = "☕" if message["role"] == "assistant" else "🧑"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# ----------------------------------------------------------------------
# Handle input
# ----------------------------------------------------------------------
typed_prompt = st.chat_input("Ask Bader...") 

prompt = quick_prompt or typed_prompt

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="☕"):
        with st.status("☕ بدر يشيّك ويرد عليك...", expanded=True) as status:
            try:
                customer = st.session_state.customer_profile
                customer_context = {
                    "role": "system",
                    "content": f"""
                CURRENT SIGNED-IN CUSTOMER CONTEXT:
                Phone number: {customer["phone_number"]}
                Customer type: {customer["customer_type"]}
                Registered customer: {customer["registered"]}
                VIP member: {customer["is_vip"]}
                Current loyalty points: {customer["loyalty_points"]}
                Free drink eligible: {customer["free_drink_eligible"]}

                RULES:
                - When the customer asks about their VIP membership, points,
                or free drink eligibility, use verify_vip with the signed-in
                phone number.
                - Do not ask the customer to provide their phone number again.
                - Do not reveal the full phone number in your response.
                - Do not rely only on this context for live information.
                Use verify_vip before answering membership-related questions.
                - If the customer explicitly provides a different phone number,
                use that number only for that specific request.
                """,
                }
                history = st.session_state.messages[-8:]

                response = agent.invoke(
                    {
                        "messages":[
                            customer_context,
                            *history,
                        ]
                    }
                )

                activities = extract_tool_activity(response)
                st.session_state.tool_activities = activities

                render_tool_activity()

                answer = response["messages"][-1].content

                status.update(
                    label="✅ تم تجهيز الرد",
                    state="complete",
                    expanded=False,
                )

            except Exception as e:
                answer = f"Error: {e}"

                status.update(
                    label="❌ صار خطأ أثناء تجهيز الرد",
                    state="error",
                )

        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    