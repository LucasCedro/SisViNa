<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2 class="sidebar-title">Viveiro Nativas</h2>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <span>Página Inicial</span>
      </router-link>
      <router-link to="/viveiro" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.8">
          <path d="M2 9L12 2L22 9" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M4 10V20H20V10" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M12 20V10" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M4 14H20" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M4 10H20" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M7 14V20" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M17 14V20" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M7 7H9" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M15 7H17" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span>Viveiro</span>
      </router-link>
      <router-link to="/fitossanidade" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.8">
          <circle cx="12" cy="12" r="5" />
          <path d="M12 7V3" stroke-linecap="round" />
          <path d="M12 21v-4" stroke-linecap="round" />
          <path d="M7 12H3" stroke-linecap="round" />
          <path d="M21 12h-4" stroke-linecap="round" />
          <path d="M9 9L6 6" stroke-linecap="round" />
          <path d="M18 18l-3-3" stroke-linecap="round" />
          <path d="M9 15l-3 3" stroke-linecap="round" />
          <path d="M18 6l-3 3" stroke-linecap="round" />
          <circle cx="12" cy="12" r="2" />
          <circle cx="14" cy="9" r="1" />
          <circle cx="9" cy="11" r="1" />
          <circle cx="15" cy="14" r="1" />
        </svg>
        <span>Fitossanidade</span>
      </router-link>
      <router-link to="/fertilizacao" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.8">
          <!-- Letra N -->
          <path d="M4 7v10" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M4 7l4 10" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M8 7v10" stroke-linecap="round" stroke-linejoin="round" />

          <!-- Letra P -->
          <path d="M10 7v10" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M10 7h3" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M13 7v4" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M10 11h3" stroke-linecap="round" stroke-linejoin="round" />

          <!-- Letra K -->
          <path d="M15 7v10" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M15 12h1.5" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M16.5 12l2.5-5" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M16.5 12l2.5 5" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span>Fertilização</span>
      </router-link>
      <router-link to="/vendas-estoque" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <span>Vendas e Estoque</span>
      </router-link>
      <router-link to="/prescricao" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span>Prescrição Técnica</span>
      </router-link>
      <router-link to="/producao" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
        </svg>
        <span>Produção</span>
      </router-link>
      <router-link to="/estoques" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
        </svg>
        <span>Estoques</span>
      </router-link>
      <router-link to="/coleta" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="1.8">
          <!-- Semente elegante e simples -->
          <path d="M12 4C15 7 18 11 18 15C18 19 15 20 12 20C9 20 6 19 6 15C6 11 9 7 12 4Z" stroke-linecap="round"
            stroke-linejoin="round" />
          <path d="M12 9V12" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <span>Coleta de Sementes</span>
      </router-link>
      <router-link to="/biblioteca" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
        <span>Biblioteca</span>
      </router-link>
      <router-link to="/financeiro" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" class="nav-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>Financeiro</span>
      </router-link>
    </nav>
  </aside>
</template>

<style>
/* Adicione estilos da barra lateral aqui se necessário */
.sidebar {
  width: 230px;
  min-width: 230px;
  height: 100%;
  background-color: #2C3E50;
  color: white;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
}

.sidebar-nav {
  padding: var(--spacing-md) 0;
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: background-color 0.2s;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.router-link-active {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
  border-left: 3px solid var(--color-primary);
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-right: var(--spacing-md);
}

/* Para responsividade em telas pequenas */
@media (max-width: 768px) {
  .sidebar {
    width: 60px;
    min-width: 60px;
  }

  .sidebar-title {
    display: none;
  }

  .nav-item span {
    display: none;
  }

  .nav-icon {
    margin-right: 0;
  }

  .sidebar-header {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: var(--spacing-md);
  }
}
</style>