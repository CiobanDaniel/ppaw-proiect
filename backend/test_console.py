try:
    from .crud import SessionLocal, UtilizatoriAccessor, CartiAccessor
except ImportError:
    from crud import SessionLocal, UtilizatoriAccessor, CartiAccessor

def run_test():
    db = SessionLocal()
    
    user_accessor = UtilizatoriAccessor(db)
    book_accessor = CartiAccessor(db)
    
    print("--- Testare ORM Database First ---")
    
    # Apelam metodele
    utilizatori = user_accessor.get_all_users()
    print(f"Numar total utilizatori in DB: {len(utilizatori)}")
    
    if utilizatori:
        primul_user = utilizatori[0]
        # Am adaugat campul 'telefon' generat de ORM
        print(f"Primul utilizator: {primul_user.nume_utilizator}")
        print(f"Rol: {primul_user.rol}")
        print(f"Telefon: {primul_user.telefon}")
        print(f"Adresa (Ex 5): {primul_user.adresa}")
        print(f"Data nasterii (Ex 5): {primul_user.data_nasterii}")
        
        # Extragem cartile scrise de el
        cartile_lui = book_accessor.get_books_by_author(primul_user.id)
        print(f"Carti scrise de {primul_user.nume_utilizator}: {len(cartile_lui)}")
        
        for carte in cartile_lui:
            print(f" - {carte.titlu}")

    db.close()

if __name__ == "__main__":
    run_test()
