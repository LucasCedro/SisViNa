import axios from 'axios'

const ADMIN_VIVEIRO_KEY = 'brotare_admin_viveiro_id'
const ADMIN_EMPRESA_KEY = 'brotare_admin_empresa_id'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    }
})

function adminViveiroHeader() {
    try {
        const raw = localStorage.getItem(ADMIN_VIVEIRO_KEY)
        if (!raw) return null
        const id = Number(raw)
        return Number.isFinite(id) && id > 0 ? id : null
    } catch {
        return null
    }
}

function adminEmpresaHeader() {
    try {
        const raw = localStorage.getItem(ADMIN_EMPRESA_KEY)
        if (!raw) return null
        const id = Number(raw)
        return Number.isFinite(id) && id > 0 ? id : null
    } catch {
        return null
    }
}

// Interceptor para autenticação + contexto empresa/viveiro (admin plataforma)
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    const empresaId = adminEmpresaHeader()
    if (empresaId) {
        config.headers['X-Empresa-Id'] = String(empresaId)
    }
    const viveiroId = adminViveiroHeader()
    if (viveiroId) {
        config.headers['X-Viveiro-Id'] = String(viveiroId)
    }
    return config
})

api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
            localStorage.removeItem('token')
            if (window.location.pathname !== '/login') {
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default api 