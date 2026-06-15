import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
from PIL import Image
import json
import re

# Σύνδεση με το Google Gemini χρησιμοποιώντας τα Secrets του Streamlit
genai.configure(api_key=st.secrets["GEMINI_KEY"])

st.title("📊 Scrap Analyzer Pro")
st.write("Ανέβασε μια φωτογραφία από το σκραπ για να δεις την κατανομή σε ποσοστά.")

uploaded_file = st.file_uploader("Επιλογή φωτογραφίας...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
	image = Image.open(uploaded_file)
	st.image(image, caption='Η φωτογραφία σου', use_column_width=True)
	st.write("🔄 Ανάλυση σωρού... Παρακαλώ περιμένετε...")
	
	model = genai.GenerativeModel('gemini-1.5-flash')
	
	prompt = """
	Είσαι ένας έμπειρος εκτιμητής μετάλλων και σκραπ. Αναλύστε αυτή τη φωτογραφία από τον σωρό.
	Υπολόγισε κατά προσέγγιση τον όγκο και βγάλε ποσοστά (%) για τις εξής 3 συγκεκριμένες κατηγορίες πάχους:
	1. Από 0 έως 6 χιλιοστά (0-6mm) -> Λαμαρίνες, στρατζαριστά, λεπτά προφίλ.
	2. Από 6 έως 8 χιλιοστά (6-8mm) -> Μεσαία σίδера, γωνιές, μικρά δοκάρια.
	3. Από 8 χιλιοστά και άνω (>8mm) -> Βαρέα σίδερα, χοντρά δοκάρια (IPN, HEA), ράγες, χοντρές πλάκες.
	
	Επέστρεψε την απάντηση ΑΠΟΚΛΕΙΣΤΙΚΑ ΚΑΙ ΜΟΝΟ σε μορφή JSON όπως αυτό το παράδειγμα, χωρίς κανένα άλλο συνοδευτικό κείμενο ή χαιρετισμό:
	{"0-6 χιλιοστά": 50, "6-8 χιλιοστά": 30, "8+ χιλιοστά": 20}
	"""
	
	try:
		response = model.generate_content([prompt, image])
		raw_text = response.text.strip()
		json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
		
		if json_match:
			data = json.loads(json_match.group(0))
			st.success("✅ Η ανάλυση ολοκληρώθηκε!")
			
			labels = list(data.keys())
			sizes = list(data.values())
			colors = ['#ff9999','#66b3ff','#99ff99']
			
			fig, ax = plt.subplots()
			ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
			ax.axis('equal')  
			
			st.pyplot(fig)
			
			st.subheader("Αναλυτικά Ποσοστά:")
			for k, v in data.items():
				st.write(f"• **{k}**: {v}%")
		else:
			st.error("Το AI δυσκολεύτηκε να αναλύσει αυτή τη φωτογραφία. Δοκίμασε με καλύτερο φωτισμό.")
	except Exception as e:
		st.error(f"Κάτι πήγε στραβά: {e}")
