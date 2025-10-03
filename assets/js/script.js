'use strict';


const hasEl = (el) => !!el;
const toggleActive = (el) => el.classList.toggle('active');


document.addEventListener('DOMContentLoaded', () => {
  /* ========== Sidebar ========== */
  const sidebar = document.querySelector('[data-sidebar]');
  const sidebarBtn = document.querySelector('[data-sidebar-btn]');
  if (hasEl(sidebar) && hasEl(sidebarBtn)) {
    sidebarBtn.addEventListener('click', () => toggleActive(sidebar));
  }

  /* ========== Testimonials Modal ========== */
  const testimonialsItem = document.querySelectorAll('[data-testimonials-item]');
  const modalContainer = document.querySelector('[data-modal-container]');
  const modalCloseBtn = document.querySelector('[data-modal-close-btn]');
  const overlay = document.querySelector('[data-overlay]');
  const modalImg = document.querySelector('[data-modal-img]');
  const modalTitle = document.querySelector('[data-modal-title]');
  const modalText = document.querySelector('[data-modal-text]');

  const canUseModal = testimonialsItem.length && hasEl(modalContainer) && hasEl(modalCloseBtn) && hasEl(overlay) && hasEl(modalImg) && hasEl(modalTitle) && hasEl(modalText);

  const toggleModal = () => {
    modalContainer.classList.toggle('active');
    overlay.classList.toggle('active');
  };

  if (canUseModal) {
    for (let i = 0; i < testimonialsItem.length; i++) {
      testimonialsItem[i].addEventListener('click', function () {
        const avatar = this.querySelector('[data-testimonials-avatar]');
        const title = this.querySelector('[data-testimonials-title]');
        const text = this.querySelector('[data-testimonials-text]');
        if (avatar) { modalImg.src = avatar.src; modalImg.alt = avatar.alt || ''; }
        if (title) { modalTitle.innerHTML = title.innerHTML; }
        if (text)  { modalText.innerHTML = text.innerHTML; }
        toggleModal();
      });
    }
    modalCloseBtn.addEventListener('click', toggleModal);
    overlay.addEventListener('click', toggleModal);
  }

  /* ========== Custom Select  ========== */
  const select = document.querySelector('[data-select]');
  const selectItems = document.querySelectorAll('[data-select-item]');
  const selectValue = document.querySelector('[data-select-value]');
  const filterBtn = document.querySelectorAll('[data-filter-btn]');
  const filterItems = document.querySelectorAll('[data-filter-item]');

  if (hasEl(select)) {
    select.addEventListener('click', function () { toggleActive(this); });
  }

  const filterFunc = function (selectedValue) {
    if (!filterItems.length) return;
    for (let i = 0; i < filterItems.length; i++) {
      if (selectedValue === 'all' || selectedValue === filterItems[i].dataset.category) {
        filterItems[i].classList.add('active');
      } else {
        filterItems[i].classList.remove('active');
      }
    }
  };

  if (selectItems.length) {
    for (let i = 0; i < selectItems.length; i++) {
      selectItems[i].addEventListener('click', function () {
        const val = this.innerText.trim();
        if (hasEl(selectValue)) selectValue.innerText = val;
        if (hasEl(select)) toggleActive(select);
        filterFunc(val.toLowerCase());
      });
    }
  }

  if (filterBtn.length) {
    let lastClickedBtn = filterBtn[0];
    for (let i = 0; i < filterBtn.length; i++) {
      filterBtn[i].addEventListener('click', function () {
        const val = this.innerText.trim();
        if (hasEl(selectValue)) selectValue.innerText = val;
        filterFunc(val.toLowerCase());
        if (lastClickedBtn) lastClickedBtn.classList.remove('active');
        this.classList.add('active');
        lastClickedBtn = this;
      });
    }
  }

  /* ========== form ========== */
  const form = document.querySelector('[data-form]');
  const formInputs = document.querySelectorAll('[data-form-input]');
  const formBtn = document.querySelector('[data-form-btn]');
  if (hasEl(form) && formInputs.length && hasEl(formBtn)) {
    for (let i = 0; i < formInputs.length; i++) {
      formInputs[i].addEventListener('input', function () {
        if (form.checkValidity()) formBtn.removeAttribute('disabled');
        else formBtn.setAttribute('disabled', '');
      });
    }
  }

  /* ========== nav ========== */
  const navigationLinks = document.querySelectorAll('[data-nav-link]');
  const pages = document.querySelectorAll('[data-page]');

  function showPage(targetName) {
    const target = (targetName || '').trim().toLowerCase();
    // nav highlight
    for (let i = 0; i < navigationLinks.length; i++) {
      const link = navigationLinks[i];
      const name = link.textContent.trim().toLowerCase();
      if (name === target) link.classList.add('active');
      else link.classList.remove('active');
    }
    // page
    for (let j = 0; j < pages.length; j++) {
      const page = pages[j];
      page.classList.toggle('active', page.dataset.page === target);
    }
    // empty page，default about
    const anyActive = Array.from(pages).some(p => p.classList.contains('active'));
    if (!anyActive && pages.length) {
      for (let j = 0; j < pages.length; j++) pages[j].classList.remove('active');
      for (let i = 0; i < navigationLinks.length; i++) navigationLinks[i].classList.remove('active');
      const fallback = 'about';
      for (let j = 0; j < pages.length; j++) {
        pages[j].classList.toggle('active', pages[j].dataset.page === fallback);
      }
      for (let i = 0; i < navigationLinks.length; i++) {
        const link = navigationLinks[i];
        if (link.textContent.trim().toLowerCase() === fallback) link.classList.add('active');
      }
    }
    window.scrollTo(0, 0);
  }

  if (navigationLinks.length && pages.length) {
    // 
    for (let i = 0; i < navigationLinks.length; i++) {
      navigationLinks[i].addEventListener('click', function () {
        const target = this.textContent.trim().toLowerCase();
        history.replaceState(null, '', '#' + target); // refresh hash
        showPage(target);
      });
    }
    // 
    const initial = (location.hash || '#about').slice(1);
    showPage(initial);
  }
});

// === Chip Gallery Lightbox ===
(function () {
  const modal = document.getElementById('chip-modal');
  if (!modal) return;

  const modalImg = document.getElementById('chip-modal-img');
  const overlay = modal.querySelector('[data-chip-overlay]');
  const btnClose = modal.querySelector('[data-chip-close]');

  // 统一给所有 chip 图片绑定点击
  const chipImgs = document.querySelectorAll('.chips-list img');
  chipImgs.forEach(img => {
    // 若 img 包在 <a href="#"> 里，阻止默认跳转
    img.closest('a')?.addEventListener('click', e => e.preventDefault());

    img.style.cursor = 'zoom-in';
    img.addEventListener('click', () => {
      modal.classList.add('active');  // 触发现有 modal 的显示样式:contentReference[oaicite:5]{index=5}
      modalImg.src = img.src;
      modalImg.alt = img.alt || 'chip enlarged preview';
      // 键盘可达性：打开后把焦点给关闭按钮
      btnClose?.focus({ preventScroll: true });
      // 防止背景滚动（可选）
      document.documentElement.style.overflow = 'hidden';
    });
  });

  function closeModal() {
    modal.classList.remove('active');
    modalImg.removeAttribute('src');
    // 恢复滚动（可选）
    document.documentElement.style.overflow = '';
  }

  overlay?.addEventListener('click', closeModal);
  btnClose?.addEventListener('click', closeModal);

  // Esc 关闭
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });
})();
