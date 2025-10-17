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
import tempfile
from dotenv import load_dotenv
import cv2
import numpy as np
import matplotlib.pyplot as plt
import ssl
import certifi

# Fix SSL context for Edge TTS
ssl._create_default_https_context = ssl._create_unverified_context
load_dotenv()

# Language translations dictionary
TRANSLATIONS = {
    "en": {
        "page_title": "🦷 Dental Analysis Portal",
        "main_header": "🦷 Dental Analysis Portal",
        "config": "⚙️ Configuration",
        "api_key_found": "✅ OpenRouter API Key found in environment variables",
        "api_key_not_found": "⚠️ OpenRouter API Key not found in environment variables",
        "api_key_label": "OpenRouter API Key",
        "language_selection": "🌍 Language / भाषा / Idioma",
        "audio_settings": "🎵 Audio Settings",
        "voice_selection": "Voice Selection",
        "speech_speed": "Speech Speed",
        "instructions": "📋 Instructions",
        "instructions_text": """
        1. Enter your OpenRouter API key
        2. Upload a clear image of the tooth/teeth
        3. Click 'Analyze Image' for instant analysis
        4. Get both report and audio summary automatically
        
        **Image Tips:**
        - Use good lighting
        - Keep the camera steady
        - Focus on the affected area
        - Avoid blurry images
        """,
        "disclaimer": "⚠️ Disclaimer",
        "disclaimer_text": "This AI analysis is for educational purposes only and should not replace professional dental consultation. Always consult with a qualified dentist for proper diagnosis and treatment.",
        "welcome_title": "Welcome to the Dental Analysis Portal",
        "welcome_text": "This AI-powered tool helps analyze dental images to identify potential cavities and provide comprehensive oral health insights with instant audio summaries.",
        "enter_api_key": "Please enter your OpenRouter API key in the sidebar to get started.",
        "upload_image": "📤 Upload Tooth Image",
        "upload_help": "Upload a clear image of the tooth or dental area you want analyzed",
        "uploaded_image": "Uploaded Image",
        "analyze_button": "🔍 Analyze Image & Generate Audio",
        "analyzing": "🤖 Analyzing dental image...",
        "generating_audio": "🎙️ Generating audio summary...",
        "creating_audio": "🎵 Creating audio file...",
        "analysis_complete": "✅ Analysis complete!",
        "analysis_results": "📊 Analysis Results",
        "audio_summary": "🎵 Audio Summary",
        "audio_summary_text": "Listen to your dental analysis summary below:",
        "download_audio": "💾 Download Audio",
        "download_report": "📄 Download Report",
        "download_script": "📝 Download Script",
        "audio_failed": "🔊 Audio generation failed, but you can still download the text summary:",
        "audio_script": "Audio Script",
        "analysis_failed": "❌ Analysis Failed",
        "cavity_stages_guide": "📚 Cavity Stages Guide",
        "stage_0": "No Cavity",
        "stage_0_desc": "Healthy tooth or very early demineralization",
        "stage_1": "Early Enamel Decay",
        "stage_1_desc": "White spots or early enamel damage",
        "stage_2": "Dentin Decay",
        "stage_2_desc": "Cavity has reached the dentin layer",
        "stage_3": "Pulp Involvement",
        "stage_3_desc": "Infection has reached the tooth's pulp",
        "stage_4": "Abscess/Severe",
        "stage_4_desc": "Advanced infection, possible abscess",
        "visible_issues": "👁️ Visible Issues",
        "possible_causes": "🔍 Possible Causes",
        "affected_teeth": "🦷 Affected Teeth",
        "recommended_treatments": "💉 Recommended Treatments",
        "immediate_concerns": "🚨 Immediate Concerns",
        "dentist_timeline": "📅 Dental Visit Timeline",
        "prevention_tips": "🛡️ Prevention Tips",
        "home_care": "🏠 Home Care Instructions",
        "additional_details": "📊 Additional Analysis Details",
        "emergency_alert": "⚠️ Emergency Alert",
        "emergency_text": "Immediate dental attention recommended!",
        "image_processing": "🖼️ Image Processing & Analysis",
        "grayscale": "Grayscale",
        "edge_detection": "Canny Edge Detection",
        "clahe_enhanced": "CLAHE Enhanced",
        "histogram_title": "Histogram of Pixel Intensities",
        "pixel_intensity": "Pixel Intensity",
        "frequency": "Frequency"
    },
    "hi": {
        "page_title": "🦷 दंत विश्लेषण पोर्टल",
        "main_header": "🦷 दंत विश्लेषण पोर्टल",
        "config": "⚙️ कॉन्फ़िगरेशन",
        "api_key_found": "✅ OpenRouter API कुंजी पर्यावरण चर में मिली",
        "api_key_not_found": "⚠️ OpenRouter API कुंजी पर्यावरण चर में नहीं मिली",
        "api_key_label": "OpenRouter API कुंजी",
        "language_selection": "🌍 भाषा चुनें / Language / Idioma",
        "audio_settings": "🎵 ऑडियो सेटिंग्स",
        "voice_selection": "आवाज़ चयन",
        "speech_speed": "बोलने की गति",
        "instructions": "📋 निर्देश",
        "instructions_text": """
        1. अपनी OpenRouter API कुंजी दर्ज करें
        2. दांत/दांतों की स्पष्ट तस्वीर अपलोड करें
        3. त्वरित विश्लेषण के लिए 'छवि विश्लेषण करें' पर क्लिक करें
        4. स्वचालित रूप से रिपोर्ट और ऑडियो सारांश प्राप्त करें
        
        **छवि सुझाव:**
        - अच्छी रोशनी का उपयोग करें
        - कैमरा स्थिर रखें
        - प्रभावित क्षेत्र पर फोकस करें
        - धुंधली छवियों से बचें
        """,
        "disclaimer": "⚠️ अस्वीकरण",
        "disclaimer_text": "यह AI विश्लेषण केवल शैक्षिक उद्देश्यों के लिए है और पेशेवर दंत परामर्श का स्थान नहीं ले सकता। उचित निदान और उपचार के लिए हमेशा योग्य दंत चिकित्सक से परामर्श करें।",
        "welcome_title": "दंत विश्लेषण पोर्टल में आपका स्वागत है",
        "welcome_text": "यह AI-संचालित उपकरण दंत छवियों का विश्लेषण करने में मदद करता है ताकि संभावित कैविटी की पहचान की जा सके और तत्काल ऑडियो सारांश के साथ व्यापक मौखिक स्वास्थ्य जानकारी प्रदान की जा सके।",
        "enter_api_key": "शुरू करने के लिए कृपया साइडबार में अपनी OpenRouter API कुंजी दर्ज करें।",
        "upload_image": "📤 दांत की छवि अपलोड करें",
        "upload_help": "विश्लेषण के लिए दांत या दंत क्षेत्र की स्पष्ट छवि अपलोड करें",
        "uploaded_image": "अपलोड की गई छवि",
        "analyze_button": "🔍 छवि विश्लेषण करें और ऑडियो बनाएं",
        "analyzing": "🤖 दंत छवि का विश्लेषण कर रहे हैं...",
        "generating_audio": "🎙️ ऑडियो सारांश बना रहे हैं...",
        "creating_audio": "🎵 ऑडियो फ़ाइल बना रहे हैं...",
        "analysis_complete": "✅ विश्लेषण पूर्ण!",
        "analysis_results": "📊 विश्लेषण परिणाम",
        "audio_summary": "🎵 ऑडियो सारांश",
        "audio_summary_text": "नीचे अपने दंत विश्लेषण सारांश को सुनें:",
        "download_audio": "💾 ऑडियो डाउनलोड करें",
        "download_report": "📄 रिपोर्ट डाउनलोड करें",
        "download_script": "📝 स्क्रिप्ट डाउनलोड करें",
        "audio_failed": "🔊 ऑडियो जेनरेशन विफल रहा, लेकिन आप अभी भी टेक्स्ट सारांश डाउनलोड कर सकते हैं:",
        "audio_script": "ऑडियो स्क्रिप्ट",
        "analysis_failed": "❌ विश्लेषण विफल",
        "cavity_stages_guide": "📚 कैविटी चरण गाइड",
        "stage_0": "कोई कैविटी नहीं",
        "stage_0_desc": "स्वस्थ दांत या बहुत प्रारंभिक डीमिनरलाइजेशन",
        "stage_1": "प्रारंभिक इनेमल क्षय",
        "stage_1_desc": "सफेद धब्बे या प्रारंभिक इनेमल क्षति",
        "stage_2": "डेंटिन क्षय",
        "stage_2_desc": "कैविटी डेंटिन परत तक पहुंच गई है",
        "stage_3": "पल्प संलग्नता",
        "stage_3_desc": "संक्रमण दांत के पल्प तक पहुंच गया है",
        "stage_4": "फोड़ा/गंभीर",
        "stage_4_desc": "उन्नत संक्रमण, संभावित फोड़ा",
        "visible_issues": "👁️ दिखाई देने वाली समस्याएं",
        "possible_causes": "🔍 संभावित कारण",
        "affected_teeth": "🦷 प्रभावित दांत",
        "recommended_treatments": "💉 अनुशंसित उपचार",
        "immediate_concerns": "🚨 तत्काल चिंताएं",
        "dentist_timeline": "📅 दंत चिकित्सक की यात्रा समयरेखा",
        "prevention_tips": "🛡️ रोकथाम युक्तियाँ",
        "home_care": "🏠 घरेलू देखभाल निर्देश",
        "additional_details": "📊 अतिरिक्त विश्लेषण विवरण",
        "emergency_alert": "⚠️ आपातकालीन चेतावनी",
        "emergency_text": "तत्काल दंत चिकित्सा ध्यान अनुशंसित!",
        "image_processing": "🖼️ छवि प्रसंस्करण और विश्लेषण",
        "grayscale": "ग्रेस्केल",
        "edge_detection": "कैनी एज डिटेक्शन",
        "clahe_enhanced": "CLAHE एन्हांस्ड",
        "histogram_title": "पिक्सेल तीव्रता का हिस्टोग्राम",
        "pixel_intensity": "पिक्सेल तीव्रता",
        "frequency": "आवृत्ति"
    },
    "es": {
        "page_title": "🦷 Portal de Análisis Dental",
        "main_header": "🦷 Portal de Análisis Dental",
        "config": "⚙️ Configuración",
        "api_key_found": "✅ Clave API de OpenRouter encontrada en variables de entorno",
        "api_key_not_found": "⚠️ Clave API de OpenRouter no encontrada en variables de entorno",
        "api_key_label": "Clave API de OpenRouter",
        "language_selection": "🌍 Seleccionar Idioma / Language / भाषा",
        "audio_settings": "🎵 Configuración de Audio",
        "voice_selection": "Selección de Voz",
        "speech_speed": "Velocidad del Habla",
        "instructions": "📋 Instrucciones",
        "instructions_text": """
        1. Ingrese su clave API de OpenRouter
        2. Cargue una imagen clara del diente/dientes
        3. Haga clic en 'Analizar Imagen' para análisis instantáneo
        4. Obtenga automáticamente el informe y resumen de audio
        
        **Consejos de Imagen:**
        - Use buena iluminación
        - Mantenga la cámara estable
        - Enfoque en el área afectada
        - Evite imágenes borrosas
        """,
        "disclaimer": "⚠️ Descargo de Responsabilidad",
        "disclaimer_text": "Este análisis de IA es solo para fines educativos y no debe reemplazar la consulta dental profesional. Siempre consulte con un dentista calificado para un diagnóstico y tratamiento adecuados.",
        "welcome_title": "Bienvenido al Portal de Análisis Dental",
        "welcome_text": "Esta herramienta impulsada por IA ayuda a analizar imágenes dentales para identificar posibles caries y proporcionar información completa sobre la salud bucal con resúmenes de audio instantáneos.",
        "enter_api_key": "Por favor, ingrese su clave API de OpenRouter en la barra lateral para comenzar.",
        "upload_image": "📤 Cargar Imagen Dental",
        "upload_help": "Cargue una imagen clara del diente o área dental que desea analizar",
        "uploaded_image": "Imagen Cargada",
        "analyze_button": "🔍 Analizar Imagen y Generar Audio",
        "analyzing": "🤖 Analizando imagen dental...",
        "generating_audio": "🎙️ Generando resumen de audio...",
        "creating_audio": "🎵 Creando archivo de audio...",
        "analysis_complete": "✅ ¡Análisis completo!",
        "analysis_results": "📊 Resultados del Análisis",
        "audio_summary": "🎵 Resumen de Audio",
        "audio_summary_text": "Escuche su resumen de análisis dental a continuación:",
        "download_audio": "💾 Descargar Audio",
        "download_report": "📄 Descargar Informe",
        "download_script": "📝 Descargar Guión",
        "audio_failed": "🔊 La generación de audio falló, pero aún puede descargar el resumen de texto:",
        "audio_script": "Guión de Audio",
        "analysis_failed": "❌ Análisis Fallido",
        "cavity_stages_guide": "📚 Guía de Etapas de Caries",
        "stage_0": "Sin Caries",
        "stage_0_desc": "Diente sano o desmineralización muy temprana",
        "stage_1": "Caries Temprana del Esmalte",
        "stage_1_desc": "Manchas blancas o daño temprano del esmalte",
        "stage_2": "Caries de Dentina",
        "stage_2_desc": "La caries ha alcanzado la capa de dentina",
        "stage_3": "Afectación Pulpar",
        "stage_3_desc": "La infección ha alcanzado la pulpa del diente",
        "stage_4": "Absceso/Grave",
        "stage_4_desc": "Infección avanzada, posible absceso",
        "visible_issues": "👁️ Problemas Visibles",
        "possible_causes": "🔍 Causas Posibles",
        "affected_teeth": "🦷 Dientes Afectados",
        "recommended_treatments": "💉 Tratamientos Recomendados",
        "immediate_concerns": "🚨 Preocupaciones Inmediatas",
        "dentist_timeline": "📅 Cronograma de Visita al Dentista",
        "prevention_tips": "🛡️ Consejos de Prevención",
        "home_care": "🏠 Instrucciones de Cuidado en Casa",
        "additional_details": "📊 Detalles Adicionales del Análisis",
        "emergency_alert": "⚠️ Alerta de Emergencia",
        "emergency_text": "¡Se recomienda atención dental inmediata!",
        "image_processing": "🖼️ Procesamiento y Análisis de Imagen",
        "grayscale": "Escala de Grises",
        "edge_detection": "Detección de Bordes Canny",
        "clahe_enhanced": "Mejorado CLAHE",
        "histogram_title": "Histograma de Intensidades de Píxeles",
        "pixel_intensity": "Intensidad de Píxel",
        "frequency": "Frecuencia"
    },
    "ta": {
        "page_title": "🦷 பல் பகுப்பாய்வு போர்டல்",
        "main_header": "🦷 பல் பகுப்பாய்வு போர்டல்",
        "config": "⚙️ உள்ளமைவு",
        "api_key_found": "✅ OpenRouter API விசை சூழல் மாறிகளில் கண்டறியப்பட்டது",
        "api_key_not_found": "⚠️ OpenRouter API விசை சூழல் மாறிகளில் காணப்படவில்லை",
        "api_key_label": "OpenRouter API விசை",
        "language_selection": "🌍 மொழியைத் தேர்ந்தெடுக்கவும் / Language / भाषा",
        "audio_settings": "🎵 ஆடியோ அமைப்புகள்",
        "voice_selection": "குரல் தேர்வு",
        "speech_speed": "பேச்சு வேகம்",
        "instructions": "📋 வழிமுறைகள்",
        "instructions_text": """
        1. உங்கள் OpenRouter API விசையை உள்ளிடவும்
        2. பல்/பற்களின் தெளிவான படத்தை பதிவேற்றவும்
        3. உடனடி பகுப்பாய்வுக்கு 'படத்தை பகுப்பாய்வு செய்' என்பதைக் கிளிக் செய்யவும்
        4. தானாகவே அறிக்கை மற்றும் ஆடியோ சுருக்கத்தைப் பெறவும்
        
        **படம் குறிப்புகள்:**
        - நல்ல வெளிச்சத்தைப் பயன்படுத்தவும்
        - கேமராவை நிலையாக வைக்கவும்
        - பாதிக்கப்பட்ட பகுதியில் கவனம் செலுத்தவும்
        - மங்கலான படங்களைத் தவிர்க்கவும்
        """,
        "disclaimer": "⚠️ மறுப்பு",
        "disclaimer_text": "இந்த AI பகுப்பாய்வு கல்வி நோக்கங்களுக்காக மட்டுமே மற்றும் தொழில்முறை பல் ஆலோசனையை மாற்றக்கூடாது. சரியான நோய் கண்டறிதல் மற்றும் சிகிச்சைக்கு எப்போதும் தகுதிவாய்ந்த பல் மருத்துவரை அணுகவும்.",
        "welcome_title": "பல் பகுப்பாய்வு போர்டலுக்கு வரவேற்கிறோம்",
        "welcome_text": "இந்த AI-இயங்கும் கருவி பல் படங்களை பகுப்பாய்வு செய்து சாத்தியமான குழிகளை அடையாளம் காணவும் உடனடி ஆடியோ சுருக்கங்களுடன் விரிவான வாய் சுகாதார நுண்ணறிவுகளை வழங்கவும் உதவுகிறது.",
        "enter_api_key": "தொடங்க பக்கப்பட்டையில் உங்கள் OpenRouter API விசையை உள்ளிடவும்.",
        "upload_image": "📤 பல் படத்தை பதிவேற்றவும்",
        "upload_help": "நீங்கள் பகுப்பாய்வு செய்ய விரும்பும் பல் அல்லது பல் பகுதியின் தெளிவான படத்தை பதிவேற்றவும்",
        "uploaded_image": "பதிவேற்றப்பட்ட படம்",
        "analyze_button": "🔍 படத்தை பகுப்பாய்வு செய்து ஆடியோவை உருவாக்கவும்",
        "analyzing": "🤖 பல் படத்தை பகுப்பாய்வு செய்கிறது...",
        "generating_audio": "🎙️ ஆடியோ சுருக்கத்தை உருவாக்குகிறது...",
        "creating_audio": "🎵 ஆடியோ கோப்பை உருவாக்குகிறது...",
        "analysis_complete": "✅ பகுப்பாய்வு முடிந்தது!",
        "analysis_results": "📊 பகுப்பாய்வு முடிவுகள்",
        "audio_summary": "🎵 ஆடியோ சுருக்கம்",
        "audio_summary_text": "கீழே உங்கள் பல் பகுப்பாய்வு சுருக்கத்தைக் கேளுங்கள்:",
        "download_audio": "💾 ஆடியோவை பதிவிறக்கவும்",
        "download_report": "📄 அறிக்கையை பதிவிறக்கவும்",
        "download_script": "📝 ஸ்கிரிப்டை பதிவிறக்கவும்",
        "audio_failed": "🔊 ஆடியோ உருவாக்கம் தோல்வியுற்றது, ஆனால் நீங்கள் இன்னும் உரை சுருக்கத்தை பதிவிறக்கலாம்:",
        "audio_script": "ஆடியோ ஸ்கிரிப்ட்",
        "analysis_failed": "❌ பகுப்பாய்வு தோல்வியடைந்தது",
        "cavity_stages_guide": "📚 குழி நிலைகள் வழிகாட்டி",
        "stage_0": "குழி இல்லை",
        "stage_0_desc": "ஆரோக்கியமான பல் அல்லது மிக ஆரம்ப நீர்மின்மாற்றம்",
        "stage_1": "ஆரம்ப பற்சிப்பி சிதைவு",
        "stage_1_desc": "வெள்ளை புள்ளிகள் அல்லது ஆரம்ப பற்சிப்பி சேதம்",
        "stage_2": "டென்டின் சிதைவு",
        "stage_2_desc": "குழி டென்டின் அடுக்கை அடைந்துள்ளது",
        "stage_3": "கூழ் சம்பந்தப்படுதல்",
        "stage_3_desc": "தொற்று பல்லின் கூழை அடைந்துள்ளது",
        "stage_4": "புண்/கடுமையான",
        "stage_4_desc": "மேம்பட்ட தொற்று, சாத்தியமான புண்",
        "visible_issues": "👁️ தெரியும் பிரச்சினைகள்",
        "possible_causes": "🔍 சாத்தியமான காரணங்கள்",
        "affected_teeth": "🦷 பாதிக்கப்பட்ட பற்கள்",
        "recommended_treatments": "💉 பரிந்துரைக்கப்பட்ட சிகிச்சைகள்",
        "immediate_concerns": "🚨 உடனடி கவலைகள்",
        "dentist_timeline": "📅 பல் மருத்துவர் வருகை காலவரிசை",
        "prevention_tips": "🛡️ தடுப்பு குறிப்புகள்",
        "home_care": "🏠 வீட்டு பராமரிப்பு வழிமுறைகள்",
        "additional_details": "📊 கூடுதல் பகுப்பாய்வு விவரங்கள்",
        "emergency_alert": "⚠️ அவசர எச்சரிக்கை",
        "emergency_text": "உடனடி பல் சிகிச்சை பரிந்துரைக்கப்படுகிறது!",
        "image_processing": "🖼️ படம் செயலாக்கம் மற்றும் பகுப்பாய்வு",
        "grayscale": "சாம்பல் அளவு",
        "edge_detection": "கேனி விளிம்பு கண்டறிதல்",
        "clahe_enhanced": "CLAHE மேம்படுத்தப்பட்டது",
        "histogram_title": "பிக்சல் தீவிரத்தின் வரலாற்று வரைபடம்",
        "pixel_intensity": "பிக்சல் தீவிரம்",
        "frequency": "அதிர்வெண்"
    }
}

