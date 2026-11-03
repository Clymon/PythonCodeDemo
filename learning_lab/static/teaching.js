const app = document.querySelector("#editor-app"),
  notice = document.querySelector("#notice");
const esc = (v) =>
  String(v ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
let courses = [],
  currentCourse,
  currentLesson,
  csrf = "",
  savedMessage = "",
  dirty = false;
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
  const v = await r.json();
  if (!r.ok) throw Error(v.error || "Unable to save.");
  if (v.csrf_token) csrf = v.csrf_token;
  return v;
}
function fields() {
  return {
    title: document.querySelector("#lesson-title").value,
    objective: document.querySelector("#lesson-objective").value,
    paragraphs: document
      .querySelector("#lesson-text")
      .value.split(/\n\s*\n/)
      .map((v) => v.trim())
      .filter(Boolean),
  };
}
function showError(e) {
  notice.textContent = e.message;
  notice.hidden = false;
}
async function chooseCourse(id, lessonId) {
  const data = await api("/api/courses/" + encodeURIComponent(id));
  currentCourse = data.course;
  currentLesson =
    currentCourse.chapters
      .flatMap((ch) => ch.lessons)
      .find((l) => l.id === lessonId) ||
    currentCourse.chapters.flatMap((ch) => ch.lessons)[0];
  dirty = false;
  render();
}
function render() {
  app.innerHTML = `<div class="editor-layout"><aside class="editor-directory"><a class="back-link" href="/">← My courses</a><label for="course-select">Course</label><select id="course-select">${courses.map((c) => `<option value="${esc(c.id)}" ${c.id === currentCourse.id ? "selected" : ""}>${esc(c.title)}</option>`).join("")}</select>${currentCourse.chapters.map((ch, i) => `<section class="chapter"><h3>${i + 1}. ${esc(ch.title)}</h3>${ch.lessons.map((l) => `<button data-edit="${esc(l.id)}" class="${currentLesson.id === l.id ? "active" : ""}">${esc(l.title)}</button>`).join("")}</section>`).join("")}</aside><section class="editor-work"><div class="editor-heading"><div><p class="eyebrow">CONTENT MANAGEMENT</p><h1>Edit lesson</h1><p>Update the title, learning objective and lesson text.</p></div><a class="button secondary" href="/courses/${encodeURIComponent(currentCourse.id)}/lessons/${encodeURIComponent(currentLesson.id)}" target="_blank" rel="noopener">Open student page ↗</a></div><p class="editor-policy">Instructor reference: saving makes the text visible to learners immediately.</p><form id="lesson-form"><label for="lesson-title">Lesson title</label><input id="lesson-title" name="title" required maxlength="160" value="${esc(currentLesson.title)}"><label for="lesson-objective">Learning objective</label><input id="lesson-objective" maxlength="1000" value="${esc(currentLesson.objective || "")}"><label for="lesson-text">Lesson text</label><p class="field-help">Separate paragraphs with a blank line.</p><textarea id="lesson-text" rows="11" required>${esc(currentLesson.paragraphs.join("\n\n"))}</textarea><div class="editor-actions"><button type="button" class="button secondary" id="preview-button">Preview text</button><button class="button primary" type="submit">Save changes</button><span id="save-message" role="status">${esc(savedMessage)}</span></div></form><section id="preview-panel" hidden></section></section></div>`;
}
app.addEventListener("input", () => {
  dirty = true;
});
app.addEventListener("change", async (e) => {
  if (e.target.id === "course-select") {
    if (dirty && !confirm("Switch course? Unsaved text will be discarded.")) {
      e.target.value = currentCourse.id;
      return;
    }
    savedMessage = "";
    try {
      await chooseCourse(e.target.value);
    } catch (err) {
      showError(err);
    }
  }
});
app.addEventListener("click", async (e) => {
  const item = e.target.closest("[data-edit]");
  if (item && item.dataset.edit !== currentLesson.id) {
    if (
      dirty &&
      !confirm("Open another lesson? Unsaved text will be discarded.")
    )
      return;
    savedMessage = "";
    try {
      await chooseCourse(currentCourse.id, item.dataset.edit);
    } catch (err) {
      showError(err);
    }
    return;
  }
  if (e.target.id === "preview-button") {
    const v = fields(),
      panel = document.querySelector("#preview-panel");
    panel.hidden = false;
    panel.innerHTML = `<p class="eyebrow">TEXT PREVIEW · NOT SAVED</p><h2>${esc(v.title)}</h2>${v.objective ? `<p class="objective">${esc(v.objective)}</p>` : ""}${v.paragraphs.map((p) => `<p>${esc(p)}</p>`).join("")}`;
    panel.scrollIntoView({ behavior: "smooth", block: "start" });
  }
});
app.addEventListener("submit", async (e) => {
  if (e.target.id !== "lesson-form") return;
  e.preventDefault();
  const b = e.target.querySelector("[type=submit]");
  b.disabled = true;
  notice.hidden = true;
  try {
    const r = await api(
      "/api/teaching/lessons/" + encodeURIComponent(currentLesson.id),
      fields(),
    );
    savedMessage = r.message;
    await chooseCourse(currentCourse.id, currentLesson.id);
  } catch (err) {
    showError(err);
    b.disabled = false;
  }
});
(async () => {
  try {
    const v = await api("/api/courses");
    courses = v.courses;
    if (!courses.length) {
      app.innerHTML =
        '<section class="empty-state"><h1>No course content yet</h1></section>';
      return;
    }
    await chooseCourse(
      courses.find((c) => c.id === "teaching-practice")?.id || courses[0].id,
    );
  } catch (e) {
    showError(e);
  }
})();
