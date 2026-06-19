import { useMemo, useState } from 'react'

import { api } from '../../api/client'
import { Card, EmptyState, ErrorMessage, Loading, OccupancyBadge } from '../../components/ui'
import { useAsync } from '../../hooks/useAsync'
import { formatNumber, formatPeriodo } from '../../utils/format'

type Filtro = 'todas' | 'baja' | 'elevada'

export function Alertas() {
  const [filtro, setFiltro] = useState<Filtro>('todas')

  const resultado = useAsync(() => api.alertas(500), [])

  const alertas = useMemo(() => {
    const data = resultado.data ?? []
    if (filtro === 'todas') return data
    return data.filter((a) => a.tipo === filtro)
  }, [resultado.data, filtro])

  return (
    <div className="report">
      <Card
        title="Alertas de ocupación"
        actions={
          <div className="segmented">
            {(['todas', 'baja', 'elevada'] as Filtro[]).map((f) => (
              <button
                key={f}
                type="button"
                className={`segmented-btn${filtro === f ? ' active' : ''}`}
                onClick={() => setFiltro(f)}
              >
                {f === 'todas' ? 'Todas' : f === 'baja' ? 'Baja' : 'Elevada'}
              </button>
            ))}
          </div>
        }
      >
        <p className="muted">
          Rutas con ocupación <strong>baja</strong> (&lt; 60%) o <strong>elevada</strong>{' '}
          (≥ 85%), según los umbrales de negocio del pipeline.
        </p>

        {resultado.loading ? (
          <Loading />
        ) : resultado.error ? (
          <ErrorMessage message={resultado.error} onRetry={resultado.reload} />
        ) : alertas.length === 0 ? (
          <EmptyState message="No hay alertas para ese filtro." />
        ) : (
          <>
            <p className="muted">{formatNumber(alertas.length)} alertas.</p>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Ruta</th>
                    <th>Período</th>
                    <th>Tipo</th>
                    <th className="num">Umbral</th>
                    <th className="num">Ocupación</th>
                  </tr>
                </thead>
                <tbody>
                  {alertas.map((a, i) => (
                    <tr key={`${a.ruta}-${a.anio}-${a.mes}-${i}`}>
                      <td>{a.ruta}</td>
                      <td>{formatPeriodo(a.anio, a.mes)}</td>
                      <td>
                        <span className={`badge badge-${a.tipo}`}>{a.tipo}</span>
                      </td>
                      <td className="num">{(a.umbral * 100).toFixed(0)}%</td>
                      <td className="num">
                        <OccupancyBadge factor={a.factor_ocupacion} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
