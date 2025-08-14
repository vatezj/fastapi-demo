<template>
  <div class="login">
    <div class="login-container">
      <div class="login-header">
        <div class="logo">
          <!-- <svg-icon icon-class="dashboard" class="logo-icon" /> -->
          <img src="../assets/logo/logo.png" alt="logo" class="logo-icon" style="width: 60px; height: 60px;">  
        </div>
        <h1 class="system-title">{{ VITE_APP_TITLE }}</h1>
        <p class="system-subtitle">安全 · 高效 · 智能</p>
      </div>
      
      <el-form ref="loginRef" :model="loginForm" :rules="loginRules" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            type="text"
            size="large"
            auto-complete="off"
            placeholder="请输入账号"
            class="custom-input"
          >
            <template #prefix>
              <svg-icon icon-class="user" class="input-icon" />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            size="large"
            auto-complete="off"
            placeholder="请输入密码"
            class="custom-input"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <svg-icon icon-class="password" class="input-icon" />
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="code" v-if="captchaEnabled">
          <div class="captcha-container">
            <el-input
              v-model="loginForm.code"
              size="large"
              auto-complete="off"
              placeholder="验证码"
              class="captcha-input"
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <svg-icon icon-class="validCode" class="input-icon" />
              </template>
            </el-input>
            <div class="captcha-image">
              <img :src="codeUrl" @click="getCode" class="captcha-img" alt="验证码"/>
            </div>
          </div>
        </el-form-item>
        
        <div class="form-options">
          <el-checkbox v-model="loginForm.rememberMe" class="remember-me">
            记住密码
          </el-checkbox>
          <div v-if="register" class="register-link">
            <router-link :to="'/register'">立即注册</router-link>
          </div>
        </div>
        
        <el-form-item class="login-button-container">
          <el-button
            :loading="loading"
            size="large"
            type="primary"
            class="login-button"
            @click.prevent="handleLogin"
          >
            <span v-if="!loading">登 录</span>
            <span v-else>登 录 中...</span>
          </el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="login-footer">
      <div class="footer-content">
        <p class="copyright">Copyright © 2025 insistence.tech All Rights Reserved.</p>
        <p class="powered-by">Powered by FastapiAdmin</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getCodeImg } from "@/api/login";
import Cookies from "js-cookie";
import { encrypt, decrypt } from "@/utils/jsencrypt";
import useUserStore from '@/store/modules/user'

const { VITE_APP_TITLE } = import.meta.env;

const userStore = useUserStore()
const route = useRoute();
const router = useRouter();
const { proxy } = getCurrentInstance();

const loginForm = ref({
  username: "",
  password: "",
  rememberMe: false,
  code: "",
  uuid: ""
});

const loginRules = {
  username: [{ required: true, trigger: "blur", message: "请输入您的账号" }],
  password: [{ required: true, trigger: "blur", message: "请输入您的密码" }],
  code: [{ required: true, trigger: "change", message: "请输入验证码" }]
};

const codeUrl = ref("");
const loading = ref(false);
// 验证码开关
const captchaEnabled = ref(true);
// 注册开关
const register = ref(false);
const redirect = ref(undefined);

watch(route, (newRoute) => {
    redirect.value = newRoute.query && newRoute.query.redirect;
}, { immediate: true });

function handleLogin() {
  proxy.$refs.loginRef.validate(valid => {
    if (valid) {
      loading.value = true;
      // 勾选了需要记住密码设置在 cookie 中设置记住用户名和密码
      if (loginForm.value.rememberMe) {
        Cookies.set("username", loginForm.value.username, { expires: 30 });
        Cookies.set("password", encrypt(loginForm.value.password), { expires: 30 });
        Cookies.set("rememberMe", loginForm.value.rememberMe, { expires: 30 });
      } else {
        // 否则移除
        Cookies.remove("username");
        Cookies.remove("password");
        Cookies.remove("rememberMe");
      }
      // 调用action的登录方法
      userStore.login(loginForm.value).then(() => {
        const query = route.query;
        const otherQueryParams = Object.keys(query).reduce((acc, cur) => {
          if (cur !== "redirect") {
            acc[cur] = query[cur];
          }
          return acc;
        }, {});
        router.push({ path: redirect.value || "/", query: otherQueryParams });
      }).catch(() => {
        loading.value = false;
        // 重新获取验证码
        if (captchaEnabled.value) {
          getCode();
        }
      });
    }
  });
}

