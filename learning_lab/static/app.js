let data;
const app = document.querySelector("#app");
const notice = document.querySelector("#notice");
const pending = new Set();
const feedback = new Map();
const escapeHTML = (value) =>
  String(value).replace(
    /[&<>"']/g,
    (ch) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        ch
      ],
  );
const ratio = () =>
  Math.round((data.completed.length / data.lessons.length) * 100);

async function api(path, body) {
  const response = await fetch(
    path,
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": data.csrf_token,
          },
          body: JSON.stringify(body),
        },
  );
  const result = await response.json();
  if (!response.ok)
    throw new Error(result.error || "Something went wrong. Please try again.");
  return result;
}

function showError(error) {
  notice.textContent = error.message;
  notice.hidden = false;
}

function updateProgress(result) {
  Object.assign(data, {
    score: result.score,
    completed: result.completed,
    attempt_count: result.attempt_count,
  });
}

function stats() {
  return `<div class="stats"><div><strong>${data.completed.length}<small> / ${data.lessons.length}</small></strong><span>Lessons completed</span></div><div><strong>${data.score.correct}<small> / ${data.score.answered}</small></strong><span>First-attempt score</span></div><div><strong>${data.attempt_count}</strong><span>Practice attempts</span></div></div>`;
}

function lessonCard(lesson) {
  const done = data.completed.includes(lesson.id);
  return `<article class="lesson-card"><a class="lesson-art ${lesson.color}" href="#lesson/${lesson.id}" aria-label="Open ${escapeHTML(lesson.title)}"><span class="art-tag">${lesson.category}</span><span class="art-number">${lesson.number}</span><span class="art-symbol">${lesson.category === "PYTHON" ? "{ }" : lesson.category === "GIT" ? "↗" : "✓"}</span><span class="art-caption">LEARNING LAB / FIELD NOTES</span></a><div class="card-content"><div class="card-meta"><span>LESSON ${lesson.number}</span><span>${lesson.minutes} MIN READ</span></div><h3><a href="#lesson/${lesson.id}">${escapeHTML(lesson.title)}</a></h3><p>${escapeHTML(lesson.description)}</p><div class="card-bottom"><span class="status ${done ? "done" : ""}">${done ? "✓ Completed" : "2 practice questions"}</span><a class="text-link" href="#lesson/${lesson.id}">${done ? "Read again" : "Open lesson"} <span aria-hidden="true">↗</span></a></div></div></article>`;
}

function home() {
  const next =
    data.lessons.find((lesson) => !data.completed.includes(lesson.id)) ||
    data.lessons[0];
  app.innerHTML = `<section class="hero"><div class="hero-copy"><p class="eyebrow">YOUR EVERYDAY LEARNING SPACE</p><h1>${escapeHTML(data.title)}</h1><p class="hero-description">${escapeHTML(data.subtitle)}</p><a class="button primary" href="#lesson/${next.id}">${data.completed.length ? "Continue learning" : "Start with lesson 01"} <span aria-hidden="true">↗</span></a><p class="hero-footnote">At your pace. One small win at a time.</p></div><div class="hero-note"><span class="note-top">THE LEARNING LOOP <span>01 / 03</span></span><div class="loop-words"><span>Explore.</span><span>Try it.</span><span class="loop-last">Make it stick.<i>✳</i></span></div><div class="note-bottom"><span>A little practice goes a long way.</span><span aria-hidden="true">↗</span></div></div></section>${stats()}<section class="library"><div class="section-heading"><div><p class="eyebrow">BUILD YOUR FOUNDATIONS</p><h2>Your next small win</h2></div><span class="section-caption">3 short lessons. Plenty to try.</span></div><div class="lesson-grid">${data.lessons.map(lessonCard).join("")}</div></section>`;
}

function questionCard(question, mode = "quiz") {
  const key = `${mode}:${question.id}`;
  const result = feedback.get(key);
  const busy = pending.has(key);
  return `<form class="question" data-question="${question.id}" data-mode="${mode}"><div class="question-top"><span class="eyebrow">QUICK CHECK</span>${result ? `<span class="result-tag ${result.correct ? "right" : "wrong"}">${result.correct ? "Correct" : "Keep practising"}</span>` : ""}</div><h3>${escapeHTML(question.prompt)}</h3><fieldset ${busy ? "disabled" : ""}><legend class="sr-only">Choose an answer</legend>${Object.entries(
    question.options,
  )
    .map(
      ([key, text]) =>
        `<label class="option"><input type="radio" name="choice" value="${key}" ${result?.choice === key ? "checked" : ""} required><span class="option-letter">${key}</span><span>${escapeHTML(text)}</span></label>`,
    )
    .join(
      "",
    )}</fieldset>${result ? `<div class="feedback ${result.correct ? "right" : "wrong"}" role="status">${escapeHTML(result.explanation)}</div>` : ""}<button class="button ${result ? "secondary" : "primary"}" type="submit" ${busy ? "disabled" : ""}>${busy ? "Checking…" : result ? "Check again" : "Check answer"} <span aria-hidden="true">↗</span></button></form>`;
}

