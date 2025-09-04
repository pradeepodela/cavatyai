import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
from datetime import datetime
import pandas as pd
import asyncio
import os

# Page configuration
st.set_page_config(
    page_title="🦷 Dental Analysis Portal",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .info-card {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
        margin: 1rem 0;
    }
    .warning-card {
        background-color: #fff5f5;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #e53e3e;
        margin: 1rem 0;
    }
    .success-card {
        background-color: #f0fff4;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #38a169;
        margin: 1rem 0;
    }
    .cavity-stage {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        margin: 1rem 0;
    }
    .stage-0 { background-color: #c6f6d5; color: #22543d; }
    .stage-1 { background-color: #fed7d7; color: #742a2a; }
    .stage-2 { background-color: #fbb6ce; color: #702459; }
    .stage-3 { background-color: #fc8181; color: #742a2a; }
    .stage-4 { background-color: #e53e3e; color: white; }
</style>
""", unsafe_allow_html=True)

def encode_image(image):
    """Convert PIL image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def analyze_tooth_image(image, api_key):
    """Analyze tooth image using Gemini API through OpenRouter"""
    
    # Convert image to base64
    img_base64 = encode_image(image)
    
    # Comprehensive prompt for dental analysis
    prompt = """
    You are an expert dental AI assistant. Analyze this tooth/dental image and provide a comprehensive analysis in JSON format with the following structure:

    {
        "cavity_stage": "Stage 0-4 (0=No cavity, 1=Early enamel decay, 2=Dentin decay, 3=Pulp involvement, 4=Abscess/severe infection)",
        "cavity_present": true/false,
        "affected_teeth": ["list of affected tooth numbers if identifiable"],
        "severity_level": "None/Mild/Moderate/Severe/Critical",
        "visible_issues": ["list all visible dental issues"],
        "possible_causes": ["detailed list of possible causes for the observed condition"],
        "immediate_concerns": ["urgent issues requiring immediate attention"],
        "recommended_treatments": ["list of recommended treatments"],
        "prevention_tips": ["specific prevention advice"],
        "emergency_level": "None/Low/Medium/High/Critical",
        "estimated_timeline": "how long this condition likely took to develop",
        "prognosis": "likely outcome with and without treatment",
        "home_care_instructions": ["immediate home care steps"],
        "when_to_see_dentist": "timeline for dental visit",
        "additional_notes": "any other relevant observations"
    }

    Analyze the image carefully and provide detailed, accurate information. If you cannot clearly see dental issues, indicate uncertainty appropriately.
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "google/gemini-flash-1.5",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.3
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON response
            try:
                # Extract JSON from response if it's wrapped in text
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = content[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    return {"error": "No valid JSON found in response", "raw_response": content}
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON response", "raw_response": content}
        else:
            return {"error": f"API request failed with status {response.status_code}", "details": response.text}
    
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def display_analysis_results(analysis):
    """Display the analysis results in a structured format"""
    
    if "error" in analysis:
        st.error(f"Analysis Error: {analysis['error']}")
        if "raw_response" in analysis:
            st.text_area("Raw Response", analysis["raw_response"], height=200)
        return

    # Cavity Stage Display
    stage = analysis.get("cavity_stage", "Unknown")
    severity = analysis.get("severity_level", "Unknown")
    
    stage_num = "0"
    if "Stage" in stage:
        stage_num = stage.split()[1][0] if len(stage.split()) > 1 else "0"
    
    st.markdown(f"""
    <div class="cavity-stage stage-{stage_num}">
        🦷 {stage} - {severity} Severity
    </div>
    """, unsafe_allow_html=True)

    # Emergency Level Alert
    emergency = analysis.get("emergency_level", "None")
    if emergency in ["High", "Critical"]:
        st.markdown(f"""
        <div class="warning-card">
            <h3>⚠️ Emergency Alert: {emergency} Priority</h3>
            <p>Immediate dental attention recommended!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create columns for organized display
    col1, col2 = st.columns(2)
    
    with col1:
        # Visible Issues
        st.subheader("👁️ Visible Issues")
        issues = analysis.get("visible_issues", [])
        if issues:
            for issue in issues:
                st.write(f"• {issue}")
        else:
            st.write("No specific issues identified")
        
        # Possible Causes
        st.subheader("🔍 Possible Causes")
        causes = analysis.get("possible_causes", [])
        if causes:
            for cause in causes:
                st.write(f"• {cause}")
        
        # Affected Teeth
        affected = analysis.get("affected_teeth", [])
        if affected:
            st.subheader("🦷 Affected Teeth")
            st.write(", ".join(affected))
    
    with col2:
        # Recommended Treatments
        st.subheader("💉 Recommended Treatments")
        treatments = analysis.get("recommended_treatments", [])
        if treatments:
            for treatment in treatments:
                st.write(f"• {treatment}")
        
        # Immediate Concerns
        concerns = analysis.get("immediate_concerns", [])
        if concerns:
            st.subheader("🚨 Immediate Concerns")
            for concern in concerns:
                st.write(f"• {concern}")
        
        # When to See Dentist
        dentist_timeline = analysis.get("when_to_see_dentist", "As soon as possible")
        st.subheader("📅 Dental Visit Timeline")
        st.write(dentist_timeline)
    
    # Prevention and Care
    st.subheader("🛡️ Prevention Tips")
    prevention = analysis.get("prevention_tips", [])
    if prevention:
        for tip in prevention:
            st.write(f"• {tip}")
    
    st.subheader("🏠 Home Care Instructions")
    home_care = analysis.get("home_care_instructions", [])
    if home_care:
        for instruction in home_care:
            st.write(f"• {instruction}")
    
    # Additional Information
    with st.expander("📊 Additional Analysis Details"):
        col3, col4 = st.columns(2)
        
        with col3:
            st.write(f"**Estimated Timeline:** {analysis.get('estimated_timeline', 'Not specified')}")
            st.write(f"**Emergency Level:** {emergency}")
            
        with col4:
            st.write(f"**Cavity Present:** {'Yes' if analysis.get('cavity_present', False) else 'No'}")
        
        prognosis = analysis.get("prognosis", "Not provided")
        if prognosis != "Not provided":
            st.write(f"**Prognosis:** {prognosis}")
        
        notes = analysis.get("additional_notes", "")
        if notes:
            st.write(f"**Additional Notes:** {notes}")

def generate_audio_summary(analysis):
    """Generate a text summary suitable for audio narration"""
    if "error" in analysis:
        return "An error occurred during the dental analysis. Please try again with a different image."

    cavity_stage = analysis.get("cavity_stage", "Unknown")
    severity = analysis.get("severity_level", "Unknown")
    emergency = analysis.get("emergency_level", "None")

    summary = f"Dental Analysis Summary. Cavity stage: {cavity_stage}. Severity level: {severity}."

    if emergency in ["High", "Critical"]:
        summary += f" Emergency level: {emergency}. Immediate dental attention is recommended."

    visible_issues = analysis.get("visible_issues", [])
    if visible_issues:
        summary += f" Visible issues include: {', '.join(visible_issues)}."

    treatments = analysis.get("recommended_treatments", [])
    if treatments:
        summary += f" Recommended treatments: {', '.join(treatments)}."

    home_care = analysis.get("home_care_instructions", [])
    if home_care:
        summary += f" Home care instructions: {', '.join(home_care)}."

    dentist_timeline = analysis.get("when_to_see_dentist", "As soon as possible")
    summary += f" When to see dentist: {dentist_timeline}."

    return summary

async def generate_edge_tts_audio(text, voice="en-US-AriaNeural", rate="+0%", pitch="+0Hz"):
    """Generate audio file using Edge TTS"""
    try:
        import edge_tts
        import tempfile

        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name

        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(temp_path)

        return temp_path
    except ImportError:
        st.error("Edge TTS is not installed. Please install it with: pip install edge-tts")
        return None
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🦷 Dental Analysis Portal</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("OpenRouter API Key", type="password", help="Enter your OpenRouter API key")
        
        st.header("📋 Instructions")
        st.markdown("""
        1. Enter your OpenRouter API key
        2. Upload a clear image of the tooth/teeth
        3. Click 'Analyze Image' for detailed analysis
        4. Review the comprehensive report
        
        **Image Tips:**
        - Use good lighting
        - Keep the camera steady
        - Focus on the affected area
        - Avoid blurry images
        """)
        
        st.header("⚠️ Disclaimer")
        st.warning("This AI analysis is for educational purposes only and should not replace professional dental consultation. Always consult with a qualified dentist for proper diagnosis and treatment.")
    
    # Main content area
    if not api_key:
        st.markdown("""
        <div class="info-card">
            <h3>Welcome to the Dental Analysis Portal</h3>
            <p>This AI-powered tool helps analyze dental images to identify potential cavities and provide comprehensive oral health insights.</p>
            <p>Please enter your OpenRouter API key in the sidebar to get started.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # File upload
    uploaded_file = st.file_uploader(
        "📤 Upload Tooth Image", 
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of the tooth or dental area you want analyzed"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Analysis button
        if st.button("🔍 Analyze Image", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is analyzing your dental image... This may take a few moments."):
                analysis = analyze_tooth_image(image, api_key)
                
                st.header("📊 Analysis Results")
                display_analysis_results(analysis)

                # Audio options - show immediately after analysis
                if "error" not in analysis:
                    st.header("🎵 Audio Options")

                    audio_summary = generate_audio_summary(analysis)

                    col_audio1, col_audio2 = st.columns(2)

                    with col_audio1:
                        st.download_button(
                            label="🎙️ Download Audio Script",
                            data=audio_summary,
                            file_name=f"dental_audio_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )

                    with col_audio2:
                        # Audio generation state management
                        if "audio_generated" not in st.session_state:
                            st.session_state.audio_generated = False
                            st.session_state.audio_bytes = None
                            st.session_state.audio_filename = None

                        if st.button("🎵 Generate & Download MP3", key="download_mp3"):
                            with st.spinner("🎙️ Generating MP3 audio file..."):
                                audio_path = asyncio.run(generate_edge_tts_audio(
                                    audio_summary,
                                    "en-US-AriaNeural",
                                    "+0%",
                                    "+0Hz"
                                ))

                                if audio_path:
                                    with open(audio_path, "rb") as audio_file:
                                        st.session_state.audio_bytes = audio_file.read()
                                    st.session_state.audio_filename = f"dental_analysis_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                                    st.session_state.audio_generated = True
                                    os.unlink(audio_path)
                                    st.success("✅ Audio generated successfully!")
                                else:
                                    st.error("❌ Failed to generate audio. Please try again.")

                        # Show download button if audio was generated
                        if st.session_state.audio_generated and st.session_state.audio_bytes:
                            st.download_button(
                                label="💾 Download MP3 Audio",
                                data=st.session_state.audio_bytes,
                                file_name=st.session_state.audio_filename,
                                mime="audio/mp3",
                                key="final_download"
                            )

                # Save analysis option
                if "error" not in analysis:
                    analysis_data = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "analysis": analysis
                    }

                    if st.button("💾 Save Analysis Report"):
                        # Convert to downloadable format
                        report_text = f"""
DENTAL ANALYSIS REPORT
Generated: {analysis_data['timestamp']}

Cavity Stage: {analysis.get('cavity_stage', 'Unknown')}
Severity: {analysis.get('severity_level', 'Unknown')}
Emergency Level: {analysis.get('emergency_level', 'None')}

Visible Issues:
{chr(10).join([f"• {issue}" for issue in analysis.get('visible_issues', [])])}

Possible Causes:
{chr(10).join([f"• {cause}" for cause in analysis.get('possible_causes', [])])}

Recommended Treatments:
{chr(10).join([f"• {treatment}" for treatment in analysis.get('recommended_treatments', [])])}

Prevention Tips:
{chr(10).join([f"• {tip}" for tip in analysis.get('prevention_tips', [])])}

Home Care Instructions:
{chr(10).join([f"• {instruction}" for instruction in analysis.get('home_care_instructions', [])])}

When to See Dentist: {analysis.get('when_to_see_dentist', 'As soon as possible')}
                        """

                        st.download_button(
                            label="� Download Report",
                            data=report_text,
                            file_name=f"dental_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
    
    # Educational content
    st.header("📚 Cavity Stages Guide")
    
    stages_info = {
        "Stage 0": ("No Cavity", "Healthy tooth or very early demineralization", "#c6f6d5"),
        "Stage 1": ("Early Enamel Decay", "White spots or early enamel damage", "#fed7d7"),
        "Stage 2": ("Dentin Decay", "Cavity has reached the dentin layer", "#fbb6ce"),
        "Stage 3": ("Pulp Involvement", "Infection has reached the tooth's pulp", "#fc8181"),
        "Stage 4": ("Abscess/Severe", "Advanced infection, possible abscess", "#e53e3e")
    }
    
    cols = st.columns(5)
    for i, (stage, (title, desc, color)) in enumerate(stages_info.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background-color: {color}; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4>{stage}</h4>
                <p><strong>{title}</strong></p>
                <p style="font-size: 0.9em;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
            analysis = analyze_tooth_image(image, api_key)
            progress_bar.progress(50)
            
            if "error" not in analysis:
                # Step 2: Generate Audio Summary
                status_text.text("🎙️ Generating audio summary...")
                progress_bar.progress(70)
                
                audio_summary = generate_audio_summary(analysis)
                
                # Step 3: Create Audio File
                status_text.text("🎵 Creating audio file...")
                progress_bar.progress(90)
                
                audio_path = run_async_audio_generation(audio_summary)
                
                # Complete
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display Results
                st.header("📊 Analysis Results")
                display_analysis_results(analysis)
                
                # Audio Section
                st.markdown("""
                <div class="audio-section">
                    <h3>🎵 Audio Summary</h3>
                    <p>Listen to your dental analysis summary below:</p>
                </div>
                """, unsafe_allow_html=True)
                
                if audio_path and os.path.exists(audio_path):
                    # Read audio file and display player
                    with open(audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                    
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    # Download options
                    col_dl1, col_dl2, col_dl3 = st.columns(3)
                    
                    with col_dl1:
                        st.download_button(
                            label="💾 Download Audio",
                            data=audio_bytes,
                            file_name=f"dental_analysis_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                            mime="audio/mp3"
                        )
                    
                    with col_dl2:
                        st.download_button(
                            label="📄 Download Report",
                            data=create_downloadable_report(analysis),
                            file_name=f"dental_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    
                    with col_dl3:
                        st.download_button(
                            label="📝 Download Script",
                            data=audio_summary,
                            file_name=f"dental_audio_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    
                    # Clean up temporary file
                    try:
                        os.unlink(audio_path)
                    except:
                        pass
                        
                else:
                    st.warning("🔊 Audio generation failed, but you can still download the text summary:")
                    st.text_area("Audio Script", audio_summary, height=150)
                    
                    col_script1, col_script2 = st.columns(2)
                    with col_script1:
                        st.download_button(
                            label="📝 Download Script",
                            data=audio_summary,
                            file_name=f"dental_audio_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    with col_script2:
                        st.download_button(
                            label="📄 Download Report",
                            data=create_downloadable_report(analysis),
                            file_name=f"dental_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
            
            else:
                # Clear progress indicators on error
                progress_bar.empty()
                status_text.empty()
                
                st.header("❌ Analysis Failed")
                st.error(f"Analysis Error: {analysis['error']}")
                if "raw_response" in analysis:
                    st.text_area("Raw Response", analysis["raw_response"], height=200)
    
    # Educational content
    st.header("📚 Cavity Stages Guide")
    
    stages_info = {
        "Stage 0": ("No Cavity", "Healthy tooth or very early demineralization", "#c6f6d5"),
        "Stage 1": ("Early Enamel Decay", "White spots or early enamel damage", "#fed7d7"),
        "Stage 2": ("Dentin Decay", "Cavity has reached the dentin layer", "#fbb6ce"),
        "Stage 3": ("Pulp Involvement", "Infection has reached the tooth's pulp", "#fc8181"),
        "Stage 4": ("Abscess/Severe", "Advanced infection, possible abscess", "#e53e3e")
    }
    
    cols = st.columns(5)
    for i, (stage, (title, desc, color)) in enumerate(stages_info.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background-color: {color}; padding: 1rem; border-radius: 8px; text-align: center;">
                <h4>{stage}</h4>
                <p><strong>{title}</strong></p>
                <p style="font-size: 0.9em;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
