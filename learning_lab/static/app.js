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
function courseRow(course, record) {
  const link = href(course.id);
  const code = escapeHTML(course.code);
  const status = course.completed.length === 0 ? "Not started" :
    course.completed.length === course.lesson_count ? "Completed" : "In progress";
  return `<article class="enrolment">
    <div class="course-code ${escapeHTML(course.accent)}">${code}</div>
    <div class="enrolment-detail">
      <p class="course-meta">${escapeHTML(course.term)}</p>
      <h2><a href="${link}">${escapeHTML(course.title)}</a></h2>
      <p>${escapeHTML(course.instructor)} · ${course.chapter_count} chapters · ${course.lesson_count} lessons</p>
      <div class="enrolment-progress"><progress value="${course.completed.length}" max="${course.lesson_count || 1}" aria-label="${code} completion"></progress><span>${course.completed.length} of ${course.lesson_count} completed</span></div>
      ${record ? `<p>First-attempt score: ${course.score.correct} / ${course.score.answered} · Practice attempts: ${course.attempt_count}</p>` : ""}
    </div>
    <div class="enrolment-actions"><span class="course-state">${status}</span>
    <a class="button secondary" href="${record ? link + '?view=progress' : link}">${record ? "My progress" : "Open course"} →</a></div>
  </article>`;
}
async function home() {
  const data = await api("/api/courses");
  const record = new URLSearchParams(location.search).get("view") === "record";
  const title = record ? "Learning record" : "My courses";
  document.title = title + " · Learning Lab";
  const completed = data.courses.reduce((n, c) => n + c.completed.length, 0);
  const total = data.courses.reduce((n, c) => n + c.lesson_count, 0);
  const attempts = data.courses.reduce((n, c) => n + c.attempt_count, 0);
  app.innerHTML = `<div class="portal-layout"><aside class="portal-sidebar">
    <p class="nav-label">Student workspace</p>
    <nav aria-label="Student workspace"><a href="/" ${record ? "" : 'aria-current="page"'}>My courses</a>
    <a href="/?view=record" ${record ? 'aria-current="page"' : ""}>Learning record</a></nav>
    <p class="nav-label">Course shortcuts</p><nav class="shortcuts" aria-label="Course shortcuts">${data.courses.map(c => `<a href="${href(c.id)}"><strong>${escapeHTML(c.code)}</strong>${escapeHTML(c.title)}</a>`).join("")}</nav>
  </aside><section class="portal-main">
    <div class="breadcrumbs"><a href="/">Student portal</a><span>/</span><b>${title}</b></div>
    <h1>${title}</h1><div class="portal-metrics">
    ${metric(data.courses.length,"Enrolled courses")}${metric(completed + " / " + total,"Lessons completed")}${metric(attempts,"Practice attempts")}</div>
    <div class="enrolments-heading"><h2>${record ? "Results by course" : "Enrolled courses"}</h2><span>${data.courses.length} courses</span></div>
    <div class="enrolments">${data.courses.map(c => courseRow(c, record)).join("")}</div>
  </section></div>`;
}
function courseNav() {
  const root = href(selected.id);
  const links = [["overview","Overview",root], ["content","Content",root + "?view=content"],
    ["progress","My progress",root + "?view=progress"]];
  return `<header class="course-heading">
    <div class="breadcrumbs"><a href="/">My courses</a><span>/</span><b>${escapeHTML(selected.code)}</b></div>
    <div class="course-identity"><div><h1>${escapeHTML(selected.title)}</h1>
    <p>${escapeHTML(selected.instructor)} · ${escapeHTML(selected.term)}</p></div>
    <div class="course-completion"><b>${state.completion_percent}% complete</b><progress value="${state.completed.length}"
      max="${state.lesson_count || 1}" aria-label="Course completion"></progress></div></div>
    <nav class="course-tabs" aria-label="Course navigation">${links.map(([key,label,url]) =>
      `<a href="${url}" ${tab === key ? 'aria-current="page"' : ""}>${label}</a>`).join("")}</nav>
  </header>`;
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
  return `<article class="lesson-body"><p class="eyebrow">LESSON${l.minutes ? " · " + escapeHTML(l.minutes) + " MIN READ" : ""}</p><h1>${escapeHTML(l.title)}</h1>${l.objective ? `<p class="objective">${escapeHTML(l.objective)}</p>` : ""}<section class="reading">${l.paragraphs.map((p) => `<p>${escapeHTML(p)}</p>`).join("")}${l.code ? `<div class="code-label">${escapeHTML(l.code_language || "Example")}</div><pre><code>${escapeHTML(l.code)}</code></pre>` : ""}${l.takeaway ? `<div class="takeaway"><b>Key idea</b><p>${escapeHTML(l.takeaway)}</p></div>` : ""}</section>${l.resources?.length ? `<section class="resources"><h2>Resources</h2>${l.resources.map((r) => `<a href="${escapeHTML(safeResource(r.url))}" download><span aria-hidden="true">↓</span> ${escapeHTML(r.label)}</a>`).join("")}</section>` : ""}${l.questions.length ? `<section class="practice"><h2>Check your understanding</h2><p>Try ${l.questions.length === 1 ? "this question" : `these ${l.questions.length} questions`}. Your first valid attempt sets the original score.</p>${l.questions.map(questionCard).join("")}</section>` : ""}<div class="complete-row"><div><h3>${done ? "Lesson completed" : "Finished this lesson?"}</h3><p>Reading completion is separate from your quiz score.</p></div><button class="button ${done ? "secondary" : "primary"}" data-complete="${escapeHTML(l.id)}">${done ? "✓ Completed · Undo" : "Mark as complete"}</button></div>${lessonNavigation(l)}</article>`;
}
function lessonNavigation(lesson) {
  const lessons = allLessons(selected);
  const index = lessons.findIndex(item => item.id === lesson.id);
  return `<nav class="lesson-pager" aria-label="Lesson navigation">
    ${index > 0 ? `<a href="${href(selected.id, lessons[index - 1].id)}">← Previous lesson</a>` : ""}
    ${index + 1 < lessons.length ? `<a href="${href(selected.id, lessons[index + 1].id)}">Next lesson →</a>` : ""}
  </nav>`;
}
function overview() {
  const lessons = allLessons(selected);
  const next = lessons.find(l => !state.completed.includes(l.id)) || lessons[0];
  return `<section class="course-overview"><div class="syllabus-header"><div><h2>Course overview</h2>
    <p>${escapeHTML(selected.description)}</p></div>
    ${next ? `<a class="button primary" href="${href(selected.id,next.id)}">${state.completed.length ? "Continue learning" : "Start learning"} →</a>` : ""}</div>
    <h2>Syllabus</h2>${selected.chapters.map((ch,i) => `<section class="syllabus-chapter">
    <h3><span>Chapter ${i+1}</span>${escapeHTML(ch.title)}</h3>
    ${ch.lessons.map(l => `<a href="${href(selected.id,l.id)}"><strong>${escapeHTML(l.title)}</strong><small>${state.completed.includes(l.id) ? "Completed" : (l.minutes ? escapeHTML(l.minutes) + " min" : "Lesson")} →</small></a>`).join("")}</section>`).join("")}</section>`;
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
  const content = tab === "overview" ? overview() : tab === "progress" ? progressView() :
    `<div class="content-workspace">${toc(l?.id)}${l ? lessonBody(l) : '<section class="empty-state"><h2>No lessons yet</h2></section>'}</div>`;
  app.innerHTML = `<div class="workspace">${courseNav()}<div class="course-work">${content}</div></div>`;
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
    const view = new URLSearchParams(location.search).get("view");
    tab = match[2] ? "content" : ["content","progress"].includes(view) ? view : "overview";
    renderCourse(match[2] ? decodeURIComponent(match[2]) : undefined);
  } catch (e) {
    app.innerHTML =
      '<section class="error-page"><h1>Unable to open this course</h1><p>Return to My courses and try again.</p><a href="/" class="button primary">My courses</a></section>';
    error(e);
  }
}
app.addEventListener("click", async (e) => {
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
