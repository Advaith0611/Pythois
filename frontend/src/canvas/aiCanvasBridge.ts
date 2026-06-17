import {
  b64Vecs,
  createShapeId,
  renderPlaintextFromRichText,
  toRichText,
  type Editor,
  type TLShape,
  type TLShapeId,
  type TLRichText,
} from 'tldraw'
import { useAppStore } from '../store/useAppStore'
import type {
  CanvasAction,
  CanvasActionBatchResult,
  CanvasActionResult,
  CanvasBounds,
  CanvasObjectKind,
  CanvasObjectSnapshot,
  CanvasRelationship,
  CanvasState,
  CanvasStyle,
  SceneGraph,
  SceneGraphNode,
} from '../ai/canvasProtocol'
import type { EmbeddedCanvasObject, EmbeddedCanvasObjectKind } from '../types'

type ShapePartial = Parameters<Editor['createShapes']>[0][number]
type ShapeUpdate = Parameters<Editor['updateShapes']>[0][number]

const DEFAULT_EMBEDDED_SIZE = { w: 420, h: 300 }

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

function shapeBounds(editor: Editor, shape: TLShape): CanvasBounds {
  const pageBounds = editor.getShapePageBounds(shape)
  if (pageBounds) {
    return {
      x: pageBounds.x,
      y: pageBounds.y,
      w: pageBounds.w,
      h: pageBounds.h,
    }
  }

  const props = shape.props as Record<string, unknown>
  return {
    x: Number(shape.x ?? 0),
    y: Number(shape.y ?? 0),
    w: propNumber(props, 'w') ?? propNumber(props, 'scale') ?? 120,
    h: propNumber(props, 'h') ?? propNumber(props, 'scale') ?? 72,
  }
}

function styleFromShape(props: Record<string, unknown>): CanvasStyle {
  return {
    color: propString(props, 'color') ?? propString(props, 'labelColor'),
    fill: propString(props, 'fill'),
    stroke: propString(props, 'color'),
    dash: propString(props, 'dash'),
    font: propString(props, 'font'),
  }
}

function kindFromShape(shape: TLShape): CanvasObjectKind {
  if (shape.type === 'geo') {
    const geo = propString(shape.props as unknown as Record<string, unknown>, 'geo')
    if (geo === 'rectangle') return 'rectangle'
    if (geo === 'ellipse' || geo === 'oval') return 'circle'
    return 'polygon'
  }

  if (shape.type === 'draw') return 'freehand'
  if (shape.type === 'arrow') return 'arrow'
  if (shape.type === 'line') return 'line'
  if (shape.type === 'text') return 'text'
  if (shape.type === 'group') return 'group'
  if (shape.type === 'image') return 'image'

  return 'shape'
}

function embeddedKind(kind: EmbeddedCanvasObjectKind, mimeType?: string): CanvasObjectKind {
  if (kind === 'file' && mimeType?.includes('markdown')) return 'markdown'
  return kind
}

function shapeRelationships(shape: TLShape, childIds: string[]): CanvasRelationship[] {
  const relationships: CanvasRelationship[] = []

  if ('parentId' in shape && shape.parentId) {
    relationships.push({ type: 'parent', objectId: String(shape.parentId) })
  }

  childIds.forEach((objectId) => relationships.push({ type: 'child', objectId }))
  return relationships
}

function buildSceneGraph(objects: CanvasObjectSnapshot[]): SceneGraph {
  const nodesById = new Map<string, SceneGraphNode>()

  objects.forEach((object) => {
    nodesById.set(object.id, {
      id: object.id,
      source: object.source,
      kind: object.kind,
      parentId: object.parentId,
      children: [],
      bounds: object.bounds,
      layerIndex: object.layerIndex,
      relationships: object.relationships,
    })
  })

  const roots: SceneGraphNode[] = []
  const flat = Array.from(nodesById.values())

  flat.forEach((node) => {
    if (node.parentId && nodesById.has(node.parentId)) {
      nodesById.get(node.parentId)?.children.push(node)
    } else {
      roots.push(node)
    }
  })

  return { nodes: roots, flat }
}

