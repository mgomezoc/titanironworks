/**
 * TITAN IRON WORKS - MAIN JAVASCRIPT
 * Custom Ornamental Iron Doors
 * ================================================
 */

(function() {
  'use strict';
  
  // ================================================
  // HEADER SCROLL EFFECT
  // ================================================
  
  const header = document.getElementById('header');
  
  function handleHeaderScroll() {
    if (window.pageYOffset > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }
  
  window.addEventListener('scroll', handleHeaderScroll);
  
  // ================================================
  // MOBILE MENU TOGGLE
  // ================================================
  
  const menuToggle = document.querySelector('.menu-toggle');
  const mobileNav = document.getElementById('mobileNav');
  const mobileNavLinks = document.querySelectorAll('.mobile-nav__link');
  
  if (menuToggle && mobileNav) {
    menuToggle.addEventListener('click', function() {
      const isActive = menuToggle.classList.toggle('active');
      mobileNav.classList.toggle('active');
      document.body.style.overflow = isActive ? 'hidden' : '';
      menuToggle.setAttribute('aria-expanded', isActive);
    });
    
    // Close mobile menu when clicking on links
    mobileNavLinks.forEach(function(link) {
      link.addEventListener('click', function() {
        menuToggle.classList.remove('active');
        mobileNav.classList.remove('active');
        document.body.style.overflow = '';
        menuToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }
  
  // ================================================
  // SMOOTH SCROLL FOR ANCHOR LINKS
  // ================================================
  
  document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      
      // Skip if it's just "#"
      if (href === '#') {
        e.preventDefault();
        return;
      }
      
      const target = document.querySelector(href);
      
      if (target) {
        e.preventDefault();
        const headerHeight = header ? header.offsetHeight : 0;
        const devBannerHeight = 40; // Dev banner height
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
        const offsetPosition = targetPosition - headerHeight - devBannerHeight;
        
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
  
  // ================================================
  // SCROLL REVEAL ANIMATION
  // ================================================
  
  const revealElements = document.querySelectorAll('.reveal');
  
  function revealOnScroll() {
    const windowHeight = window.innerHeight;
    
    revealElements.forEach(function(element) {
      const elementTop = element.getBoundingClientRect().top;
      const revealPoint = windowHeight - 100;
      
      if (elementTop < revealPoint) {
        element.classList.add('active');
      }
    });
  }
  
  if (revealElements.length > 0) {
    window.addEventListener('scroll', revealOnScroll);
    window.addEventListener('load', revealOnScroll);
    // Initial check
    revealOnScroll();
  }
  
  // ================================================
  // ACTIVE NAVIGATION HIGHLIGHTING
  // ================================================
  
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav__link');
  
  function highlightActiveNav() {
    if (!header || navLinks.length === 0) return;
    
    const scrollPos = window.scrollY + header.offsetHeight + 100;
    
    sections.forEach(function(section) {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');
      
      if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
        navLinks.forEach(function(link) {
          link.classList.remove('active');
          
          if (link.getAttribute('href') === '#' + sectionId) {
            link.classList.add('active');
          }
        });
      }
    });
  }
  
  if (sections.length > 0 && navLinks.length > 0) {
    window.addEventListener('scroll', highlightActiveNav);
  }
  
  // ================================================
  // CONTACT FORM HANDLING
  // ================================================
  
  const contactForm = document.getElementById('contactForm');
  
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Get form data
      const formData = new FormData(this);
      const name = formData.get('name');
      const email = formData.get('email');
      const phone = formData.get('phone');
      const message = formData.get('message');
      
      // Basic validation
      if (!name || !email || !message) {
        alert('Please fill in all required fields.');
        return;
      }
      
      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        alert('Please enter a valid email address.');
        return;
      }
      
      // Success message (In production, this should send to a backend)
      alert('Thank you for your message, ' + name + '! We will get back to you shortly at ' + email + '.');
      
      // Reset form
      this.reset();
    });
  }
  
  // ================================================
  // LAZY LOADING FOR IMAGES (FALLBACK)
  // ================================================
  
  if ('loading' in HTMLImageElement.prototype) {
    // Browser supports native lazy loading
    const images = document.querySelectorAll('img[loading="lazy"]');
    images.forEach(function(img) {
      img.src = img.src;
    });
  } else {
    // Fallback for browsers that don't support native lazy loading
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
    document.body.appendChild(script);
  }
  
  // ================================================
  // PREVENT FLASH OF UNSTYLED CONTENT
  // ================================================
  
  window.addEventListener('load', function() {
    document.body.classList.add('loaded');
  });
  
  // ================================================
  // DEV BANNER DISMISSIBLE (OPTIONAL)
  // ================================================
  
  const devBanner = document.querySelector('.dev-banner');
  
  if (devBanner) {
    // You can add a close button functionality here if needed
    // For now, the banner is persistent as requested
  }
  
  // ================================================
  // CONSOLE MESSAGE (OPTIONAL)
  // ================================================
  
  console.log('%c🔨 Titan Iron Works', 'font-size: 20px; font-weight: bold; color: #8b7355;');
  console.log('%cHandcrafted Ornamental Iron Doors', 'font-size: 14px; color: #666;');
  console.log('%c⚠️ Website in Development - Payment Pending', 'font-size: 12px; color: #ff6b35; font-weight: bold;');
  console.log('%cDeveloped by: Cesar Gomez (Rudo)', 'font-size: 12px; color: #888;');
  
})();
