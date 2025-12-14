import streamlit as st

st.set_page_config(page_title="Magazyn Wyrobów Gotowych", page_icon="🏭")
st.title("🏭 Magazyn Wyrobów Gotowych")

# --- GLOBALNA PAMIĘĆ SERWERA ---
# Przechowujemy słownik z dwoma kluczami: 'stany' (produkty) i 'finanse' (pieniądze)
@st.cache_resource
def globalny_stan():
    return {
        "magazyn": {},      # Format: {'Nazwa': ilosc_sztuk}
        "bilans": 0.0       # Startujemy od zera
    }

state = globalny_stan()

# --- WYŚWIETLANIE BILANSU ---
# Wyświetlamy to na górze, aby od razu widzieć wynik finansowy
st.divider()
col_bilans1, col_bilans2 = st.columns([3, 1])
with col_bilans1:
    st.subheader("Aktualny Bilans Finansowy")
with col_bilans2:
    # Kolorowanie wyniku: zielony jeśli na plusie, czerwony jeśli na minusie
    st.metric(label="Zysk / Strata", value=f"{state['bilans']:.2f} PLN")
st.divider()

# --- SEKCJA: PRZYJĘCIE (ZAKUP/PRODUKCJA) ---
st.header("➕ Przyjęcie towaru (Koszt)")
st.caption("Dodanie towaru spowoduje odjęcie kwoty zakupu od bilansu.")

with st.form("dodaj_form"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        nowa_nazwa = st.text_input("Nazwa wyrobu")
    with col2:
        ilosc_dodawana = st.number_input("Ilość (szt)", min_value=1, value=1, step=1)
    with col3:
        cena_zakupu = st.number_input("Cena zakupu/szt (PLN)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
    
    przycisk_dodaj = st.form_submit_button("Przyjmij na magazyn")

if przycisk_dodaj and nowa_nazwa:
    koszt_calkowity = ilosc_dodawana * cena_zakupu
    
    # 1. Aktualizacja stanu magazynowego
    if nowa_nazwa in state["magazyn"]:
        state["magazyn"][nowa_nazwa] += ilosc_dodawana
    else:
        state["magazyn"][nowa_nazwa] = ilosc_dodawana
    
    # 2. Aktualizacja finansów (Wydajemy pieniądze -> Bilans maleje)
    state["bilans"] -= koszt_calkowity
    
    st.success(f"Przyjęto: {nowa_nazwa} ({ilosc_dodawana} szt.). Koszt: -{koszt_calkowity:.2f} PLN")
    st.rerun()

# --- SEKCJA: WYDANIE (SPRZEDAŻ) ---
st.header("➖ Wydanie towaru (Sprzedaż)")
st.caption("Wydanie towaru spowoduje dodanie kwoty sprzedaży do bilansu.")

if state["magazyn"]:
    # Wybór produktu
    produkt_do_edycji = st.selectbox("Wybierz wyrób do sprzedaży", list(state["magazyn"].keys()))
    dostepna_ilosc = state["magazyn"][produkt_do_edycji]
    
    with st.form("sprzedaj_form"):
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            ilosc_do_sprzedazy = st.number_input(
                f"Ilość do sprzedania (Max: {dostepna_ilosc})", 
                min_value=1, 
                max_value=dostepna_ilosc, 
                step=1
            )
        with col_u2:
            cena_sprzedazy = st.number_input("Cena sprzedaży/szt (PLN)", min_value=0.0, value=0.0, step=0.01, format="%.2f")
            
        btn_sprzedaj = st.form_submit_button("Sprzedaj i wydaj z magazynu")

        if btn_sprzedaj:
            przychod = ilosc_do_sprzedazy * cena_sprzedazy
            
            # 1. Aktualizacja stanu magazynowego
            state["magazyn"][produkt_do_edycji] -= ilosc_do_sprzedazy
            if state["magazyn"][produkt_do_edycji] <= 0:
                del state["magazyn"][produkt_do_edycji]
            
            # 2. Aktualizacja finansów (Zarabiamy pieniądze -> Bilans rośnie)
            state["bilans"] += przychod
            
            st.success(f"Sprzedano: {ilosc_do_sprzedazy} szt. {produkt_do_edycji}. Przychód: +{przychod:.2f} PLN")
            st.rerun()
else:
    st.info("Magazyn jest pusty. Brak towarów do sprzedaży.")

# --- SEKCJA: TABELA STANÓW ---
st.divider()
st.subheader("📦 Aktualne stany magazynowe")

if state["magazyn"]:
    dane_do_tabeli = [
        {"Nazwa Wyrobu": k, "Ilość na stanie": v} 
        for k, v in state["magazyn"].items()
    ]
    st.dataframe(dane_do_tabeli, use_container_width=True)
else:
    st.text("Brak wyrobów na stanie.")
