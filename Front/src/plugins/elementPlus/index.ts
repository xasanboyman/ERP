import type { App } from 'vue'
import { ElLoading, ElScrollbar, ElImage, ElImageViewer } from 'element-plus'
import 'element-plus/dist/index.css'

const plugins = [ElLoading]
const components = [ElScrollbar, ElImage, ElImageViewer]

export const setupElementPlus = (app: App<Element>) => {
  plugins.forEach((plugin) => {
    app.use(plugin)
  })

  components.forEach((component) => {
    if (component.name) {
      app.component(component.name, component)
    }
  })
}
