import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="page">
      <div className="notfound">
        <div className="notfound-code">404</div>
        <p>La página que buscás no existe o despegó sin vos.</p>
        <Link to="/" className="btn btn-primary">
          ← Volver al dashboard
        </Link>
      </div>
    </div>
  )
}
