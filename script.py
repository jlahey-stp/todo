with open('index.html', 'r') as f:
    html = f.read()

# Replace save/load functions and add import/export UI
old_storage_js = """  // Storage
  function save() { try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(allTasks)); } catch(e){} }
  function load() { try { const r = sessionStorage.getItem(STORAGE_KEY); if(r) allTasks = JSON.parse(r); } catch(e){} }"""

# We already replaced sessionStorage with localStorage via sed, so match the updated version
old_storage_js = """  // Storage
  function save() { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(allTasks)); } catch(e){} }
  function load() { try { const r = localStorage.getItem(STORAGE_KEY); if(r) allTasks = JSON.parse(r); } catch(e){} }"""

new_storage_js = """  // Storage — localStorage with in-memory fallback for sandboxed environments
  let _memStore = null;
  function save() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(allTasks));
      _memStore = null; // localStorage worked, no need for mem fallback
    } catch(e) {
      _memStore = JSON.stringify(allTasks); // fallback: keep in memory
    }
  }
  function load() {
    try {
      const r = localStorage.getItem(STORAGE_KEY);
      if(r) allTasks = JSON.parse(r);
    } catch(e) {
      if(_memStore) { try { allTasks = JSON.parse(_memStore); } catch(e2){} }
    }
  }
  function exportData() {
    const blob = new Blob([JSON.stringify(allTasks, null, 2)], {type:'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'weekly-todo-backup.json';
    a.click();
    URL.revokeObjectURL(a.href);
  }
  function importData(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
      try {
        const data = JSON.parse(e.target.result);
        if (typeof data === 'object' && !Array.isArray(data)) {
          allTasks = data;
          save();
          renderWeek();
          showToast('Tasks imported successfully!', 'success');
        } else { showToast('Invalid backup file.', 'error'); }
      } catch(err) { showToast('Could not read file.', 'error'); }
    };
    reader.readAsText(file);
  }
  function showToast(msg, type='success') {
    const existing = document.getElementById('app-toast');
    if(existing) existing.remove();
    const t = document.createElement('div');
    t.id = 'app-toast';
    t.textContent = msg;
    t.style.cssText = `position:fixed;bottom:var(--space-6);right:var(--space-6);z-index:9999;
      padding:var(--space-3) var(--space-5);border-radius:var(--radius-lg);font-size:var(--text-sm);
      font-weight:600;box-shadow:var(--shadow-lg);animation:toastIn 220ms cubic-bezier(0.16,1,0.3,1);
      background:${type==='success'?'var(--color-success)':'var(--color-error)'};color:#fff;`;
    document.body.appendChild(t);
    setTimeout(()=>{ t.style.opacity='0'; t.style.transition='opacity 300ms'; setTimeout(()=>t.remove(),300); }, 2500);
  }"""

html = html.replace(old_storage_js, new_storage_js)

# Add toast keyframe animation to the style block
old_anim = "@keyframes taskIn { from{opacity:0;transform:translateY(-6px)} to{opacity:1;transform:translateY(0)} }"
new_anim = """@keyframes taskIn { from{opacity:0;transform:translateY(-6px)} to{opacity:1;transform:translateY(0)} }
    @keyframes toastIn { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }"""
html = html.replace(old_anim, new_anim)

# Add Export/Import buttons to the header-right section
old_header_right_end = """      <button class="theme-toggle" data-theme-toggle aria-label="Switch theme"></button>
    </div>
  </header>"""

new_header_right_end = """      <div style="display:flex;gap:var(--space-2);">
        <button class="week-btn" id="export-btn" title="Export backup" aria-label="Export tasks as JSON backup">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        </button>
        <label class="week-btn" title="Import backup" aria-label="Import tasks from JSON backup" style="cursor:pointer;" tabindex="0">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <input type="file" accept=".json" style="display:none" id="import-input">
        </label>
      </div>
      <button class="theme-toggle" data-theme-toggle aria-label="Switch theme"></button>
    </div>
  </header>"""

html = html.replace(old_header_right_end, new_header_right_end)

# Add event listeners for export/import before the closing </script>
old_script_end = """  load();
  renderWeek();
</script>"""

new_script_end = """  // Export / Import bindings
  document.getElementById('export-btn').addEventListener('click', exportData);
  document.getElementById('import-input').addEventListener('change', e => {
    importData(e.target.files[0]);
    e.target.value = ''; // reset so same file can be re-imported
  });

  load();
  renderWeek();
</script>"""

html = html.replace(old_script_end, new_script_end)

# Also update the title to reflect persistence
html = html.replace('<title>Weekly To-Do</title>', '<title>Weekly To-Do</title>')

with open('index.html', 'w') as f:
    f.write(html)

print("Done writing file")
print(f"File size: {len(html)} chars")

# Quick sanity checks
assert 'localStorage' in html, "localStorage missing"
assert '_memStore' in html, "memory fallback missing"
assert 'exportData' in html, "exportData missing"
assert 'importData' in html, "importData missing"
assert 'showToast' in html, "showToast missing"
assert 'export-btn' in html, "export button missing"
assert 'import-input' in html, "import input missing"
print("All sanity checks passed ✓")