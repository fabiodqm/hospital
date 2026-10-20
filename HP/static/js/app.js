window.addEventListener('load', function () {
  function refreshIcons() {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  refreshIcons();

  document.querySelectorAll('textarea').forEach(function (textarea) {
    textarea.addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 420) + 'px';
    });
  });

  document.querySelectorAll('select').forEach(function (select) {
    select.dataset.enhanced = 'true';
  });

  function setTheme(theme) {
    var safeTheme = theme === 'light' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', safeTheme);
    localStorage.setItem('hp-theme', safeTheme);
  }

  document.querySelectorAll('[data-theme-set]').forEach(function (button) {
    button.addEventListener('click', function () {
      setTheme(button.getAttribute('data-theme-set'));
      var menu = button.closest('.dropdown-menu');
      if (menu) menu.classList.add('hidden');
    });
  });

  document.querySelectorAll('[data-theme-toggle]').forEach(function (button) {
    button.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  });

  document.querySelectorAll('[data-dropdown-toggle]').forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.stopPropagation();
      var id = button.getAttribute('data-dropdown-toggle');
      var menu = document.getElementById(id);
      if (!menu) return;
      var shouldOpen = menu.classList.contains('hidden');
      document.querySelectorAll('.dropdown-menu').forEach(function (item) {
        item.classList.add('hidden');
      });
      menu.classList.toggle('hidden', !shouldOpen);
      button.setAttribute('aria-expanded', String(shouldOpen));
    });
  });

  document.addEventListener('click', function () {
    document.querySelectorAll('.dropdown-menu').forEach(function (item) {
      item.classList.add('hidden');
    });
    document.querySelectorAll('[data-dropdown-toggle]').forEach(function (button) {
      button.setAttribute('aria-expanded', 'false');
    });
  });
});

// Landing/menu polish for Centro Médico SHINE.
window.addEventListener('load', function () {
  if (window.lucide) window.lucide.createIcons();

  document.querySelectorAll('.landing-nav a').forEach(function (link) {
    link.addEventListener('click', function () {
      document.querySelectorAll('.landing-nav a').forEach(function (item) { item.classList.remove('active'); });
      link.classList.add('active');
    });
  });

  var revealItems = document.querySelectorAll('.reveal-on-scroll, .shine-chapter, .shine-about-quote, .shine-stat-ribbon');
  if ('IntersectionObserver' in window && revealItems.length) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.18 });
    revealItems.forEach(function (item) { observer.observe(item); });
  } else {
    revealItems.forEach(function (item) { item.classList.add('is-visible'); });
  }
});


// Landing: mantém o menu sincronizado no scroll e evita o usuário se perder.
window.addEventListener('load', function () {
  var links = Array.prototype.slice.call(document.querySelectorAll('.landing-nav a[href^="#"]'));
  var sections = links
    .map(function (link) { return document.querySelector(link.getAttribute('href')); })
    .filter(Boolean);

  function setActive(hash) {
    links.forEach(function (link) {
      link.classList.toggle('active', link.getAttribute('href') === hash);
    });
  }

  links.forEach(function (link) {
    link.addEventListener('click', function () {
      setActive(link.getAttribute('href'));
    });
  });

  if ('IntersectionObserver' in window && sections.length) {
    var navObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          setActive('#' + entry.target.id);
        }
      });
    }, { rootMargin: '-35% 0px -55% 0px', threshold: 0.01 });

    sections.forEach(function (section) { navObserver.observe(section); });
  }
});
