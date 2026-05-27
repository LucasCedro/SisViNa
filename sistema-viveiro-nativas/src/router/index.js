import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '../store/auth'
import { canAccess, resolvePerfisFromUser } from '../constants/roles'

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
        component: HomeView,
        meta: { hidePageTitle: true, permission: 'home.view' }
    },
    {
        path: '/viveiro',
        name: 'viveiro',
        component: () => import('../views/viveiro/ViveiroView.vue'),
        meta: { permission: 'viveiro.view' }
    },
    {
        path: '/producao',
        name: 'producao',
        component: () => import('../views/viveiro/ProducaoView.vue'),
        meta: { permission: 'producao.view' }
    },
    {
        path: '/estoques',
        name: 'estoques',
        component: () => import('../views/viveiro/EstoquesView.vue'),
        meta: { permission: 'estoques.view' }
    },
    {
        path: '/viveiro/planta-editor',
        name: 'planta-editor',
        component: () => import('../views/viveiro/PlantaBaixaEditorView.vue'),
        meta: { permission: 'viveiro.edit' }
    },
    {
        path: '/fitossanidade',
        name: 'fitossanidade',
        component: () => import('../views/viveiro/FitossanidadeView.vue'),
        meta: { permission: 'fitossanidade.view' }
    },
    {
        path: '/fertilizacao',
        name: 'fertilizacao',
        component: () => import('../views/viveiro/FertilizacaoView.vue'),
        meta: { permission: 'fertilizacao.view' }
    },
    {
        path: '/vendas',
        name: 'vendas',
        component: () => import('../views/viveiro/VendasView.vue'),
        meta: { permission: 'vendas.view' }
    },
    {
        path: '/vendas-estoque',
        redirect: '/vendas'
    },
    {
        path: '/prescricao',
        name: 'prescricao',
        component: () => import('../views/prescricao/PrescricaoView.vue'),
        meta: { permission: 'prescricao.view' }
    },
    {
        path: '/coleta',
        name: 'coleta',
        component: () => import('../views/coleta/ColetaView.vue'),
        meta: { permission: 'coleta.view' }
    },
    {
        path: '/biblioteca',
        name: 'biblioteca',
        component: () => import('../views/biblioteca/BibliotecaView.vue'),
        meta: { permission: 'biblioteca.view' }
    },
    {
        path: '/financeiro',
        name: 'financeiro',
        component: () => import('../views/financeiro/FinanceiroView.vue'),
        meta: { permission: 'financeiro.view' }
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

    const perm = to.meta.permission
    if (perm) {
        const perfis = resolvePerfisFromUser(auth.user)
        if (!canAccess(perfis, perm)) {
            return { path: '/', query: { acesso: 'negado' } }
        }
    }

    return true
})

export default router
