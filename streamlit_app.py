import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, date

# Page configuratie
st.set_page_config(
    page_title="Mijn Multi-Page App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigatie
st.sidebar.title("🚀 Navigatie")
st.sidebar.markdown("---")

# Navigatie opties
paginas = {
    "🏠 Homepage": "homepage",
    "🧮 Calculator": "calculator", 
    "📊 Data & Grafieken": "data",
    "📝 To-Do Lijst": "todo",
    "📞 Contact": "contact",
    "ℹ️ Over deze App": "about"
}

# Selecteer pagina
geselecteerde_pagina = st.sidebar.selectbox(
    "Kies een pagina:",
    list(paginas.keys())
)

# Gebruikersinformatie in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Gebruiker")
gebruiker_naam = st.sidebar.text_input("Je naam:", "Bezoeker")

# Homepage functie
def homepage():
    st.title("🏠 Welkom bij Mijn App!")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        ### Hallo {gebruiker_naam}! 👋
        
        Welkom bij deze multi-page Streamlit applicatie. Hier kun je verschillende functies uitproberen:
        
        - **🧮 Calculator**: Eenvoudige rekenmachine
        - **📊 Data & Grafieken**: Interactieve visualisaties
        - **📝 To-Do Lijst**: Beheer je taken
        - **📞 Contact**: Stuur feedback
        - **ℹ️ Over deze App**: Meer informatie
        
        Gebruik het menu aan de linkerkant om te navigeren tussen de pagina's.
        """)
    
    with col2:
        st.info("💡 **Tip**: Probeer alle pagina's uit om te zien wat er mogelijk is met Streamlit!")
    
    # Snelle statistieken
    st.subheader("📈 App Statistieken")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Totaal Pagina's", "6", "2")
    with col2:
        st.metric("Actieve Gebruiker", gebruiker_naam, "")
    with col3:
        st.metric("Laatste Update", "Vandaag", "")
    with col4:
        st.metric("Status", "Online", "✅")

# Calculator functie
def calculator():
    st.title("🧮 Calculator")
    
    tab1, tab2 = st.tabs(["Basis Calculator", "Geavanceerde Calculator"])
    
    with tab1:
        st.subheader("Basis Bewerkingen")
        col1, col2 = st.columns(2)
        
        with col1:
            getal1 = st.number_input("Eerste getal", value=0.0, key="calc1")
        with col2:
            getal2 = st.number_input("Tweede getal", value=0.0, key="calc2")
        
        operatie = st.selectbox("Kies operatie", ["+", "-", "×", "÷"])
        
        if st.button("Bereken", type="primary"):
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
                    return
            
            st.success(f"**Resultaat:** {getal1} {operatie} {getal2} = **{resultaat}**")
    
    with tab2:
        st.subheader("Geavanceerde Functies")
        col1, col2 = st.columns(2)
        
        with col1:
            getal = st.number_input("Voer een getal in", value=0.0, key="advanced")
            
        functie = st.selectbox("Kies functie", ["Kwadraat", "Wortel", "Kwadraat Wortel", "Percentage"])
        
        if st.button("Bereken Geavanceerd", type="primary"):
            if functie == "Kwadraat":
                resultaat = getal ** 2
                st.success(f"{getal}² = **{resultaat}**")
            elif functie == "Wortel":
                if getal >= 0:
                    resultaat = getal ** 0.5
                    st.success(f"√{getal} = **{resultaat:.4f}**")
                else:
                    st.error("Kan geen wortel trekken van een negatief getal!")
            elif functie == "Kwadraat Wortel":
                resultaat = getal ** 2
                wortel = resultaat ** 0.5
                st.success(f"{getal}² = {resultaat}, √{resultaat} = **{wortel}**")

# Data & Grafieken functie
def data_en_grafieken():
    st.title("📊 Data & Grafieken")
    
    # Gegenereerde data
    st.subheader("📈 Verkoopcijfers (Gesimuleerd)")
    
    # Data genereren
    dagen = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)  # Voor consistente resultaten
    verkopen = np.random.normal(100, 20, len(dagen)) + np.sin(np.arange(len(dagen)) * 2 * np.pi / 365) * 15
    
    df = pd.DataFrame({
        'Datum': dagen,
        'Verkopen': np.maximum(verkopen, 0),  # Geen negatieve verkopen
        'Maand': dagen.strftime('%B'),
        'Kwartaal': dagen.quarter
    })
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        start_datum = st.date_input("Start datum", date(2024, 1, 1))
    with col2:
        eind_datum = st.date_input("Eind datum", date(2024, 12, 31))
    
    # Filter data
    mask = (df['Datum'] >= pd.Timestamp(start_datum)) & (df['Datum'] <= pd.Timestamp(eind_datum))
    gefilterde_data = df.loc[mask]
    
    # Grafieken
    col1, col2 = st.columns(2)
    
    with col1:
        fig_line = px.line(gefilterde_data, x='Datum', y='Verkopen', 
                          title='Verkopen over tijd')
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        maandelijkse_data = gefilterde_data.groupby('Maand')['Verkopen'].sum().reset_index()
        fig_bar = px.bar(maandelijkse_data, x='Maand', y='Verkopen',
                        title='Totale verkopen per maand')
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Data tabel
    st.subheader("📋 Data Overzicht")
    if st.checkbox("Toon ruwe data"):
        st.dataframe(gefilterde_data, use_container_width=True)
    
    # Statistieken
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gemiddelde Verkoop", f"€{gefilterde_data['Verkopen'].mean():.2f}")
    with col2:
        st.metric("Totale Verkoop", f"€{gefilterde_data['Verkopen'].sum():.2f}")
    with col3:
        st.metric("Max Verkoop", f"€{gefilterde_data['Verkopen'].max():.2f}")
    with col4:
        st.metric("Min Verkoop", f"€{gefilterde_data['Verkopen'].min():.2f}")

# To-Do Lijst functie
def todo_lijst():
    st.title("📝 To-Do Lijst")
    
    # Initialiseer session state
    if 'todos' not in st.session_state:
        st.session_state.todos = []
    
    # Nieuwe taak toevoegen
    st.subheader("➕ Nieuwe Taak Toevoegen")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        nieuwe_taak = st.text_input("Wat moet je doen?", key="nieuwe_taak")
    with col2:
        prioriteit = st.selectbox("Prioriteit", ["🔴 Hoog", "🟡 Gemiddeld", "🟢 Laag"])
    
    if st.button("Taak Toevoegen", type="primary"):
        if nieuwe_taak:
            st.session_state.todos.append({
                'taak': nieuwe_taak,
                'prioriteit': prioriteit,
                'voltooid': False,
                'datum': datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.success(f"✅ Taak '{nieuwe_taak}' toegevoegd!")
            st.rerun()
    
    # Taken weergeven
    st.subheader("📋 Jouw Taken")
    
    if st.session_state.todos:
        for i, todo in enumerate(st.session_state.todos):
            col1, col2, col3, col4 = st.columns([0.5, 3, 1.5, 1])
            
            with col1:
                voltooid = st.checkbox("", todo['voltooid'], key=f"check_{i}")
                if voltooid != todo['voltooid']:
                    st.session_state.todos[i]['voltooid'] = voltooid
                    st.rerun()
            
            with col2:
                if todo['voltooid']:
                    st.markdown(f"~~{todo['taak']}~~")
                else:
                    st.write(todo['taak'])
            
            with col3:
                st.write(todo['prioriteit'])
            
            with col4:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.todos.pop(i)
                    st.rerun()
        
        # Statistieken
        st.markdown("---")
        totaal = len(st.session_state.todos)
        voltooid = sum(1 for todo in st.session_state.todos if todo['voltooid'])
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Totaal Taken", totaal)
        with col2:
            st.metric("Voltooid", voltooid)
        with col3:
            st.metric("Te Doen", totaal - voltooid)
        
        if st.button("🧹 Voltooide Taken Wissen"):
            st.session_state.todos = [todo for todo in st.session_state.todos if not todo['voltooid']]
            st.rerun()
    else:
        st.info("Geen taken gevonden. Voeg je eerste taak toe!")

# Contact functie
def contact():
    st.title("📞 Contact & Feedback")
    
    tab1, tab2 = st.tabs(["💌 Feedback Versturen", "📧 Contact Info"])
    
    with tab1:
        st.subheader("We horen graag van je!")
        
        col1, col2 = st.columns(2)
        with col1:
            naam = st.text_input("Je naam", value=gebruiker_naam)
            email = st.text_input("Je email")
        
        with col2:
            onderwerp = st.selectbox("Onderwerp", [
                "Algemene feedback",
                "Bug rapport", 
                "Feature verzoek",
                "Vraag",
                "Anders"
            ])
            beoordeling = st.slider("Hoe beoordeel je deze app?", 1, 5, 5)
        
        bericht = st.text_area("Je bericht", height=150)
        
        if st.button("📤 Verstuur Feedback", type="primary"):
            if naam and email and bericht:
                st.balloons()
                st.success("🎉 Bedankt voor je feedback! We nemen zo snel mogelijk contact op.")
                
                # Toon samenvatting
                with st.expander("📋 Samenvatting van je bericht"):
                    st.write(f"**Naam:** {naam}")
                    st.write(f"**Email:** {email}")
                    st.write(f"**Onderwerp:** {onderwerp}")
                    st.write(f"**Beoordeling:** {'⭐' * beoordeling}")
                    st.write(f"**Bericht:** {bericht}")
            else:
                st.error("❌ Vul alle velden in voordat je verstuurt.")
    
    with tab2:
        st.subheader("📫 Contact Informatie")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🏢 Bedrijf:** Streamlit Demo App  
            **📧 Email:** demo@streamlit-app.nl  
            **📱 Telefoon:** +31 20 123 4567  
            **🌐 Website:** www.streamlit-demo.nl  
            """)
        
        with col2:
            st.markdown("""
            **📍 Adres:**  
            Demostraat 123  
            1234 AB Amsterdam  
            Nederland  
            
            **🕒 Openingstijden:**  
            Ma-Vr: 09:00 - 17:00  
            Za-Zo: Gesloten  
            """)

