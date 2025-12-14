import streamlit as st

st.title("📦 Magazyn z Ilościami")

# --- GLOBALNA PAMIĘĆ SERWERA (SŁOWNIK) ---
# Używamy cache_resource, aby przechować słownik {nazwa_produktu: ilosc_sztuk}
# Dane są wspólne dla wszystkich użytkowników i znikają po restarcie serwera.
@st.cache_resource
def dane_magazynu():
    return {}

magazyn = dane_magazynu()

# --- SEKCJA: DODAWANIE TOWARU ---
st.header("Dodaj towar")

with st.form("dodaj_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        nowa_nazwa = st.text_input("Nazwa produktu")
    with col2:
        # step=1 zapewnia liczby całkowite, min_value=1 blokuje ujemne/zero
        ilosc_dodawana = st.number_input("Ilość sztuk", min_value=1, value=1, step=1)
    
    przycisk_dodaj = st.form_submit_button("Przyjmij do magazynu")

if przycisk_dodaj and nowa_nazwa:
    # Logika: Jeśli produkt jest, dodajemy ilość. Jeśli nie ma, tworzymy nowy wpis.
    if nowa_nazwa in magazyn:
        magazyn[nowa_nazwa] += ilosc_dodawana
    else:
        magazyn[nowa_nazwa] = ilosc_dodawana
    
    st.success(f"Zaktualizowano: {nowa_nazwa} (Dodano: {ilosc_dodawana} szt.)")
    st.rerun()

# --- SEKCJA: USUWANIE TOWARU ---
st.divider()
st.header("Wydaj / Usuń towar")

if magazyn:
    # Wybór produktu z listy kluczy słownika
    produkt_do_edycji = st.selectbox("Wybierz produkt", list(magazyn.keys()))
    
    # Pobieramy aktualną ilość, aby ograniczyć pole usuwania
    dostepna_ilosc = magazyn[produkt_do_edycji]
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        ilosc_do_usuniecia = st.number_input(
            f"Ile sztuk usunąć? (Dostępne: {dostepna_ilosc})", 
            min_value=1, 
            max_value=dostepna_ilosc, 
            step=1
        )
    with col_u2:
        # Pusty kontener dla wyrównania przycisku w dół
        st.write("") 
        st.write("")
        if st.button("Wydaj z magazynu"):
            magazyn[produkt_do_edycji] -= ilosc_do_usuniecia
            
            st.warning(f"Wydano {ilosc_do_usuniecia} szt. produktu {produkt_do_edycji}")
            
            # Jeśli ilość spadła do 0, usuwamy produkt całkowicie z listy
            if magazyn[produkt_do_edycji] <= 0:
                del magazyn[produkt_do_edycji]
                
            st.rerun()
else:
    st.info("Brak towarów do wydania.")

# --- SEKCJA: STAN MAGAZYNU (TABELA) ---
st.divider()
st.subheader("📊 Aktualny stan magazynu")

if magazyn:
    # Wyświetlamy jako prostą tabelę
    # Zamieniamy słownik na format czytelny dla st.dataframe (lista słowników)
    dane_do_tabeli = [
        {"Produkt": towar, "Ilość sztuk": ilosc} 
        for towar, ilosc in magazyn.items()
    ]
    st.dataframe(dane_do_tabeli, use_container_width=True)
else:
    st.text("Magazyn jest pusty.")
