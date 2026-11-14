"""Shared Ask experience used by Home and policy finder."""
import streamlit as st
from policy_engine import PolicyIndex, INTENTS, CATALOGUE, answer, classify
from session_inputs import SessionInputs


def render_question(profile,navigate,pages):
    ui=SessionInputs(pages[4])
    question=ui.text_input('What do you need help with?',placeholder='Can I claim my lunch back today?',key='guided_search',max_chars=1500)
    st.caption('Document search and guided checks · No generative AI or automatic eligibility decisions')
    if not question.strip():
        st.info('Ask about meals, mileage, posting, pensions, leave or career support.')
        return
    st.session_state.active_question=question
    intent=classify(question)
    topic=INTENTS.get(intent,{})
    circumstances={}
    if topic.get('questions'):
        with st.expander('Clarify your circumstances',expanded=True):
            for key,label,options in topic['questions']:
                circumstances[key]=ui.selectbox(label,options,key=key)
    result=answer(question,profile,circumstances)
    st.markdown('#### '+result['subject'])
    st.markdown('**Answer**')
    st.write(result['answer'])
    # Keep authorisation status explicit; profile data cannot award an allowance.
    if intent=='mileage' and circumstances.get('v07_approved')=='No':
        st.info('Duty mileage is not confirmed without the required authorisation. Check with unit admin before claiming.')
    st.caption(result['status'])
    st.markdown('**Why**')
    if result['missing']:
        st.write('Still unknown: '+'; '.join(result['missing']))
    else:
        st.write('The circumstances are recorded, but exceptions, current rules and evidence still require checking. These answers do not confirm eligibility.')
    st.markdown('**Policy reference and supporting evidence**')
    if not result['hits']:
        st.warning('Source unavailable: no relevant passage is available in the local official-document index. I cannot verify a chapter, paragraph, quotation or entitlement for this question.')
        for source_id in result['source_ids']:
            if source_id in CATALOGUE:st.link_button('Check official publication: '+source_id,CATALOGUE[source_id][1])
    else:
        for hit in result['hits']:
            locator=' · '.join(v for v in (hit['source_id'],hit['chapter'],hit['section'],('paragraph '+hit['paragraph']) if hit['paragraph'] else '',f"PDF page {hit['page']}") if v)
            st.markdown('**'+locator+'**')
            st.caption('Extract from the indexed document (whitespace normalised)')
            st.write(hit['text'][:500]+('…' if len(hit['text'])>500 else ''))
            st.link_button('Open source at page '+str(hit['page']),hit['url']+'#page='+str(hit['page']))
            st.caption('Retrieved '+hit['retrieved_at'][:10]+' · SHA-256 '+hit['sha256'][:12]+' · Check publication page for later revisions')
    st.markdown('**What applies to me**')
    st.write(result['context'])
    st.markdown('**Next step**')
    st.write('Resolve the missing circumstances above, read the full provision and exceptions, and confirm the authorised claim or advice route with unit staff. No claim has been submitted.')
    related={'entitlements':(3,'Explore related entitlements'),'pension':(8,'Open pay and pension scenario'),'career':(5,'Open career milestones')}
    if result['related'] in related:
        index,label=related[result['related']]
        st.button(label,on_click=navigate,args=(pages[index],),key='ask_related')
    with st.expander('Source availability and search method'):
        status=PolicyIndex().status()
        st.write('Local corpus: '+status['state'])
        st.caption('Full-text BM25 retrieval with subject expansion and relevance filters. Clarifications are retained in this session. The question and profile are not sent to an external AI service. A retrieved passage is evidence, not an eligibility ruling.')
        for document in status.get('documents',[]):st.caption(document['source_id']+' · '+document['title']+' · '+document['retrieved_at'][:10])
        for error in status.get('errors',[]):st.caption(str(error.get('source',''))+': retrieval unavailable')