def t(key, lang="en"):
    """Translation helper function"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)

# Page configuration
st.set_page_config(
    page_title="🦷 Dental Analysis Portal",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'en'

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
    .audio-section {
        background-color: #f8f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4c51bf;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def encode_image(image):
    """Convert PIL image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def show_image_processing(image, lang):
    """Perform and display image processing analysis"""
    st.header(t("image_processing", lang))

    # Convert PIL to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Canny edge detection
    edges = cv2.Canny(gray, 100, 200)

    # Histogram of pixel intensities
    fig, ax = plt.subplots()
    ax.hist(gray.ravel(), bins=256, range=(0, 256), color='gray')
    ax.set_title(t("histogram_title", lang))
    ax.set_xlabel(t("pixel_intensity", lang))
    ax.set_ylabel(t("frequency", lang))
    st.pyplot(fig)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe.apply(gray)

    # Display results
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(gray, caption=t("grayscale", lang), use_column_width=True, clamp=True)
    with col2:
        st.image(edges, caption=t("edge_detection", lang), use_column_width=True, clamp=True)
    with col3:
        st.image(clahe_img, caption=t("clahe_enhanced", lang), use_column_width=True, clamp=True)


def translate_text(text, target_lang, api_key):
    """Translate text using OpenRouter API with Gemini"""
    if target_lang == "en":
        return text
    
    lang_names = {
        "hi": "Hindi",
        "es": "Spanish", 
        "ta": "Tamil"
    }
    
    prompt = f"Translate the following text to {lang_names.get(target_lang, 'English')}. Only provide the translation, no additional text:\n\n{text}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "google/gemini-2.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            return text
    except:
        return text


