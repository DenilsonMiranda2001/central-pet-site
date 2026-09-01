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

// In Dog — tema visual do modal de agendamento
// O modal ainda possui estilos inline antigos. Este bloco aplica o visual atual
// da loja sem alterar a lógica de validação, localStorage ou envio por WhatsApp.
(function () {
  'use strict';

  var style = document.createElement('style');
  style.id = 'indog-appointment-theme';
  style.textContent = [
    '#modal-agendamento{background:rgba(47,29,19,.52)!important;backdrop-filter:blur(10px)!important;-webkit-backdrop-filter:blur(10px)!important;padding:1.25rem!important;align-items:flex-start!important;}',
    '#modal-agendamento>div{width:min(100%,760px)!important;max-width:760px!important;margin:2.5rem auto!important;background:#fffaf4!important;border:1px solid #eadbc8!important;border-radius:24px!important;box-shadow:0 28px 80px rgba(72,43,22,.24)!important;color:#2f1d13!important;overflow:hidden!important;}',
    '#modal-agendamento>div>div:first-child{background:linear-gradient(135deg,#fff8ee 0%,#f8ecdc 100%)!important;border-bottom:1px solid #eadbc8!important;padding:1.4rem 1.6rem!important;}',
    '#modal-agendamento>div>div:first-child>div:first-child{gap:.85rem!important;}',
    '#modal-agendamento>div>div:first-child>div:first-child>span{width:46px!important;height:46px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;border-radius:14px!important;background:#f09a25!important;font-size:1.35rem!important;box-shadow:0 8px 20px rgba(200,115,25,.2)!important;}',
    '#modal-titulo{color:#2f1d13!important;font-size:1.35rem!important;font-weight:900!important;letter-spacing:-.02em!important;}',
    '#modal-titulo+ p{color:#76543e!important;font-size:.82rem!important;margin-top:.18rem!important;}',
    '#modal-agendamento>div>div:first-child>button{background:#ffffff!important;border:1px solid #eadbc8!important;color:#76543e!important;border-radius:999px!important;width:38px!important;height:38px!important;box-shadow:0 5px 14px rgba(89,54,25,.08)!important;}',
    '#form-agendamento{padding:1.5rem 1.6rem 1.65rem!important;background:#fffaf4!important;}',
    '#form-agendamento .appointment-modal-grid{gap:1rem 1.15rem!important;}',
    '#form-agendamento label{color:#4a2d1d!important;font-size:.78rem!important;font-weight:800!important;letter-spacing:.005em!important;}',
    '#form-agendamento label span:not(:first-child){color:#7d6a5a!important;}',
    '#form-agendamento input:not([type="checkbox"]),#form-agendamento select,#form-agendamento textarea{width:100%!important;background:#ffffff!important;border:1px solid #ddc7ad!important;border-radius:12px!important;color:#2f1d13!important;padding:.72rem .9rem!important;font-family:inherit!important;font-size:.9rem!important;line-height:1.35!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.95)!important;transition:border-color .18s ease,box-shadow .18s ease!important;}',
    '#form-agendamento input:not([type="checkbox"]):focus,#form-agendamento select:focus,#form-agendamento textarea:focus{border-color:#c87319!important;box-shadow:0 0 0 4px rgba(200,115,25,.12)!important;outline:none!important;}',
    '#form-agendamento input::placeholder,#form-agendamento textarea::placeholder{color:#9a8775!important;opacity:1!important;}',
    '#form-agendamento select{color:#4a2d1d!important;}',
    '#form-agendamento textarea{min-height:88px!important;resize:vertical!important;}',
    '#form-agendamento [id$="-erro"]{color:#b74242!important;font-size:.7rem!important;font-weight:700!important;}',
    '#agendamento-alerta{background:#fff1ef!important;border:1px solid #f0c7c0!important;color:#9f3535!important;border-radius:12px!important;}',
    '#ag-salvar{accent-color:#c87319!important;width:16px!important;height:16px!important;margin-top:1px!important;}',
    '#ag-salvar+span{color:#695747!important;font-size:.78rem!important;}',
    '#ag-limpar-dados{color:#b74242!important;font-weight:700!important;}',
    '#form-agendamento .appointment-modal-grid>div[style*="border-top"]{border-top-color:#eadbc8!important;}',
    '#form-agendamento button[type="submit"]{background:linear-gradient(135deg,#219653,#16733e)!important;color:#fff!important;border-radius:999px!important;padding:.92rem 1.35rem!important;box-shadow:0 12px 28px rgba(33,150,83,.22)!important;font-size:.92rem!important;font-weight:900!important;}',
    '#form-agendamento button[type="submit"]+p{color:#7d6a5a!important;}',
    '#form-agendamento>p:last-child{color:#7d6a5a!important;}',
    '@media (max-width:640px){#modal-agendamento{padding:.65rem!important;}#modal-agendamento>div{margin:.65rem auto 1.25rem!important;border-radius:20px!important;}#modal-agendamento>div>div:first-child{padding:1.1rem 1rem!important;}#form-agendamento{padding:1rem!important;}#form-agendamento .appointment-modal-grid{grid-template-columns:1fr!important;gap:.85rem!important;}#form-agendamento .appointment-modal-grid>div{grid-column:1/-1!important;}#modal-titulo{font-size:1.15rem!important;}#modal-agendamento>div>div:first-child>div:first-child>span{width:40px!important;height:40px!important;font-size:1.15rem!important;}}'
  ].join('');

  document.head.appendChild(style);
})();
