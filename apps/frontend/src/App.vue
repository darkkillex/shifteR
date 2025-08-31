<template><n-config-provider><n-message-provider><div class='layout'><header><h1>Shift Suite</h1><nav><router-link to='/'>Planner</router-link><router-link to='/employees'>Dipendenti</router-link></nav></header><main><router-view /></main></div></n-message-provider></n-config-provider></template>
<script setup lang='ts'>import { NConfigProvider, NMessageProvider } from 'naive-ui'</script>
<style>body{margin:0;font-family:system-ui,sans-serif}.layout header{display:flex;gap:24px;align-items:center;padding:12px 16px;border-bottom:1px solid #eee}nav a{margin-right:12px}main{padding:16px}</style>
