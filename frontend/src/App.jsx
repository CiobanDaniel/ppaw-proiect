import { useEffect, useState } from 'react'
import './App.css'

const API_URL = '/api/v1'

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

function App() {
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

export default App
