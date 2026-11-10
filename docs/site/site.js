/* Static product page. No API calls, credentials, analytics or simulated model execution. */
(() => {
  "use strict";
  const $ = (selector) => document.querySelector(selector);
  const dialog = $("#demo-dialog");
  let demoOpener;
  $("[data-open-demo]").addEventListener("click", (event) => {
    demoOpener = event.currentTarget;
    dialog.showModal();
  });
  document.querySelectorAll("[data-close-demo]").forEach((control) => {
    control.addEventListener("click", () => dialog.close());
  });
  dialog.addEventListener("close", () =>
    demoOpener?.focus({ preventScroll: true }),
  );
  dialog.addEventListener("click", (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (
      event.clientX < rect.left ||
      event.clientX > rect.right ||
      event.clientY < rect.top ||
      event.clientY > rect.bottom
    )
      dialog.close();
  });

  $("[data-load-film]").addEventListener("click", async (event) => {
    const frame = event.currentTarget.parentElement;
    const player = $("#film-template").content.cloneNode(true);
    frame.replaceChildren(player);
    const video = frame.querySelector("video");
    video.tabIndex = 0;
    video.focus({ preventScroll: true });
    try {
      await video.play();
    } catch {
      /* Native controls and the YouTube fallback remain available. */
    }
  });

  const copy = $("[data-copy]");
  let copyTimer;
  copy.addEventListener("click", async () => {
    const status = $("[data-copy-status]");
    try {
      await navigator.clipboard.writeText(copy.dataset.copy);
      $(".copy-label").textContent = "Copied ✓";
      status.textContent = "Install command copied to clipboard.";
      clearTimeout(copyTimer);
      copyTimer = setTimeout(() => {
        $(".copy-label").textContent = "Copy ⧉";
      }, 2200);
    } catch {
      status.textContent =
        "Clipboard unavailable. Select and copy the visible command.";
      $(".copy-label").textContent = "Select";
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(copy.querySelector("code"));
      selection.removeAllRanges();
      selection.addRange(range);
    }
  });

  const captures = [
    {
      image: "policy.webp",
      original: "02-policy-evidence.jpg",
      title: "Understand why the order was held.",
      description:
        "Incoming values and the approved reference sit beside the deterministic outcome. A critical contradiction cannot be approved through review.",
      alt: "Policy evidence for the recorded unsupported 20 CASE order.",
    },
    {
      image: "agent.webp",
      original: "03-native-agent.jpg",
      title: "Inspect the evidence behind the proposal.",
      description:
        "The recorded recommendation includes actual case-scoped tool reads. Evidence is inspectable; the recommendation does not authorize delivery.",
      alt: "Recorded native agent recommendation with case-scoped tool reads.",
    },
    {
      image: "review.webp",
      original: "04-workflow-review.jpg",
      title: "See the boundary of human review.",
      description:
        "The native Workflow task remains visible. This critical case cannot be approved; no review decision was submitted while making the capture.",
      alt: "Native Workflow review task for a critical case, with approval disabled.",
    },
    {
      image: "trace.webp",
      original: "07-provider-native-metadata.jpg",
      title: "Read the provider exchange in its business session.",
      description:
        "Persisted native Body properties include model, provider, prompt version, recorded mode, timing and tool call. Replay usage and cost are not new inference.",
      alt: "Native Visual Trace Body properties for the recorded provider response.",
    },
  ];
  const tabs = [...document.querySelectorAll("[data-tour-index]")];
  function selectCapture(index, focus = false) {
    const selected = captures[index];
    tabs.forEach((tab, i) => {
      tab.setAttribute("aria-selected", String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
    });
    const image = $("#tour-image");
    image.src = `assets/${selected.image}`;
    image.alt = selected.alt;
    image.parentElement.classList.toggle("is-trace", index === 3);
    $("#tour-title").textContent = selected.title;
    $("#tour-description").textContent = selected.description;
    $("#tour-original").href = `assets/${selected.original}`;
    $("#tour-panel").setAttribute("aria-labelledby", tabs[index].id);
    if (focus) {
      tabs[index].focus({ preventScroll: true });
      tabs[index].scrollIntoView({
        block: "nearest",
        inline: "nearest",
        behavior: "instant",
      });
    }
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => selectCapture(index));
    tab.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight" || event.key === "ArrowDown")
        next = (index + 1) % tabs.length;
      if (event.key === "ArrowLeft" || event.key === "ArrowUp")
        next = (index + tabs.length - 1) % tabs.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = tabs.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      selectCapture(next, true);
    });
  });

  const media = matchMedia("(prefers-reduced-motion: reduce)");
  const motionButton = $("[data-motion-toggle]");
  let paused = false;
  let context;
  let split;
  let match;
  let magneticCleanup = [];
  function configureMotion() {
    context?.revert();
    split?.revert();
    match?.revert();
    magneticCleanup.forEach((cleanup) => cleanup());
    magneticCleanup = [];
    $(".story-shell").classList.remove("pinned-mode");
    const disabled = paused || media.matches;
    document.documentElement.dataset.motion = disabled ? "paused" : "enabled";
    motionButton.setAttribute("aria-pressed", String(disabled));
    motionButton.innerHTML = disabled
      ? 'Motion off <span aria-hidden="true">▶</span>'
      : 'Pause motion <span aria-hidden="true">Ⅱ</span>';
    if (disabled || !window.gsap || !window.ScrollTrigger || !window.SplitText)
      return;
    gsap.registerPlugin(ScrollTrigger, SplitText);
    context = gsap.context(() => {
      split = SplitText.create(".hero-title", {
        type: "words",
        wordsClass: "hero-word",
        aria: "auto",
      });
      gsap.from(split.words, {
        y: 18,
        opacity: 0,
        duration: 0.65,
        stagger: 0.055,
        ease: "power3.out",
      });
      gsap.from(".hero-visual", {
        y: 20,
        opacity: 0,
        duration: 0.8,
        ease: "power3.out",
        delay: 0.12,
      });
      gsap.from(".caption-rule", {
        scaleY: 0,
        duration: 0.6,
        delay: 0.4,
        ease: "power2.out",
      });
      gsap.utils.toArray(".reveal").forEach((element) => {
        gsap.from(element, {
          y: 16,
          opacity: 0,
          duration: 0.55,
          ease: "power2.out",
          scrollTrigger: { trigger: element, start: "top 94%", once: true },
        });
      });
    });
    match = gsap.matchMedia();
    match.add("(min-width: 960px)", () => {
      const shell = $(".story-shell");
      shell.classList.add("pinned-mode");
      const panels = gsap.utils.toArray(".story-panel");
      gsap.set(panels.slice(1), { opacity: 0, y: 20 });
      const timeline = gsap.timeline({
        scrollTrigger: {
          trigger: shell,
          start: "top 55px",
          end: () => `+=${innerHeight * 1.8}`,
          pin: ".story-stage",
          scrub: 0.5,
          invalidateOnRefresh: true,
        },
      });
      timeline.to({}, { duration: 0.3 });
      timeline.to(panels[0], { opacity: 0, y: -14, duration: 0.25 });
      timeline.to(panels[1], { opacity: 1, y: 0, duration: 0.35 }, "<");
      timeline.to(".story-progress i", { scaleX: 0.667, duration: 0.35 }, "<");
      timeline.to({}, { duration: 0.4 });
      timeline.to(panels[1], { opacity: 0, y: -14, duration: 0.25 });
      timeline.to(panels[2], { opacity: 1, y: 0, duration: 0.35 }, "<");
      timeline.to(".story-progress i", { scaleX: 1, duration: 0.35 }, "<");
      timeline.to({}, { duration: 0.4 });
      return () => shell.classList.remove("pinned-mode");
    });
    if (matchMedia("(hover: hover) and (pointer: fine)").matches) {
      document.querySelectorAll(".magnetic").forEach((button) => {
        const move = (event) => {
          const rect = button.getBoundingClientRect();
          gsap.to(button, {
            x: ((event.clientX - rect.left) / rect.width - 0.5) * 6,
            y: ((event.clientY - rect.top) / rect.height - 0.5) * 6,
            duration: 0.25,
            ease: "power2.out",
            overwrite: true,
          });
        };
        const leave = () =>
          gsap.to(button, {
            x: 0,
            y: 0,
            duration: 0.3,
            ease: "power2.out",
            overwrite: true,
          });
        button.addEventListener("pointermove", move);
        button.addEventListener("pointerleave", leave);
        magneticCleanup.push(() => {
          button.removeEventListener("pointermove", move);
          button.removeEventListener("pointerleave", leave);
          gsap.set(button, { clearProps: "transform" });
        });
      });
    }
    ScrollTrigger.refresh();
  }
  motionButton.addEventListener("click", () => {
    paused = !paused;
    configureMotion();
  });
  media.addEventListener("change", configureMotion);
  configureMotion();
})();
