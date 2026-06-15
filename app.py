import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
from PIL import Image
import json
import re
import io

genai.configure(api_key=st.secrets["GEMINI_KEY"])

st.title("📊 Scrap Analyzer Pro")
st.write("AnEvAse mIa fwtografia apo to skrap gia na deis thn katanomh se pososta.")

uploaded_file = st.file_uploader("Epilogh fwtografias...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
	# Άνοιγμα της αρχικής εικόνας
	raw_image = Image.open(uploaded_file)
	
	# --- ΝΕΑ ΣΚΛΗΡΗ ΣΥΜΠΙΕΣΗ ΚΑΙ ΜΕΙΩΣΗ ΑΝΑΛΥΣΗΣ ---
	# 1. Μειώνουμε τις διαστάσεις στο μέγιστο 1024px
	raw_image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
	
	# 2. Τη μετατρέπουμε σε bytes με χαμηλότερη ποιότητα (quality=60) για να πέσει το μέγεθος στα <500KB
	buffer = io.BytesIO()
	if raw_image.mode in ("RGBA", "P"):  # Μετατροπή σε RGB αν είναι PNG με διαφάνεια
		raw_image = raw_image.convert("RGB")
	raw_image.save(buffer, format="JPEG", quality=60)
	buffer.seek(0)
	
	# Αυτή είναι η νέα, ελαφριά εικόνα που θα χρησιμοποιήσουμε παντού
	image = Image.open(buffer)
	# -----------------------------------------------

	st.image(image, caption='H fwtografia sou (Αυτόματα Συμπιεσμένη)', use_column_width=True)
	st.write("🔄 Analysh swrou... Parakalw perimene...")
	
	model = genai.GenerativeModel('gemini-2.0-flash')
	prompt = "Analyze this scrap metal pile. Calculate approximate volume and give percentages (%) for 3 categories: '0-6mm', '6-8mm', '>8mm'. Return ONLY a JSON like this: {'0-6 χιλιοστά': 50, '6-8 χιλιοστά': 30, '8+ χιλιοστά': 20}"
	
	try:
		response = model.generate_content([prompt, image])
		raw_text = response.text.strip()
		json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
		if json_match:
			data = json.loads(json_match.group(0))
			st.success("✅ H analysh oloklhrwthhke!")
			labels = list(data.keys())
			sizes = list(data.values())
			colors = ['#ff9999','#66b3ff','#99ff99']
			fig, ax = plt.subplots()
			ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
			ax.axis('equal')
			st.pyplot(fig)
			st.subheader("Analytika Pososta:")
			for k, v in data.items():
				st.write(f"• **{k}**: {v}%")
		else:
			st.error("To AI dyskolefthke na fwtografisei. Dokimase ksana.")
	except Exception as e:
		st.error(f"Kati phge vrady: {e}")
