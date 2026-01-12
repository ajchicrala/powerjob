import { createRouter, createWebHistory } from 'vue-router'

// Layouts
import PublicLayout from '@/layouts/PublicLayout.vue'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

// Páginas
import Login from '@/components/Login.vue'
// import Dashboard from '@/views/Dashboard.vue' // futuro

const routes = [
  // Redirect raiz → login
  {
    path: '/',
    redirect: '/login'
  },

  // 🔓 Rotas públicas (login)
  {
    path: '/login',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'Login',
        component: Login
      }
    ]
  },

  // 🔒 Rotas privadas (sistema)
  {
    path: '/app',
    component: DefaultLayout,
    children: [
      // Exemplo futuro:
      // {
      //   path: 'dashboard',
      //   name: 'Dashboard',
      //   component: Dashboard
      // }
    ]
  },

  // Fallback (rota não encontrada)
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  },

  {
    path: '/app',
    component: () => import('@/layouts/DefaultLayout.vue')
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
