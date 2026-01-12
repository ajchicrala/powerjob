<template>

  <div class="login-page">
    <!-- resto do layout -->

    <!-- Lado esquerdo -->
    <section class="left">
      <div class="brand">
        <span>PowerJob</span>
      </div>

      <h1>Gerencie suas cotações<br />de forma inteligente</h1>

      <p>
        Acompanhe todo o pipeline de cotações, desde a solicitação inicial
        até o fechamento, com visibilidade completa do seu processo comercial.
      </p>

      <div class="stats">
        <div>
          <strong>500+</strong>
          <span>Cotações mensais</span>
        </div>
        <div>
          <strong>98%</strong>
          <span>Taxa de conversão</span>
        </div>
        <div>
          <strong>24h</strong>
          <span>Tempo médio</span>
        </div>
      </div>
    </section>

    <!-- Lado direito -->
    <section class="right">
      <router-view />
    </section>
  </div>
</template>

<style scoped>
.login-page {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  height: 100vh;
}

/* Lado esquerdo */
.left {
  background: linear-gradient(135deg, #1f3556, #223f68);
  color: #fff;
  padding: 96px 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.left h1 {
  font-size: 44px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 28px;
}

.left p {
  font-size: 16px;
  max-width: 480px;
  opacity: 0.9;
  line-height: 1.6;
}

.stats {
  display: flex;
  gap: 56px;
  margin-top: 72px;
}

.stats strong {
  font-size: 30px;
}

.stats span {
  font-size: 14px;
  opacity: 0.85;
}

/* Lado direito */
.right {
  background: #f6f8fb;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}


@media (max-width: 1024px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .left {
    display: none;
  }
}

</style>


