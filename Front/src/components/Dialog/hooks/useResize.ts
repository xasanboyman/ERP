import { ref } from 'vue'

export const useResize = (props?: {
  minHeightPx?: number
  minWidthPx?: number
  initHeight?: number | string
  initWidth?: number | string
  storageKey?: string
  autoHeight?: boolean
}) => {
  const {
    minHeightPx = 220,
    minWidthPx = 360,
    initHeight,
    initWidth,
    storageKey,
    autoHeight = true
  } = props || {}

  let normKey = storageKey ? storageKey.toLowerCase() : ''
  if (normKey.includes('xodim') || normKey.includes('worker')) {
    normKey = 'worker'
  } else if (normKey.includes('mahsulot') || normKey.includes('product')) {
    normKey = 'product'
  } else if (
    normKey.includes('maosh') ||
    normKey.includes('salary') ||
    normKey.includes('payout')
  ) {
    normKey = 'salary'
  } else if (normKey.includes("bo'lim") || normKey.includes('department')) {
    normKey = 'department'
  } else if (normKey.includes('foydalanuvchi') || normKey.includes('user')) {
    normKey = 'user'
  } else if (normKey.includes('rol') || normKey.includes('role')) {
    normKey = 'role'
  } else if (normKey.includes('menyu') || normKey.includes('menu')) {
    normKey = 'menu'
  }

  const isManualResized = ref(false)

  let savedWidth: number | null = null
  let savedHeight: number | null = null
  if (normKey) {
    const saved = localStorage.getItem(`dialog_size_${normKey}`)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        if (parsed.width && parsed.width >= minWidthPx) savedWidth = parsed.width
        if (parsed.height && parsed.height >= minHeightPx) savedHeight = parsed.height
        if (savedWidth || savedHeight) {
          isManualResized.value = true
        }
      } catch (e) {
        console.error(e)
      }
    }
  }

  // Width calculation
  const getInitialWidth = (): string => {
    if (savedWidth) return `${savedWidth}px`
    if (initWidth) {
      if (typeof initWidth === 'number') return `${initWidth}px`
      return initWidth
    }
    return 'auto'
  }

  // Height calculation - auto by default so dialog naturally hugs content
  const getInitialHeight = (): string => {
    if (savedHeight) return `${savedHeight}px`
    if (!autoHeight && initHeight) {
      if (typeof initHeight === 'number') return `${initHeight}px`
      return initHeight
    }
    return 'auto'
  }

  const dialogHeight = ref<string>(getInitialHeight())
  const minWidth = ref<string>(getInitialWidth())
  const maxHeight = ref<string>('calc(92vh - 70px)')

  const setupDrag = (elDialog: HTMLElement, _el?: HTMLElement) => {
    if (!elDialog) return

    let isResizing = false
    let currentResizeDirection = ''
    const edgeMargin = 14

    const handleMouseMove = (e: MouseEvent) => {
      if (isResizing) return

      const rect = elDialog.getBoundingClientRect()
      const offsetX = e.clientX - rect.left
      const offsetY = e.clientY - rect.top
      const width = rect.width
      const height = rect.height

      if (offsetX < edgeMargin && offsetY < edgeMargin) {
        elDialog.style.cursor = 'nwse-resize'
        currentResizeDirection = 'top-left'
      } else if (offsetX > width - edgeMargin && offsetY < edgeMargin) {
        elDialog.style.cursor = 'nesw-resize'
        currentResizeDirection = 'top-right'
      } else if (offsetX < edgeMargin && offsetY > height - edgeMargin) {
        elDialog.style.cursor = 'nesw-resize'
        currentResizeDirection = 'bottom-left'
      } else if (offsetX > width - edgeMargin && offsetY > height - edgeMargin) {
        elDialog.style.cursor = 'nwse-resize'
        currentResizeDirection = 'bottom-right'
      } else if (offsetX < edgeMargin) {
        elDialog.style.cursor = 'ew-resize'
        currentResizeDirection = 'left'
      } else if (offsetX > width - edgeMargin) {
        elDialog.style.cursor = 'ew-resize'
        currentResizeDirection = 'right'
      } else if (offsetY < edgeMargin) {
        elDialog.style.cursor = 'ns-resize'
        currentResizeDirection = 'top'
      } else if (offsetY > height - edgeMargin) {
        elDialog.style.cursor = 'ns-resize'
        currentResizeDirection = 'bottom'
      } else {
        elDialog.style.cursor = 'default'
        currentResizeDirection = ''
      }
    }

    const handleMouseDown = (e: MouseEvent) => {
      if (!currentResizeDirection) return

      isResizing = true
      isManualResized.value = true
      e.preventDefault()

      const initialX = e.clientX
      const initialY = e.clientY
      const rect = elDialog.getBoundingClientRect()
      const initialWidth = rect.width
      const initialHeight = rect.height

      const handleResizing = (e: MouseEvent) => {
        if (!isResizing) return

        let newWidth = initialWidth
        let newHeight = initialHeight

        const deltaX = e.clientX - initialX
        const deltaY = e.clientY - initialY

        if (currentResizeDirection.includes('right')) {
          newWidth = Math.max(minWidthPx, initialWidth + deltaX)
          newWidth = Math.min(newWidth, window.innerWidth - 20)
          minWidth.value = `${newWidth}px`
        }

        if (currentResizeDirection.includes('left')) {
          newWidth = Math.max(minWidthPx, initialWidth - deltaX)
          newWidth = Math.min(newWidth, window.innerWidth - 20)
          minWidth.value = `${newWidth}px`
        }

        if (currentResizeDirection.includes('bottom')) {
          newHeight = Math.max(minHeightPx, initialHeight + deltaY)
          newHeight = Math.min(newHeight, window.innerHeight - 30)
          dialogHeight.value = `${newHeight}px`
          maxHeight.value = `${newHeight - 60}px`
        }

        if (currentResizeDirection.includes('top')) {
          newHeight = Math.max(minHeightPx, initialHeight - deltaY)
          newHeight = Math.min(newHeight, window.innerHeight - 30)
          dialogHeight.value = `${newHeight}px`
          maxHeight.value = `${newHeight - 60}px`
        }
      }

      const stopResizing = () => {
        isResizing = false
        elDialog.style.cursor = 'default'
        document.removeEventListener('mousemove', handleResizing)
        document.removeEventListener('mouseup', stopResizing)

        if (normKey) {
          const finalWidth = parseInt(minWidth.value)
          const finalHeight = parseInt(dialogHeight.value)
          if (!isNaN(finalWidth) && !isNaN(finalHeight)) {
            localStorage.setItem(
              `dialog_size_${normKey}`,
              JSON.stringify({ width: finalWidth, height: finalHeight })
            )
          }
        }
      }

      document.addEventListener('mousemove', handleResizing)
      document.addEventListener('mouseup', stopResizing)
    }

    // Double click header or title bar resets size to natural auto-fit!
    const handleDblClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (target && target.closest('.el-dialog__header')) {
        isManualResized.value = false
        dialogHeight.value = 'auto'
        minWidth.value = initWidth
          ? typeof initWidth === 'number'
            ? `${initWidth}px`
            : initWidth
          : 'auto'
        maxHeight.value = 'calc(92vh - 70px)'
        if (normKey) {
          localStorage.removeItem(`dialog_size_${normKey}`)
        }
      }
    }

    elDialog.addEventListener('mousemove', handleMouseMove)
    elDialog.addEventListener('mousedown', handleMouseDown)
    elDialog.addEventListener('dblclick', handleDblClick)
  }

  return {
    setupDrag,
    dialogHeight,
    maxHeight,
    minWidth,
    isManualResized
  }
}
