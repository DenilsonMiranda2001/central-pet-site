// In Dog — Mini Carrinho (localStorage, sem backend)
(function () {
  'use strict';

  var KEY = 'indog_cart_v1';

  // ── Armazenamento ────────────────────────────────────────────────
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || '[]'); }
    catch (_) { return []; }
  }

  function _save(items) {
    localStorage.setItem(KEY, JSON.stringify(items));
    _badge();
    _renderPanel();
    document.dispatchEvent(new CustomEvent('indogCartChange', { detail: { items: items } }));
  }

  // ── API pública ──────────────────────────────────────────────────
  function add(product) {
    var items = load();
    var id = String(product.id);
    var idx = items.findIndex(function (i) { return String(i.id) === id; });
    if (idx >= 0) {
      items[idx].qty = Math.min(items[idx].qty + 1, 99);
    } else {
      items.push({ id: id, name: product.name, price: product.price || '', image: product.image || '', qty: 1 });
    }
    _save(items);
    _toast(product.name);
  }

  function remove(id) {
    _save(load().filter(function (i) { return String(i.id) !== String(id); }));
  }

  function setQty(id, qty) {
    var items = load();
    var idx = items.findIndex(function (i) { return String(i.id) === String(id); });
    if (idx < 0) return;
    if (qty <= 0) { remove(id); return; }
    items[idx].qty = Math.min(qty, 99);
    _save(items);
  }

  function clear() { _save([]); }

  function totalItems() {
    return load().reduce(function (s, i) { return s + i.qty; }, 0);
  }

  function buildMessage() {
    var items = load();
    if (!items.length) return '';
    var lines = items.map(function (i) {
      var p = parseFloat(i.price);
      var priceStr = p > 0 ? ' — R$ ' + p.toFixed(2).replace('.', ',') : '';
      return i.qty + 'x ' + i.name + priceStr;
    });
    var msg = 'Olá! Gostaria de fazer um pedido na In Dog. 🐾\n\n' +
      '*Itens do pedido:*\n' +
      lines.join('\n') +
      '\n\nPode confirmar disponibilidade e valores?';
    if (window.InDogCustomer) {
      var cData = _readCartCustomerFields();
      var footer = window.InDogCustomer.buildFooter(cData);
      if (footer) msg += footer;
    }
    return msg;
  }

  function sendToWhatsApp() {
    var msg = buildMessage();
    if (!msg) return;
    // Salvar dados do cliente se checkbox marcado
    if (window.InDogCustomer) {
      var cb = document.getElementById('cart-salvar-dados');
      if (cb && cb.checked) {
        var cData = _readCartCustomerFields();
        if (cData) window.InDogCustomer.save(cData);
      }
    }
    var panel = document.getElementById('cart-panel');
    var number = panel ? panel.dataset.waNumber : '';
    window.open('https://wa.me/' + number + '?text=' + encodeURIComponent(msg), '_blank', 'noopener,noreferrer');
    if (window.InDogInteractions) window.InDogInteractions.track({ tipo: 'whatsapp_geral' });
  }

  // ── Interface ────────────────────────────────────────────────────
  function _badge() {
    var badge = document.getElementById('cart-count');
    if (!badge) return;
    var n = totalItems();
    badge.textContent = n > 99 ? '99+' : String(n);
    badge.style.display = n > 0 ? 'flex' : 'none';
  }

  function _priceStr(price) {
    var n = parseFloat(price);
    return n > 0 ? 'R$ ' + n.toFixed(2).replace('.', ',') : null;
  }

  function _esc(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function _renderPanel() {
    var list = document.getElementById('cart-items-list');
    var empty = document.getElementById('cart-empty');
    var footer = document.getElementById('cart-footer');
    var totalEl = document.getElementById('cart-total');
    if (!list) return;

    var items = load();
    list.innerHTML = '';

    if (!items.length) {
      if (empty) empty.style.display = 'flex';
      if (footer) footer.style.display = 'none';
      return;
    }
    if (empty) empty.style.display = 'none';
    if (footer) footer.style.display = 'flex';

    items.forEach(function (item) {
      var price = _priceStr(item.price);
      var el = document.createElement('div');
      el.className = 'cart-item';
      el.innerHTML =
        '<div class="cart-item-img">' +
          (item.image
            ? '<img src="' + _esc(item.image) + '" alt="' + _esc(item.name) + '" loading="lazy"' +
              ' onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'">'
            : '') +
          '<div class="cart-item-img-ph" style="' + (item.image ? 'display:none' : '') + '">🐾</div>' +
        '</div>' +
        '<div class="cart-item-info">' +
          '<p class="cart-item-name">' + _esc(item.name) + '</p>' +
          (price
            ? '<p class="cart-item-price">' + price + '</p>'
            : '<p class="cart-item-no-price">Consultar preço</p>') +
          '<div class="cart-item-ctrls">' +
            '<button class="cart-qty-btn" data-act="dec" data-id="' + _esc(item.id) + '" aria-label="Diminuir">−</button>' +
            '<span class="cart-qty">' + item.qty + '</span>' +
            '<button class="cart-qty-btn" data-act="inc" data-id="' + _esc(item.id) + '" aria-label="Aumentar">+</button>' +
            '<button class="cart-remove-btn" data-id="' + _esc(item.id) + '" aria-label="Remover produto">' +
              '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">' +
                '<path d="M18 6L6 18M6 6l12 12"/></svg>' +
            '</button>' +
          '</div>' +
        '</div>';
      list.appendChild(el);
    });

    // vincular controles
    list.querySelectorAll('[data-act]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = btn.dataset.id;
        var it = load().find(function (i) { return String(i.id) === String(id); });
        if (!it) return;
        setQty(id, it.qty + (btn.dataset.act === 'inc' ? 1 : -1));
      });
    });
    list.querySelectorAll('.cart-remove-btn').forEach(function (btn) {
      btn.addEventListener('click', function () { remove(btn.dataset.id); });
    });

    // total
    if (totalEl) {
      var currentItems = load();
      var totalPrice = currentItems.reduce(function (s, i) { return s + (parseFloat(i.price) || 0) * i.qty; }, 0);
      var allPriced = currentItems.every(function (i) { return parseFloat(i.price) > 0; });
      if (totalPrice > 0) {
        totalEl.innerHTML =
          '<strong>Total' + (allPriced ? '' : ' parcial') + ':</strong> R$ ' +
          totalPrice.toFixed(2).replace('.', ',') +
          (!allPriced ? '<br><small>Itens sem preço não incluídos</small>' : '');
        totalEl.style.display = 'block';
      } else {
        totalEl.style.display = 'none';
      }
    }
  }

  function _toast(name) {
    var t = document.getElementById('cart-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'cart-toast';
      t.className = 'cart-toast';
      document.body.appendChild(t);
    }
    var short = name.length > 34 ? name.slice(0, 34) + '…' : name;
    t.innerHTML = '<span style="color:#25D366;margin-right:0.3rem">✔</span><strong>' + _esc(short) + '</strong> adicionado ao pedido';
    t.classList.add('show');
    clearTimeout(t._t);
    t._t = setTimeout(function () { t.classList.remove('show'); }, 2800);
  }

  function _readCartCustomerFields() {
    var map = { tutor: 'cart-tutor', whatsapp: 'cart-whatsapp', pet_nome: 'cart-pet',
                pet_tipo: 'cart-pet-tipo', endereco: 'cart-endereco', bairro: 'cart-bairro' };
    var data = {};
    var any = false;
    Object.keys(map).forEach(function (key) {
      var el = document.getElementById(map[key]);
      if (el && el.value.trim()) { data[key] = el.value.trim(); any = true; }
    });
    return any ? data : null;
  }

  function _autofillCartCustomer() {
    if (!window.InDogCustomer) return;
    var has = window.InDogCustomer.hasData();
    window.InDogCustomer.autofill({
      'cart-tutor':    'tutor',
      'cart-whatsapp': 'whatsapp',
      'cart-pet':      'pet_nome',
      'cart-pet-tipo': 'pet_tipo',
      'cart-endereco': 'endereco',
      'cart-bairro':   'bairro',
    });
    var clearBtn = document.getElementById('cart-limpar-dados');
    if (clearBtn) clearBtn.style.display = has ? 'block' : 'none';
    var cb = document.getElementById('cart-salvar-dados');
    if (cb && !cb.dataset.touched) cb.checked = has;
    var details = document.getElementById('cart-customer-details');
    if (details && has) details.open = true;
  }

  function openPanel() {
    var panel = document.getElementById('cart-panel');
    var overlay = document.getElementById('cart-overlay');
    if (panel) { panel.classList.add('open'); panel.setAttribute('aria-hidden', 'false'); }
    if (overlay) overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    _renderPanel();
    _autofillCartCustomer();
  }

  function closePanel() {
    var panel = document.getElementById('cart-panel');
    var overlay = document.getElementById('cart-overlay');
    if (panel) { panel.classList.remove('open'); panel.setAttribute('aria-hidden', 'true'); }
    if (overlay) overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  // ── Expor API ────────────────────────────────────────────────────
  window.InDogCart = {
    add: add, remove: remove, setQty: setQty, clear: clear,
    load: load, totalItems: totalItems,
    sendToWhatsApp: sendToWhatsApp,
    open: openPanel, close: closePanel,
  };

  // ── Inicializar após DOM ─────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    _badge();

    // Abrir painel
    var toggle = document.getElementById('cart-toggle');
    if (toggle) toggle.addEventListener('click', openPanel);

    // Fechar
    var overlay = document.getElementById('cart-overlay');
    if (overlay) overlay.addEventListener('click', closePanel);
    var closeBtn = document.getElementById('cart-close-btn');
    if (closeBtn) closeBtn.addEventListener('click', closePanel);

    // Tecla Escape
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePanel(); });

    // Enviar para WhatsApp
    var sendBtn = document.getElementById('cart-send-wa');
    if (sendBtn) sendBtn.addEventListener('click', function () { sendToWhatsApp(); closePanel(); });

    // Limpar carrinho
    var clearBtn = document.getElementById('cart-clear');
    if (clearBtn) {
      clearBtn.addEventListener('click', function () {
        if (window.confirm('Limpar todos os itens do pedido?')) clear();
      });
    }

    // Limpar dados do cliente salvos
    var cartClearData = document.getElementById('cart-limpar-dados');
    if (cartClearData) {
      cartClearData.addEventListener('click', function () {
        if (!window.InDogCustomer) return;
        window.InDogCustomer.clear();
        ['cart-tutor', 'cart-whatsapp', 'cart-pet', 'cart-endereco', 'cart-bairro'].forEach(function (id) {
          var el = document.getElementById(id);
          if (el) el.value = '';
        });
        var sel = document.getElementById('cart-pet-tipo');
        if (sel) sel.selectedIndex = 0;
        var cb = document.getElementById('cart-salvar-dados');
        if (cb) { cb.checked = false; cb.dataset.touched = '1'; }
        var self = cartClearData;
        var orig = self.textContent;
        self.textContent = '✔ Dados limpos';
        setTimeout(function () { self.style.display = 'none'; self.textContent = orig; }, 1400);
      });
    }

    // Registrar interação manual no checkbox de salvar
    var cartSalvarCb = document.getElementById('cart-salvar-dados');
    if (cartSalvarCb) {
      cartSalvarCb.addEventListener('change', function () { this.dataset.touched = '1'; });
    }

    // Delegação de clique em botões "Adicionar ao pedido"
    document.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-add-to-cart]');
      if (!btn) return;
      add({
        id: btn.dataset.productId,
        name: btn.dataset.productName,
        price: btn.dataset.productPrice || '',
        image: btn.dataset.productImage || '',
      });
    });
  });

})();
