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
      .navbar .indog-brand-link{display:flex!important;align-items:center!important;justify-content:flex-start!important;width:70px!important;height:64px!important;flex:0 0 70px!important;overflow:visible!important}
      .navbar .indog-brand-logo{display:block;width:62px;height:62px;object-fit:cover;border-radius:50%;box-shadow:0 4px 14px rgba(43,27,20,.14);border:1px solid rgba(185,107,44,.35)}
      body.indog-menu-open,body.indog-cart-open{overflow:hidden}

      /* Mini pedido — visual premium, mantendo a lógica existente */
      .cart-overlay{background:rgba(43,27,20,.42)!important;backdrop-filter:blur(5px);-webkit-backdrop-filter:blur(5px);transition:opacity .25s ease!important}
      .cart-panel{background:#fbf6ef!important;color:#2b1b14!important;border-left:1px solid #e8ddd1!important;box-shadow:-30px 0 80px rgba(43,27,20,.18)!important}
      .cart-panel-header{background:rgba(255,253,249,.96)!important;border-bottom:1px solid #e8ddd1!important;padding:22px!important}
      .cart-panel-title{font-family:Georgia,'Times New Roman',serif!important;color:#2b1b14!important;letter-spacing:-.02em}
      .cart-panel-sub{color:#806d60!important}
      .cart-close-btn{border:1px solid #e8ddd1!important;background:#fffdf9!important;color:#5d4638!important;border-radius:50%!important;width:38px!important;height:38px!important}
      .cart-items-list{padding:14px!important}
      .cart-item{background:#fffdf9!important;border:1px solid #e8ddd1!important;border-radius:18px!important;box-shadow:0 8px 24px rgba(61,38,23,.05)!important;padding:12px!important;margin-bottom:10px!important}
      .cart-item-img{border-radius:12px!important;background:#f3e9dd!important;overflow:hidden}
      .cart-item-name{color:#2b1b14!important;font-weight:800!important}
      .cart-item-price{color:#8d4c1e!important;font-weight:900!important}
      .cart-item-ctrls{align-items:center!important}
      .cart-qty-btn,.cart-remove-btn{border:1px solid #e8ddd1!important;background:#fff!important;color:#5d4638!important;border-radius:10px!important}
      .cart-remove-btn{border-radius:50%!important}
      .cart-footer{background:#fffdf9!important;border-top:1px solid #e8ddd1!important;padding:16px!important}
      .cart-customer-section{border:1px solid #e8ddd1!important;border-radius:16px!important;background:#fbf6ef!important;overflow:hidden}
      .cart-customer-summary{color:#5d4638!important;padding:13px 14px!important}
      .cart-customer-body{padding:0 14px 14px!important}
      .cart-field{border:1px solid #dfd1c4!important;background:#fffdf9!important;border-radius:11px!important;color:#2b1b14!important}
      .cart-field:focus{border-color:#b96b2c!important;box-shadow:0 0 0 3px rgba(185,107,44,.1)!important;outline:0!important}
      #cart-send-wa{background:#23804d!important;border-radius:999px!important;box-shadow:0 12px 28px rgba(35,128,77,.18)!important;font-weight:900!important}
      #cart-clear{color:#8d4c1e!important}
      .cart-empty{color:#806d60!important;padding:42px 24px!important}
      .cart-empty-icon{filter:saturate(.7)!important}
      .cart-toast{background:#2b1b14!important;border:1px solid rgba(255,255,255,.08)!important;border-radius:999px!important;box-shadow:0 18px 50px rgba(43,27,20,.22)!important}

      @media(max-width:640px){
        .navbar #mobile-menu{left:8px;right:8px}
        .navbar #mobile-menu .grid{grid-template-columns:1fr!important}
        .navbar .nav-search{min-width:0}
        .navbar .logo-sub{letter-spacing:.1em!important}
        .navbar .btn-whatsapp-nav{display:none!important}
        .navbar .indog-brand-link{width:58px!important;height:56px!important;flex-basis:58px!important}
        .navbar .indog-brand-logo{width:54px;height:54px}
        .cart-panel{width:min(100vw,430px)!important;max-width:100vw!important}
        .cart-panel-header{padding:18px 16px!important}
        .cart-items-list{padding:12px!important}
      }
      @media(min-width:641px) and (max-width:1279px){.navbar #mobile-menu{left:16px;right:16px}}
      @media(prefers-reduced-motion:reduce){.navbar,.navbar #menu-toggle svg,.cart-overlay{transition:none!important}}
    `;
    document.head.appendChild(style);
  }

  function setupBrandingAssets() {
    const logoUrl = '/static/images/indog/indog-logo.jpg';

    let favicon = document.querySelector('link[rel="icon"]');
    if (!favicon) {
      favicon = document.createElement('link');
      favicon.rel = 'icon';
      document.head.appendChild(favicon);
    }
    favicon.type = 'image/jpeg';
    favicon.href = logoUrl;

    let shortcut = document.querySelector('link[rel="shortcut icon"]');
    if (!shortcut) {
      shortcut = document.createElement('link');
      shortcut.rel = 'shortcut icon';
      document.head.appendChild(shortcut);
    }
    shortcut.type = 'image/jpeg';
    shortcut.href = logoUrl;

    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    const brand = navbar.querySelector('a[href="/"]') || navbar.querySelector('a');
    if (!brand || brand.querySelector('.indog-brand-logo')) return;

    brand.classList.add('indog-brand-link');
    brand.setAttribute('aria-label', 'In Dog - We Trust Pet Boutique');
    brand.innerHTML = `<img class="indog-brand-logo" src="${logoUrl}" alt="In Dog - We Trust Pet Boutique">`;
  }

  function setMultilineText(element, value) {
    if (!element || !value) return;
    element.textContent = '';
    String(value).split(/\r?\n/).forEach((line, index) => {
      if (index) element.appendChild(document.createElement('br'));
      element.appendChild(document.createTextNode(line));
    });
  }

  function addPrivacyLinks() {
    const privacyHref = '/politica-de-privacidade/';

    const linksHeading = Array.from(document.querySelectorAll('.footer-col-title'))
      .find(el => el.textContent.trim().toLowerCase() === 'links úteis');
    const linksList = linksHeading?.nextElementSibling;
    if (linksList && !linksList.querySelector(`a[href="${privacyHref}"]`)) {
      const li = document.createElement('li');
      li.innerHTML = `<a href="${privacyHref}" class="footer-link"><span class="footer-arrow">›</span>Política de Privacidade</a>`;
      linksList.appendChild(li);
    }

    const privacyNote = document.querySelector('.cart-privacy-note');
    if (privacyNote && !privacyNote.querySelector(`a[href="${privacyHref}"]`)) {
      privacyNote.appendChild(document.createTextNode(' '));
      const link = document.createElement('a');
      link.href = privacyHref;
      link.textContent = 'Ver política de privacidade';
      link.style.color = '#8d4c1e';
      link.style.textDecoration = 'underline';
      privacyNote.appendChild(link);
    }
  }

  async function syncPublicStoreInfo() {
    try {
      const response = await fetch('/loja/info/', {
        credentials: 'same-origin',
        headers: { 'Accept': 'application/json' },
      });
      if (!response.ok) return;
      const data = await response.json();

      if (data.opening_hours) {
        document.querySelectorAll('.footer-contact-item').forEach(item => {
          const label = item.querySelector('.footer-contact-label');
          if (label?.textContent.trim().toLowerCase() === 'atendimento') {
            setMultilineText(item.querySelector('.footer-contact-text'), data.opening_hours);
          }
        });
      }

      if (data.phone_number) {
        const navPhone = document.querySelector('.nav-phone strong');
        if (navPhone) navPhone.textContent = data.phone_number;
      }
    } catch (_) {}
  }

  function setupProductionReadiness() {
    // A página de Medicamentos já existe; links antigos de busca são normalizados
    // para a experiência correta de consulta e catálogo relacionado.
    document.querySelectorAll('a[href*="?q=medicamentos"]').forEach(link => {
      link.setAttribute('href', '/medicamentos/');
    });

    addPrivacyLinks();
    syncPublicStoreInfo();
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

  function syncBodyLock() {
    const panel = document.getElementById('cart-panel');
    if (!panel) return;
    const observer = new MutationObserver(() => {
      document.body.classList.toggle('indog-cart-open', panel.classList.contains('open'));
    });
    observer.observe(panel, { attributes: true, attributeFilter: ['class'] });
  }

  document.addEventListener('DOMContentLoaded', () => {
    injectNavigationPolish();
    setupBrandingAssets();
    setupProductionReadiness();

    setupNavbarScroll();
    setupMobileMenu();
    setupInteractions();
    syncBodyLock();

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
