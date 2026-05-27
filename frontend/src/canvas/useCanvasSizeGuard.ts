import { useEffect, useRef, type RefObject } from 'react'

interface CanvasSize {
  width: number
  height: number
}

export function useCanvasSizeGuard(elementRef: RefObject<HTMLElement | null>) {
  const sizeRef = useRef<CanvasSize>({ width: 0, height: 0 })

  useEffect(() => {
    const element = elementRef.current
    if (!element) return

    const applySize = (width: number, height: number) => {
      sizeRef.current = { width, height }
      element.dataset.canvasReady = width > 0 && height > 0 ? 'true' : 'false'

      if (width === 0 || height === 0) {
        console.warn('Pythios canvas container has zero size.', { width, height })
      }
    }

    const rect = element.getBoundingClientRect()
    applySize(rect.width, rect.height)

    const observer = new ResizeObserver(([entry]) => {
      if (!entry) return
      applySize(entry.contentRect.width, entry.contentRect.height)
    })

    observer.observe(element)
    return () => observer.disconnect()
  }, [elementRef])

  return sizeRef
}