function lessonView(id) {
  const lesson = data.lessons.find((item) => item.id === id);
  if (!lesson) return notFound();
  const done = data.completed.includes(id);
  app.innerHTML = `<div class="lesson-layout"><aside class="lesson-sidebar"><a class="back-link" href="#home">← All lessons</a><p class="eyebrow">YOUR LEARNING PATH</p><h2>AI Coding<br>Essentials</h2><ol>${data.lessons.map((item) => `<li><a href="#lesson/${item.id}" class="${item.id === id ? "current" : ""}"><span>${data.completed.includes(item.id) ? "✓" : item.number}</span>${escapeHTML(item.title)}</a></li>`).join("")}</ol><div class="sidebar-progress"><div><span>Course progress</span><strong>${ratio()}%</strong></div><progress value="${data.completed.length}" max="${data.lessons.length}" aria-label="Course progress"></progress><small>${data.completed.length} of ${data.lessons.length} lessons completed</small></div></aside><article class="lesson-body"><div class="lesson-heading"><p class="eyebrow">LESSON ${lesson.number} <span>/</span> ${lesson.category} <span>/</span> ${lesson.minutes} MIN READ</p><h1>${escapeHTML(lesson.title)}</h1><p class="lesson-objective">${escapeHTML(lesson.objective)}</p></div><section class="lesson-reading">${lesson.paragraphs.map((p) => `<p>${escapeHTML(p)}</p>`).join("")}<div class="code-label">${lesson.category === "GIT" ? "TERMINAL" : "PYTHON"}</div><pre><code>${escapeHTML(lesson.code)}</code></pre><p class="takeaway"><strong>Take it with you</strong>${escapeHTML(lesson.takeaway)}</p></section><div class="practice-heading"><p class="eyebrow">PUT IT INTO PRACTICE</p><h2>A small check for understanding</h2><p>Try both questions. Your first-attempt score stays as your starting point.</p></div>${lesson.questions.map((q) => questionCard(q)).join("")}<div class="complete-row"><div><h3>${done ? "One small win, saved." : "Ready for the next small win?"}</h3><p>Mark the lesson when you have finished reading.</p></div><button class="button ${done ? "secondary" : "primary"}" data-complete="${id}">${done ? "✓ Completed · Undo" : "Mark lesson complete"}</button></div></article></div>`;
}

function progressView() {
  app.innerHTML = `<section class="page-intro"><p class="eyebrow">YOUR LEARNING JOURNEY</p><h1>Progress you can see.</h1><p>Your reading progress and first-attempt quiz score measure different things.</p></section>${stats()}<section class="progress-panel"><div class="progress-summary"><h2>Keep the momentum</h2><strong>${ratio()}%</strong></div><progress value="${data.completed.length}" max="${data.lessons.length}" aria-label="Completed lessons"></progress>${data.lessons.map((lesson) => `<a class="progress-lesson" href="#lesson/${lesson.id}"><span class="lesson-index ${data.completed.includes(lesson.id) ? "finished" : ""}">${data.completed.includes(lesson.id) ? "✓" : lesson.number}</span><div><h3>${escapeHTML(lesson.title)}</h3><p>${data.completed.includes(lesson.id) ? "Completed" : "Ready when you are"}</p></div><span aria-hidden="true">↗</span></a>`).join("")}<p class="score-note">Your first valid quiz answer sets the original score for each question. Answering again does not rewrite it. Your progress stays in this browser’s practice profile.</p></section>`;
}

function notFound() {
  app.innerHTML =
    '<section class="empty-state"><span>↗</span><h1>Let’s get back on track.</h1><p>That lesson is not in this classroom.</p><a class="button primary" href="#home">Back to classroom</a></section>';
}

function render() {
  if (!data) return;
  const route = location.hash.slice(1) || "home";
  document
    .querySelectorAll("[data-nav]")
    .forEach((link) =>
      link.classList.toggle(
        "active",
        link.dataset.nav === (route.startsWith("lesson/") ? "home" : route),
      ),
    );
  if (route.startsWith("lesson/")) lessonView(route.slice(7));
  else if (route === "progress") progressView();
  else if (route === "home") home();
  else notFound();
}

app.addEventListener("submit", async (event) => {
  const form = event.target.closest("[data-question]");
  if (!form) return;
  event.preventDefault();
  const key = `${form.dataset.mode}:${form.dataset.question}`;
  if (pending.has(key)) return;
  const choice = new FormData(form).get("choice");
  if (!choice) return;
  const scrollY = window.scrollY;
  pending.add(key);
  render();
  notice.hidden = true;
  try {
    const result = await api("/api/answers", {
      question_id: form.dataset.question,
      choice,
      mode: form.dataset.mode,
    });
    feedback.set(key, result);
    updateProgress(result);
  } catch (error) {
    showError(error);
  } finally {
    pending.delete(key);
    render();
    window.scrollTo(0, scrollY);
  }
});

app.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-complete]");
  if (!button || button.disabled) return;
  button.disabled = true;
  notice.hidden = true;
  const scrollY = window.scrollY;
  try {
    updateProgress(
      await api(`/api/lessons/${button.dataset.complete}/complete`, {
        completed: !data.completed.includes(button.dataset.complete),
      }),
    );
    render();
    window.scrollTo(0, scrollY);
  } catch (error) {
    button.disabled = false;
    showError(error);
  }
});

window.addEventListener("hashchange", () => {
  render();
  window.scrollTo(0, 0);
});
api("/api/dashboard")
  .then((result) => {
    data = result;
    render();
  })
  .catch((error) => {
    app.innerHTML =
      '<section class="empty-state"><h1>Your classroom could not load.</h1><p>Check that the Python server is running, then reload this page.</p><button class="button primary" onclick="location.reload()">Try again</button></section>';
    showError(error);
  });
