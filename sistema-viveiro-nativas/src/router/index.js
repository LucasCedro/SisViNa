import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '../store/auth'

const routes = [
    {
        path: '/login',
        name: 'login',
        component: () => import('../views/LoginView.vue'),
        meta: { public: true, layout: 'blank' }
    },
    {
        path: '/',
        name: 'home',
        component: HomeView
    },
    {
        path: '/viveiro',
        name: 'viveiro',
        component: () => import('../views/viveiro/ViveiroView.vue')
    },
    {
        path: '/viveiro/planta-editor',
        name: 'planta-editor',
        component: () => import('../views/viveiro/PlantaBaixaEditorView.vue')
    },
    {
        path: '/fitossanidade',
        name: 'fitossanidade',
        component: () => import('../views/viveiro/FitossanidadeView.vue')
    },
    {
        path: '/fertilizacao',
        name: 'fertilizacao',
        component: () => import('../views/viveiro/FertilizacaoView.vue')
    },
    {
        path: '/vendas-estoque',
        name: 'vendas-estoque',
        component: () => import('../views/viveiro/VendasEstoqueView.vue')
    },
    {
        path: '/prescricao',
        name: 'prescricao',
        component: () => import('../views/prescricao/PrescricaoView.vue')
    },
    {
        path: '/coleta',
        name: 'coleta',
        component: () => import('../views/coleta/ColetaView.vue')
    },
    {
        path: '/biblioteca',
        name: 'biblioteca',
        component: () => import('../views/biblioteca/BibliotecaView.vue')
    },
    {
        path: '/financeiro',
        name: 'financeiro',
        component: () => import('../views/financeiro/FinanceiroView.vue')
    }
]

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
})

router.beforeEach(async (to) => {
    const auth = useAuthStore()

    if (to.meta.public) {
        if (to.name === 'login' && auth.isAuthenticated) {
            return { path: '/' }
        }
        return true
    }

    if (!auth.isAuthenticated) {
        return { name: 'login', query: { redirect: to.fullPath } }
    }

    if (!auth.user) {
        try {
            await auth.hydrate()
        } catch {
            return { name: 'login', query: { redirect: to.fullPath } }
        }
    }

    return true
})

export default router
