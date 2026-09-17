import { defineAsyncComponent } from 'vue'

const CodeEditor = defineAsyncComponent(() => import('./src/CodeEditor.vue'))

export { CodeEditor }
