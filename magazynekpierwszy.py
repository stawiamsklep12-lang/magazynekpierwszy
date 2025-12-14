import streamlit as st

st.set_page_config(page_title="Magazyn Wyrobów Gotowych", page_icon="🏭")
st.title("🏭 Magazyn Wyrobów Gotowych")
st.caption("Auto-kalkulacja: Marża 25% | VAT 8%")

# --- KONFIGURACJA STAŁYCH ---
MARZA_PROCENT = 0.25  # 25% narzutu
VAT_PROCENT = 0.08    # 8% VAT

# --- GLOBALNA PAMIĘĆ SERWERA ---
# Struktura magazynu:
# {
#   "Nazwa Produktu": {
#       "ilosc": 10, 
#       "srednia_cena_zakupu": 50.00
#   }
# }
@st.cache_resource
def globalny_stan():
    return {
        "magazyn": {},
        "bilans": 0.0
    }

state = globalny_stan()

# --- WYŚWIETLANIE BILANSU ---
st.divider()
col_bilans1, col_bilans2 = st.columns([3, 1])
with col_bilans1:
    st.subheader("Aktualny Bilans Finansowy")
with col_bilans2:
    color = "green" if state['bilans'] >= 0 else "red"
    st.markdown(f"<h2 style='color:{color};'>{state['bilans']:.2f} PLN</h2>", unsafe_allow_html=True)
st.divider()

# --- SEKCJA: PRZYJĘCIE (ZAKUP/PRODUKCJA) ---
st.header("➕ Przyjęcie towaru (Koszt)")

with st.form("dodaj_form"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        nowa_nazwa = st.text_input("Nazwa wyrobu")
    with col2:
        ilosc_dodawana = st.number_input("Ilość (szt)", min_value=1, value=1, step=1)
    with col3:
        cena_zakupu = st.number_input("Cena zakupu netto/szt", min_value=0.0, value=0.0, step=0.01, format="%.2f")
    
    przycisk_dodaj = st.form_submit_button("Przyjmij na magazyn")

if przycisk_dodaj and nowa_nazwa:
    koszt_transakcji = ilosc_dodawana * cena_zakupu
    
    # Logika średniej ceny ważonej (jeśli towar już istnieje)
    if nowa_nazwa in state["magazyn"]:
        stare_dane = state["magazyn"][nowa_nazwa]
        stara_ilosc = stare_dane["ilosc"]
        stara_cena = stare_dane["srednia_cena_zakupu"]
        
        nowa_ilosc_calkowita = stara_ilosc + ilosc_dodawana
        # Wzór na nową średnią cenę: ((stara_ilosc * stara_cena) + (nowa_ilosc * nowa_cena)) / suma_ilosci
        nowa_srednia_cena = ((stara_ilosc * stara_cena) + koszt_transakcji) / nowa_ilosc_calkowita
        
        state["magazyn"][nowa_nazwa]["ilosc"] = nowa_ilosc_calkowita
        state["magazyn"][nowa_nazwa]["srednia_cena_zakupu"] = nowa_srednia_cena
    else:
        # Nowy towar
        state["magazyn"][nowa_nazwa] = {
            "ilosc": ilosc_dodawana,
            "srednia_cena_zakupu": cena_zakupu
        }
    
    # Aktualizacja bilansu (odejmujemy koszt zakupu)
    state["bilans"] -= koszt_transakcji
    
    st.success(f"Przyjęto: {nowa_nazwa}. Koszt operacji: -{koszt_transakcji:.2f} PLN")
    st.rerun()

# --- SEKCJA: WYDANIE (SPRZEDAŻ Z AUTOMATYCZNĄ WYCENĄ) ---
st.header("➖ Wydanie towaru (Sprzedaż)")

if state["magazyn"]:
    produkt_do_edycji = st.selectbox("Wybierz wyrób do sprzedaży", list(state["magazyn"].keys()))
    
    # Pobieramy dane o produkcie
    dane_produktu = state["magazyn"][produkt_do_edycji]
    dostepna_ilosc = dane_produktu["ilosc"]
    koszt_zakupu_jednostkowy = dane_produktu["srednia_cena_zakupu"]
    
    # --- KALKULACJA CEN ---
    # 1. Cena z narzutem (Netto) = Koszt zakupu * (1 + 25%)
    cena_sprzedazy_netto = koszt_zakupu_jednostkowy * (1 + MARZA_PROCENT)
    # 2. Cena z VAT (Brutto) = Cena Netto * (1 + 8%)
    cena_sprzedazy_brutto = cena_sprzedazy_netto * (1 + VAT_PROCENT)
    
    st.info(f"""
    📦 **Kalkulacja dla: {produkt_do_edycji}**
    * Średnia cena zakupu: {koszt_zakupu_jednostkowy:.2f} PLN
    * + Marża {int(MARZA_PROCENT*100)}% (Netto): **{cena_sprzedazy_netto:.2f} PLN**
    * + VAT {int(VAT_PROCENT*100)}% (Brutto): **{cena_sprzedazy_brutto:.2f} PLN**
    """)
    
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
            # Wyświetlamy cenę brutto, ale jako "disabled" (zablokowaną), żeby użytkownik widział, ale nie zmieniał ręcznie
            st.text_input("Cena sprzedaży (Brutto/szt)", value=f"{cena_sprzedazy_brutto:.2f} PLN", disabled=True)
            
        btn_sprzedaj = st.form_submit_button(f"Sprzedaj po cenie {cena_sprzedazy_brutto:.2f} PLN")

        if btn_sprzedaj:
            # Do bilansu dodajemy kwotę Brutto (to co płaci klient)
            przychod_calkowity = ilosc_do_sprzedazy * cena_sprzedazy_brutto
            
            # 1. Aktualizacja stanu magazynowego
            state["magazyn"][produkt_do_edycji]["ilosc"] -= ilosc_do_sprzedazy
            
            # Jeśli ilość spadła do 0, usuwamy produkt z listy
            if state["magazyn"][produkt_do_edycji]["ilosc"] <= 0:
                del state["magazyn"][produkt_do_edycji]
            
            # 2. Aktualizacja finansów (Dodajemy przychód do bilansu)
            state["bilans"] += przychod_calkowity
            
            st.success(f"Sprzedano {ilosc_do_sprzedazy} szt. Przychód do kasy: +{przychod_calkowity:.2f} PLN")
            st.rerun()
else:
    st.info("Magazyn jest pusty.")

# --- SEKCJA: TABELA STANÓW ---
st.divider()
st.subheader("📦 Aktualne stany magazynowe")

if state["magazyn"]:
    # Przekształcamy zagnieżdżony słownik na płaską listę do tabeli
    dane_do_tabeli = []
    for nazwa, info in state["magazyn"].items():
        cena_n = info['srednia_cena_zakupu'] * (1 + MARZA_PROCENT)
        cena_b = cena_n * (1 + VAT_PROCENT)
        
        dane_do_tabeli.append({
            "Nazwa Wyrobu": nazwa,
            "Ilość": info['ilosc'],
            "Śr. Cena Zakupu": f"{info['srednia_cena_zakupu']:.2f}",
            "Wycena Brutto (szt)": f"{cena_b:.2f}"
        })
        
    st.dataframe(dane_do_tabeli, use_container_width=True)
else:
    st.text("Brak wyrobów na stanie.")