# Over de App functie
def about():
    st.title("ℹ️ Over deze App")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 Welkom bij de Streamlit Demo App!
        
        Deze applicatie is gemaakt om de mogelijkheden van Streamlit te demonstreren. 
        Streamlit is een open-source Python framework waarmee je snel interactieve 
        web-applicaties kunt bouwen.
        
        ### ✨ Functies van deze app:
        
        - **Multi-page navigatie** met sidebar menu
        - **Interactieve calculators** voor basis en geavanceerde berekeningen  
        - **Data visualisatie** met Plotly grafieken
        - **To-Do lijst** met session state management
        - **Contact formulier** met feedback opties
        - **Responsive design** dat werkt op alle apparaten
        
        ### 🛠️ Technologieën gebruikt:
        
        - **Streamlit** - Hoofdframework
        - **Pandas** - Data manipulatie
        - **NumPy** - Numerieke berekeningen
        - **Plotly** - Interactieve grafieken
        """)
    
    with col2:
        st.info("""
        **💡 Wist je dat?**
        
        Streamlit apps kunnen worden gedeployed naar:
        - Streamlit Community Cloud
        - Heroku
        - AWS
        - Google Cloud
        - Azure
        
        En nog veel meer platforms!
        """)
    
    st.markdown("---")
    
    # Technische info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Python Versie", "3.9+")
    with col2:
        st.metric("Streamlit Versie", "1.28+")
    with col3:
        st.metric("Laatste Update", "December 2024")
    
    # Credits
    st.subheader("👨‍💻 Credits")
    st.markdown("""
    Deze app is gemaakt als demonstratie van Streamlit's mogelijkheden.
    
    **Bronnen:**
    - [Streamlit Documentatie](https://docs.streamlit.io)
    - [Streamlit Community](https://discuss.streamlit.io)
    - [GitHub Repository](https://github.com/streamlit/streamlit)
    """)

# Hoofdlogica voor pagina routing
def main():
    pagina_functie = paginas[geselecteerde_pagina]
    
    if pagina_functie == "homepage":
        homepage()
    elif pagina_functie == "calculator":
        calculator()
    elif pagina_functie == "data":
        data_en_grafieken()
    elif pagina_functie == "todo":
        todo_lijst()
    elif pagina_functie == "contact":
        contact()
    elif pagina_functie == "about":
        about()

# App uitvoeren
if __name__ == "__main__":
    main()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("*Gemaakt met ❤️ en Streamlit*")
