import { renderPlaintextFromRichText, type Editor, type TLShape, type TLRichText } from 'tldraw'
import { useAppStore } from '../store/useAppStore'
import type { SpatialShape } from '../types'

function propString(props: Record<string, unknown>, key: string) {
  const value = props[key]
  return typeof value === 'string' ? value : undefined
}

function propNumber(props: Record<string, unknown>, key: string) {
  const value = props[key]
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function shapeText(editor: Editor, props: Record<string, unknown>) {
  const text = propString(props, 'text') ?? propString(props, 'url')
  if (text) return text

  const richText = props.richText
  if (richText && typeof richText === 'object') {
    return renderPlaintextFromRichText(editor, richText as TLRichText)
  }

  return undefined
}

export function serializeShape(editor: Editor, shape: TLShape): SpatialShape {
  const props = shape.props as Record<string, unknown>
  return {
    id: String(shape.id),
    type: shape.type,
    x: Number(shape.x ?? 0),
    y: Number(shape.y ?? 0),
    w: propNumber(props, 'w') ?? propNumber(props, 'scale') ?? 120,
    h: propNumber(props, 'h') ?? propNumber(props, 'scale') ?? 72,
    text: shapeText(editor, props),
    geo: propString(props, 'geo'),
    color: propString(props, 'color'),
  }
}

export function getSerializableShapes(editor: Editor, selectedOnly: boolean): SpatialShape[] {
  const selectedIds = new Set(editor.getSelectedShapeIds())
  const { embeddedObjects, selectedEmbeddedObjectId } = useAppStore.getState()
  const tldrawShapes = editor
    .getCurrentPageShapes()
    .filter((shape) => !selectedOnly || selectedIds.has(shape.id))
    .map((shape) => serializeShape(editor, shape))
  const embeddedShapes = embeddedObjects
    .filter((object) => !selectedOnly || selectedEmbeddedObjectId === object.id)
    .map((object) => ({
      id: object.id,
      type: `embed:${object.kind}`,
      x: object.x,
      y: object.y,
      w: object.w,
      h: object.h,
      text: object.url ?? object.title,
      geo: object.mimeType,
    }))

  return [...tldrawShapes, ...embeddedShapes]
}