function getCode() {
  getCodeImg().then(res => {
    captchaEnabled.value = res.captchaEnabled === undefined ? true : res.captchaEnabled;
    register.value = res.registerEnabled === undefined ? false : res.registerEnabled;
    if (captchaEnabled.value) {
      codeUrl.value = "data:image/gif;base64," + res.img;
      loginForm.value.uuid = res.uuid;
    }
  });
}

function getCookie() {
  const username = Cookies.get("username");
  const password = Cookies.get("password");
  const rememberMe = Cookies.get("rememberMe");
  loginForm.value = {
    username: username === undefined ? loginForm.value.username : username,
    password: password === undefined ? loginForm.value.password : decrypt(password),
    rememberMe: rememberMe === undefined ? false : Boolean(rememberMe)
  };
}

getCode();
getCookie();
</script>

<style lang='scss' scoped>
.login {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    z-index: 1;
  }
}

.login-container {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
  padding: 40px;
  width: 420px;
  max-width: 90vw;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  
  .logo {
    margin-bottom: 20px;
    
    .logo-icon {
      font-size: 48px;
      color: #667eea;
      filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
    }
  }
  
  .system-title {
    font-size: 28px;
    font-weight: 600;
    color: #2c3e50;
    margin: 0 0 10px 0;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .system-subtitle {
    font-size: 14px;
    color: #7f8c8d;
    margin: 0;
    font-weight: 400;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .custom-input {
    :deep(.el-input__wrapper) {
      background: rgba(255, 255, 255, 0.8);
      border: 2px solid rgba(102, 126, 234, 0.1);
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
      transition: all 0.3s ease;
      
      &:hover {
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
      }
      
      &.is-focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
    }
    
    :deep(.el-input__inner) {
      height: 48px;
      font-size: 16px;
      color: #2c3e50;
      
      &::placeholder {
        color: #95a5a6;
      }
    }
  }
  
  .input-icon {
    font-size: 18px;
    color: #667eea;
    margin-right: 8px;
  }
}

.captcha-container {
  display: flex;
  gap: 12px;
  align-items: center;
  
  .captcha-input {
    flex: 1;
  }
  
  .captcha-image {
    .captcha-img {
      height: 48px;
      border-radius: 8px;
      cursor: pointer;
      border: 2px solid rgba(102, 126, 234, 0.1);
      transition: all 0.3s ease;
      
      &:hover {
        border-color: #667eea;
        transform: scale(1.02);
      }
    }
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  .remember-me {
    :deep(.el-checkbox__label) {
      color: #7f8c8d;
      font-size: 14px;
    }
    
    :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
      background-color: #667eea;
      border-color: #667eea;
    }
  }
  
  .register-link {
    a {
      color: #667eea;
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
      transition: color 0.3s ease;
      
      &:hover {
        color: #764ba2;
        text-decoration: underline;
      }
    }
  }
}

.login-button-container {
  margin-bottom: 0;
  
  .login-button {
    width: 100%;
    height: 48px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    color: white;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 25px rgba(102, 126, 234, 0.4);
    }
    
    &:active {
      transform: translateY(0);
    }
    
    &.is-loading {
      background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
    }
  }
}

.login-footer {
  position: absolute;
  bottom: 20px;
  left: 0;
  right: 0;
  text-align: center;
  z-index: 2;
  
  .footer-content {
    .copyright {
      color: rgba(255, 255, 255, 0.8);
      font-size: 12px;
      margin: 0 0 5px 0;
      font-weight: 400;
    }
    
    .powered-by {
      color: rgba(255, 255, 255, 0.6);
      font-size: 11px;
      margin: 0;
      font-weight: 300;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .login-container {
    width: 90vw;
    padding: 30px 20px;
  }
  
  .login-header .system-title {
    font-size: 24px;
  }
  
  .captcha-container {
    flex-direction: column;
    gap: 16px;
    
    .captcha-input {
      width: 100%;
    }
    
    .captcha-image .captcha-img {
      width: 100%;
      height: auto;
      max-height: 48px;
    }
  }
}
</style>