def analyze_tooth_image(image, api_key, lang):
    """Analyze tooth image using Gemini API through OpenRouter"""
    
    # Convert image to base64
    img_base64 = encode_image(image)
    
    # Comprehensive prompt for dental analysis
    lang_instruction = ""
    if lang != "en":
        lang_names = {"hi": "Hindi", "es": "Spanish", "ta": "Tamil"}
        lang_instruction = f"\n\nIMPORTANT: Provide all text fields in {lang_names.get(lang, 'English')} language."
    
    prompt = f"""
    You are an expert dental AI assistant. Analyze this tooth/dental image and provide a comprehensive analysis in JSON format with the following structure:
    If you think there is no cavity or dental issues, please indicate uncertainty appropriately.{lang_instruction}

    {{
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
    }}

    Analyze the image carefully and provide detailed, accurate information. If you cannot clearly see dental issues, indicate uncertainty appropriately.
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "google/gemini-2.5-flash",
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

def display_analysis_results(analysis, lang):
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
            <h3>{t("emergency_alert", lang)}: {emergency} Priority</h3>
            <p>{t("emergency_text", lang)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create columns for organized display
    col1, col2 = st.columns(2)
    
    with col1:
        # Visible Issues
        st.subheader(t("visible_issues", lang))
        issues = analysis.get("visible_issues", [])
        if issues:
            for issue in issues:
                st.write(f"• {issue}")
        else:
            st.write("No specific issues identified")
        
        # Possible Causes
        st.subheader(t("possible_causes", lang))
        causes = analysis.get("possible_causes", [])
        if causes:
            for cause in causes:
                st.write(f"• {cause}")
        
        # Affected Teeth
        affected = analysis.get("affected_teeth", [])
        if affected:
            st.subheader(t("affected_teeth", lang))
            st.write(", ".join(affected))
    
    with col2:
        # Recommended Treatments
        st.subheader(t("recommended_treatments", lang))
        treatments = analysis.get("recommended_treatments", [])
        if treatments:
            for treatment in treatments:
                st.write(f"• {treatment}")
        
        # Immediate Concerns
        concerns = analysis.get("immediate_concerns", [])
        if concerns:
            st.subheader(t("immediate_concerns", lang))
            for concern in concerns:
                st.write(f"• {concern}")
        
        # When to See Dentist
        dentist_timeline = analysis.get("when_to_see_dentist", "As soon as possible")
        st.subheader(t("dentist_timeline", lang))
        st.write(dentist_timeline)
    
    # Prevention and Care
    st.subheader(t("prevention_tips", lang))
    prevention = analysis.get("prevention_tips", [])
    if prevention:
        for tip in prevention:
            st.write(f"• {tip}")
    
    st.subheader(t("home_care", lang))
    home_care = analysis.get("home_care_instructions", [])
    if home_care:
        for instruction in home_care:
            st.write(f"• {instruction}")
    
    # Additional Information
    with st.expander(t("additional_details", lang)):
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

def generate_audio_summary(analysis, lang):
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
    if visible_issues and len(visible_issues) > 0:
        summary += f" Visible issues include: {', '.join(visible_issues[:3])}."

    treatments = analysis.get("recommended_treatments", [])
    if treatments and len(treatments) > 0:
        summary += f" Recommended treatments: {', '.join(treatments[:2])}."

    home_care = analysis.get("home_care_instructions", [])
    if home_care and len(home_care) > 0:
        summary += f" Home care instructions: {', '.join(home_care[:2])}."

    dentist_timeline = analysis.get("when_to_see_dentist", "As soon as possible")
    summary += f" When to see dentist: {dentist_timeline}."

    return summary

async def generate_edge_tts_audio(text, voice="en-US-AriaNeural", rate="+0%", pitch="+0Hz"):
    """Generate audio file using Edge TTS"""
    try:
        import edge_tts
        import aiohttp
        
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_path = temp_file.name

        # Create SSL context that doesn't verify certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with custom SSL context
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        # Create communicate object with custom connector
        async with aiohttp.ClientSession(connector=connector) as session:
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            # Monkey patch the session
            communicate._session = session
            await communicate.save(temp_path)

        return temp_path
    except ImportError:
        st.error("Edge TTS is not installed. Please install it with: pip install edge-tts")
        return None
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

def run_async_audio_generation(audio_summary, voice, speed):
    """Run async audio generation in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        if loop.is_running():
            try:
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(generate_edge_tts_audio(audio_summary, voice, speed))
            except ImportError:
                st.warning("Audio generation requires nest_asyncio. Install with: pip install nest_asyncio")
                return None
        else:
            return loop.run_until_complete(generate_edge_tts_audio(audio_summary, voice, speed))
    except Exception as e:
        st.error(f"Error in audio generation: {str(e)}")
        return None

