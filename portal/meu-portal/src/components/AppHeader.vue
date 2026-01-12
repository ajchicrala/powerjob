<template>
  <header class="header">
    <button class="toggle" @click="$emit('toggle-sidebar')">
      ☰
    </button>
    <strong>Dashboard</strong>
  </header>
</template>

<style scoped>
.header {
  height: 56px;
  background: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.toggle {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}
</style>
