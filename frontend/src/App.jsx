import { useEffect, useState } from 'react'
import './App.css'

const API_URL = '/api/v1'
const ADMIN_CATEGORIES_PATH = '/admin/categorii-api'

function messageFrom(error) {
  return error instanceof Error ? error.message : 'A apărut o eroare neașteptată.'
}

async function requestJson(path) {
  const response = await fetch(`${API_URL}${path}`, { credentials: 'same-origin' })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail || 'Datele nu au putut fi încărcate.')
  }
  return response.json()
}

async function categoriesRequest(path, options = {}) {
  const response = await fetch(`/api/categorii${path}`, {
    credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail || 'Operația nu a putut fi finalizată.')
  }
  return response.status === 204 ? null : response.json()
}

function CategoryManager() {
  const [categorii, setCategorii] = useState([])
  const [nume, setNume] = useState('')
  const [descriere, setDescriere] = useState('')
  const [editId, setEditId] = useState(null)
  const [eroare, setEroare] = useState('')
  const [mesaj, setMesaj] = useState('')
  const [incarca, setIncarca] = useState(true)

  const incarcaCategorii = () => {
    setIncarca(true)
    return categoriesRequest('')
      .then(setCategorii)
      .catch((error) => setEroare(messageFrom(error)))
      .finally(() => setIncarca(false))
  }

  useEffect(() => {
    let active = true
    categoriesRequest('')
      .then((date) => { if (active) setCategorii(date) })
      .catch((error) => { if (active) setEroare(messageFrom(error)) })
      .finally(() => { if (active) setIncarca(false) })
    return () => { active = false }
  }, [])

  function resetForm() {
    setEditId(null)
    setNume('')
    setDescriere('')
  }

  async function salveazaCategorie(event) {
    event.preventDefault()
    setEroare('')
    setMesaj('')
    try {
      const payload = { nume, descriere: descriere || null }
      if (editId) {
        await categoriesRequest(`/${editId}`, { method: 'PUT', body: JSON.stringify(payload) })
        setMesaj('Categoria a fost actualizată.')
      } else {
        await categoriesRequest('', { method: 'POST', body: JSON.stringify(payload) })
        setMesaj('Categoria a fost creată.')
      }
      resetForm()
      await incarcaCategorii()
    } catch (error) {
      setEroare(messageFrom(error))
    }
  }

  function editeazaCategorie(categorie) {
    setEditId(categorie.id)
    setNume(categorie.nume)
    setDescriere(categorie.descriere || '')
    setMesaj('')
    setEroare('')
  }

  async function stergeCategorie(categorie) {
    if (!window.confirm(`Ștergi categoria „${categorie.nume}”?`)) return
    setEroare('')
    setMesaj('')
    try {
      await categoriesRequest(`/${categorie.id}`, { method: 'DELETE' })
      if (editId === categorie.id) resetForm()
      setMesaj('Categoria a fost ștearsă.')
      await incarcaCategorii()
    } catch (error) {
      setEroare(messageFrom(error))
    }
  }

  return (
    <main className="admin-api-shell">
      <header className="admin-api-header"><a className="brand" href="/admin">Creator Hub · Admin</a><a href="/">Vezi platforma</a></header>
      <div className="admin-api-content">
        <p className="eyebrow">Laborator 8 · frontend + API</p>
        <h1>Gestionare categorii</h1>
        <p className="description">Acest ecran React consumă direct endpointurile REST pentru categorii.</p>
        {eroare && <div className="notice error" role="alert">{eroare}</div>}
        {mesaj && <div className="notice" role="status">{mesaj}</div>}
        <section className="category-manager">
          <form className="category-form" onSubmit={salveazaCategorie}>
            <h2>{editId ? 'Editează categoria' : 'Categorie nouă'}</h2>
            <label>Nume<input value={nume} onChange={(event) => setNume(event.target.value)} required maxLength="100" /></label>
            <label>Descriere<textarea value={descriere} onChange={(event) => setDescriere(event.target.value)} rows="4" /></label>
            <div><button className="primary-button" type="submit">{editId ? 'Salvează' : 'Creează'}</button>{editId && <button className="text-button cancel-button" type="button" onClick={resetForm}>Anulează</button>}</div>
          </form>
          <section className="category-list" aria-labelledby="categories-title">
            <h2 id="categories-title">Categorii existente</h2>
            {incarca ? <p className="loading">Se încarcă…</p> : <ul>{categorii.map((categorie) => <li key={categorie.id}><div><strong>{categorie.nume}</strong><p>{categorie.descriere || 'Fără descriere'}</p></div><div className="category-actions"><button className="text-button" onClick={() => editeazaCategorie(categorie)}>Editează</button><button className="danger-button" onClick={() => stergeCategorie(categorie)}>Șterge</button></div></li>)}</ul>}
          </section>
        </section>
      </div>
    </main>
  )
}

