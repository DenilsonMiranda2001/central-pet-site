// ── In Dog — Main JS ──

(function() {
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
    return Object.fromEntries(
      Object.entries(payload || {}).filter(([, value]) => value !== undefined && value !== null && value !== '')
    );
  }

  window.InDogInteractions = {
    track(payload) {
      const body = JSON.stringify(cleanPayload(payload));
      try {
        fetch(endpoint(), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken(),
          },
          body,
          keepalive: true,
          credentials: 'same-origin',
        }).catch(() => {});
      } catch (error) {
        // Tracking must never block the customer flow.
      }
    }
  };
})();

document.addEventListener('DOMContentLoaded', () => {

  // Navbar scroll effect
  const navbar = document.getElementById('navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 60) navbar.classList.add('scrolled');
      else navbar.classList.remove('scrolled');
    }, { passive: true });
  }

  // Mobile menu toggle
  const menuToggle = document.getElementById('menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!menuToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.add('hidden');
      }
    });
  }

  // Fade-up intersection observer
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

  // Active nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      link.classList.add('active');
    }
  });

  // WhatsApp button — encode URI
  document.querySelectorAll('[data-whatsapp]').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const number = this.dataset.whatsapp;
      const msg = this.dataset.message || '';
      const url = `https://wa.me/${number}?text=${encodeURIComponent(msg)}`;
      window.open(url, '_blank', 'noopener');
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

  // Lazy load images (native)
  document.querySelectorAll('img[data-src]').forEach(img => {
    img.setAttribute('loading', 'lazy');
    img.src = img.dataset.src;
  });

  // Product image placeholder
  document.querySelectorAll('.product-img').forEach(img => {
    img.addEventListener('error', function() {
      this.parentElement.innerHTML = '<div class="product-img-placeholder">🐾</div>';
    });
  });

});
