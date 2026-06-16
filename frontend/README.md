# AeroPredict Argentina — Frontend

Panel web (SPA) para **AeroPredict**, el trabajo práctico de análisis de
conectividad aérea argentina. Consume la API REST del backend (FastAPI) y
muestra rutas, aeropuertos y reportes con tablas y gráficos.

> Esta es la **parte de frontend** del TP. El backend (FastAPI + PostgreSQL),
> el pipeline de datos y el modelo viven en otras ramas del repositorio.

## Stack

- **React 18** + **TypeScript**
- **Vite** (servidor de desarrollo y build)
- **React Router** (ruteo SPA)
- **Recharts** (gráficos)
- Sin framework de CSS: estilos propios en `src/index.css`.

## Requisitos

- Node.js 18+ (probado con Node 22)
- El backend de AeroPredict corriendo (por defecto en `http://localhost:8000`)

## Puesta en marcha

```bash
cd frontend
npm install
cp .env.example .env     # opcional: ajustar VITE_API_URL si el backend no está en :8000
npm run dev
```

La app queda disponible en **http://localhost:3000** (puerto elegido a
propósito porque el CORS del backend ya lo permite).

### Scripts

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo con hot-reload en el puerto 3000 |
| `npm run build` | Chequeo de tipos (`tsc`) + build de producción en `dist/` |
| `npm run preview` | Sirve el build de producción |
| `npm run typecheck` | Solo chequeo de tipos |

## Configuración

La única variable es la URL del backend:

```
VITE_API_URL=http://localhost:8000
```

Si no se define, se usa `http://localhost:8000` por defecto.

## Estructura

```
frontend/
├── index.html
├── vite.config.ts          # servidor en puerto 3000
├── src/
│   ├── main.tsx            # entrada (Router + AuthProvider)
│   ├── App.tsx            # definición de rutas
│   ├── index.css          # estilos globales
│   ├── constants.ts       # años, meses, paleta de gráficos
│   ├── api/
│   │   ├── client.ts      # cliente HTTP + JWT + manejo de errores
│   │   └── types.ts       # tipos espejo de los schemas Pydantic
│   ├── context/
│   │   └── AuthContext.tsx # login/logout, token en localStorage
│   ├── hooks/
│   │   └── useAsync.ts     # hook de fetch (data/loading/error/reload)
│   ├── components/
│   │   ├── Layout.tsx      # sidebar + topbar + estado del backend
│   │   ├── ProtectedRoute.tsx
│   │   ├── Pagination.tsx
│   │   └── ui.tsx          # Card, StatCard, badges, loading, errores
│   └── pages/
│       ├── Dashboard.tsx
│       ├── Rutas.tsx
│       ├── RutaDetalle.tsx
│       ├── Aeropuertos.tsx
│       ├── Reportes.tsx    # contenedor con pestañas
│       ├── reportes/       # Top rutas, Tendencias, Aerolíneas, Alertas, Ocupación
│       ├── Admin.tsx       # protegida con JWT
│       ├── Login.tsx
│       └── NotFound.tsx
```

## Funcionalidades

- **Dashboard**: totales (rutas, aeropuertos, alertas), top rutas por año y
  vista rápida de alertas de ocupación.
- **Rutas**: listado paginado con búsqueda por nombre y filtros avanzados
  (año, mes, origen, destino, factor de ocupación). Detalle con desglose por
  aerolínea.
- **Aeropuertos**: listado y búsqueda por nombre / localidad / provincia, con
  enlace al mapa.
- **Reportes**: top rutas, tendencias de una ruta, participación por aerolínea,
  alertas y ocupación por período (gráficos de barras, líneas y torta).
- **Admin** (requiere login JWT): metadata del último sync y recarga de datos
  desde el pipeline (`POST /admin/reload-data`).

## Autenticación

La mayoría de los endpoints son de consulta libre, así que el panel funciona
sin iniciar sesión. El login (usuario/contraseña → JWT) solo es necesario para
la sección **Admin**. El token se guarda en `localStorage` y se envía como
`Authorization: Bearer <token>` en los endpoints protegidos.

> Para crear el usuario inicial seguí las instrucciones del `BACKEND.md`
> (por defecto `admin` / `admin123`).

## Mapeo de endpoints

| Pantalla | Endpoint del backend |
|---|---|
| Dashboard | `GET /api/rutas`, `GET /api/aeropuertos`, `GET /api/reportes/alertas`, `GET /api/reportes/top-rutas` |
| Rutas | `GET /api/rutas`, `GET /api/rutas/buscar/avanzada`, `GET /api/rutas/ruta/{nombre}` |
| Detalle de ruta | `GET /api/rutas/{id}` |
| Aeropuertos | `GET /api/aeropuertos`, `GET /api/aeropuertos/buscar/avanzada` |
| Reportes | `GET /api/reportes/{ocupacion,tendencias,alertas,top-rutas,aerolineas}` |
| Login | `POST /auth/login` |
| Admin | `GET /admin/last-sync`, `POST /admin/reload-data` |
