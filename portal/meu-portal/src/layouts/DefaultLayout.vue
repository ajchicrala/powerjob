<template>
  <div class="layout">
    <!-- Header -->
    <header class="header">
      <h1 class="logo">PowerJob</h1>
    </header>

    <div class="body">
      <!-- Sidebar -->
      <aside class="sidebar">
        <nav>
          <ul>
            <li>Dashboard</li>
            <li>Cotações</li>
            <li>Relatórios</li>
            <li>Configurações</li>
          </ul>
        </nav>
      </aside>

      <!-- Conteúdo principal -->
      <main class="content">
        <!-- AQUI entra o Login.vue e qualquer outra página -->
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
// Layout não precisa de lógica por enquanto
</script>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f6f8;
}

/* Header */
.header {
  height: 64px;
  background-color: #1f3556;
  color: #fff;
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

/* Corpo */
.body {
  flex: 1;
  display: flex;
}

/* Sidebar */
.sidebar {
  width: 220px;
  background-color: #1f3556;
  color: #fff;
  padding: 24px 16px;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  padding: 10px 8px;
  cursor: pointer;
  border-radius: 4px;
}

.sidebar li:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Conteúdo */
.content {
  flex: 1;
  padding: 32px;
  background-color: #ffffff;
}
</style>
