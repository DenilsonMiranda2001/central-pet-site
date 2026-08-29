// In Dog — Main JS
(function() {
  'use strict';

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }

  function csrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content || getCookie('csrftoken');
  }

  function endpoint() {
    return document.querySelector('meta[name="interaction-endpoint"]')?.content || '/interacoes/registrar/';
  }

  function cleanPayload(payload) {
    return Object.fromEntries(Object.entries(payload || {}).filter(([, value]) => value !== undefined && value !== null && value !== ''));
  }

  window.InDogInteractions = {
    track(payload) {
      const body = JSON.stringify(cleanPayload(payload));
      try {
        fetch(endpoint(), { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() }, body, keepalive: true, credentials: 'same-origin' }).catch(() => {});
      } catch (_) {}
    }
  };

  function injectNavigationPolish() {
    if (document.getElementById('indog-nav-polish')) return;
    const style = document.createElement('style');
    style.id = 'indog-nav-polish';
    style.textContent = `
      .navbar{transition:background .28s ease,box-shadow .28s ease,transform .28s ease!important}
      .navbar #mobile-menu{position:absolute;left:12px;right:12px;top:calc(100% + 10px);padding:12px!important;border:1px solid #e8ddd1;border-radius:22px;background:rgba(255,253,249,.98);box-shadow:0 24px 70px rgba(43,27,20,.14);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);max-height:calc(100vh - 92px);overflow:auto}
      .navbar #mobile-menu.hidden{display:none!important}
      .navbar #mobile-menu .grid{gap:8px!important}
      .navbar #mobile-menu .mobile-nav-link{min-height:46px;justify-content:flex-start;padding:11px 12px!important;border-color:#e8ddd1!important;background:#fffdf9!important;transition:background .2s ease,color .2s ease,transform .2s ease}
      .navbar #mobile-menu .mobile-nav-link:hover{transform:translateY(-1px);background:#f6eee6!important}
      .navbar #menu-toggle{width:42px;height:42px;display:inline-flex;align-items:center;justify-content:center;border:1px solid #e8ddd1;border-radius:50%;background:#fffdf9;position:relative}
      .navbar #menu-toggle svg{transition:transform .2s ease}
      .navbar #menu-toggle[aria-expanded="true"] svg{transform:rotate(90deg)}
      .navbar .cart-toggle-btn{position:relative;width:42px;height:42px;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 5px 16px rgba(43,27,20,.06)}
      .navbar .cart-count{position:absolute!important;right:-2px;top:-3px;min-width:17px;height:17px;padding:0 4px;border-radius:999px;background:#2b1b14!important;color:#fff!important;border:2px solid #fbf6ef;font-size:9px;font-weight:900;align-items:center;justify-content:center}
      .navbar .logo-mark:after{content:""}
      .navbar .nav-search{box-shadow:0 6px 20px rgba(43,27,20,.04)}
      body.indog-menu-open{overflow:hidden}
      @media(max-width:640px){.navbar #mobile-menu{left:8px;right:8px}.navbar #mobile-menu .grid{grid-template-columns:1fr!important}.navbar .nav-search{min-width:0}.navbar .logo-sub{letter-spacing:.1em!important}.navbar .btn-whatsapp-nav{display:none!important}}
      @media(min-width:641px) and (max-width:1279px){.navbar #mobile-menu{left:16px;right:16px}}
      @media(prefers-reduced-motion:reduce){.navbar,.navbar #menu-toggle svg{transition:none!important}}
    `;
    document.head.appendChild(style);
  }

  function setupMobileMenu() {
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    if (!menuToggle || !mobileMenu) return;

    menuToggle.setAttribute('aria-expanded', mobileMenu.classList.contains('hidden') ? 'false' : 'true');
    menuToggle.setAttribute('aria-controls', 'mobile-menu');

    const close = () => {
      mobileMenu.classList.add('hidden');
      menuToggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('indog-menu-open');
    };

    menuToggle.addEventListener('click', (event) => {
      event.stopPropagation();
      const willOpen = mobileMenu.classList.contains('hidden');
      if (willOpen) {
        mobileMenu.classList.remove('hidden');
        menuToggle.setAttribute('aria-expanded', 'true');
        document.body.classList.add('indog-menu-open');
      } else close();
    });

    mobileMenu.addEventListener('click', (event) => {
      const link = event.target.closest('a');
      if (link) close();
    });

    document.addEventListener('click', (event) => {
      if (!mobileMenu.contains(event.target) && !menuToggle.contains(event.target)) close();
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') close();
    });
  }

  function setupNavbarScroll() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;
    const update = () => navbar.classList.toggle('scrolled', window.scrollY > 40);
    update();
    window.addEventListener('scroll', update, { passive: true });
  }

  function setupInteractions() {
    document.querySelectorAll('[data-whatsapp]').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        const number = this.dataset.whatsapp;
        const msg = this.dataset.message || '';
        window.open(`https://wa.me/${number}?text=${encodeURIComponent(msg)}`, '_blank', 'noopener');
      });
    });

    document.querySelectorAll('[data-interaction-type]').forEach(link => {
      link.addEventListener('click', function() {
        window.InDogInteractions.track({
          tipo: this.dataset.interactionType,
          produto_id: this.dataset.productId || '',
          servico_id: this.dataset.serviceId || '',
          nome_produto: this.dataset.productName || '',
          nome_servico: this.dataset.serviceName || '',
        });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    injectNavigationPolish();
    setupNavbarScroll();
    setupMobileMenu();
    setupInteractions();

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
      const href = link.getAttribute('href');
      if (href === currentPath || (href && href !== '/' && currentPath.startsWith(href))) link.classList.add('active');
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
      img.setAttribute('loading', 'lazy');
      img.src = img.dataset.src;
    });

    document.querySelectorAll('.product-img').forEach(img => {
      img.addEventListener('error', function() {
        this.parentElement.innerHTML = '<div class="product-img-placeholder">✦</div>';
      });
    });
  });
})();
