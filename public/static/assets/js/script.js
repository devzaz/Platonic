// script.js
document.addEventListener("DOMContentLoaded", () => {
  const tl = gsap.timeline({ paused: true });
  const sidebar = document.getElementById("sidebarNav");
  const panel = sidebar.querySelector(".sidebar-nav__panel");
  const overlay = sidebar.querySelector(".sidebar-nav__overlay");

  tl.set(sidebar, { pointerEvents: "auto" })
    .to(overlay, { opacity: 1, duration: 0.3 }, 0)
    .to(panel, { x: "-300px", duration: 0.4, ease: "power3.out" }, 0);

  document.getElementById("menuToggle").addEventListener("click", () => {
    tl.play();
  });

  document.getElementById("menuClose").addEventListener("click", () => {
    tl.reverse();
  });

  overlay.addEventListener("click", () => {
    tl.reverse();
  });

  // GSAP hero text animation (same as before)
  gsap.from(".hero__headline", {
    y: 80,
    opacity: 0,
    duration: 1.2,
    ease: "power4.out",
  });

  gsap.from(".hero__subhead", {
    y: 20,
    opacity: 0,
    duration: 1,
    ease: "power2.out",
    delay: 0.4,
  });

  gsap.from(".hero__cta", {
    scale: 0.9,
    opacity: 1,
    duration: 0.8,
    ease: "back.out(1.7)",
    delay: 0.8,
  });
});

const heroSwiper = new Swiper(".hero.swiper", {
  loop: true,
  autoplay: {
    delay: 7000,
    disableOnInteraction: false,
  },
  effect: "fade",
  fadeEffect: {
    crossFade: true,
  },
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
});

// Scroll fade-in
const scrollFadeEls = document.querySelectorAll(".scroll-fade");

const fadeObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
      }
    });
  },
  { threshold: 0.2 }
);

scrollFadeEls.forEach((el) => fadeObserver.observe(el));

const aboutBoxes = document.querySelectorAll(".about-box");

const scrollReveal = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      const dir = entry.target.getAttribute("data-anim") || "bottom";

      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";

        if (dir === "left") entry.target.style.transform = "translateX(0)";
        else if (dir === "right")
          entry.target.style.transform = "translateX(0)";
        else if (dir === "top") entry.target.style.transform = "translateY(0)";
        else entry.target.style.transform = "translateY(0)";
      }
    });
  },
  { threshold: 0.25 }
);

aboutBoxes.forEach((box) => {
  const dir = box.getAttribute("data-anim") || "bottom";

  if (dir === "left") box.style.transform = "translateX(-60px)";
  else if (dir === "right") box.style.transform = "translateX(60px)";
  else if (dir === "top") box.style.transform = "translateY(-60px)";
  else box.style.transform = "translateY(60px)";

  scrollReveal.observe(box);
});

const philosophyCards = document.querySelectorAll(".philosophy-card");

window.addEventListener("scroll", () => {
  const triggerBottom = window.innerHeight * 0.9;

  philosophyCards.forEach((card) => {
    const top = card.getBoundingClientRect().top;
    if (top < triggerBottom) {
      const delay = card.getAttribute("data-delay");
      setTimeout(() => {
        card.style.transform = "translateY(0)";
        card.style.opacity = "1";
      }, delay);
    }
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const track = document.querySelector(".modular-track");
  const modules = document.querySelectorAll(".module");
  const section = document.getElementById("studioJourney");

  let ticking = false;

  function handleScroll() {
    const rect = section.getBoundingClientRect();
    const windowHeight = window.innerHeight;

    if (rect.top < windowHeight && rect.bottom > 0) {
      const progress = (windowHeight - rect.top) / (windowHeight + rect.height);
      const maxScroll = track.scrollWidth - window.innerWidth;
      track.style.transform = `translateX(-${progress * maxScroll}px)`;
    }
  }

  const observer = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const module = entry.target;
          const delay = module.getAttribute("data-delay") || 0;
          setTimeout(() => {
            module.style.opacity = "1";
            module.style.transform = "translateY(0) rotateX(0deg)";
          }, delay);
          observer.unobserve(module);
        }
      });
    },
    { threshold: 0.15 }
  );

  modules.forEach((module) => {
    module.style.opacity = "0";
    module.style.transform = "translateY(30px) rotateX(20deg)";
    observer.observe(module);
  });

  window.addEventListener("scroll", () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        handleScroll();
        ticking = false;
      });
      ticking = true;
    }
  });

  // Initialize on load
  handleScroll();
});