function normalizeTldrawColor(value?: string) {
  if (!value) return undefined
  const named = value.trim().toLowerCase()
  const supported = new Set([
    'black',
    'blue',
    'green',
    'grey',
    'light-blue',
    'light-green',
    'light-red',
    'light-violet',
    'orange',
    'red',
    'violet',
    'white',
    'yellow',
  ])

  return supported.has(named) ? named : undefined
}

function normalizeFill(value?: string) {
  if (!value) return undefined
  const named = value.trim().toLowerCase()
  if (['none', 'semi', 'solid', 'fill', 'pattern', 'lined-fill'].includes(named)) return named
  return named.startsWith('#') ? 'solid' : undefined
}

function embeddedId(id?: string) {
  return id ?? `embed-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function shapeId(id?: string) {
  return id ? createShapeId(id.replace(/^shape:/, '')) : createShapeId()
}

function asShapePartial(shape: unknown) {
  return shape as ShapePartial
}

function drawSizeFromStrokeWidth(strokeWidth?: number) {
  if (!strokeWidth || strokeWidth <= 3) return 's'
  if (strokeWidth <= 6) return 'm'
  if (strokeWidth <= 10) return 'l'
  return 'xl'
}

function createEmbeddedObject(
  action: Extract<
    CanvasAction,
    { action: 'create_file' | 'create_image' | 'create_pdf' | 'create_markdown' | 'create_webpage' }
  >,
): EmbeddedCanvasObject {
  if (action.action === 'create_webpage') {
    return {
      id: embeddedId(action.id),
      kind: 'webpage',
      x: action.x,
      y: action.y,
      w: action.width,
      h: action.height,
      title: action.title ?? new URL(action.url).hostname.replace(/^www\./, ''),
      url: action.url,
      createdAt: new Date().toISOString(),
      metadata: action.metadata,
    }
  }

  const kind =
    action.action === 'create_image'
      ? 'image'
      : action.action === 'create_pdf'
        ? 'pdf'
        : 'file'

  return {
    id: embeddedId(action.id),
    kind,
    x: action.x,
    y: action.y,
    w: action.width || DEFAULT_EMBEDDED_SIZE.w,
    h: action.height || DEFAULT_EMBEDDED_SIZE.h,
    title: action.title,
    mimeType: action.mimeType,
    size: action.size,
    dataUrl: action.dataUrl,
    createdAt: new Date().toISOString(),
    metadata: action.metadata,
  }
}

function createShapeFromAction(action: CanvasAction): ShapePartial | null {
  if (action.action === 'create_rectangle' || action.action === 'create_circle') {
    return asShapePartial({
      id: shapeId(action.id),
      type: 'geo',
      x: action.x,
      y: action.y,
      meta: action.metadata ?? {},
      props: {
        geo: action.action === 'create_circle' ? 'ellipse' : 'rectangle',
        w: action.width,
        h: action.height,
        color: normalizeTldrawColor(action.color) ?? 'black',
        fill: normalizeFill(action.fill) ?? 'semi',
        richText: toRichText(action.text ?? ''),
      },
    })
  }

  if (action.action === 'create_text') {
    return asShapePartial({
      id: shapeId(action.id),
      type: 'text',
      x: action.x,
      y: action.y,
      meta: action.metadata ?? {},
      props: {
        w: action.width ?? 240,
        color: normalizeTldrawColor(action.color) ?? 'black',
        richText: toRichText(action.text),
      },
    })
  }

  if (action.action === 'create_arrow') {
    return asShapePartial({
      id: shapeId(action.id),
      type: 'arrow',
      x: action.x,
      y: action.y,
      meta: action.metadata ?? {},
      props: {
        color: normalizeTldrawColor(action.color) ?? 'black',
        start: { x: 0, y: 0 },
        end: { x: action.endX - action.x, y: action.endY - action.y },
        richText: toRichText(action.text ?? ''),
      },
    })
  }

  if (action.action === 'create_line') {
    return asShapePartial({
      id: shapeId(action.id),
      type: 'line',
      x: action.x,
      y: action.y,
      meta: action.metadata ?? {},
      props: {
        color: normalizeTldrawColor(action.color) ?? 'black',
        points: {
          a1: { id: 'a1', index: 'a1', x: 0, y: 0 },
          a2: { id: 'a2', index: 'a2', x: action.endX - action.x, y: action.endY - action.y },
        },
      },
    })
  }

  if (action.action === 'create_freehand') {
    const first = action.points[0]
    if (!first) return null
    const localPoints = action.points.map((point) => ({
      x: point.x - first.x,
      y: point.y - first.y,
      z: 0.5,
    }))

    return asShapePartial({
      id: shapeId(action.id),
      type: 'draw',
      x: first.x,
      y: first.y,
      meta: action.metadata ?? {},
      props: {
        color: normalizeTldrawColor(action.color) ?? 'black',
        fill: 'none',
        dash: 'draw',
        size: drawSizeFromStrokeWidth(action.strokeWidth),
        segments: [{ type: 'free', path: b64Vecs.encodePoints(localPoints) }],
        isComplete: true,
        isClosed: false,
        isPen: false,
        scale: 1,
        scaleX: 1,
        scaleY: 1,
      },
    })
  }

  if (action.action === 'create_polygon') {
    const first = action.points[0]
    if (!first) return null
    const points = Object.fromEntries(
      action.points.map((point, index) => {
        const id = `a${index + 1}`
        return [id, { id, index: id, x: point.x - first.x, y: point.y - first.y }]
      }),
    )

    return asShapePartial({
      id: shapeId(action.id),
      type: 'line',
      x: first.x,
      y: first.y,
      meta: action.metadata ?? {},
      props: {
        color: normalizeTldrawColor(action.color) ?? 'black',
        spline: 'line',
        points,
      },
    })
  }

  return null
}

function objectExists(editor: Editor, id: string) {
  return Boolean(editor.getShape(id as TLShapeId) ?? useAppStore.getState().embeddedObjects.find((object) => object.id === id))
}

function applyTldrawStyle(editor: Editor, id: string, style: CanvasStyle) {
  const shape = editor.getShape(id as TLShapeId)
  if (!shape) return false

  const props: Record<string, unknown> = {}
  const color = normalizeTldrawColor(style.color ?? style.stroke)
  const fill = normalizeFill(style.fill)

  if (color) props.color = color
  if (fill) props.fill = fill
  if (style.dash) props.dash = style.dash
  if (style.font) props.font = style.font

  editor.updateShapes([{ id: shape.id, type: shape.type, props } as ShapeUpdate])
  return true
}

function applyAction(editor: Editor, action: CanvasAction): CanvasActionResult {
  const embeddedStore = useAppStore.getState()

  try {
    const shape = createShapeFromAction(action)
    if (shape) {
      editor.createShapes([shape])
      return { action: action.action, ok: true, objectIds: [String(shape.id)] }
    }

    if (
      action.action === 'create_file' ||
      action.action === 'create_image' ||
      action.action === 'create_pdf' ||
      action.action === 'create_markdown' ||
      action.action === 'create_webpage'
    ) {
      const object = createEmbeddedObject(action)
      embeddedStore.addEmbeddedObject(object)
      return { action: action.action, ok: true, objectIds: [object.id] }
    }

    if (action.action === 'move_object') {
      const shapeToMove = editor.getShape(action.id as TLShapeId)
      if (shapeToMove) {
        editor.updateShapes([{ id: shapeToMove.id, type: shapeToMove.type, x: action.x, y: action.y } as ShapeUpdate])
      } else {
        embeddedStore.updateEmbeddedObject(action.id, { x: action.x, y: action.y })
      }
      return { action: action.action, ok: objectExists(editor, action.id), objectIds: [action.id] }
    }

    if (action.action === 'resize_object') {
      const shapeToResize = editor.getShape(action.id as TLShapeId)
      if (shapeToResize) {
        editor.updateShapes([
          { id: shapeToResize.id, type: shapeToResize.type, props: { w: action.width, h: action.height } } as ShapeUpdate,
        ])
      } else {
        embeddedStore.updateEmbeddedObject(action.id, { w: action.width, h: action.height })
      }
      return { action: action.action, ok: objectExists(editor, action.id), objectIds: [action.id] }
    }

    if (action.action === 'update_style') {
      return { action: action.action, ok: applyTldrawStyle(editor, action.id, action.style), objectIds: [action.id] }
    }

    if (action.action === 'relabel_object') {
      const shapeToRelabel = editor.getShape(action.id as TLShapeId)
      if (shapeToRelabel) {
        editor.updateShapes([
          { id: shapeToRelabel.id, type: shapeToRelabel.type, props: { richText: toRichText(action.text) } } as ShapeUpdate,
        ])
      } else {
        embeddedStore.updateEmbeddedObject(action.id, { title: action.text })
      }
      return { action: action.action, ok: objectExists(editor, action.id), objectIds: [action.id] }
    }

    if (action.action === 'update_webpage') {
      embeddedStore.updateEmbeddedObject(action.id, { url: action.url, title: action.title })
      return { action: action.action, ok: objectExists(editor, action.id), objectIds: [action.id] }
    }

    if (action.action === 'update_metadata') {
      const shapeToUpdate = editor.getShape(action.id as TLShapeId)
      if (shapeToUpdate) {
        editor.updateShapes([{ id: shapeToUpdate.id, type: shapeToUpdate.type, meta: action.metadata } as ShapeUpdate])
      } else {
        embeddedStore.updateEmbeddedObject(action.id, { metadata: action.metadata })
      }
      return { action: action.action, ok: objectExists(editor, action.id), objectIds: [action.id] }
    }

    if (action.action === 'delete_object') {
      if (editor.getShape(action.id as TLShapeId)) editor.deleteShapes([action.id as TLShapeId])
      else embeddedStore.deleteEmbeddedObject(action.id)
      return { action: action.action, ok: true, objectIds: [action.id] }
    }

    if (action.action === 'duplicate_object') {
      if (editor.getShape(action.id as TLShapeId)) editor.duplicateShapes([action.id as TLShapeId], { x: 32, y: 32 })
      else embeddedStore.duplicateEmbeddedObject(action.id)
      return { action: action.action, ok: true, objectIds: [action.id] }
    }

    if (action.action === 'bring_to_front') {
      editor.bringToFront([action.id as TLShapeId])
      return { action: action.action, ok: true, objectIds: [action.id] }
    }

    if (action.action === 'send_to_back') {
      editor.sendToBack([action.id as TLShapeId])
      return { action: action.action, ok: true, objectIds: [action.id] }
    }

    if (action.action === 'group_objects') {
      const ids = action.ids.map((id) => id as TLShapeId)
      editor.groupShapes(ids, action.id ? { groupId: shapeId(action.id) } : undefined)
      return { action: action.action, ok: true, objectIds: action.ids }
    }

    if (action.action === 'ungroup_objects') {
      editor.ungroupShapes(action.ids.map((id) => id as TLShapeId))
      return { action: action.action, ok: true, objectIds: action.ids }
    }

    if (action.action === 'select_objects') {
      const tldrawIds = action.ids.filter((id) => editor.getShape(id as TLShapeId)).map((id) => id as TLShapeId)
      const embeddedIdToSelect = action.ids.find((id) => embeddedStore.embeddedObjects.some((object) => object.id === id)) ?? null
      editor.select(...tldrawIds)
      embeddedStore.setSelectedEmbeddedObjectId(embeddedIdToSelect)
      return { action: action.action, ok: true, objectIds: action.ids }
    }

    return { action: action.action, ok: false, objectIds: [], error: 'Unsupported canvas action' }
  } catch (error) {
    return { action: action.action, ok: false, objectIds: [], error: error instanceof Error ? error.message : String(error) }
  }
}

export function getCanvasState(editor: Editor): CanvasState {
  const embeddedObjects = useAppStore.getState().embeddedObjects
  const selectedEmbeddedObjectId = useAppStore.getState().selectedEmbeddedObjectId
  const shapes = editor.getCurrentPageShapes()
  const childrenByParent = new Map<string, string[]>()

  shapes.forEach((shape) => {
    if ('parentId' in shape && shape.parentId) {
      const parentId = String(shape.parentId)
      childrenByParent.set(parentId, [...(childrenByParent.get(parentId) ?? []), String(shape.id)])
    }
  })

  const shapeSnapshots: CanvasObjectSnapshot[] = shapes.map((shape, layerIndex) => {
    const props = shape.props as Record<string, unknown>

    return {
      id: String(shape.id),
      source: 'tldraw',
      kind: kindFromShape(shape),
      type: shape.type,
      bounds: shapeBounds(editor, shape),
      rotation: Number(shape.rotation ?? 0),
      layerIndex,
      parentId: 'parentId' in shape ? String(shape.parentId) : undefined,
      text: shapeText(editor, props),
      url: propString(props, 'url'),
      style: styleFromShape(props),
      relationships: shapeRelationships(shape, childrenByParent.get(String(shape.id)) ?? []),
      metadata: { ...shape.meta },
      raw: shape,
    }
  })

  const embeddedSnapshots: CanvasObjectSnapshot[] = embeddedObjects.map((object, index) => ({
    id: object.id,
    source: 'embedded',
    kind: embeddedKind(object.kind, object.mimeType),
    type: `embed:${object.kind}`,
    bounds: { x: object.x, y: object.y, w: object.w, h: object.h },
    layerIndex: shapes.length + index,
    text: object.url ?? object.title,
    url: object.url,
    mimeType: object.mimeType,
    size: object.size,
    title: object.title,
    style: {},
    relationships: [],
    metadata: object.metadata ?? {},
    raw: object,
  }))

  const objects = [...shapeSnapshots, ...embeddedSnapshots]
  const screenBounds = editor.getViewportScreenBounds()
  const selectedObjectIds = [
    ...editor.getSelectedShapeIds().map(String),
    ...(selectedEmbeddedObjectId ? [selectedEmbeddedObjectId] : []),
  ]

  return {
    schemaVersion: 'pythios.canvas.v1',
    capturedAt: new Date().toISOString(),
    viewport: {
      ...editor.getCamera(),
      screenBounds: { x: screenBounds.x, y: screenBounds.y, w: screenBounds.w, h: screenBounds.h },
    },
    objects,
    selectedObjectIds,
    visibleObjectIds: objects.map((object) => object.id),
    sceneGraph: buildSceneGraph(objects),
    embeddedObjects,
    metadata: {
      pageId: String(editor.getCurrentPageId()),
      shapeCount: shapes.length,
      embeddedObjectCount: embeddedObjects.length,
    },
  }
}

export function getSceneGraph(editor: Editor) {
  return getCanvasState(editor).sceneGraph
}

export function getSelectedObjects(editor: Editor) {
  const state = getCanvasState(editor)
  const selectedIds = new Set(state.selectedObjectIds)
  return state.objects.filter((object) => selectedIds.has(object.id))
}

export function getVisibleObjects(editor: Editor) {
  return getCanvasState(editor).objects
}

export function applyCanvasActions(editor: Editor, actions: CanvasAction[]): CanvasActionBatchResult {
  return {
    schemaVersion: 'pythios.canvas.actions.v1',
    appliedAt: new Date().toISOString(),
    results: actions.map((action) => applyAction(editor, action)),
  }
}