def create_downloadable_report(analysis, lang):
    """Create downloadable text report"""
    if "error" in analysis:
        return "Analysis Error: Unable to generate report"
    
    report_text = f"""
DENTAL ANALYSIS REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

═══════════════════════════════════════════════════════
SUMMARY
═══════════════════════════════════════════════════════
Cavity Stage: {analysis.get('cavity_stage', 'Unknown')}
Severity: {analysis.get('severity_level', 'Unknown')}
Emergency Level: {analysis.get('emergency_level', 'None')}
Cavity Present: {'Yes' if analysis.get('cavity_present', False) else 'No'}

═══════════════════════════════════════════════════════
VISIBLE ISSUES
═══════════════════════════════════════════════════════
{chr(10).join([f"• {issue}" for issue in analysis.get('visible_issues', ['None identified'])])}

═══════════════════════════════════════════════════════
POSSIBLE CAUSES
═══════════════════════════════════════════════════════
{chr(10).join([f"• {cause}" for cause in analysis.get('possible_causes', ['Not specified'])])}

═══════════════════════════════════════════════════════
RECOMMENDED TREATMENTS
═══════════════════════════════════════════════════════
{chr(10).join([f"• {treatment}" for treatment in analysis.get('recommended_treatments', ['Consult dentist'])])}

═══════════════════════════════════════════════════════
IMMEDIATE CONCERNS
═══════════════════════════════════════════════════════
{chr(10).join([f"• {concern}" for concern in analysis.get('immediate_concerns', ['None identified'])])}

═══════════════════════════════════════════════════════
PREVENTION TIPS
═══════════════════════════════════════════════════════
{chr(10).join([f"• {tip}" for tip in analysis.get('prevention_tips', ['Maintain good oral hygiene'])])}

═══════════════════════════════════════════════════════
HOME CARE INSTRUCTIONS
═══════════════════════════════════════════════════════
{chr(10).join([f"• {instruction}" for instruction in analysis.get('home_care_instructions', ['Follow dentist recommendations'])])}

═══════════════════════════════════════════════════════
ADDITIONAL INFORMATION
═══════════════════════════════════════════════════════
When to See Dentist: {analysis.get('when_to_see_dentist', 'As soon as possible')}
Estimated Timeline: {analysis.get('estimated_timeline', 'Not specified')}
Prognosis: {analysis.get('prognosis', 'Consult dentist for detailed prognosis')}

Affected Teeth: {', '.join(analysis.get('affected_teeth', [])) or 'Not specified'}

Additional Notes: {analysis.get('additional_notes', 'None')}

═══════════════════════════════════════════════════════
DISCLAIMER
═══════════════════════════════════════════════════════
This AI analysis is for educational purposes only and should not replace 
professional dental consultation. Always consult with a qualified dentist 
for proper diagnosis and treatment.
    """
    return report_text.strip()

