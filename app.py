import streamlit as st
from news_utils import load_rss_sources, fetch_articles, generate_journalist_story
from pdf_utils import generate_news_pdf
from datetime import datetime
import base64
import os

st.set_page_config(page_title="IAcine News Feed", page_icon="🌐")
st.title("📰 Your Daily News in Live with IAcine")

st.markdown("""
Welcome! I'm **IAcine**, your AI-powered news assistant. Just type a topic (like "cyber", "AI", "politics", etc.), and I’ll summarize the most recent global events with context, storytelling, and clickable sources.
""")

keyword = st.text_input("🔍 What topic are you interested in?")
question = st.text_area("🤔 Got a specific question about this topic? (Optional)")

if keyword:
    with st.spinner("📡 Scanning RSS feeds and writing your news story..."):
        feeds = load_rss_sources()
        articles = fetch_articles(keyword, feeds)

    if articles:
        st.success(f"✅ I found {len(articles)} relevant articles. Here's your news report:")
        story = generate_journalist_story(articles)
        st.markdown(story, unsafe_allow_html=True)

        pdf_path = generate_news_pdf(
            content=story,
            filename="iacine_news_report.pdf",
            header_logo="logo1.png",
            footer_logo="logo2.png",
            author="IAcine"
        )

        with open(pdf_path, "rb") as f:
            b64_pdf = base64.b64encode(f.read()).decode()
            st.markdown(f'''
                <a href="data:application/octet-stream;base64,{b64_pdf}" download="iacine_news_report.pdf">
                    <button style="padding:10px 20px; font-size:16px;">📄 Download Professional PDF Report</button>
                </a>
            ''', unsafe_allow_html=True)


        if question:
            with st.spinner("✍️ Let me think..."):
                from openai import OpenAI
                from dotenv import load_dotenv
                load_dotenv()
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

                context = story + f"\n\nUser question: {question}"
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": context}],
                    max_tokens=500
                )
                st.markdown("### 💬 IAcine’s Answer:")
                st.write(response.choices[0].message.content.strip())
    else:
        st.warning("⚠️ No recent news found for that keyword. Try another one!")