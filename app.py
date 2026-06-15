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
	raw_image = Image.open(uploaded_file)
	
	# Συμπίεση για σιγουριά
	raw_image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
	buffer = io.BytesIO()
	if raw_image.mode in ("RGBA", "P"):
		raw_image = raw_image.convert("RGB")
	raw_image.save(buffer, format="JPEG", quality=60)
	buffer.seek(0)
	image = Image.open(buffer)

	st.image(image, caption='H fwtografia sou (Έτοιμη για ανάλυση)', use_column_width=True)
	st.write("🔄 Analysh swrou... Parakalw perimene...")
	
	# Αλλαγή στο μοντέλο 1.5-flash που έχει καλύτερα δωρεάν όρια
	model = genai.GenerativeModel('gemini-1.5-flash')
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
