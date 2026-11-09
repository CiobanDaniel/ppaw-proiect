import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [utilizatori, setUtilizatori] = useState([]);
  const [eroare, setEroare] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8080/utilizatori')
      .then(response => response.json())
      .then(data => {
        if (data.eroare) {
          setEroare(data.eroare);
        } else {
          setUtilizatori(data);
        }
      })
      .catch(err => setEroare(err.toString()));
  }, []);

  return (
    <div className="App">
      <h1>Utilizatori din Baza de Date (Test Conexiune)</h1>
      {eroare && <p style={{ color: 'red' }}>Eroare: {eroare}</p>}
      <table border="1" cellPadding="10" style={{ margin: '0 auto', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nume Utilizator</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Puncte</th>
          </tr>
        </thead>
        <tbody>
          {utilizatori.map(user => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.nume_utilizator}</td>
              <td>{user.email}</td>
              <td>{user.rol}</td>
              <td>{user.puncte}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;