import { addCollection } from '@iconify/vue'

export const setupIconify = () => {
  const loadIcons = async () => {
    try {
      const [ep, ant, ri, fa] = await Promise.all([
        import('@iconify/json/json/ep.json'),
        import('@iconify/json/json/ant-design.json'),
        import('@iconify/json/json/ri.json'),
        import('@iconify/json/json/fa.json')
      ])
      addCollection((ep.default || ep) as any)
      addCollection((ant.default || ant) as any)
      addCollection((ri.default || ri) as any)
      addCollection((fa.default || fa) as any)
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