def main():
    lang = st.session_state.language
    
    # Header
    st.markdown(f'<h1 class="main-header">{t("main_header", lang)}</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header(t("config", lang))
        
        # Language Selection
        st.header(t("language_selection", lang))
        language_options = {
            "English": "en",
            "हिन्दी (Hindi)": "hi",
            "Español (Spanish)": "es",
            "தமிழ் (Tamil)": "ta"
        }
        selected_lang = st.selectbox(
            "Select Language",
            list(language_options.keys()),
            index=list(language_options.values()).index(st.session_state.language)
        )
        
        if language_options[selected_lang] != st.session_state.language:
            st.session_state.language = language_options[selected_lang]
            st.rerun()
        
        lang = st.session_state.language
        
        # API Key
        if "OPENROUTER_API_KEY" in os.environ:
            api_key = os.getenv("OPENROUTER_API_KEY")
            st.success(t("api_key_found", lang))
        else:
            st.warning(t("api_key_not_found", lang))
            api_key = st.text_input(t("api_key_label", lang), type="password")

        st.header(t("audio_settings", lang))
        
        # Voice options based on language
        voice_options = {
            "en": {
                "🇺🇸 Aria (Female)": "en-US-AriaNeural",
                "🇺🇸 Guy (Male)": "en-US-GuyNeural",
                "🇺🇸 Jenny (Female)": "en-US-JennyNeural",
                "🇬🇧 Libby (Female)": "en-GB-LibbyNeural",
                "🇬🇧 Ryan (Male)": "en-GB-RyanNeural"
            },
            "hi": {
                "🇮🇳 Swara (Female)": "hi-IN-SwaraNeural",
                "🇮🇳 Madhur (Male)": "hi-IN-MadhurNeural"
            },
            "es": {
                "🇪🇸 Elvira (Female)": "es-ES-ElviraNeural",
                "🇪🇸 Alvaro (Male)": "es-ES-AlvaroNeural",
                "🇲🇽 Dalia (Female)": "es-MX-DaliaNeural",
                "🇲🇽 Jorge (Male)": "es-MX-JorgeNeural"
            },
            "ta": {
                "🇮🇳 Pallavi (Female)": "ta-IN-PallaviNeural",
                "🇮🇳 Valluvar (Male)": "ta-IN-ValluvarNeural"
            }
        }
        
        current_voices = voice_options.get(lang, voice_options["en"])
        selected_voice = st.selectbox(t("voice_selection", lang), list(current_voices.keys()))
        audio_speed = st.selectbox(t("speech_speed", lang), ["-20%", "-10%", "+0%", "+10%", "+20%"], index=2)
        
        st.header(t("instructions", lang))
        st.markdown(t("instructions_text", lang))
        
        st.header(t("disclaimer", lang))
        st.warning(t("disclaimer_text", lang))
    
    # Main content area
    if not api_key:
        st.markdown(f"""
        <div class="info-card">
            <h3>{t("welcome_title", lang)}</h3>
            <p>{t("welcome_text", lang)}</p>
            <p>{t("enter_api_key", lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # File upload
    uploaded_file = st.file_uploader(
        t("upload_image", lang), 
        type=['png', 'jpg', 'jpeg'],
        help=t("upload_help", lang)
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption=t("uploaded_image", lang), use_column_width=True)
        
        show_image_processing(image, lang)
        
        # Analysis button
        if st.button(t("analyze_button", lang), type="primary", use_container_width=True):
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Image Analysis
            status_text.text(t("analyzing", lang))
            progress_bar.progress(20)
            
            analysis = analyze_tooth_image(image, api_key, lang)
            progress_bar.progress(50)
            
            if "error" not in analysis:
                # Step 2: Generate Audio Summary
                status_text.text(t("generating_audio", lang))
                progress_bar.progress(70)
                
                audio_summary = generate_audio_summary(analysis, lang)
                
                # Step 3: Create Audio File
                status_text.text(t("creating_audio", lang))
                progress_bar.progress(90)
                
                voice_name = voice_options.get(lang, voice_options["en"])[selected_voice]
                audio_path = run_async_audio_generation(audio_summary, voice_name, audio_speed)
                
                # Complete
                progress_bar.progress(100)
                status_text.text(t("analysis_complete", lang))
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display Results
                st.header(t("analysis_results", lang))
                display_analysis_results(analysis, lang)
                
                # Audio Section
                st.markdown(f"""
                <div class="audio-section">
                    <h3>{t("audio_summary", lang)}</h3>
                    <p>{t("audio_summary_text", lang)}</p>
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
                            label=t("download_audio", lang),
                            data=audio_bytes,
                            file_name=f"dental_analysis_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                            mime="audio/mp3"
                        )
                    
                    with col_dl2:
                        st.download_button(
                            label=t("download_report", lang),
                            data=create_downloadable_report(analysis, lang),
                            file_name=f"dental_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    
                    with col_dl3:
                        st.download_button(
                            label=t("download_script", lang),
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
                    st.warning(t("audio_failed", lang))
                    st.text_area(t("audio_script", lang), audio_summary, height=150)
                    
                    col_script1, col_script2 = st.columns(2)
                    with col_script1:
                        st.download_button(
                            label=t("download_script", lang),
                            data=audio_summary,
                            file_name=f"dental_audio_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                    with col_script2:
                        st.download_button(
                            label=t("download_report", lang),
                            data=create_downloadable_report(analysis, lang),
                            file_name=f"dental_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
            
            else:
                # Clear progress indicators on error
                progress_bar.empty()
                status_text.empty()
                
                st.header(t("analysis_failed", lang))
                st.error(f"Analysis Error: {analysis['error']}")
                if "raw_response" in analysis:
                    st.text_area("Raw Response", analysis["raw_response"], height=200)
    
    # Educational content
    st.header(t("cavity_stages_guide", lang))
    
    stages_info = {
        "Stage 0": (t("stage_0", lang), t("stage_0_desc", lang), "#c6f6d5"),
        "Stage 1": (t("stage_1", lang), t("stage_1_desc", lang), "#fed7d7"),
        "Stage 2": (t("stage_2", lang), t("stage_2_desc", lang), "#fbb6ce"),
        "Stage 3": (t("stage_3", lang), t("stage_3_desc", lang), "#fc8181"),
        "Stage 4": (t("stage_4", lang), t("stage_4_desc", lang), "#e53e3e")
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
