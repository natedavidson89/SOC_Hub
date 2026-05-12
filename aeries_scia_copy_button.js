(function () {
  'use strict';
    console.log('✅ Tampermonkey SCIA Copy script LOADED');
  /* -------------------------------------------------- */
  /* 🔁 Inject Copy Button                              */
  /* -------------------------------------------------- */

  function injectCopyButtons() {
    document.querySelectorAll('.DataContainer').forEach(container => {
      const actions = container.querySelector('.DataActions');
      if (!actions || actions.querySelector('.Copy')) return;

      const copyWrapper = document.createElement('div');
      copyWrapper.id = 'ctl00_MainContent_subCustom_rptSummary_ctl00_divCopy';

      copyWrapper.innerHTML = `
        <i class="fa fa-copy Copy" title="Copy Record"></i>
      `;

      actions.appendChild(copyWrapper);

      copyWrapper.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();

        const data = {};

        container.querySelectorAll('.InlineData').forEach(item => {
          const labelEl = item.querySelector('.DataLabel');
          if (!labelEl) return;

          const key = labelEl.textContent
            .replace(/\u00A0/g, ' ')
            .replace(/:+/g, '')
            .replace(/\s+/g, ' ')
            .trim()
            .toLowerCase();

          const clone = item.cloneNode(true);
          clone.querySelector('.DataLabel')?.remove();

          data[key] = clone.textContent
            .replace(/\u00A0/g, ' ')
            .trim();
        });

        // ✅ Create NEW record
        document
          .querySelector('#ctl00_MainContent_subCustom_lnkAddAction')
          ?.click();

        waitUntilReady(data);
      });
    });
  }

  /* -------------------------------------------------- */
  /* 🛠️ Utilities                                      */
  /* -------------------------------------------------- */

  function cleanNumber(value) {
    if (!value) return null;
    return value
      .replace(/\u00A0/g, '')
      .replace(/[^\d]/g, '')
      .trim();
  }

  function parseMDY(dateStr) {
    if (!dateStr) return null;

    dateStr = dateStr.replace(/\u00A0/g, '').trim();
    const parts = dateStr.split('/');
    if (parts.length !== 3) return null;

    const m = Number(parts[0]) - 1;
    const d = Number(parts[1]);
    const y = Number(parts[2]);

    return new Date(y, m, d);
  }

  function setValue(selector, value) {
    const el = document.querySelector(selector);
    if (!el || value == null) return;

    el.focus();
    el.value = value;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    el.dispatchEvent(new Event('blur', { bubbles: true }));

    console.log('Set', selector, value);
  }

  /* -------------------------------------------------- */
  /* ✅ Robust Kendo Date Setter                        */
  /* -------------------------------------------------- */

  function setKendoDate(selector, rawDate, attempts = 12) {
    const el = document.querySelector(selector);
    if (!el || !rawDate) return;

    const dateObj = parseMDY(rawDate);
    if (!dateObj || isNaN(dateObj)) return;

    const trySet = () => {
      const widget = $(selector).data('kendoDatePicker');
      if (!widget) return false;

      widget.value(dateObj);
      widget.trigger('change');
      widget.input.trigger('blur');

      console.log('✅ Kendo date set:', dateObj);
      return true;
    };

    if (trySet()) return;

    if (attempts > 0) {
      setTimeout(
        () => setKendoDate(selector, rawDate, attempts - 1),
        250
      );
    } else {
      console.warn('❌ Failed to set Kendo date:', rawDate);
    }
  }

  /* -------------------------------------------------- */
  /* ⏳ Wait for Rewrite Form                           */
  /* -------------------------------------------------- */

  function waitUntilReady(data) {
    const interval = setInterval(() => {
      const monthField =
        document.querySelector('#ctl00_MainContent_subCustom_txtMO_txtValue');
      const saveBtn =
        document.querySelector('#ctl00_MainContent_subCustom_btnUpdateCustom');

      if (!monthField || !saveBtn || monthField.offsetParent === null) return;

      clearInterval(interval);
      console.log('Form ready, filling…');

      setTimeout(() => {
        const ok = fillForm(data);
        if (ok !== false) {
          setTimeout(() => {
            console.log('Saving…');
            saveBtn.click();
          }, 1200);
        }
      }, 1000);
    }, 300);
  }

  /* -------------------------------------------------- */
  /* 📝 Fill Form                                      */
  /* -------------------------------------------------- */

  function fillForm(data) {
    console.log('Normalized keys available:', Object.keys(data));

    const monthMap = {
      january: 'JAN',
      february: 'FEB',
      march: 'MAR',
      april: 'APR',
      may: 'MAY',
      june: 'JUN',
      july: 'JUL',
      august: 'AUG',
      september: 'SEP',
      october: 'OCT',
      november: 'NOV',
      december: 'DEC'
    };

    const monthOrder = Object.values(monthMap);

    const rawMonth = data['month (required)'];
    const currentMonth = rawMonth
      ? monthMap[rawMonth.toLowerCase()]
      : null;

    if (currentMonth) {
      const idx = monthOrder.indexOf(currentMonth);
      const nextMonth = monthOrder[(idx + 1) % 12];
      setValue('#ctl00_MainContent_subCustom_txtMO_txtValue', nextMonth);
    }

    // YEAR
    let year = null;
    const rawYear = cleanNumber(data['year (required)']);
    if (rawYear) {
      const parsed = parseInt(rawYear, 10);
      if (!isNaN(parsed)) year = parsed;
    }

    if (year !== null && currentMonth === 'DEC') year++;
    if (year !== null) {
      setValue(
        '#ctl00_MainContent_subCustom_txtYR_txtValue',
        year.toString()
      );
    }

    // DATE
    const startDate =
      data['start of 1 1 service (required)'] ??
      data['start of 11 service (required)'];

    setTimeout(() => {
      setKendoDate(
        '#ctl00_MainContent_subCustom_txtSD_txtKendoDatePicker',
        startDate
      );
    }, 400);

    // Other fields
    setValue(
      '#ctl00_MainContent_subCustom_txtDA',
      data['district authorizer (required)']
    );
    setValue(
      '#ctl00_MainContent_subCustom_txtSAN',
      data['scia aide name']
    );
    setValue(
      '#ctl00_MainContent_subCustom_txtSHR',
      data['scia aide hrs per day']
    );
    setValue(
      '#ctl00_MainContent_subCustom_txtSPC',
      data['scia aide pc #']
    );

    setValue('#ctl00_MainContent_subCustom_txtSAT_txtValue', 'DS');
    setValue('#ctl00_MainContent_subCustom_txtSST_txtValue', 'D');

    console.log('✅ Finished filling form');
    return true;
  }

  /* -------------------------------------------------- */
  /* 🚀 Startup                                        */
  /* -------------------------------------------------- */

  injectCopyButtons();

  const observer = new MutationObserver(injectCopyButtons);
  observer.observe(document.body, { childList: true, subtree: true });

})();