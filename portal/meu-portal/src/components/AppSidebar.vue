<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="logo">
      <span v-if="!collapsed">MyPortal</span>
      <span v-else>MP</span>
    </div>

    <nav class="menu">
      <a href="#">Social</a>
      <a href="#">Newsletter</a>
      <a href="#">Bookings</a>
      <a href="#">Promotions</a>
      <a href="#">Training</a>
      <a href="#">Trips</a>
      <a href="#">News</a>
      <a href="#">Profile</a>
    </nav>
  </aside>
</template>

<script setup>
defineProps({
  collapsed: Boolean
})
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: #1f2d3d;
  color: #ffffff;
  padding: 20px;
  overflow-y: auto;
  transition: width 0.25s ease;
}

.sidebar.collapsed {
  width: 64px;
  padding: 20px 8px;
}

.logo {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 24px;
  text-align: center;
}

.menu a {
  display: block;
  color: #cfd8dc;
  text-decoration: none;
  padding: 10px 0;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.menu a:hover {
  color: #ffffff;
}
</style>
