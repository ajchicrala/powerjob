<template>
  <form class="login-form" @submit.prevent="handleLogin">
    <h2>Bem-vindo de volta</h2>
    <p>Entre com suas credenciais para acessar o sistema</p>

    <label>Email</label>
    <input
      type="email"
      placeholder="seu@email.com"
      v-model="email"
      required
    />

    <label>Senha</label>
    <input
      type="password"
      placeholder="••••••••"
      v-model="senha"
      required
    />

    <div class="options">
      <label>
        <input type="checkbox" v-model="lembrar" />
        Lembrar-me
      </label>

      <a href="#">Esqueceu a senha?</a>
    </div>

    <button type="submit" :disabled="loading">
      {{ loading ? 'Entrando...' : 'Entrar' }}
    </button>

    <p v-if="error" class="error">{{ error }}</p>

    <small>
      Não tem uma conta?
      <a href="#">Entre em contato com o administrador</a>
    </small>
  </form>
</template>


<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '@/services/authService'

const router = useRouter()

const email = ref('')
const senha = ref('')
const lembrar = ref(false)

const loading = ref(false)
const error = ref(null)

async function handleLogin() {
  error.value = null
  loading.value = true

  try {
    const user = await login(email.value, senha.value)

    // 🔐 Salvar usuário
    const storage = lembrar.value ? localStorage : sessionStorage
    storage.setItem('user', JSON.stringify(user))

    // 🚀 Redirecionar
    router.push('/app')

  } catch (err) {
  console.error(err)

  if (err.response?.status === 401) {
    error.value = 'Email ou senha inválidos'
  } else if (err.response?.status === 405) {
    error.value = 'Método não permitido'
  } else {
    error.value = 'Erro ao conectar com o servidor'
  }
}
 finally {
    loading.value = false
  }
}
</script>


<style scoped>
.error {
  margin-top: 16px;
  color: #dc2626;
  font-size: 14px;
  text-align: center;
}


.login-form {
  width: 90%;
  background: #ffffff;
  padding: 48px;
  border-radius: 14px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
}

.login-form h2 {
  font-size: 26px;
  margin-bottom: 10px;
}

.login-form p {
  margin-bottom: 36px;
  font-size: 15px;
  color: #6b7280;
}

label {
  font-size: 14px;
  margin-bottom: 6px;
  display: block;
}

input[type='email'],
input[type='password'] {
  width: 100%;
  padding: 14px 16px;
  border-radius: 10px;
  border: 1px solid #d1d5db;
  margin-bottom: 18px;
  font-size: 15px;
}

.options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  margin-bottom: 28px;
}

button {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  background: #1f3556;
  color: #ffffff;
  font-weight: 600;
  font-size: 15px;
  border: none;
  cursor: pointer;
  transition: background 0.2s ease;
}

button:hover {
  background: #223f68;
}

small {
  display: block;
  margin-top: 28px;
  text-align: center;
  font-size: 13px;
  color: #6b7280;
}

</style>
