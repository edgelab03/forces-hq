from datetime import date, timedelta
import math
import streamlit as st

st.set_page_config(page_title="Forces HQ | Career & Money", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
st.markdown('''<style>
:root{--ink:#e9f0fa;--navy:#10213a;--accent:#38bdf8}
.stApp {background:linear-gradient(160deg,#0b1425 0%,#101e35 100%);color:#eaf0fa}
[data-testid="stSidebar"]{background:#0b172b}
.hero{padding:25px 27px;border:1px solid #304766;border-radius:18px;background:linear-gradient(115deg,#183457,#102039);margin-bottom:20px}
.hero h1{margin:0 0 5px;font-size:2.2rem;color:white}.hero p{color:#b8cde4;margin:0}
.smallbox{border:1px solid #32455e;background:#14243b;border-radius:14px;padding:17px;min-height:115px}
.smallbox .label{color:#9db8d1;font-size:.85rem}.smallbox .value{color:#f8fafc;font-size:1.55rem;font-weight:750;margin-top:7px}
.note{border-left:3px solid #38bdf8;background:#122b40;padding:11px 15px;border-radius:5px;font-size:.89rem}
a{color:#7dd3fc!important}
</style>''', unsafe_allow_html=True)

PAGES=["🏠 Dashboard","🎖️ Military profile","📅 Reporting tracker","✍️ Achievement assistant","💷 Money planner","📚 Policy library"]
if "records" not in st.session_state: st.session_state.records=[]
if "profile" not in st.session_state: st.session_state.profile={"service":"British Army","rank":"Sergeant","years":12,"report":"SJAR"}
if "events" not in st.session_state: st.session_state.events=[]

with st.sidebar:
    st.markdown("## 🛡️ FORCES HQ")
    st.caption("Career. Money. Future. | V0.1")
    page=st.radio("Navigate",PAGES,label_visibility="collapsed")
    st.divider()
    st.info("DEMO MODE: do not enter names, service numbers, official appraisals, restricted information or real personal financial data. Inputs are not saved to a database.")
    st.caption("Independent educational prototype — not affiliated with or endorsed by the MOD.")

st.markdown('<div class="hero"><h1>🛡️ Forces HQ</h1><p>Your military career and financial planning — in one place.</p></div>',unsafe_allow_html=True)
p=st.session_state.profile

def box(label,value):
    st.markdown(f'<div class="smallbox"><div class="label">{label}</div><div class="value">{value}</div></div>',unsafe_allow_html=True)

def money(v):return f"£{v:,.0f}"

if page==PAGES[0]:
    st.subheader("Your dashboard")
    a,b,c=st.columns(3)
    with a: box("Service",p["service"])
    with b: box("Rank",p["rank"])
    with c: box("Years served (demo)",str(p["years"]))
    st.write("")
    a,b=st.columns([1.15,1])
    with a:
        st.markdown("### 📅 Your reporting milestones")
        if not st.session_state.events: st.info("No milestones added. Visit Reporting tracker to set your OWN dates. No dates are assumed.")
        for event in sorted(st.session_state.events,key=lambda e:e['date'])[:5]:
            st.write(f"**{event['label']}** — {event['date'].strftime('%d %b %Y')}")
        st.markdown("### ✍️ Achievement log")
        st.write(f"{len(st.session_state.records)} demo achievement(s) recorded this session")
    with b:
        st.markdown("### 💡 Explore your next steps")
        st.write("✅ Record an MPAR review date")
        st.write("✅ Practise an evidence-based SJAR/OJAR summary")
        st.write("✅ Explore a savings scenario")
        st.write("✅ Check official policy sources")
    st.markdown('<div class="note">This is a functional first prototype. It deliberately avoids eligibility decisions, promotion predictions or access to Defence systems.</div>',unsafe_allow_html=True)

elif page==PAGES[1]:
    st.subheader("🎖️ Military profile")
    st.caption("Use fictional/test details. This profile stays only in the current app session.")
    with st.form("profile_form"):
        service=st.selectbox("Service",["British Army","Royal Navy","Royal Air Force","Royal Marines"],index=["British Army","Royal Navy","Royal Air Force","Royal Marines"].index(p["service"]))
        rank=st.selectbox("Rank (simplified demo)",["Private / equivalent","Lance Corporal / equivalent","Corporal / equivalent","Sergeant","Staff Sergeant","Warrant Officer","Commissioned Officer"],index=["Private / equivalent","Lance Corporal / equivalent","Corporal / equivalent","Sergeant","Staff Sergeant","Warrant Officer","Commissioned Officer"].index(p["rank"]))
        years=st.number_input("Completed years of service",0,40,int(p["years"]))
        report=st.selectbox("Appraisal type",["SJAR","OJAR"],index=["SJAR","OJAR"].index(p["report"]))
        if st.form_submit_button("Update demo profile",use_container_width=True):
            st.session_state.profile=dict(service=service,rank=rank,years=int(years),report=report)
            st.success("Demo profile updated for this session.")
    st.info("Reporting and promotion windows vary. Do not treat this demo profile as an eligibility determination.")

elif page==PAGES[2]:
    st.subheader("📅 SJAR / OJAR / MPAR tracker")
    st.write("Set your own confirmed dates. **The app does not invent universal annual reporting windows.**")
    with st.form("event_form",clear_on_submit=True):
        label=st.selectbox("Milestone",["Start-of-period objectives","MPAR","SJAR / OJAR draft","SJAR / OJAR close","Promotion / board window (verify)","Other personal career milestone"])
        due=st.date_input("Date confirmed by your chain of command",value=date.today()+timedelta(days=60))
        if st.form_submit_button("Add milestone"):
            st.session_state.events.append({"label":label,"date":due})
            st.success("Milestone added for this session")
    if st.session_state.events:
        for i,event in enumerate(st.session_state.events):
            cols=st.columns([4,1])
            cols[0].write(f"**{event['label']}** — {event['date']:%d %B %Y} ({(event['date']-date.today()).days} days away)")
            if cols[1].button("Remove",key=f"event{i}"):
                st.session_state.events.pop(i);st.rerun()
    else: st.info("No milestones yet. Add your first MPAR or appraisal date above.")
    st.caption("V0.1 provides in-app date tracking only, not automatic emails, notifications or secure storage.")

elif page==PAGES[3]:
    st.subheader("✍️ Achievement and appraisal preparation assistant")
    st.warning("Only use fictional, generic or non-sensitive examples. Never paste official SJAR/OJAR text, other people's details or restricted information.")
    with st.form("achievement_form",clear_on_submit=True):
        action=st.text_area("What did you do?",placeholder="Example: Designed a training schedule for a fictional team...")
        impact=st.text_area("What was the measurable result?",placeholder="Example: Training completion rose from 70% to 95%...")
        skill=st.selectbox("Theme",["Leadership","Delivery","Teamwork","Development","Planning","Communication","Other"])
        if st.form_submit_button("Add practice achievement"):
            if action.strip() and impact.strip():
                st.session_state.records.append({"action":action.strip(),"impact":impact.strip(),"theme":skill})
                st.success("Practice achievement added.")
            else: st.error("Enter an action and a result.")
    if st.session_state.records:
        st.markdown("### Your evidence-based draft")
        st.caption("Template-generated, NOT AI-generated: no outside API is called and no claims are invented.")
        pieces=[f"**{r['theme']}:** {r['action'].rstrip('.')} — Outcome: {r['impact']}" for r in st.session_state.records]
        draft="\n\n".join(pieces)
        st.text_area("Draft to review and edit",value=draft,height=210)
        st.download_button("Download practice notes",draft,file_name="practice_achievements.txt",mime="text/plain")
        if st.button("Clear achievement examples"):
            st.session_state.records=[];st.rerun()
    else: st.info("Add a fictional achievement to see the structured writing assistant in action.")
    st.markdown("**Quality checklist:** Was your own contribution clear? Is the outcome truthful? Could a reporting officer verify the evidence? Have you removed names and sensitive details?")

elif page==PAGES[4]:
    st.subheader("💷 Money planner")
    st.caption("Enter fictional or illustrative figures only. This is educational modelling, not personal financial advice.")
    left,right=st.columns(2)
    with left:
        income=st.number_input("Monthly take-home income (£)",0,20000,2600,50)
        essential=st.number_input("Monthly essential spending (£)",0,20000,1550,50)
        flexible=st.number_input("Monthly flexible spending (£)",0,20000,450,50)
        surplus=income-essential-flexible
        st.metric("Illustrative monthly surplus",money(surplus))
        if surplus<0: st.warning("Spending exceeds income in this example.")
    with right:
        monthly=st.slider("Monthly investment (£)",0,1000,200,25)
        years=st.slider("Investment years",1,35,15)
        rate=st.slider("Assumed annual return after fees (%)",0.0,10.0,5.0,.5)
        r=(1+rate/100)**(1/12)-1
        total=monthly*years*12 if r==0 else monthly*((1+r)**(years*12)-1)/r
        st.metric("Illustrative future value",money(total))
        st.caption(f"Contributed: {money(monthly*years*12)} | Modelled growth: {money(total-monthly*years*12)}")
    st.info("Returns are illustrative and not guaranteed. Model assumes end-of-month contributions, constant annual growth after fees, no tax and no inflation adjustment. Capital is at risk.")

elif page==PAGES[5]:
    st.subheader("📚 Official information and policy library")
    st.write("A starting collection of official sources. This first version **links to policies** but does not interpret or certify individual entitlement or reporting eligibility.")
    sources=[
        ("JSP 752 — Service expenses and allowances","https://www.gov.uk/government/publications/jsp-752-tri-service-regulations-for-expenses-and-allowances"),
        ("MOD Joint Service Publication index (JSP 757 may require internal access)","https://www.gov.uk/government/collections/joint-service-publication-jsp"),
        ("Discover My Benefits — Armed Forces","https://discovermybenefits.mod.gov.uk/"),
        ("Armed Forces Pension Calculator","https://www.gov.uk/armed-forces-pension-calculator"),
    ]
    for title,url in sources: st.markdown(f"- [{title}]({url})")
    st.warning("Always check the latest authorised guidance and your chain of command. Never upload restricted Defence documents to this public demo.")

st.divider()
st.caption("Forces HQ V0.1 • Independent proof of concept • No accounts, database, payments, AI API or automated notifications")
