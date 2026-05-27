import type { GeneratedComponent, GeneratedUI, GenerationRequest, SpatialShape } from '../types'

const WORDS_TO_COMPONENTS: Array<[RegExp, GeneratedComponent['type']]> = [
  [/chart|graph|trend|analytics|revenue|sales/i, 'chart'],
  [/table|grid|rows|data|report/i, 'table'],
  [/task|kanban|board|todo|pipeline/i, 'kanban'],
  [/flow|workflow|steps|process|journey/i, 'workflow'],
  [/timeline|roadmap|milestone/i, 'timeline'],
  [/button|cta|submit|save|run|generate/i, 'button'],
  [/input|field|form|search|filter/i, 'input'],
  [/list|feed|notes|menu/i, 'list'],
]

const labels = ['Revenue', 'Activation', 'Retention', 'Quality', 'Throughput']

function cleanText(value?: string) {
  return value?.replace(/\s+/g, ' ').trim()
}

function inferComponent(shape: SpatialShape, index: number): GeneratedComponent {
  const text = cleanText(shape.text)
  const source = `${text ?? ''} ${shape.geo ?? ''} ${shape.type}`
  const found = WORDS_TO_COMPONENTS.find(([pattern]) => pattern.test(source))
  let type = found?.[1]

  if (!type && shape.type === 'arrow') type = 'workflow'
  if (!type && shape.type === 'text') type = text && text.length < 22 ? 'button' : 'note'
  if (!type && shape.w > shape.h * 2.6) type = 'table'
  if (!type && shape.h > shape.w * 1.35) type = 'list'
  if (!type) type = index % 4 === 0 ? 'metric' : 'chart'

  const title = text || `${type[0].toUpperCase()}${type.slice(1)} ${index + 1}`

  if (type === 'table') {
    return {
      id: shape.id,
      type,
      title,
      columns: ['Segment', 'Status', 'Score'],
      rows: [
        { Segment: 'New users', Status: 'Growing', Score: 84 },
        { Segment: 'Teams', Status: 'Stable', Score: 71 },
        { Segment: 'Enterprise', Status: 'Review', Score: 63 },
      ],
    }
  }

  if (type === 'kanban') {
    return {
      id: shape.id,
      type,
      title,
      items: ['Intake', 'Design', 'Build', 'Validate'],
      detail: 'Four-stage workspace derived from grouped canvas objects.',
    }
  }

  if (type === 'workflow' || type === 'timeline') {
    return {
      id: shape.id,
      type,
      title,
      items: ['Capture intent', 'Parse layout', 'Generate UI', 'Refine region'],
    }
  }

  if (type === 'button' || type === 'input') {
    return {
      id: shape.id,
      type,
      title,
      label: text || (type === 'button' ? 'Run action' : 'Search workspace'),
    }
  }

  if (type === 'list' || type === 'note') {
    return {
      id: shape.id,
      type,
      title,
      detail: text || 'Canvas note converted into an interactive panel.',
      items: ['Primary requirement', 'Supporting context', 'Next refinement'],
    }
  }

  if (type === 'metric') {
    return {
      id: shape.id,
      type,
      title: text || labels[index % labels.length],
      value: `${72 + ((index * 7) % 21)}%`,
      detail: 'Live KPI placeholder',
    }
  }

  return {
    id: shape.id,
    type: 'chart',
    title,
    value: `${38 + index * 9}`,
    detail: 'Generated from a spatial block on the canvas.',
  }
}

function defaultComponents(): GeneratedComponent[] {
  return [
    { id: 'metric-1', type: 'metric', title: 'Intent Confidence', value: '91%', detail: 'Canvas parse score' },
    { id: 'metric-2', type: 'metric', title: 'Regions', value: '4', detail: 'Detected interface zones' },
    { id: 'chart-1', type: 'chart', title: 'Generated App Activity', detail: 'Trend inferred from dashboard sketch' },
    {
      id: 'table-1',
      type: 'table',
      title: 'Spatial Objects',
      columns: ['Object', 'Role', 'State'],
      rows: [
        { Object: 'Large rectangle', Role: 'Main panel', State: 'Rendered' },
        { Object: 'Label text', Role: 'Control', State: 'Interactive' },
        { Object: 'Arrow', Role: 'Workflow', State: 'Connected' },
      ],
    },
    { id: 'flow-1', type: 'workflow', title: 'Generation Loop', items: ['Draw', 'Interpret', 'Render', 'Refine'] },
  ]
}

export function generateLocalInterface(request: GenerationRequest): GeneratedUI {
  const sortedShapes = [...request.shapes].sort((a, b) => a.y - b.y || a.x - b.x)
  const text = sortedShapes.map((shape) => shape.text).filter(Boolean).join(' ')
  const prompt = cleanText(request.prompt)
  const components = sortedShapes.length ? sortedShapes.map(inferComponent).slice(0, 12) : defaultComponents()
  const hasWorkflow = components.some((component) => component.type === 'workflow' || component.type === 'timeline')
  const hasTables = components.some((component) => component.type === 'table' || component.type === 'kanban')

  return {
    id: crypto.randomUUID(),
    app_type: hasWorkflow ? 'workflow_builder' : hasTables ? 'operations_workspace' : 'analytics_dashboard',
    title: prompt || cleanText(text) || 'Spatial AI Workspace',
    summary: sortedShapes.length
      ? `Generated from ${sortedShapes.length} canvas object${sortedShapes.length === 1 ? '' : 's'}.`
      : 'Starter interface generated from the MVP blueprint.',
    theme: 'dark',
    layout: hasWorkflow ? 'workflow' : 'dashboard',
    generated_at: new Date().toISOString(),
    source: 'local',
    components,
  }
}
