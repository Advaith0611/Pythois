export type ComponentType =
  | 'metric'
  | 'chart'
  | 'table'
  | 'button'
  | 'input'
  | 'list'
  | 'kanban'
  | 'timeline'
  | 'workflow'
  | 'note'

export interface SpatialShape {
  id: string
  type: string
  x: number
  y: number
  w: number
  h: number
  text?: string
  geo?: string
  color?: string
}

export interface GeneratedComponent {
  id: string
  type: ComponentType
  title: string
  label?: string
  value?: string
  detail?: string
  items?: string[]
  columns?: string[]
  rows?: Array<Record<string, string | number>>
  accent?: string
}

export interface GeneratedUI {
  id: string
  app_type: string
  title: string
  summary: string
  theme: 'light' | 'dark'
  layout: 'dashboard' | 'app' | 'workflow' | 'wireframe'
  generated_at: string
  source: 'backend' | 'local'
  components: GeneratedComponent[]
}

export interface GenerationRequest {
  shapes: SpatialShape[]
  prompt?: string
  selectedOnly?: boolean
}
