const BASE = ''

async function checkBackendAlive() {
  try {
    const r = await fetch(`${BASE}/api/health`, { method: 'GET' })
    return r.ok
  } catch {
    return false
  }
}

function buildInputs(form) {
  return {
    request: form.request || `请为我规划 ${form.days} 天 ${form.people} 人的 ${form.destination} 旅行`,
    destination: form.destination,
    departure: form.departure || '-',
    days: Number(form.days),
    people: String(form.people),
    budget: String(form.budget),
    style: form.style || '休闲',
    special_request: form.special_request || '无'
  }
}

export async function runWorkflowStream(form, handlers) {
  const {
    onWorkflowStart,
    onNodeStart,
    onNodeFinish,
    onTextChunk,
    onWorkflowFinish,
    onError,
    onRaw
  } = handlers || {}

  const inputs = buildInputs(form)

  try {
    const resp = await fetch(`${BASE}/dify/workflow/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        inputs,
        query: inputs.request,
        user: 'frontend-user'
      })
    })

    if (!resp.ok || !resp.body) {
      throw new Error(`HTTP ${resp.status} ${resp.statusText}`)
    }

    const reader = resp.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      let idx
      while ((idx = buffer.indexOf('\n\n')) !== -1) {
        const raw = buffer.slice(0, idx)
        buffer = buffer.slice(idx + 2)
        parseSseEvent(raw, {
          onWorkflowStart, onNodeStart, onNodeFinish,
          onTextChunk, onWorkflowFinish, onError, onRaw
        })
      }
    }
  } catch (e) {
    onError && onError(e)
  }
}

function parseSseEvent(raw, handlers) {
  if (!raw.startsWith('data:')) return
  const dataStr = raw.slice(5).trim()
  if (!dataStr || dataStr === '[DONE]') return

  let data
  try { data = JSON.parse(dataStr) } catch { return }

  handlers.onRaw && handlers.onRaw(data)

  const ev = data.event
  if (ev === 'workflow_started') {
    handlers.onWorkflowStart && handlers.onWorkflowStart({
      workflow_run_id: data.workflow_run_id,
      stage: data.stage
    })
  } else if (ev === 'node_started') {
    handlers.onNodeStart && handlers.onNodeStart({
      title: data.stage?.replace(/^节点开始：/, '') || '',
      node_id: data.node_id,
      node_type: data.node_type,
      stage: data.stage
    })
  } else if (ev === 'node_finished') {
    handlers.onNodeFinish && handlers.onNodeFinish({
      title: data.stage?.replace(/^节点结束：/, '') || '',
      node_id: data.node_id,
      node_type: data.node_type,
      status: data.status,
      outputs: data.outputs,
      stage: data.stage
    })
  } else if (ev === 'text_chunk') {
    handlers.onTextChunk && handlers.onTextChunk(data.content || '')
  } else if (ev === 'workflow_finished') {
    handlers.onWorkflowFinish && handlers.onWorkflowFinish({
      status: data.status,
      outputs: data.outputs,
      error: data.error,
      stage: data.stage
    })
  } else if (ev === 'error') {
    handlers.onError && handlers.onError(new Error(data.error || 'unknown error'))
  }
}

export { checkBackendAlive }
