import { useState } from 'react'

import { Aerolineas } from './reportes/Aerolineas'
import { Alertas } from './reportes/Alertas'
import { Ocupacion } from './reportes/Ocupacion'
import { Tendencias } from './reportes/Tendencias'
import { TopRutas } from './reportes/TopRutas'

type Tab = 'top' | 'tendencias' | 'aerolineas' | 'alertas' | 'ocupacion'

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'top', label: 'Top rutas', icon: '🏆' },
  { id: 'tendencias', label: 'Tendencias', icon: '📈' },
  { id: 'aerolineas', label: 'Aerolíneas', icon: '🏢' },
  { id: 'alertas', label: 'Alertas', icon: '🚨' },
  { id: 'ocupacion', label: 'Ocupación', icon: '🎟️' },
]

export function Reportes() {
  const [tab, setTab] = useState<Tab>('top')

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Reportes y análisis</h1>
          <p className="page-sub">Métricas agregadas sobre la conectividad aérea.</p>
        </div>
      </div>

      <div className="tabs" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            className={`tab${tab === t.id ? ' active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            <span aria-hidden="true">{t.icon}</span> {t.label}
          </button>
        ))}
      </div>

      {tab === 'top' && <TopRutas />}
      {tab === 'tendencias' && <Tendencias />}
      {tab === 'aerolineas' && <Aerolineas />}
      {tab === 'alertas' && <Alertas />}
      {tab === 'ocupacion' && <Ocupacion />}
    </div>
  )
}
