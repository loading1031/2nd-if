(() => {
  // design/prototype.ts
  function required(selector) {
    const element = document.querySelector(selector);
    if (!element) throw new Error(`Missing design element: ${selector}`);
    return element;
  }
  var labels = {
    insights: "\uB3C5\uC11C \uC778\uC0AC\uC774\uD2B8",
    sharing: "\uC9C0\uD45C \uACF5\uAC1C \uC124\uC815",
    books: "\uC124\uC815\uC9D1\uACFC \uC5D0\uC14B"
  };
  var previewState = required("#preview-state");
  var stateMessages = {
    loading: ["\uBD88\uB7EC\uC624\uB294 \uC911", "\uCD5C\uC2E0 \uC9D1\uACC4\uB97C \uD655\uC778\uD558\uACE0 \uC788\uC2B5\uB2C8\uB2E4."],
    empty: ["\uC544\uC9C1 \uD45C\uC2DC\uD560 \uB370\uC774\uD130\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4", "\uC77D\uAE30 \uC774\uBCA4\uD2B8\uAC00 \uC9D1\uACC4\uB418\uAC70\uB098 \uC124\uC815\uC9D1\uC744 \uCC44\uD0DD\uD558\uBA74 \uC774\uACF3\uC5D0\uC11C \uD655\uC778\uD560 \uC218 \uC788\uC2B5\uB2C8\uB2E4."],
    error: ["\uB370\uC774\uD130\uB97C \uBD88\uB7EC\uC624\uC9C0 \uBABB\uD588\uC2B5\uB2C8\uB2E4", "\uC7A0\uC2DC \uD6C4 \uB2E4\uC2DC \uC2DC\uB3C4\uD574 \uC8FC\uC138\uC694."],
    denied: ["\uC811\uADFC \uAD8C\uD55C\uC774 \uC5C6\uC2B5\uB2C8\uB2E4", "\uC774 \uD654\uBA74\uC744 \uBCFC \uC218 \uC788\uB294 \uD604\uC7AC \uAD8C\uD55C\uC744 \uD655\uC778\uD574 \uC8FC\uC138\uC694."]
  };
  function renderPreviewState() {
    const state = previewState.value;
    required("#screens").hidden = state !== "normal";
    required("#state-panel").hidden = state === "normal";
    if (state === "normal") return;
    const [title, description] = stateMessages[state];
    required("#state-title").textContent = title;
    required("#state-description").textContent = description;
    required("#state-spinner").hidden = state !== "loading";
    required("#state-retry").hidden = state !== "error";
  }
  function navigate() {
    const screen = location.hash.slice(1);
    const active = Object.prototype.hasOwnProperty.call(labels, screen) ? screen : "insights";
    document.querySelectorAll("[data-screen]").forEach((section) => {
      section.hidden = section.id !== active;
    });
    document.querySelectorAll("[data-nav]").forEach((link) => {
      const selected = link.dataset.nav === active;
      link.classList.toggle("menu-active", selected);
      if (selected) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    required("#breadcrumb").textContent = labels[active];
    previewState.value = "normal";
    renderPreviewState();
  }
  window.addEventListener("hashchange", navigate);
  previewState.addEventListener("change", renderPreviewState);
  required("#state-retry").addEventListener("click", () => {
    previewState.value = "normal";
    renderPreviewState();
  });
  document.querySelectorAll("[data-insight-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-insight-panel]").forEach((panel) => {
        panel.hidden = panel.id !== button.dataset.insightTab;
      });
      document.querySelectorAll("[data-insight-tab]").forEach((tab) => {
        tab.classList.toggle("tab-active", tab === button);
        tab.setAttribute("aria-selected", String(tab === button));
      });
    });
  });
  var periods = {
    "30": {
      starts: 2714,
      completed: 1936,
      resolved: 2481,
      dropped: 545,
      rejoins: 184,
      episodes: [["1\uD654 \xB7 \uC720\uB9AC \uC628\uC2E4", 1e3, 182], ["2\uD654 \xB7 \uC624\uB798\uB41C \uC5F4\uC1E0", 800, 180], ["3\uD654 \xB7 \uBC24\uC758 \uC190\uB2D8", 681, 183]]
    },
    "7": {
      starts: 700,
      completed: 490,
      resolved: 620,
      dropped: 130,
      rejoins: 42,
      episodes: [["1\uD654 \xB7 \uC720\uB9AC \uC628\uC2E4", 250, 45], ["2\uD654 \xB7 \uC624\uB798\uB41C \uC5F4\uC1E0", 210, 45], ["3\uD654 \xB7 \uBC24\uC758 \uC190\uB2D8", 160, 40]]
    }
  };
  required("#period").addEventListener("change", (event) => {
    const data = periods[event.currentTarget.value];
    const format = (n) => n.toLocaleString("ko-KR");
    required("#stat-starts").textContent = format(data.starts);
    required("#stat-completed").textContent = format(data.completed);
    required("#stat-dropout").textContent = `${(data.dropped / data.resolved * 100).toFixed(1)}%`;
    required("#stat-resolved").textContent = `${format(data.dropped)} / \uD310\uC815 \uC644\uB8CC ${format(data.resolved)}\uD68C`;
    required("#stat-rejoins").textContent = format(data.rejoins);
    required("#rejoin-total").textContent = format(data.rejoins);
    required("#pending-count").textContent = `\uC544\uC9C1 \uD310\uC815 \uC911\uC778 ${format(data.starts - data.resolved)}\uD68C\uB294 \uC774\uD0C8\uB960\uC5D0 \uD3EC\uD568\uB418\uC9C0 \uC54A\uC2B5\uB2C8\uB2E4.`;
    const tbody = required("#episode-rows");
    const rowTemplate = required("#episode-row-template");
    tbody.replaceChildren(...data.episodes.map(([label, resolved, dropped]) => {
      const row = rowTemplate.content.firstElementChild.cloneNode(true);
      const cells = row.querySelectorAll("th, td");
      cells[0].textContent = label;
      cells[1].textContent = format(resolved);
      cells[2].textContent = `${(dropped / resolved * 100).toFixed(1)}%`;
      return row;
    }));
    const week = event.currentTarget.value === "7";
    const times = week ? [39, 31, 54] : [42, 29, 58];
    const counts = week ? [190, 186, 181] : [756, 742, 736];
    document.querySelectorAll("[data-page-time]").forEach((element, i) => {
      element.textContent = `${times[i]}\uCD08`;
    });
    document.querySelectorAll("[data-page-count]").forEach((element, i) => {
      element.textContent = `${counts[i]}\uAC74`;
    });
    document.querySelectorAll("[data-page-progress]").forEach((element, i) => {
      element.value = times[i];
      element.setAttribute("aria-label", `${i + 1}\uCABD \uC804\uD658 \uC2DC\uAC04 ${times[i]}\uCD08`);
    });
    const traffic = week ? [["\uD648 \uCD94\uCC9C", 103, 78], ["\uC791\uAC00 \uD504\uB85C\uD544", 56, 46], ["\uAC80\uC0C9 \uACB0\uACFC", 45, 31]] : [["\uD648 \uCD94\uCC9C", 412, 312], ["\uC791\uAC00 \uD504\uB85C\uD544", 226, 184], ["\uAC80\uC0C9 \uACB0\uACFC", 180, 123]];
    const shared = week ? [["\uD648 \uCD94\uCC9C", 20600, 1030], ["\uAC80\uC0C9 \uACB0\uACFC", 6250, 438]] : [["\uD648 \uCD94\uCC9C", 82400, 4120], ["\uAC80\uC0C9 \uACB0\uACFC", 25e3, 1750]];
    renderRows("#traffic-rows", traffic.map(([name, clicks, starts]) => [name, format(clicks), format(starts)]));
    renderRows("#shared-rows", shared.map(([name, impressions, clicks]) => [name, format(impressions), format(clicks), `${(clicks / impressions * 100).toFixed(1)}%`]));
  });
  required("#episode-select").addEventListener("change", (event) => {
    const select = event.currentTarget;
    const index = select.selectedIndex;
    const week = required("#period").value === "7";
    const times = week ? [[39, 31, 54], [35, 27, 48], [44, 33, 51]][index] : [[42, 29, 58], [37, 31, 49], [46, 35, 53]][index];
    const counts = week ? [[190, 186, 181], [160, 154, 149], [131, 127, 122]][index] : [[756, 742, 736], [623, 611, 598], [504, 489, 472]][index];
    required("#episode-label").textContent = select.value.split(" \xB7 ")[0];
    document.querySelectorAll("[data-page-time]").forEach((element, i) => {
      element.textContent = `${times[i]}\uCD08`;
    });
    document.querySelectorAll("[data-page-count]").forEach((element, i) => {
      element.textContent = `${counts[i]}\uAC74`;
    });
    document.querySelectorAll("[data-page-progress]").forEach((element, i) => {
      element.value = times[i];
      element.setAttribute("aria-label", `${i + 1}\uCABD \uC804\uD658 \uC2DC\uAC04 ${times[i]}\uCD08`);
    });
  });
  function renderRows(selector, rows) {
    required(selector).replaceChildren(...rows.map((values) => {
      const row = document.createElement("tr");
      values.forEach((value, index) => {
        const cell = document.createElement("td");
        cell.textContent = value;
        if (index > 0) cell.className = "text-right";
        row.append(cell);
      });
      return row;
    }));
  }
  var visibility = () => required('input[name="visibility"]:checked').value;
  required("#sharing-form").addEventListener("change", () => {
    required("#invites-panel").hidden = visibility() !== "invited";
  });
  required("#sharing-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const names = { private: "\uC791\uAC00\uB9CC", invited: "\uCD08\uB300\uD55C \uACC4\uC815\uB9CC", public: "\uC804\uCCB4 \uACF5\uAC1C" };
    required("#sharing-status").textContent = `\uD604\uC7AC \uC800\uC7A5\uB41C \uBC94\uC704: ${names[visibility()]} (\uC2DC\uC548 \uB0B4 \uC0C1\uD0DC)`;
    toast("\uC2DC\uC548\uC5D0\uC11C \uACF5\uAC1C \uC124\uC815\uC744 \uC800\uC7A5\uD588\uC2B5\uB2C8\uB2E4.");
  });
  required("#add-invite").addEventListener("click", () => {
    const input = required("#invite-email");
    const email = input.value.trim();
    const error = required("#invite-error");
    const existing = Array.from(document.querySelectorAll("#invite-list li span")).map((span) => span.textContent);
    if (!email || !input.checkValidity() || existing.includes(email)) {
      error.textContent = existing.includes(email) ? "\uC774\uBBF8 \uCD94\uAC00\uB41C \uACC4\uC815\uC785\uB2C8\uB2E4." : "\uC720\uD6A8\uD55C \uC774\uBA54\uC77C\uC744 \uC785\uB825\uD574 \uC8FC\uC138\uC694.";
      error.hidden = false;
      return;
    }
    error.hidden = true;
    const item = required("#invite-row-template").content.firstElementChild.cloneNode(true);
    const name = item.querySelector("span");
    if (!name) throw new Error("Missing invite account label");
    name.textContent = email;
    required("#invite-list").append(item);
    input.value = "";
  });
  required("#invite-list").addEventListener("click", (event) => {
    const target = event.target;
    if (target instanceof Element) target.closest("[data-remove-invite]")?.closest("li")?.remove();
  });
  var books = {
    flora: { title: "\uBD81\uBD80\uC758 \uC2DD\uBB3C \uB3C4\uAC10", current: "v1.4", next: "v1.5", changes: "\uCD94\uAC00: \uC2DD\uBB3C \uC774\uBBF8\uC9C0 3\uAC1C. \uAE30\uC874\uC5D0 \uC120\uD0DD\uD55C \uD56D\uBAA9\uACFC \uD45C\uD604 \uC5F0\uACB0\uC744 \uC720\uC9C0\uD569\uB2C8\uB2E4.", license: "\uB77C\uC774\uC120\uC2A4: \uBB34\uB8CC \uC791\uD488 \uC774\uC6A9 \uD5C8\uC6A9 \u2192 \uB3D9\uC77C \uC870\uAC74" },
    city: { title: "\uBE44 \uC624\uB294 \uB3C4\uC2DC\uC758 \uC18C\uD488", current: "v1.0", next: "v1.1", changes: "\uAC1C\uC120: \uC6B0\uC0B0\xB7\uAC00\uB85C\uB4F1 \uC774\uBBF8\uC9C0 \uD574\uC0C1\uB3C4. \uAE30\uC874 \uC5D0\uC14B \uC2DD\uBCC4\uC790\uC640 \uD45C\uD604 \uC5F0\uACB0\uC744 \uC720\uC9C0\uD569\uB2C8\uB2E4.", license: "\uB77C\uC774\uC120\uC2A4: \uC0C1\uC5C5 \uC774\uC6A9 \uD5C8\uC6A9 \u2192 \uB3D9\uC77C \uC870\uAC74" }
  };
  var selectedBook = null;
  var updateDialog = required("#update-dialog");
  document.querySelectorAll("[data-review-update]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedBook = button.dataset.reviewUpdate ?? null;
      if (!selectedBook) return;
      const book = books[selectedBook];
      required("#update-title").textContent = book.title;
      required("#update-current").textContent = book.current;
      required("#update-next").textContent = book.next;
      required("#update-changes").textContent = book.changes;
      required("#update-license").textContent = book.license;
      updateDialog.showModal();
    });
  });
  required("#confirm-update").addEventListener("click", () => {
    if (!selectedBook) return;
    const book = books[selectedBook];
    book.current = book.next;
    required(`[data-current-version="${selectedBook}"]`).textContent = book.current;
    required(`[data-review-update="${selectedBook}"]`).hidden = true;
    required(`[data-latest="${selectedBook}"]`).hidden = false;
    if (selectedBook === "flora") required("#asset-flora-version").textContent = book.current;
    updateDialog.close();
    toast(`${book.title}\uB9CC ${book.current}\uB85C \uC5C5\uB370\uC774\uD2B8\uD588\uC2B5\uB2C8\uB2E4. (\uC2DC\uC548)`);
  });
  var assetDialog = required("#asset-dialog");
  required("#choose-asset").addEventListener("click", () => assetDialog.showModal());
  assetDialog.addEventListener("change", () => {
    required("#confirm-asset").disabled = false;
  });
  required("#confirm-asset").addEventListener("click", () => {
    const selected = required('input[name="asset-choice"]:checked');
    required("#mapping-status").textContent = `${selected.value} \uC5F0\uACB0\uB428 \xB7 \uC774 \uD45C\uD604\uC5D0\uC11C \uB3C5\uC790\uC5D0\uAC8C \uD45C\uC2DC\uB429\uB2C8\uB2E4.`;
    required("#choose-asset").textContent = "\uC5F0\uACB0 \uBCC0\uACBD";
    assetDialog.close();
  });
  required("#browse-books").addEventListener("click", () => required("#catalog-dialog").showModal());
  var toastTimer;
  function toast(message) {
    clearTimeout(toastTimer);
    required("#toast-text").textContent = message;
    required("#toast").hidden = false;
    toastTimer = setTimeout(() => {
      required("#toast").hidden = true;
    }, 4e3);
  }
  navigate();
})();
