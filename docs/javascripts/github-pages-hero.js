const screenshotData = {
  directory: {
    src: "design/concepts/directory.png",
    alt: "Citizen Karen agency directory with search and featured official destinations",
    caption: "Verified wayfinding across 28 official federal complaint destinations.",
  },
  filing: {
    src: "design/concepts/file-with-fcc.png",
    alt: "Citizen Karen FCC complaint form with explicit consent and privacy guidance",
    caption: "Guided filing with progressive disclosure and consent captured before submission.",
  },
  tracking: {
    src: "design/concepts/track-case.png",
    alt: "Citizen Karen case tracker showing a submitted FCC complaint timeline",
    caption: "Durable receipts, visible status transitions, and local-content deletion controls.",
  },
  command: {
    src: "design/concepts/command-center.png",
    alt: "Citizen Karen Command Center with case status, upcoming actions, and telemetry",
    caption: "A unified command center for cases, reminders, failures, retries, and escalation.",
  },
};

const tabs = Array.from(document.querySelectorAll("[data-shot]"));
const image = document.querySelector("#showcase-image");
const caption = document.querySelector("#showcase-caption");
const basePath = new URL(".", document.baseURI).pathname;

function selectScreenshot(tab) {
  const shot = screenshotData[tab.dataset.shot];
  if (!shot || !image || !caption) return;
  tabs.forEach((item) => item.setAttribute("aria-selected", String(item === tab)));
  image.src = `${basePath}${shot.src}`;
  image.alt = shot.alt;
  caption.textContent = shot.caption;
}

tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => selectScreenshot(tab));
  tab.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") return;
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    const nextTab = tabs[(index + direction + tabs.length) % tabs.length];
    nextTab.focus();
    selectScreenshot(nextTab);
  });
});
