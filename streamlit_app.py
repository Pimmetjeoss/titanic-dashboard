import streamlit as st
import pandas as pd
import numpy as np

# Titel van de app
st.title("Mijn Eerste Streamlit App")

# Welkomstbericht
st.write("Welkom bij deze eenvoudige Streamlit applicatie!")

# Sidebar
st.sidebar.header("Instellingen")
naam = st.sidebar.text_input("Wat is je naam?", "Gebruiker")

# Begroeting
st.header(f"Hallo {naam}! 👋")

# Simpele calculator
st.subheader("Eenvoudige Calculator")
col1, col2 = st.columns(2)

with col1:
    getal1 = st.number_input("Eerste getal", value=0.0)
    
with col2:
    getal2 = st.number_input("Tweede getal", value=0.0)

operatie = st.selectbox("Kies een operatie", ["+", "-", "×", "÷"])

if st.button("Bereken"):
    if operatie == "+":
        resultaat = getal1 + getal2
    elif operatie == "-":
        resultaat = getal1 - getal2
    elif operatie == "×":
        resultaat = getal1 * getal2
    elif operatie == "÷":
        if getal2 != 0:
            resultaat = getal1 / getal2
        else:
            st.error("Kan niet delen door nul!")
            resultaat = None
    
    if resultaat is not None:
        st.success(f"Resultaat: {resultaat}")

# Data visualisatie
st.subheader("Simpele Grafiek")

if st.checkbox("Toon grafiek"):
    # Genereer willekeurige data
    data = pd.DataFrame({
        'Dag': range(1, 8),
        'Verkopen': np.random.randint(10, 100, 7)
    })
    
    st.line_chart(data.set_index('Dag'))
    st.write("Data gebruikt voor de grafiek:")
    st.dataframe(data)

# Feedback sectie
st.subheader("Feedback")
feedback = st.text_area("Wat vind je van deze app?", "")

if st.button("Verstuur feedback"):
    if feedback:
        st.balloons()
        st.success("Bedankt voor je feedback!")
    else:
        st.warning("Schrijf eerst wat feedback voordat je verstuurt.")

# Footer
st.markdown("---")
st.markdown("*Gemaakt met Streamlit* 🚀")
