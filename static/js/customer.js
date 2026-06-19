// In Dog — Dados do cliente (localStorage, sem backend, sem cookies)
(function () {
  'use strict';

  var KEY = 'indog_customer_v1';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || 'null'); }
    catch (_) { return null; }
  }

  function save(data) {
    if (!data) return;
    localStorage.setItem(KEY, JSON.stringify(data));
  }

  function clear() {
    localStorage.removeItem(KEY);
  }

  function hasData() {
    var d = load();
    return !!(d && (d.tutor || d.whatsapp || d.pet_nome || d.endereco || d.bairro));
  }

  // Gera bloco de dados do cliente para mensagem WhatsApp
  // Recebe objeto { tutor, whatsapp, pet_nome, pet_tipo, endereco, bairro }
  // Se não receber, tenta localStorage
  function buildFooter(data) {
    if (!data) data = load();
    if (!data) return '';
    var lines = [];
    if (data.tutor)    lines.push('Nome: ' + data.tutor);
    if (data.whatsapp) lines.push('WhatsApp: ' + data.whatsapp);
    if (data.pet_nome) {
      var pet = 'Pet: ' + data.pet_nome;
      if (data.pet_tipo) pet += ' (' + data.pet_tipo + ')';
      lines.push(pet);
    }
    if (data.endereco) lines.push('Endereço: ' + data.endereco);
    if (data.bairro)   lines.push('Bairro: ' + data.bairro);
    if (!lines.length) return '';
    return '\n\n*Dados do cliente:*\n' + lines.join('\n');
  }

  // Preenche campos do DOM com dados salvos.
  // mapping: { 'idDoInput': 'chaveNoStorage' }
  // Só preenche campos que ainda estão vazios (não sobrescreve o que o usuário digitou).
  function autofill(mapping) {
    var data = load();
    if (!data) return false;
    var filled = false;
    Object.keys(mapping).forEach(function (fieldId) {
      var key = mapping[fieldId];
      if (!data[key]) return;
      var el = document.getElementById(fieldId);
      if (!el) return;
      if (el.tagName === 'SELECT') {
        if (el.value) return;
        for (var i = 0; i < el.options.length; i++) {
          if (el.options[i].value === data[key]) { el.selectedIndex = i; filled = true; break; }
        }
      } else {
        if (el.value) return;
        el.value = data[key];
        filled = true;
      }
    });
    return filled;
  }

  window.InDogCustomer = { load: load, save: save, clear: clear, hasData: hasData, buildFooter: buildFooter, autofill: autofill };
})();
