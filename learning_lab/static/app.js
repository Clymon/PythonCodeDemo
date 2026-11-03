const app = document.querySelector("#app"),
  notice = document.querySelector("#notice");
let csrf = "",
  selected,
  state,
  tab = "content";
const pending = new Set(),
  feedback = new Map();
const escapeHTML = (v) =>
  String(v ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const allLessons = (c) => c.chapters.flatMap((ch) => ch.lessons);
const href = (c, l) =>
  "/courses/" +
  encodeURIComponent(c) +
  (l ? "/lessons/" + encodeURIComponent(l) : "");
async function api(path, body) {
  const r = await fetch(
    path,
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
          body: JSON.stringify(body),
        },
  );
  const value = await r.json();
  if (!r.ok) throw Error(value.error || "Please try again.");
  if (value.csrf_token) csrf = value.csrf_token;
  return value;
}
function error(e) {
  notice.textContent = e.message;
  notice.hidden = false;
}
function lessonProgress() {
  const ids = new Set(allLessons(selected).map((l) => l.id));
  state.completed = state.completed.filter((id) => ids.has(id));
  state.completion_percent = state.lesson_count
    ? Math.round((state.completed.length / state.lesson_count) * 100)
    : 0;
}
function metric(value, label) {
  return `<div class="metric"><strong>${value}</strong><span>${label}</span></div>`;
}
async function home() {
  const data = await api("/api/courses");
  document.title = "My courses · Learning Lab";
  app.innerHTML = `<div class="course-index"><div class="page-heading"><div><p class="eyebrow">LEARNING SPACE</p><h1>My courses</h1><p>Open a course to explore its chapters and continue learning.</p></div><span class="count-label">${data.courses.length} courses</span></div><div class="course-grid">${data.courses.map((c) => `<article class="course-card"><div class="course-cover ${escapeHTML(c.accent)}"><span>${escapeHTML(c.code)}</span><div class="cover-motif" aria-hidden="true">${c.accent === "blue" ? "&lt;/&gt;" : "Aa"}</div><small>${escapeHTML(c.term)}</small></div><div class="course-card-body"><div class="course-card-meta"><span>COURSE</span><span>${c.chapter_count} chapters · ${c.lesson_count} lessons</span></div><h2><a href="${href(c.id)}">${escapeHTML(c.title)}</a></h2><p>${escapeHTML(c.description)}</p><div class="instructor">${escapeHTML(c.instructor)}</div><div class="progress-label"><span>Learning progress</span><b>${c.completion_percent}%</b></div><progress value="${c.completed.length}" max="${c.lesson_count || 1}" aria-label="${escapeHTML(c.title)} progress"></progress><div class="course-card-bottom"><span>${c.completed.length} of ${c.lesson_count} completed</span><a class="button primary" href="${href(c.id)}">Open course <span aria-hidden="true">→</span></a></div></div></article>`).join("")}</div><p class="sample-note">Workshop sample courses. Learning progress is saved in this browser profile.</p></div>`;
}
function courseNav() {
  return `<aside class="course-nav"><a class="back-link" href="/">← My courses</a><div class="course-symbol ${escapeHTML(selected.accent)}">${escapeHTML(selected.code)}</div><h2>${escapeHTML(selected.title)}</h2><p class="instructor">${escapeHTML(selected.instructor)}</p><nav aria-label="Course navigation">${[
    ["overview", "Overview", "◫"],
    ["content", "Content", "☷"],
    ["progress", "My progress", "◷"],
  ]
    .map(
      ([key, label, icon]) =>
        `<button data-tab="${key}" class="${tab === key ? "active" : ""}" ${tab === key ? 'aria-current="page"' : ""}><span aria-hidden="true">${icon}</span>${label}</button>`,
    )
    .join(
      "",
    )}</nav><div class="nav-progress"><div class="progress-label"><span>Course progress</span><b>${state.completion_percent}%</b></div><progress value="${state.completed.length}" max="${state.lesson_count || 1}" aria-label="Course progress"></progress><small>${state.completed.length} of ${state.lesson_count} lessons</small></div></aside>`;
}
function toc(current) {
  return `<aside class="chapter-tree" aria-label="Chapter and lesson directory"><div class="tree-title">Course content<span>${state.lesson_count} lessons</span></div>${selected.chapters.map((ch, i) => `<section class="chapter"><h3><span>${String(i + 1).padStart(2, "0")}</span>${escapeHTML(ch.title)}</h3><ol>${ch.lessons.map((l, j) => `<li><a href="${href(selected.id, l.id)}" class="${current === l.id ? "selected" : ""}" ${current === l.id ? 'aria-current="page"' : ""}><span class="lesson-status ${state.completed.includes(l.id) ? "done" : ""}">${state.completed.includes(l.id) ? "✓" : i + 1 + "." + (j + 1)}</span><span>${escapeHTML(l.title)}<small>${l.minutes ? escapeHTML(l.minutes) + " min" : ""}${l.questions.length ? " · " + l.questions.length + " checks" : ""}</small></span></a></li>`).join("")}</ol></section>`).join("")}</aside>`;
}
function questionCard(q) {
  const r = feedback.get(q.id),
    busy = pending.has(q.id);
  return `<form class="question" data-question="${escapeHTML(q.id)}"><p class="eyebrow">KNOWLEDGE CHECK</p><h3>${escapeHTML(q.prompt)}</h3><fieldset ${busy ? "disabled" : ""}><legend class="sr-only">Choose an answer</legend>${Object.entries(
    q.options,
  )
    .map(
      ([key, text]) =>
        `<label class="option"><input type="radio" name="choice" value="${escapeHTML(key)}" ${r?.choice === key ? "checked" : ""} required><b>${escapeHTML(key)}</b><span>${escapeHTML(text)}</span></label>`,
    )
    .join(
      "",
    )}</fieldset>${r ? `<p class="feedback ${r.correct ? "right" : "wrong"}" role="status"><b>${r.correct ? "Correct." : "Try again."}</b> ${escapeHTML(r.explanation)}</p>` : ""}<button type="submit" class="button ${r ? "secondary" : "primary"}" ${busy ? "disabled" : ""}>${busy ? "Checking…" : r ? "Check again" : "Check answer"}</button></form>`;
}
function safeResource(u) {
  return /^(https?:\/\/|\/static\/resources\/)/i.test(u) ? u : "#";
}
function lessonBody(l) {
  const done = state.completed.includes(l.id);
  return `<article class="lesson-body"><p class="eyebrow">LESSON${l.minutes ? " · " + escapeHTML(l.minutes) + " MIN READ" : ""}</p><h1>${escapeHTML(l.title)}</h1>${l.objective ? `<p class="objective">${escapeHTML(l.objective)}</p>` : ""}<section class="reading">${l.paragraphs.map((p) => `<p>${escapeHTML(p)}</p>`).join("")}${l.code ? `<div class="code-label">${escapeHTML(l.code_language || "Example")}</div><pre><code>${escapeHTML(l.code)}</code></pre>` : ""}${l.takeaway ? `<div class="takeaway"><b>Key idea</b><p>${escapeHTML(l.takeaway)}</p></div>` : ""}</section>${l.resources?.length ? `<section class="resources"><h2>Resources</h2>${l.resources.map((r) => `<a href="${escapeHTML(safeResource(r.url))}" download><span aria-hidden="true">↓</span> ${escapeHTML(r.label)}</a>`).join("")}</section>` : ""}${l.questions.length ? `<section class="practice"><h2>Check your understanding</h2><p>Try ${l.questions.length === 1 ? "this question" : `these ${l.questions.length} questions`}. Your first valid attempt sets the original score.</p>${l.questions.map(questionCard).join("")}</section>` : ""}<div class="complete-row"><div><h3>${done ? "Lesson completed" : "Finished this lesson?"}</h3><p>Reading completion is separate from your quiz score.</p></div><button class="button ${done ? "secondary" : "primary"}" data-complete="${escapeHTML(l.id)}">${done ? "✓ Completed · Undo" : "Mark as complete"}</button></div></article>`;
}
function overview() {
  return `<section class="course-overview"><p class="eyebrow">COURSE OVERVIEW</p><h1>${escapeHTML(selected.title)}</h1><p class="objective">${escapeHTML(selected.description)}</p><div class="overview-metrics">${metric(selected.chapters.length, "Chapters")}${metric(state.lesson_count, "Lessons")}${metric(state.question_count, "Knowledge checks")}</div><h2>Course outline</h2>${selected.chapters.map((ch, i) => `<div class="outline-row"><b>${String(i + 1).padStart(2, "0")}</b><div><h3>${escapeHTML(ch.title)}</h3><p>${ch.lessons.length} lesson${ch.lessons.length === 1 ? "" : "s"}</p></div></div>`).join("")}<a class="button primary" href="${href(selected.id)}">Open course content →</a></section>`;
}
function progressView() {
  return `<section class="course-progress"><p class="eyebrow">YOUR LEARNING</p><h1>My progress</h1><p>Progress belongs to this course and this browser profile.</p><div class="overview-metrics">${metric(state.completed.length + " / " + state.lesson_count, "Lessons completed")}${metric(state.score.correct + " / " + state.score.answered, "First-attempt score")}${metric(state.attempt_count, "Practice attempts")}</div><h2>Lessons</h2>${allLessons(
    selected,
  )
    .map(
      (l) =>
        `<a class="progress-row" href="${href(selected.id, l.id)}"><span class="lesson-status ${state.completed.includes(l.id) ? "done" : ""}">${state.completed.includes(l.id) ? "✓" : "○"}</span><span>${escapeHTML(l.title)}</span><small>${state.completed.includes(l.id) ? "Completed" : "Not completed"}</small><span>→</span></a>`,
    )
    .join(
      "",
    )}<p class="sample-note">Later attempts do not rewrite your first-attempt score. Marking a lesson complete does not award a quiz mark.</p></section>`;
}
function renderCourse(current) {
  lessonProgress();
  const first = allLessons(selected)[0];
  const l = allLessons(selected).find((l) => l.id === current) || first;
  document.title =
    (tab === "content"
      ? l?.title || "Content"
      : tab === "progress"
        ? "My progress"
        : selected.title) + " · Learning Lab";
  app.innerHTML = `<div class="workspace">${courseNav()}<div class="course-work"><div class="breadcrumbs"><a href="/">My courses</a><span>/</span><a href="${href(selected.id)}">${escapeHTML(selected.title)}</a>${tab === "content" && l ? `<span>/</span><b>${escapeHTML(l.title)}</b>` : ""}</div>${tab === "overview" ? overview() : tab === "progress" ? progressView() : `<div class="content-workspace">${toc(l?.id)}${l ? lessonBody(l) : '<section class="empty-state"><h1>No lessons yet</h1><p>This course does not contain learning content.</p></section>'}</div>`}</div></div>`;
}
async function start() {
  try {
    const match = location.pathname.match(
      /^\/courses\/([^/]+)(?:\/lessons\/([^/]+))?\/?$/,
    );
    if (!match) return await home();
    const r = await api(
      "/api/courses/" + encodeURIComponent(decodeURIComponent(match[1])),
    );
    selected = r.course;
    state = r.progress;
    renderCourse(match[2] ? decodeURIComponent(match[2]) : undefined);
  } catch (e) {
    app.innerHTML =
      '<section class="error-page"><h1>Unable to open this course</h1><p>Return to My courses and try again.</p><a href="/" class="button primary">My courses</a></section>';
    error(e);
  }
}
app.addEventListener("click", async (e) => {
  const nav = e.target.closest("[data-tab]");
  if (nav) {
    tab = nav.dataset.tab;
    renderCourse(location.pathname.split("/lessons/")[1]);
    return;
  }
  const b = e.target.closest("[data-complete]");
  if (!b) return;
  b.disabled = true;
  try {
    const value = await api(
      "/api/lessons/" + encodeURIComponent(b.dataset.complete) + "/complete",
      { completed: !state.completed.includes(b.dataset.complete) },
    );
    Object.assign(state, { completed: value.completed });
    renderCourse(b.dataset.complete);
  } catch (err) {
    error(err);
    b.disabled = false;
  }
});
app.addEventListener("submit", async (e) => {
  const form = e.target.closest("[data-question]");
  if (!form) return;
  e.preventDefault();
  const id = form.dataset.question;
  if (pending.has(id)) return;
  const choice = new FormData(form).get("choice");
  if (!choice) return;
  pending.add(id);
  const scroll = window.scrollY;
  renderCourse(location.pathname.split("/lessons/")[1]);
  try {
    feedback.set(id, await api("/api/answers", { question_id: id, choice }));
    const r = await api("/api/courses/" + encodeURIComponent(selected.id));
    state = r.progress;
  } catch (err) {
    error(err);
  } finally {
    pending.delete(id);
    renderCourse(location.pathname.split("/lessons/")[1]);
    window.scrollTo(0, scroll);
  }
});
start();