document.addEventListener("DOMContentLoaded", () => {
  const items = document.querySelectorAll(".insight");

  const reveal = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        const delay = parseInt(el.dataset.delay) || 0;
        setTimeout(() => {
          el.classList.add("visible");
        }, delay);
        reveal.unobserve(el);
      });
    },
    { threshold: 0.3 }
  );

  items.forEach((item) => reveal.observe(item));
});

//new

document.addEventListener("DOMContentLoaded", () => {
  const reveals = document.querySelectorAll(".reveal");

  function revealOnScroll() {
    for (let el of reveals) {
      const windowHeight = window.innerHeight;
      const elementTop = el.getBoundingClientRect().top;
      const revealPoint = 150;

      if (elementTop < windowHeight - revealPoint) {
        el.classList.add("active");
      }
    }
  }

  window.addEventListener("scroll", revealOnScroll);
});

//new

document.addEventListener("DOMContentLoaded", () => {
  const section = document.getElementById("materialsProcess");
  const slider = section.querySelector(".ps-slider");
  const panels = section.querySelectorAll(".ps-panel");
  const header = section.querySelector(".ps-header");
  let currentPanel = -1;

  // Entrance reveal via IntersectionObserver
  const panelObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          panelObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.3 }
  );

  panels.forEach((panel) => {
    panelObserver.observe(panel);
  });

  // Track scroll to slide panel
  window.addEventListener("scroll", () => {
    const rect = section.getBoundingClientRect();
    const scrollProgress = Math.min(
      Math.max(
        (window.innerHeight - rect.top) / (rect.height + window.innerHeight),
        0
      ),
      1
    );
    const index = Math.min(
      Math.floor(scrollProgress * panels.length),
      panels.length - 1
    );

    if (index !== currentPanel) {
      currentPanel = index;
      slider.style.transform = `translateX(-${index * 100}vw)`;
      const content = panels[index].querySelector(".ps-content");
      setTimeout(() => {
        content.classList.add("content-visible");
      }, 400);
    }

    // Parallax bg images
    panels.forEach((p, i) => {
      const bg = p.querySelector(".ps-bg");
      const depth = (i + 1) * 10;
      bg.style.transform = `translateY(${scrollProgress * depth}px)`;
    });
  });
});

//new
document.addEventListener("DOMContentLoaded", () => {
  const mediaElems = document.querySelectorAll(".media-section [data-animate]");

  mediaElems.forEach((el, i) => {
    gsap.from(el, {
      opacity: 0,
      y: 60,
      duration: 1.2,
      ease: "power3.out",
      delay: i * 0.2,
      scrollTrigger: {
        trigger: el,
        start: "top 85%",
      },
    });
  });
});

//new

document.addEventListener("DOMContentLoaded", () => {
  const testimonialBlocks = document.querySelectorAll(
    ".testimonial-section [data-animate]"
  );

  testimonialBlocks.forEach((el, i) => {
    gsap.from(el, {
      opacity: 0,
      y: 40,
      duration: 1.2,
      delay: i * 0.3,
      ease: "power3.out",
      scrollTrigger: {
        trigger: el,
        start: "top 85%",
      },
    });
  });
});

//new

document.addEventListener("DOMContentLoaded", () => {
  const ctaElements = document.querySelectorAll(".cta-section [data-animate]");

  ctaElements.forEach((el, i) => {
    gsap.from(el, {
      opacity: 0,
      y: 40,
      duration: 1.2,
      delay: i * 0.2,
      ease: "power3.out",
      scrollTrigger: {
        trigger: el,
        start: "top 80%",
      },
    });
  });
});

//new
document.addEventListener("DOMContentLoaded", () => {
  const footerItems = document.querySelectorAll(
    ".footer-complex [data-animate]"
  );

  footerItems.forEach((el, i) => {
    gsap.from(el, {
      opacity: 0,
      y: 50,
      duration: 1.2,
      delay: i * 0.2,
      ease: "power3.out",
      scrollTrigger: {
        trigger: el,
        start: "top 85%",
      },
    });
  });

  // Optional magnetic link hover
  const navLinks = document.querySelectorAll(".footer-nav a");
  navLinks.forEach((link) => {
    link.addEventListener("mousemove", (e) => {
      const rect = link.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      gsap.to(link, {
        x: x * 0.15,
        y: y * 0.3,
        duration: 0.3,
        ease: "power3.out",
      });
    });

    link.addEventListener("mouseleave", () => {
      gsap.to(link, {
        x: 0,
        y: 0,
        duration: 0.4,
        ease: "power3.out",
      });
    });
  });
});
