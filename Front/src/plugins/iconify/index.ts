import { addCollection } from '@iconify/vue'

export const setupIconify = () => {
  const loadIcons = async () => {
    try {
      const [ep, ant] = await Promise.all([
        import('@iconify/json/json/ep.json'),
        import('@iconify/json/json/ant-design.json')
      ])
      addCollection((ep.default || ep) as any)
      addCollection((ant.default || ant) as any)
    } catch (e) {
      console.debug('Icon collection async load note:', e)
    }
  }

  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    window.requestIdleCallback(
      () => {
        loadIcons()
      },
      { timeout: 1000 }
    )
  } else {
    setTimeout(loadIcons, 50)
  }
}
