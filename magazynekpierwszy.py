import streamlit as st

st.title("📦 Prosty Magazyn")

# --- MECHANIZM PAMIĘCI (BEZ PLIKÓW I BEZ SESSION_STATE) ---
# Używamy cache_resource, aby stworzyć jedną listę w pamięci RAM.
# Uwaga: Ta lista będzie wspólna dla wszystkich osób otwierających stronę!
@st.cache_resource
def dane_magazynu():
    return []

# Pobieramy referencję do listy (to działa jak żywa zmienna globalna)
magazyn = dane_magazynu()

# --- DODAWANIE TOWARU ---
st.header("Dodaj towar")
col1, col2 = st.columns([3, 1])

with col1:
    # Formularz ułatwia obsługę entera
    with st.form("dodaj_form"):
        nowa_nazwa = st.text_input("Nazwa produktu")
        przycisk_dodaj = st.form_submit_button("Dodaj")

    if przycisk_dodaj and nowa_nazwa:
        magazyn.append(nowa_nazwa)
        st.success(f"Dodano: {nowa_nazwa}")
        st.rerun() # Odświeżamy, aby pokazać zmiany na liście poniżej

# --- USUWANIE TOWARU ---
st.divider()
st.header("Usuń towar")

if magazyn:
    # Wybieramy z listy rozwijanej, co usunąć
    do_usuniecia = st.selectbox("Wybierz produkt do usunięcia", magazyn)
    
    if st.button("Usuń wybrany"):
        magazyn.remove(do_usuniecia)
        st.warning(f"Usunięto: {do_usuniecia}")
        st.rerun() # Odświeżamy stronę
else:
    st.info("Magazyn jest pusty.")

# --- WYŚWIETLANIE LISTY ---
st.divider()
st.subheader(f"Aktualny stan (Liczba produktów: {len(magazyn)})")

# Wyświetlamy prostą listę wypunktowaną
for produkt in magazyn:
    st.text(f"- {produkt}")
