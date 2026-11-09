from typing import Optional
import datetime
import decimal

from sqlalchemy import Boolean, CheckConstraint, Column, Date, DateTime, ForeignKeyConstraint, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Categorii(Base):
    __tablename__ = 'categorii'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categorii_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nume: Mapped[str] = mapped_column(String(100), nullable=False)
    descriere: Mapped[Optional[str]] = mapped_column(Text)

    carti: Mapped[list['Carti']] = relationship('Carti', secondary='categorii_carti', back_populates='categorii')


class EvenimentePromotionale(Base):
    __tablename__ = 'evenimente_promotionale'
    __table_args__ = (
        CheckConstraint('recompensa_puncte >= 0', name='evenimente_recompensa_pozitiva_check'),
        PrimaryKeyConstraint('id', name='evenimente_promotionale_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nume: Mapped[str] = mapped_column(String(100), nullable=False)
    recompensa_puncte: Mapped[int] = mapped_column(Integer, nullable=False)
    data_inceput: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    data_sfarsit: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    este_activ: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))


class NiveleAbonament(Base):
    __tablename__ = 'nivele_abonament'
    __table_args__ = (
        CheckConstraint('pret_real >= 0', name='nivele_pret_pozitiv_check'),
        PrimaryKeyConstraint('id', name='nivele_abonament_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nume: Mapped[str] = mapped_column(String(50), nullable=False)
    pret_real: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    descriere_beneficii: Mapped[Optional[str]] = mapped_column(Text)

    utilizatori: Mapped[list['Utilizatori']] = relationship('Utilizatori', back_populates='nivele_abonament')
    istoric_abonamente: Mapped[list['IstoricAbonamente']] = relationship('IstoricAbonamente', back_populates='nivele_abonament')


class SetariPlatforma(Base):
    __tablename__ = 'setari_platforma'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='setari_platforma_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nume_setare: Mapped[str] = mapped_column(String(50), nullable=False)
    valoare_setare: Mapped[str] = mapped_column(String(255), nullable=False)
    data_actualizarii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))


