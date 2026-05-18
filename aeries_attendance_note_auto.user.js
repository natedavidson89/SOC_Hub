// ==UserScript==
// @name         Aeries Attendance Note Auto Button
// @namespace    soc-hub
// @version      1.1
// @description  Adds automation button to attenance management
// @match        https://santaclaracoe.aeries.net/admin/AttendanceManagement.aspx*
// @grant        none
// @downloadURL  https://raw.githubusercontent.com/natedavidson89/SOC_Hub/main/aeries_attendance_note_auto.user.js
// @updateURL    https://raw.githubusercontent.com/natedavidson89/SOC_Hub/main/aeries_attendance_note_auto.user.js
// ==/UserScript==

(function () {
  "use strict";
  console.log('✅ Tampermonkey Attendance Automation script LOADED');

  // =====================================================
  // CONFIG
  // =====================================================

  const BUTTON_ID = "btnCustomAction";

  const TARGET_TD_SELECTOR =
    "#aTabFilters > table > tbody > tr:nth-child(1) > td:nth-child(5)";

  const absenceCodeMap = [
    { keywords: ["sick", "flu", "covid", "sk - sick", "hospital"], code: "B" },
    {
      keywords: [
        "doctor",
        "appointment",
        "therapist",
        "therapy",
        "dd - doctor/dentist appointment",
        "appt"
      ],
      code: "D"
    },
    { keywords: ["vacation", "out of"], code: "V" },
    { keywords: ["nr - no response from parent"], code: "U" }
  ];

  const DEFAULT_NOTE_TEXT =
    "Office unable to contact parents. Absence marked as Unexcused.";

  const NOTE_LOAD_DELAY = 300;
  const BETWEEN_NOTES_DELAY = 900;

  // =====================================================
  // UTIL
  // =====================================================

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  // =====================================================
  // INSERT BUTTON
  // =====================================================

  function insertButton() {
    const td = document.querySelector(TARGET_TD_SELECTOR);
    if (!td || document.getElementById(BUTTON_ID)) return;

    const btn = document.createElement("a");
    btn.className = "abtn";
    btn.id = BUTTON_ID;
    btn.title = "Process attendance notes";
    btn.href = "javascript:void(0);";
    btn.innerHTML = '<i class="fa fa-bolt" aria-hidden="true"></i>';

    btn.addEventListener("click", () => {
      processAttendanceNotes();
    });

    td.appendChild(btn);
  }

  new MutationObserver(insertButton).observe(document.body, {
    childList: true,
    subtree: true
  });
  insertButton();

  // =====================================================
  // WAIT FOR IFRAME
  // =====================================================

  async function waitForNoteIframe(timeout = 3000) {
    const start = Date.now();

    while (Date.now() - start < timeout) {
      const iframe = document.querySelector(".k-window-iframecontent iframe");
      if (
        iframe &&
        iframe.contentWindow &&
        iframe.contentWindow.document &&
        iframe.contentWindow.document.readyState === "complete"
      ) {
        return iframe;
      }
      await sleep(100);
    }

    throw new Error("Timed out waiting for attendance note iframe.");
  }

  // =====================================================
  // ABSENCE CODE LOGIC (WORKING VERSION)
  // =====================================================

  function getAttendanceCodeFromReasons(reasons) {
    if (!reasons || !reasons.length) return "U";

    const text = reasons.join(" ").toLowerCase();

    for (const entry of absenceCodeMap) {
      if (entry.keywords.some(k => k && text.includes(k.toLowerCase()))) {
        return entry.code;
      }
    }

    // ✅ non‑matching text stays A
    return "A";
  }

    function closeLastAttendanceModal() {
  const closes = document.querySelectorAll(".k-i-close");
  if (closes.length > 4) {
    closes[4].click();
    console.log("✅ Final attendance modal closed via k-i-close[4]");
  } else {
    console.warn("⚠️ Expected k-i-close[4] not found");
  }
}

  // =====================================================
  // SCRAPE REASONS (WORKING VERSION)
  // =====================================================

  function getReasonsFromOpenNote() {
    try {
      const iframe = document.querySelector(".k-window-iframecontent iframe");
      if (!iframe?.contentWindow) return [];

      const doc = iframe.contentWindow.document;
      const reasons = new Set();

      doc.querySelectorAll(".DataMainContent.col-sm-6.ar").forEach(el => {
        const t = el.textContent.trim();
        if (t && t !== "-") reasons.add(t);
      });

      doc.querySelectorAll(".CommentDisplay").forEach(el => {
        const t = el.textContent.replace(/\s+/g, " ").trim();
        if (t) reasons.add(t);
      });

      doc
        .querySelectorAll(
          "input[type=checkbox]:checked, input[type=radio]:checked"
        )
        .forEach(el => {
          if (el.labels?.length) reasons.add(el.labels[0].innerText.trim());
          else if (el.value) reasons.add(el.value.trim());
        });

      doc.querySelectorAll("select option:checked").forEach(o =>
        reasons.add(o.textContent.trim())
      );

      doc.querySelectorAll("textarea").forEach(t => {
        if (t.value && t.value.trim()) reasons.add(t.value.trim());
      });

      return Array.from(reasons);
    } catch (e) {
      console.warn("⚠️ Could not read reasons:", e);
      return [];
    }
  }

  // =====================================================
  // WRITE DEFAULT NOTE
  // =====================================================

  function writeDefaultNoteAndSave() {
    const iframe = document.querySelector(".k-window-iframecontent iframe");
    if (!iframe?.contentWindow) return;

    const doc = iframe.contentWindow.document;
    const textarea =
      doc.querySelector("textarea[id*='txtCO']") ||
      doc.querySelector("textarea[name*='txtCO']");
    const saveBtn =
      doc.querySelector("a[id*='LinkButton'][title*='Save']") ||
      doc.querySelector("a.abtnSave");

    if (!textarea || textarea.value.trim()) return;

    textarea.value = DEFAULT_NOTE_TEXT;
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
    textarea.dispatchEvent(new Event("change", { bubbles: true }));
    saveBtn?.click();
  }

  // =====================================================
  // ENTER ATTENDANCE CODE
  // =====================================================

  function enterAttendanceCode(noteLink, code) {
    const row = noteLink.closest("tr");
    if (!row) return;

    const input = row.querySelector("input.txtA");
    if (!input) return;

    input.value = code;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    input.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true }));
  }

  // =====================================================
  // MODAL CONTROL
  // =====================================================

  function closeAttendanceNoteModal() {
    const closeBtn = document.querySelector(
      ".k-window .k-window-action .k-i-close"
    );
    if (closeBtn) closeBtn.click();
  }

  // =====================================================
  // MAIN (WORKING VERSION)
  // =====================================================

  async function processAttendanceNotes() {
    const noteLinks = Array.from(
      document.querySelectorAll("a.abtn[onclick^='AttNote']")
    );

    console.log(`Found ${noteLinks.length} notes to process.`);

    for (let i = 0; i < noteLinks.length; i++) {
      const link = noteLinks[i];

      link.click();
      await sleep(NOTE_LOAD_DELAY);

      let reasons = [];
      try {
        await waitForNoteIframe();
        reasons = getReasonsFromOpenNote();
      } catch {}

      const code = getAttendanceCodeFromReasons(reasons);

      if (!reasons.length) {
        writeDefaultNoteAndSave();
        await sleep(700);
      }

      enterAttendanceCode(link, code);

      await sleep(400);
      closeAttendanceNoteModal();
      await sleep(BETWEEN_NOTES_DELAY);
    }

      // ✅ FINAL close — only once, after all processing
      closeLastAttendanceModal();


    console.log("✅ All attendance notes processed.");
  }
})();
