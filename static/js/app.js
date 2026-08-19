(() => {
  const form = document.querySelector('[data-multistep]');
  if (form) {
    const steps = [...form.querySelectorAll('[data-step]')];
    const tabs = [...form.querySelectorAll('[data-step-tab]')];
    const next = form.querySelector('[data-next]');
    const prev = form.querySelector('[data-prev]');
    const submit = form.querySelector('[data-submit]');
    const progress = form.querySelector('[data-progress]');
    const progressShell = form.querySelector('[role="progressbar"]');
    const stepStatus = form.querySelector('[data-step-status]');
    const submitStatus = form.querySelector('[data-submit-status]');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let dirty = false;
    let submitting = false;
    let current = 0;

    const show = (index) => {
      current = Math.max(0, Math.min(index, steps.length - 1));
      steps.forEach((step, i) => step.classList.toggle('active', i === current));
      tabs.forEach((tab, i) => {
        tab.classList.toggle('active', i === current);
        tab.setAttribute('aria-selected', String(i === current));
      });
      prev.classList.toggle('hidden', current === 0);
      next.classList.toggle('hidden', current === steps.length - 1);
      submit.classList.toggle('hidden', current !== steps.length - 1);
      progress.style.width = `${((current + 1) / steps.length) * 100}%`;
      progressShell?.setAttribute('aria-valuenow', String(current + 1));
      if (stepStatus) stepStatus.textContent = `Step ${current + 1} of ${steps.length}`;
      window.scrollTo({ top: Math.max(0, form.offsetTop - 15), behavior: reduceMotion ? 'auto' : 'smooth' });
    };

    const validCurrent = () => {
      const fields = [...steps[current].querySelectorAll('input, select, textarea')];
      for (const field of fields) {
        if (!field.checkValidity()) {
          field.reportValidity();
          return false;
        }
      }
      return true;
    };
    next?.addEventListener('click', () => validCurrent() && show(current + 1));
    prev?.addEventListener('click', () => show(current - 1));
    tabs.forEach((tab, i) => tab.addEventListener('click', () => {
      if (i <= current || validCurrent()) show(i);
    }));
    form.addEventListener('input', () => { dirty = true; });
    form.addEventListener('submit', () => {
      submitting = true;
      dirty = false;
      submit.disabled = true;
      submit.textContent = 'Creating profile…';
      if (submitStatus) submitStatus.textContent = 'Creating your capital profile…';
    });
    window.addEventListener('beforeunload', (event) => {
      if (!dirty || submitting) return;
      event.preventDefault();
      event.returnValue = '';
    });
    show(0);
  }

  const search = document.querySelector('[data-table-search]');
  const rows = [...document.querySelectorAll('[data-admin-table] tbody tr[data-search]')];
  search?.addEventListener('input', () => {
    const term = search.value.toLowerCase().trim();
    rows.forEach(row => {
      row.hidden = term && !row.dataset.search.toLowerCase().includes(term);
    });
  });
})();
