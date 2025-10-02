'use strict';

/* 小工具 */
const hasEl = (el) => !!el;
const toggleActive = (el) => el.classList.toggle('active');

/* 等 DOM 准备好再绑事件，避免早绑定找不到元素 */
document.addEventListener('DOMContentLoaded', () => {
  /* ========== Sidebar（可选） ========== */
  const sidebar = document.querySelector('[data-sidebar]');
  const sidebarBtn = document.querySelector('[data-sidebar-btn]');
  if (hasEl(sidebar) && hasEl(sidebarBtn)) {
    sidebarBtn.addEventListener('click', () => toggleActive(sidebar));
  }

  /* ========== Testimonials Modal（可选） ========== */
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

  /* ========== Custom Select & 过滤（可选） ========== */
  const select = document.querySelector('[data-select]');
  const selectItems = document.querySelectorAll('[data-select-item]');
  const selectValue = document.querySelector('[data-select-value]'); // ← 修正拼写
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

  /* ========== 表单（可选） ========== */
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

  /* ========== 关键：页面导航（修复版） ========== */
  const navigationLinks = document.querySelectorAll('[data-nav-link]');
  const pages = document.querySelectorAll('[data-page]');

  function showPage(targetName) {
    const target = (targetName || '').trim().toLowerCase();
    // 切 nav 高亮
    for (let i = 0; i < navigationLinks.length; i++) {
      const link = navigationLinks[i];
      const name = link.textContent.trim().toLowerCase();
      if (name === target) link.classList.add('active');
      else link.classList.remove('active');
    }
    // 切页面
    for (let j = 0; j < pages.length; j++) {
      const page = pages[j];
      page.classList.toggle('active', page.dataset.page === target);
    }
    // 若没匹配到任何 page，默认 about
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
    // 绑定点击
    for (let i = 0; i < navigationLinks.length; i++) {
      navigationLinks[i].addEventListener('click', function () {
        const target = this.textContent.trim().toLowerCase();
        history.replaceState(null, '', '#' + target); // 更新哈希
        showPage(target);
      });
    }
    // 根据 URL 哈希初始化
    const initial = (location.hash || '#about').slice(1);
    showPage(initial);
  }
});