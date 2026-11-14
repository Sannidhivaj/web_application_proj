
import streamlit as st
import os
import re
import zipfile
from io import BytesIO
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEM") or os.getenv("GOOGLE_API_KEY")

# Streamlit page settings
st.set_page_config(
    page_title="AI Website Creator",
    page_icon="🪄"
)

st.title("🪄 Sannidhi's AI Website Creator")
st.write("Turn your ideas into a website with AI!")

up = st.text_area(
    "Enter your website idea here:",
    placeholder="Example: Create a modern portfolio website.",
    height=150
)

if st.button("✨ Generate Website"):

    if not up.strip():
        st.warning("Please enter your website idea first.")

    elif not API_KEY:
        st.error(
            "Gemini API key not found. Add GEM=your_api_key "
            "to your .env file."
        )

    else:
        try:
            with st.spinner("Creating your website... 🪄"):

                model = ChatGoogleGenerativeAI(
                    model="gemini-3.5-flash-lite",
                    google_api_key=API_KEY,
                    temperature=0.7
                )

                prompt = [
                    (
                        "system",
                        """
You are an experienced frontend web developer.

Generate a complete, attractive, responsive frontend website
based on the user's idea.

Return ONLY the code using exactly these markers:

--html--
HTML CODE HERE
--html--

--css--
CSS CODE HERE
--css--

--js--
JAVASCRIPT CODE HERE
--js--

Requirements:
1. HTML must be complete and valid.
2. Put CSS only in the CSS section.
3. Put JavaScript only in the JavaScript section.
4. The HTML must link to style.css.
5. The HTML must load script.js.
6. Make the website responsive and visually appealing.
7. Do not use Markdown code fences.
8. Do not omit any of the required markers.
"""
                    ),
                    ("user", up)
                ]

                response = model.invoke(prompt).content

                # Handle responses returned as text blocks
                if isinstance(response, list):
                    response = "".join(
                        block.get("text", "")
                        if isinstance(block, dict)
                        else str(block)
                        for block in response
                    )

                # Extract HTML, CSS, and JavaScript
                def extract_section(text, section):
                    pattern = (
                        rf"--{section}--\s*"
                        rf"(.*?)"
                        rf"\s*--{section}--"
                    )

                    match = re.search(
                        pattern,
                        text,
                        flags=re.DOTALL | re.IGNORECASE
                    )

                    if not match:
                        raise ValueError(
                            f"Could not find the {section} section. "
                            "Please generate the website again."
                        )

                    return match.group(1).strip()

                html_code = extract_section(response, "html")
                css_code = extract_section(response, "css")
                js_code = extract_section(response, "js")

                # Create ZIP file in memory
                zip_buffer = BytesIO()

                with zipfile.ZipFile(
                    zip_buffer,
                    "w",
                    zipfile.ZIP_DEFLATED
                ) as zip_file:

                    zip_file.writestr("index.html", html_code)
                    zip_file.writestr("style.css", css_code)
                    zip_file.writestr("script.js", js_code)

                zip_buffer.seek(0)

                # Save ZIP for downloading
                st.session_state["website_zip"] = (
                    zip_buffer.getvalue()
                )

            st.success(
                "Your website has been generated successfully! 🎉"
            )

        except Exception as error:
            st.error(f"Something went wrong: {error}")

# Display the download button
if st.session_state.get("website_zip"):

    st.download_button(
        label="📦 Download Your Website",
        data=st.session_state["website_zip"],
        file_name="website.zip",
        mime="application/zip",
        use_container_width=True
    )
