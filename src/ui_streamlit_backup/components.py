"""Reusable UI widgets and presentation components for Student Retention Intelligence."""
import streamlit as st


def render_header(title: str, subtitle: str, status_tag: str = "Pipeline Verified", tag_type: str = "info"):
    """Render top page header with title, subtitle, and status pill."""
    tag_class = f"badge-{tag_type}"
    st.markdown(f"""
<div class="saas-header">
  <div>
    <h2 style="margin: 0; font-size: 1.65rem; color: #F8FAFC;">{title}</h2>
    <p style="margin: 4px 0 0 0; color: #94A3B8; font-size: 0.92rem;">{subtitle}</p>
  </div>
  <div>
    <span class="{tag_class}">{status_tag}</span>
  </div>
</div>
""", unsafe_allow_html=True)


def render_sidebar_branding():
    """Render the sleek enterprise sidebar product logo and group metadata."""
    st.sidebar.markdown("""
<div style="padding: 10px 0 18px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 12px;">
  <div style="display: flex; align-items: center; gap: 10px;">
    <div style="background: linear-gradient(135deg, #3B82F6, #22D3EE); width: 34px; height: 34px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.15rem; color: #0B1020;">
      🎓
    </div>
    <div>
      <div style="font-weight: 700; font-size: 1.05rem; color: #F8FAFC; letter-spacing: -0.02em;">EduPulse Retention</div>
      <div style="font-size: 0.76rem; color: #94A3B8;">Early Warning & Decision Support</div>
    </div>
  </div>
  <div style="margin-top: 10px; font-size: 0.72rem; color: #64748B; background: rgba(255, 255, 255, 0.03); padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.05);">
    <b>INT395 Group 12:</b> Kabya Varun • Duggisetty Vasavi Vignan • Shivraj Singh
  </div>
</div>
""", unsafe_allow_html=True)


def render_before_after_card(before_profile: dict, after_profile: dict,
                             before_risk: float, after_risk: float,
                             before_pred: str, after_pred: str,
                             threshold: float = 0.38):
    """Render an interactive Before-and-After comparative sensitivity panel (Section 4 requirement)."""
    delta_pp = (after_risk - before_risk) * 100
    risk_direction = "Decreased Risk" if delta_pp < 0 else "Increased Risk" if delta_pp > 0 else "No Change"
    delta_color = "#10B981" if delta_pp < 0 else "#EF4444" if delta_pp > 0 else "#94A3B8"

    col_before, col_arrow, col_after = st.columns([1.2, 0.4, 1.2])

    with col_before:
        st.markdown("""
        <div style="background: #111827; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 16px;">
          <div style="font-size: 0.78rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 8px;">BEFORE (Baseline Profile)</div>
        """, unsafe_allow_html=True)
        st.write(f"**Predicted Outcome:** `{before_pred}`")
        st.write(f"**Dropout Probability:** `{before_risk:.1%}`")
        st.write(f"**Approved Units:** `{before_profile.get('Curricular units 1st sem (approved)', 'N/A')}` / {before_profile.get('Curricular units 1st sem (enrolled)', 'N/A')}")
        st.write(f"**Semester Grade:** `{before_profile.get('Curricular units 1st sem (grade)', 'N/A'):.2f}/20`")
        fee_stat = "Past Due / Debtor" if before_profile.get('Debtor', 0) == 1 or before_profile.get('Tuition fees up to date', 1) == 0 else "Up to date"
        st.write(f"**Fee Status:** `{fee_stat}`")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_arrow:
        st.markdown(f"""
        <div style="text-align: center; padding-top: 45px;">
          <div style="font-size: 1.8rem; color: #3B82F6;">➔</div>
          <div style="font-size: 0.82rem; font-weight: 700; color: {delta_color};">{delta_pp:+.1f} pp</div>
          <div style="font-size: 0.72rem; color: #94A3B8;">{risk_direction}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_after:
        after_badge = '<span class="badge-critical">Above Review Threshold</span>' if after_risk >= threshold else '<span class="badge-success">Below Review Threshold</span>'
        st.markdown(f"""
        <div style="background: #111827; border: 1px solid rgba(34, 211, 238, 0.25); border-radius: 10px; padding: 16px;">
          <div style="font-size: 0.78rem; font-weight: 700; color: #22D3EE; text-transform: uppercase; margin-bottom: 8px;">AFTER (Modified Sensitivity)</div>
        """, unsafe_allow_html=True)
        st.write(f"**Predicted Outcome:** `{after_pred}`")
        st.write(f"**Dropout Probability:** `{after_risk:.1%}`")
        st.write(f"**Approved Units:** `{after_profile.get('Curricular units 1st sem (approved)', 'N/A')}` / {after_profile.get('Curricular units 1st sem (enrolled)', 'N/A')}")
        st.write(f"**Semester Grade:** `{after_profile.get('Curricular units 1st sem (grade)', 'N/A'):.2f}/20`")
        after_fee_stat = "Past Due / Debtor" if after_profile.get('Debtor', 0) == 1 or after_profile.get('Tuition fees up to date', 1) == 0 else "Up to date"
        st.write(f"**Fee Status:** `{after_fee_stat}`")
        st.markdown(f"<div style='margin-top: 8px;'>{after_badge}</div></div>", unsafe_allow_html=True)

    st.caption("ℹ️ **Sensitivity Notice:** What-if changes explore model sensitivity. They describe associative statistical shifts and do not prove that altering grades or fees will causally guarantee retention.")
