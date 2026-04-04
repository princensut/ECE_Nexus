// ─── Mermaid init ──────────────────────────────────────────────
    mermaid.initialize({ startOnLoad: false, theme: 'dark' });

    // ─── State ────────────────────────────────────────────────────
    let masterMap = {};         // { "Topic": { prereqs: [...] } }
    let knownTopics = new Set(); // topics marked as already mastered
    let topoOrder = [];          // topological sort result (computed client-side)

    // ─── SPA routing ──────────────────────────────────────────────
    function switchPage(pageId) {
        document.querySelectorAll('.spa-page').forEach(p => p.classList.add('hidden'));
        document.getElementById(pageId).classList.remove('hidden');

        document.querySelectorAll('.nav-btn').forEach(b => {
            b.classList.remove('border-blue-500', 'text-blue-400');
            b.classList.add('border-transparent', 'text-slate-400');
        });
        const btn = document.getElementById('nav_' + pageId);
        if (btn) {
            btn.classList.add('border-blue-500', 'text-blue-400');
            btn.classList.remove('border-transparent', 'text-slate-400');
        }
    }

    // ─── Topological sort (Kahn's algorithm) ──────────────────────
    function topoSort(map) {
        const inDegree = {};
        const adj = {};

        for (const node of Object.keys(map)) {
            inDegree[node] = inDegree[node] || 0;
            adj[node] = adj[node] || [];
            for (const req of (map[node].prereqs || [])) {
                adj[req] = adj[req] || [];
                adj[req].push(node);
                inDegree[node] = (inDegree[node] || 0) + 1;
                inDegree[req] = inDegree[req] || 0;
            }
        }

        const queue = Object.keys(inDegree).filter(n => inDegree[n] === 0);
        const result = [];
        while (queue.length) {
            const node = queue.shift();
            result.push(node);
            for (const neighbor of (adj[node] || [])) {
                inDegree[neighbor]--;
                if (inDegree[neighbor] === 0) queue.push(neighbor);
            }
        }
        return result;
    }

    // ─── Mermaid render ───────────────────────────────────────────
    function renderMermaid() {
        let g = "graph TD;\n";
        g += "  classDef required fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:white;\n";
        g += "  classDef known fill:#059669,stroke:#047857,stroke-width:2px,color:white;\n";

        for (const topic of topoOrder) {
            const nodeId = sanitize(topic);
            const cls = knownTopics.has(topic) ? "known" : "required";
            const label = topic.replace(/"/g, "'");
            g += `  ${nodeId}["${label}"]:::${cls};\n`;
        }

        for (const [topic, data] of Object.entries(masterMap)) {
            for (const req of (data.prereqs || [])) {
                g += `  ${sanitize(req)} --> ${sanitize(topic)};\n`;
            }
        }

        const container = document.getElementById('mermaid-container');
        container.removeAttribute('data-processed');
        container.innerHTML = g;
        mermaid.init(undefined, container);
    }

    function sanitize(text) {
        return text.replace(/[^a-zA-Z0-9]/g, '_');
    }

    // ─── Checkbox list ────────────────────────────────────────────
    function renderCheckboxes() {
        const container = document.getElementById('topic-checkboxes');
        container.innerHTML = '';

        for (const topic of topoOrder) {
            const div = document.createElement('div');
            div.className = 'flex items-center space-x-3 p-2 hover:bg-slate-800 rounded transition';

            const safeId = sanitize(topic);
            const checked = knownTopics.has(topic) ? '' : 'checked';
            div.innerHTML = `
                <label class="flex items-center cursor-pointer w-full">
                    <input type="checkbox" id="chk_${safeId}"
                        class="form-checkbox h-5 w-5 text-blue-500 rounded bg-slate-900 border-slate-600" ${checked}>
                    <span class="ml-3 text-sm font-medium text-slate-300">${topic}</span>
                </label>`;
            container.appendChild(div);

            document.getElementById(`chk_${safeId}`).addEventListener('change', e => {
                if (e.target.checked) knownTopics.delete(topic);
                else knownTopics.add(topic);
                renderMermaid();
            });
        }
    }

    // ─── Graph synthesis ──────────────────────────────────────────
    document.getElementById('generate-graph-btn').addEventListener('click', async () => {
        const concept = document.getElementById('topic-input').value.trim();
        if (!concept) return;

        const btn = document.getElementById('generate-graph-btn');
        const errBox = document.getElementById('graph-error');
        btn.innerHTML = `<div class="spinner mr-3"></div> Computing Architecture...`;
        btn.disabled = true;
        errBox.classList.add('hidden');

        try {
            const res = await fetch('/api/synthesize-graph', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ concept })
            });
            const data = await res.json();

            if (data.error) throw new Error(data.error);

            masterMap = data.graph;
            knownTopics = new Set();
            topoOrder = topoSort(masterMap);

            renderCheckboxes();
            renderMermaid();
            switchPage('page3');

        } catch (err) {
            errBox.textContent = `Error: ${err.message}`;
            errBox.classList.remove('hidden');
        } finally {
            btn.innerHTML = 'Synthesize Graph';
            btn.disabled = false;
        }
    });

    // ─── Schedule generation ──────────────────────────────────────
    document.getElementById('generate-schedule-btn').addEventListener('click', async () => {
        const goal = document.getElementById('goal-input').value.trim();
        if (!goal) return;

        const btn = document.getElementById('generate-schedule-btn');
        const status = document.getElementById('schedule-status');
        const container = document.getElementById('schedule-container');

        btn.innerHTML = `<div class="spinner"></div>`;
        btn.disabled = true;
        status.textContent = 'Prompting LLM...';
        status.className = 'ml-3 px-2 py-1 bg-yellow-900 text-yellow-400 text-xs rounded animate-pulse';

        const requiredTopics = topoOrder.filter(t => !knownTopics.has(t));

        try {
            const res = await fetch('/api/generate-schedule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ goal, required_topics: requiredTopics })
            });
            const data = await res.json();

            if (data.error) throw new Error(data.error);

            if (data.all_complete) {
                container.innerHTML = `<div class="bg-green-900/40 border border-green-700 rounded-lg p-6 text-center text-green-400 font-bold">All topological prerequisites met. You are ready.</div>`;
            } else {
                container.innerHTML = data.schedule.map(item => `
                    <div class="bg-slate-800 border border-slate-700 rounded-lg p-5 hover:border-blue-500 transition shadow-lg">
                        <div class="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-700 pb-3 mb-3">
                            <h4 class="text-lg font-bold text-blue-400">${item.title || 'Module'}</h4>
                            <span class="text-sm font-mono text-emerald-400 bg-emerald-900/30 px-3 py-1 rounded mt-2 md:mt-0">${item.time || 'TBD'}</span>
                        </div>
                        <p class="text-sm text-slate-300 leading-relaxed">${item.description || ''}</p>
                    </div>`).join('');
            }

            status.textContent = 'Path Generated';
            status.className = 'ml-3 px-2 py-1 bg-slate-800 text-slate-400 text-xs rounded';

        } catch (err) {
            container.innerHTML = `<div class="bg-red-900/40 border border-red-700 rounded-lg p-6 text-red-400">Error: ${err.message}</div>`;
            status.textContent = 'Error';
            status.className = 'ml-3 px-2 py-1 bg-slate-800 text-slate-400 text-xs rounded';
        } finally {
            btn.innerHTML = 'Execute';
            btn.disabled = false;
        }
    });

    // ─── Proceed button ───────────────────────────────────────────
    document.getElementById('proceed-plan-btn').addEventListener('click', () => {
        switchPage('page2');
        document.getElementById('goal-input').focus();
    });

    // Enter key on topic input
    document.getElementById('topic-input').addEventListener('keydown', e => {
        if (e.key === 'Enter') document.getElementById('generate-graph-btn').click();
    });