class Utilizatori(Base):
    __tablename__ = 'utilizatori'
    __table_args__ = (
        CheckConstraint("rol::text = ANY (ARRAY['cititor'::character varying, 'autor'::character varying, 'admin'::character varying]::text[])", name='utilizatori_rol_check'),
        ForeignKeyConstraint(['id_nivel_curent'], ['nivele_abonament.id'], ondelete='SET NULL', name='utilizatori_id_nivel_curent_fkey'),
        PrimaryKeyConstraint('id', name='utilizatori_pkey'),
        UniqueConstraint('email', name='utilizatori_email_key'),
        UniqueConstraint('nume_utilizator', name='utilizatori_nume_utilizator_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nume_utilizator: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    parola_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    url_avatar: Mapped[Optional[str]] = mapped_column(String(255))
    rol: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'cititor'::character varying"))
    stare_cont: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'activ'::character varying"))
    puncte: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    id_nivel_curent: Mapped[Optional[int]] = mapped_column(Integer)
    expira_pro_la: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    data_ultimei_logari: Mapped[Optional[datetime.date]] = mapped_column(Date)
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    adresa: Mapped[Optional[str]] = mapped_column(String(150))
    data_nasterii: Mapped[Optional[datetime.date]] = mapped_column(Date)
    telefon: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'Necompletat'::character varying"))

    nivele_abonament: Mapped[Optional['NiveleAbonament']] = relationship('NiveleAbonament', back_populates='utilizatori')
    carti: Mapped[list['Carti']] = relationship('Carti', back_populates='utilizatori')
    cereri_retragere: Mapped[list['CereriRetragere']] = relationship('CereriRetragere', foreign_keys='[CereriRetragere.id_autor]', back_populates='utilizatori')
    cereri_retragere_procesate: Mapped[list['CereriRetragere']] = relationship('CereriRetragere', foreign_keys='[CereriRetragere.id_admin_procesare]', back_populates='admin_procesare')
    notificari: Mapped[list['Notificari']] = relationship('Notificari', back_populates='utilizatori')
    plati: Mapped[list['Plati']] = relationship('Plati', foreign_keys='[Plati.id_utilizator]', back_populates='utilizatori')
    plati_rambursate: Mapped[list['Plati']] = relationship('Plati', foreign_keys='[Plati.id_admin_rambursare]', back_populates='admin_rambursare')
    rapoarte_continut_id_admin_rezolvare: Mapped[list['RapoarteContinut']] = relationship('RapoarteContinut', foreign_keys='[RapoarteContinut.id_admin_rezolvare]', back_populates='utilizatori')
    rapoarte_continut_id_raportor: Mapped[list['RapoarteContinut']] = relationship('RapoarteContinut', foreign_keys='[RapoarteContinut.id_raportor]', back_populates='utilizatori_')
    tranzactii_puncte: Mapped[list['TranzactiiPuncte']] = relationship('TranzactiiPuncte', back_populates='utilizatori')
    urmariri_autori_id_autor_urmarit: Mapped[list['UrmaririAutori']] = relationship('UrmaririAutori', foreign_keys='[UrmaririAutori.id_autor_urmarit]', back_populates='utilizatori')
    urmariri_autori_id_urmaritor: Mapped[list['UrmaririAutori']] = relationship('UrmaririAutori', foreign_keys='[UrmaririAutori.id_urmaritor]', back_populates='utilizatori_')
    biblioteca_utilizator: Mapped[list['BibliotecaUtilizator']] = relationship('BibliotecaUtilizator', back_populates='utilizatori')
    istoric_abonamente: Mapped[list['IstoricAbonamente']] = relationship('IstoricAbonamente', back_populates='utilizatori')
    recenzii: Mapped[list['Recenzii']] = relationship('Recenzii', back_populates='utilizatori')
    venituri_autori: Mapped[list['VenituriAutori']] = relationship('VenituriAutori', back_populates='utilizatori')
    comentarii: Mapped[list['Comentarii']] = relationship('Comentarii', back_populates='utilizatori')
    deblocari_capitole: Mapped[list['DeblocariCapitole']] = relationship('DeblocariCapitole', back_populates='utilizatori')
    progres_lectura: Mapped[list['ProgresLectura']] = relationship('ProgresLectura', back_populates='utilizatori')
    vizualizari_capitole: Mapped[list['VizualizariCapitole']] = relationship('VizualizariCapitole', back_populates='utilizatori')


class Carti(Base):
    __tablename__ = 'carti'
    __table_args__ = (
        ForeignKeyConstraint(['id_autor'], ['utilizatori.id'], ondelete='CASCADE', name='carti_id_autor_fkey'),
        PrimaryKeyConstraint('id', name='carti_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titlu: Mapped[str] = mapped_column(String(150), nullable=False)
    id_autor: Mapped[Optional[int]] = mapped_column(Integer)
    descriere: Mapped[Optional[str]] = mapped_column(Text)
    url_imagine_coperta: Mapped[Optional[str]] = mapped_column(String(255))
    stare: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'ciorna'::character varying"))
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='carti')
    categorii: Mapped[list['Categorii']] = relationship('Categorii', secondary='categorii_carti', back_populates='carti')
    biblioteca_utilizator: Mapped[list['BibliotecaUtilizator']] = relationship('BibliotecaUtilizator', back_populates='carti')
    capitole: Mapped[list['Capitole']] = relationship('Capitole', back_populates='carti')
    recenzii: Mapped[list['Recenzii']] = relationship('Recenzii', back_populates='carti')
    progres_lectura: Mapped[list['ProgresLectura']] = relationship('ProgresLectura', back_populates='carti')


class CereriRetragere(Base):
    __tablename__ = 'cereri_retragere'
    __table_args__ = (
        CheckConstraint('suma >= 0', name='cereri_retragere_suma_pozitiva_check'),
        ForeignKeyConstraint(['id_autor'], ['utilizatori.id'], ondelete='CASCADE', name='cereri_retragere_id_autor_fkey'),
        ForeignKeyConstraint(['id_admin_procesare'], ['utilizatori.id'], ondelete='SET NULL', name='cereri_retragere_id_admin_procesare_fkey'),
        PrimaryKeyConstraint('id', name='cereri_retragere_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    suma: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    id_autor: Mapped[Optional[int]] = mapped_column(Integer)
    stare: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'in_asteptare'::character varying"))
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    data_procesarii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    id_admin_procesare: Mapped[Optional[int]] = mapped_column(Integer)
    observatii_procesare: Mapped[Optional[str]] = mapped_column(Text)

    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', foreign_keys=[id_autor], back_populates='cereri_retragere')
    admin_procesare: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', foreign_keys=[id_admin_procesare], back_populates='cereri_retragere_procesate')


class Notificari(Base):
    __tablename__ = 'notificari'
    __table_args__ = (
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='notificari_id_utilizator_fkey'),
        PrimaryKeyConstraint('id', name='notificari_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    titlu: Mapped[str] = mapped_column(String(150), nullable=False)
    mesaj: Mapped[str] = mapped_column(Text, nullable=False)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    este_citita: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='notificari')


class Plati(Base):
    __tablename__ = 'plati'
    __table_args__ = (
        CheckConstraint('suma_reala >= 0', name='plati_suma_pozitiva_check'),
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='plati_id_utilizator_fkey'),
        ForeignKeyConstraint(['id_admin_rambursare'], ['utilizatori.id'], ondelete='SET NULL', name='plati_id_admin_rambursare_fkey'),
        PrimaryKeyConstraint('id', name='plati_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    suma_reala: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    scop_plata: Mapped[str] = mapped_column(String(50), nullable=False)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    moneda: Mapped[Optional[str]] = mapped_column(String(3), server_default=text("'RON'::character varying"))
    stare: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'finalizat'::character varying"))
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    id_admin_rambursare: Mapped[Optional[int]] = mapped_column(Integer)
    motiv_rambursare: Mapped[Optional[str]] = mapped_column(Text)
    data_rambursarii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', foreign_keys=[id_utilizator], back_populates='plati')
    admin_rambursare: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', foreign_keys=[id_admin_rambursare], back_populates='plati_rambursate')
    istoric_abonamente: Mapped[list['IstoricAbonamente']] = relationship('IstoricAbonamente', back_populates='plati')
    venituri_autori: Mapped[list['VenituriAutori']] = relationship('VenituriAutori', back_populates='plati')


class RapoarteContinut(Base):
    __tablename__ = 'rapoarte_continut'
    __table_args__ = (
        ForeignKeyConstraint(['id_admin_rezolvare'], ['utilizatori.id'], ondelete='SET NULL', name='rapoarte_continut_id_admin_rezolvare_fkey'),
        ForeignKeyConstraint(['id_raportor'], ['utilizatori.id'], ondelete='CASCADE', name='rapoarte_continut_id_raportor_fkey'),
        PrimaryKeyConstraint('id', name='rapoarte_continut_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tip_tinta: Mapped[str] = mapped_column(String(50), nullable=False)
    id_tinta: Mapped[int] = mapped_column(Integer, nullable=False)
    motiv: Mapped[str] = mapped_column(Text, nullable=False)
    id_raportor: Mapped[Optional[int]] = mapped_column(Integer)
    stare: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'deschis'::character varying"))
    id_admin_rezolvare: Mapped[Optional[int]] = mapped_column(Integer)
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', foreign_keys=[id_admin_rezolvare], back_populates='rapoarte_continut_id_admin_rezolvare')
    utilizatori_: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', foreign_keys=[id_raportor], back_populates='rapoarte_continut_id_raportor')


class TranzactiiPuncte(Base):
    __tablename__ = 'tranzactii_puncte'
    __table_args__ = (
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='tranzactii_puncte_id_utilizator_fkey'),
        PrimaryKeyConstraint('id', name='tranzactii_puncte_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    valoare: Mapped[int] = mapped_column(Integer, nullable=False)
    tip_tranzactie: Mapped[str] = mapped_column(String(10), nullable=False)
    motiv: Mapped[str] = mapped_column(String(100), nullable=False)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    tip_referinta: Mapped[Optional[str]] = mapped_column(String(50))
    id_referinta: Mapped[Optional[int]] = mapped_column(Integer)
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='tranzactii_puncte')


class UrmaririAutori(Base):
    __tablename__ = 'urmariri_autori'
    __table_args__ = (
        ForeignKeyConstraint(['id_autor_urmarit'], ['utilizatori.id'], ondelete='CASCADE', name='urmariri_autori_id_autor_urmarit_fkey'),
        ForeignKeyConstraint(['id_urmaritor'], ['utilizatori.id'], ondelete='CASCADE', name='urmariri_autori_id_urmaritor_fkey'),
        PrimaryKeyConstraint('id_urmaritor', 'id_autor_urmarit', name='urmariri_autori_pkey')
    )

    id_urmaritor: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_autor_urmarit: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    utilizatori: Mapped['Utilizatori'] = relationship('Utilizatori', foreign_keys=[id_autor_urmarit], back_populates='urmariri_autori_id_autor_urmarit')
    utilizatori_: Mapped['Utilizatori'] = relationship('Utilizatori', foreign_keys=[id_urmaritor], back_populates='urmariri_autori_id_urmaritor')


class BibliotecaUtilizator(Base):
    __tablename__ = 'biblioteca_utilizator'
    __table_args__ = (
        ForeignKeyConstraint(['id_carte'], ['carti.id'], ondelete='CASCADE', name='biblioteca_utilizator_id_carte_fkey'),
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='biblioteca_utilizator_id_utilizator_fkey'),
        PrimaryKeyConstraint('id_utilizator', 'id_carte', name='biblioteca_utilizator_pkey')
    )

    id_utilizator: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_carte: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_adaugarii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    carti: Mapped['Carti'] = relationship('Carti', back_populates='biblioteca_utilizator')
    utilizatori: Mapped['Utilizatori'] = relationship('Utilizatori', back_populates='biblioteca_utilizator')


class Capitole(Base):
    __tablename__ = 'capitole'
    __table_args__ = (
        CheckConstraint('numar_capitol >= 1', name='capitole_numar_pozitiv_check'),
        CheckConstraint('cost_puncte >= 0', name='capitole_cost_pozitiv_check'),
        ForeignKeyConstraint(['id_carte'], ['carti.id'], ondelete='CASCADE', name='capitole_id_carte_fkey'),
        PrimaryKeyConstraint('id', name='capitole_pkey'),
        UniqueConstraint('id_carte', 'numar_capitol', name='unique_book_chapter')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numar_capitol: Mapped[int] = mapped_column(Integer, nullable=False)
    titlu: Mapped[str] = mapped_column(String(150), nullable=False)
    continut: Mapped[str] = mapped_column(Text, nullable=False)
    id_carte: Mapped[Optional[int]] = mapped_column(Integer)
    este_gratuit: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))
    cost_puncte: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    stare: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'ciorna'::character varying"))
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    carti: Mapped[Optional['Carti']] = relationship('Carti', back_populates='capitole')
    comentarii: Mapped[list['Comentarii']] = relationship('Comentarii', back_populates='capitole')
    deblocari_capitole: Mapped[list['DeblocariCapitole']] = relationship('DeblocariCapitole', back_populates='capitole')
    progres_lectura: Mapped[list['ProgresLectura']] = relationship('ProgresLectura', back_populates='capitole')
    vizualizari_capitole: Mapped[list['VizualizariCapitole']] = relationship('VizualizariCapitole', back_populates='capitole')


t_categorii_carti = Table(
    'categorii_carti', Base.metadata,
    Column('id_carte', Integer, primary_key=True),
    Column('id_categorie', Integer, primary_key=True),
    ForeignKeyConstraint(['id_carte'], ['carti.id'], ondelete='CASCADE', name='categorii_carti_id_carte_fkey'),
    ForeignKeyConstraint(['id_categorie'], ['categorii.id'], ondelete='CASCADE', name='categorii_carti_id_categorie_fkey'),
    PrimaryKeyConstraint('id_carte', 'id_categorie', name='categorii_carti_pkey')
)


class IstoricAbonamente(Base):
    __tablename__ = 'istoric_abonamente'
    __table_args__ = (
        ForeignKeyConstraint(['id_nivel'], ['nivele_abonament.id'], ondelete='CASCADE', name='istoric_abonamente_id_nivel_fkey'),
        ForeignKeyConstraint(['id_plata'], ['plati.id'], ondelete='SET NULL', name='istoric_abonamente_id_plata_fkey'),
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='istoric_abonamente_id_utilizator_fkey'),
        PrimaryKeyConstraint('id', name='istoric_abonamente_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data_inceput: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    data_sfarsit: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    id_nivel: Mapped[Optional[int]] = mapped_column(Integer)
    id_plata: Mapped[Optional[int]] = mapped_column(Integer)
    stare: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'activ'::character varying"))

    nivele_abonament: Mapped[Optional['NiveleAbonament']] = relationship('NiveleAbonament', back_populates='istoric_abonamente')
    plati: Mapped[Optional['Plati']] = relationship('Plati', back_populates='istoric_abonamente')
    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='istoric_abonamente')


class Recenzii(Base):
    __tablename__ = 'recenzii'
    __table_args__ = (
        CheckConstraint('nota >= 1 AND nota <= 5', name='recenzii_nota_check'),
        ForeignKeyConstraint(['id_carte'], ['carti.id'], ondelete='CASCADE', name='recenzii_id_carte_fkey'),
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='recenzii_id_utilizator_fkey'),
        PrimaryKeyConstraint('id', name='recenzii_pkey'),
        UniqueConstraint('id_utilizator', 'id_carte', name='unique_user_review')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    id_carte: Mapped[Optional[int]] = mapped_column(Integer)
    nota: Mapped[Optional[int]] = mapped_column(Integer)
    text_comentariu: Mapped[Optional[str]] = mapped_column(Text)
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    carti: Mapped[Optional['Carti']] = relationship('Carti', back_populates='recenzii')
    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='recenzii')


class VenituriAutori(Base):
    __tablename__ = 'venituri_autori'
    __table_args__ = (
        ForeignKeyConstraint(['id_autor'], ['utilizatori.id'], ondelete='CASCADE', name='venituri_autori_id_autor_fkey'),
        ForeignKeyConstraint(['id_plata_sursa'], ['plati.id'], ondelete='SET NULL', name='venituri_autori_id_plata_sursa_fkey'),
        PrimaryKeyConstraint('id', name='venituri_autori_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    suma_castigata: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    comision_platforma: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    id_autor: Mapped[Optional[int]] = mapped_column(Integer)
    id_plata_sursa: Mapped[Optional[int]] = mapped_column(Integer)
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='venituri_autori')
    plati: Mapped[Optional['Plati']] = relationship('Plati', back_populates='venituri_autori')


class Comentarii(Base):
    __tablename__ = 'comentarii'
    __table_args__ = (
        ForeignKeyConstraint(['id_capitol'], ['capitole.id'], ondelete='CASCADE', name='comentarii_id_capitol_fkey'),
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='comentarii_id_utilizator_fkey'),
        PrimaryKeyConstraint('id', name='comentarii_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    continut: Mapped[str] = mapped_column(Text, nullable=False)
    id_capitol: Mapped[Optional[int]] = mapped_column(Integer)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    capitole: Mapped[Optional['Capitole']] = relationship('Capitole', back_populates='comentarii')
    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='comentarii')


class DeblocariCapitole(Base):
    __tablename__ = 'deblocari_capitole'
    __table_args__ = (
        ForeignKeyConstraint(['id_capitol'], ['capitole.id'], ondelete='CASCADE', name='deblocari_capitole_id_capitol_fkey'),
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='deblocari_capitole_id_utilizator_fkey'),
        PrimaryKeyConstraint('id', name='deblocari_capitole_pkey'),
        UniqueConstraint('id_utilizator', 'id_capitol', name='unique_user_chapter_unlock')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    id_capitol: Mapped[Optional[int]] = mapped_column(Integer)
    data_deblocarii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    capitole: Mapped[Optional['Capitole']] = relationship('Capitole', back_populates='deblocari_capitole')
    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='deblocari_capitole')


class ProgresLectura(Base):
    __tablename__ = 'progres_lectura'
    __table_args__ = (
        ForeignKeyConstraint(['id_carte'], ['carti.id'], ondelete='CASCADE', name='progres_lectura_id_carte_fkey'),
        ForeignKeyConstraint(['id_ultimul_capitol_citit'], ['capitole.id'], ondelete='CASCADE', name='progres_lectura_id_ultimul_capitol_citit_fkey'),
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='progres_lectura_id_utilizator_fkey'),
        PrimaryKeyConstraint('id', name='progres_lectura_pkey'),
        UniqueConstraint('id_utilizator', 'id_carte', name='unique_user_book')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    id_carte: Mapped[Optional[int]] = mapped_column(Integer)
    id_ultimul_capitol_citit: Mapped[Optional[int]] = mapped_column(Integer)
    data_actualizarii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    carti: Mapped[Optional['Carti']] = relationship('Carti', back_populates='progres_lectura')
    capitole: Mapped[Optional['Capitole']] = relationship('Capitole', back_populates='progres_lectura')
    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='progres_lectura')


class VizualizariCapitole(Base):
    __tablename__ = 'vizualizari_capitole'
    __table_args__ = (
        ForeignKeyConstraint(['id_capitol'], ['capitole.id'], ondelete='CASCADE', name='vizualizari_capitole_id_capitol_fkey'),
        ForeignKeyConstraint(['id_utilizator'], ['utilizatori.id'], ondelete='CASCADE', name='vizualizari_capitole_id_utilizator_fkey'),
        PrimaryKeyConstraint('id', name='vizualizari_capitole_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_capitol: Mapped[Optional[int]] = mapped_column(Integer)
    id_utilizator: Mapped[Optional[int]] = mapped_column(Integer)
    data_vizualizarii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    capitole: Mapped[Optional['Capitole']] = relationship('Capitole', back_populates='vizualizari_capitole')
    utilizatori: Mapped[Optional['Utilizatori']] = relationship('Utilizatori', back_populates='vizualizari_capitole')

class AlerteSistem(Base):
    __tablename__ = 'alerte_sistem'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='alerte_sistem_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mesaj: Mapped[str] = mapped_column(String(255), nullable=False)
    tip_alerta: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'info'::character varying"))
    data_crearii: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