function PublicCatalog() {
  const [carti, setCarti] = useState([])
  const [carteSelectata, setCarteSelectata] = useState(null)
  const [capitolCitit, setCapitolCitit] = useState(null)
  const [incarca, setIncarca] = useState(true)
  const [eroare, setEroare] = useState('')

  useEffect(() => {
    requestJson('/carti')
      .then(setCarti)
      .catch((error) => setEroare(messageFrom(error)))
      .finally(() => setIncarca(false))
  }, [])

  async function deschideCarte(carteId) {
    setEroare('')
    setCapitolCitit(null)
    try {
      setCarteSelectata(await requestJson(`/carti/${carteId}`))
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (error) {
      setEroare(messageFrom(error))
    }
  }

  async function citesteCapitol(capitolId) {
    setEroare('')
    try {
      setCapitolCitit(await requestJson(`/capitole/${capitolId}/citire`))
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (error) {
      setEroare(messageFrom(error))
    }
  }

  if (capitolCitit) {
    return (
      <main className="reader-shell">
        <button className="back-link" onClick={() => setCapitolCitit(null)}>← Înapoi la carte</button>
        <article className="reader">
          <p className="eyebrow">Capitolul {capitolCitit.numar_capitol}</p>
          <h1>{capitolCitit.titlu}</h1>
          <div className="reader-content">{capitolCitit.continut}</div>
        </article>
      </main>
    )
  }

  if (carteSelectata) {
    return (
      <main className="detail-shell">
        <button className="back-link" onClick={() => setCarteSelectata(null)}>← Toate publicațiile</button>
        <section className="book-detail">
          <div className="book-cover large-cover" aria-hidden="true">
            {carteSelectata.url_imagine_coperta ? <img src={carteSelectata.url_imagine_coperta} alt="" /> : 'CH'}
          </div>
          <div>
            <p className="eyebrow">{carteSelectata.autor || 'Autor Creator Hub'}</p>
            <h1>{carteSelectata.titlu}</h1>
            <p className="description">{carteSelectata.descriere || 'Descrierea acestei publicații va fi disponibilă în curând.'}</p>
            {carteSelectata.categorii.length > 0 && <div className="tags">{carteSelectata.categorii.map((categorie) => <span key={categorie}>{categorie}</span>)}</div>}
          </div>
        </section>
        <section className="chapters" aria-labelledby="chapters-title">
          <h2 id="chapters-title">Capitole</h2>
          {carteSelectata.capitole.length === 0 ? <p>Nu există capitole publicate momentan.</p> : (
            <ol>{carteSelectata.capitole.map((capitol) => (
              <li key={capitol.id}>
                <div><strong>{capitol.numar_capitol}. {capitol.titlu}</strong><small>{capitol.este_gratuit ? 'Disponibil pentru guest' : `${capitol.cost_puncte} puncte`}</small></div>
                {capitol.este_gratuit ? <button className="primary-button" onClick={() => citesteCapitol(capitol.id)}>Citește</button> : <span className="locked">Acces restricționat</span>}
              </li>
            ))}</ol>
          )}
        </section>
      </main>
    )
  }

  return (
    <main>
      <header className="hero-section">
        <nav><a className="brand" href="/">Creator Hub</a><span>Lectură pentru orice moment</span></nav>
        <div className="hero-copy">
          <p className="eyebrow">Platformă pentru creatori și cititori</p>
          <h1>Descoperă povești create pentru tine.</h1>
          <p>Poți explora gratuit capitolele publicate. O sesiune de guest este creată doar atunci când începi să citești, fără a crea un cont în baza de date.</p>
        </div>
      </header>
      <section className="catalog" aria-labelledby="catalog-title">
        <div className="section-heading"><div><p className="eyebrow">Catalog public</p><h2 id="catalog-title">Ce poți citi acum</h2></div><span>{carti.length} publicații</span></div>
        {eroare && <div className="notice error" role="alert">{eroare}</div>}
        {incarca ? <p className="loading">Se încarcă publicațiile…</p> : (
          <div className="book-grid">{carti.map((carte) => (
            <article className="book-card" key={carte.id}>
              <div className="book-cover" aria-hidden="true">{carte.url_imagine_coperta ? <img src={carte.url_imagine_coperta} alt="" /> : carte.titlu.slice(0, 2).toUpperCase()}</div>
              <div className="book-card-content"><p className="author">{carte.autor || 'Autor Creator Hub'}</p><h3>{carte.titlu}</h3><p>{carte.descriere || 'O publicație disponibilă în catalogul Creator Hub.'}</p><button className="text-button" onClick={() => deschideCarte(carte.id)}>Vezi cartea <span aria-hidden="true">→</span></button></div>
            </article>
          ))}</div>
        )}
        {!incarca && carti.length === 0 && !eroare && <div className="notice">Catalogul nu are încă publicații.</div>}
      </section>
    </main>
  )
}

function App() {
  return window.location.pathname === ADMIN_CATEGORIES_PATH ? <CategoryManager /> : <PublicCatalog />
}

export default App
